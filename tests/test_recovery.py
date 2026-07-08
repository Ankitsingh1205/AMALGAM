"""Regression tests for scripts/recovery.py.

Covers failure classification, backoff computation, retry strategy,
state restore, recovery records, and the recoverable_stage wrapper.

All tests operate on isolated per-test temp directories.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from scripts.recovery import (
    FailureClass,
    RetryStrategy,
    RecoveryRecord,
    RETRY_STRATEGIES,
    MAX_RETRIES_DEFAULT,
    classify,
    retry,
    recover,
    restore,
    report,
    log_recovery,
    recoverable_stage,
    _backoff_delay,
    log,
)
from scripts.loop import StageResult, ALL_STAGES


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_core(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create an isolated .amalgam-core with seeded files."""
    with tempfile.TemporaryDirectory(prefix="amalgam_test_recovery_") as tmp:
        root = Path(tmp)
        core = root / ".amalgam-core"
        core.mkdir()

        prod_schema = Path(r"C:\AMALGAM\.amalgam-core\STATE.schema.json")
        if prod_schema.exists():
            (core / "STATE.schema.json").write_text(
                prod_schema.read_text(encoding="utf-8"), encoding="utf-8"
            )

        monkeypatch.setattr("scripts.context.get_project_root", lambda _root=root: _root)
        monkeypatch.setattr("scripts.context.core_dir", lambda _core=core: _core)

        yield core


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_max_retries_default() -> None:
    assert MAX_RETRIES_DEFAULT == 3


def test_failure_class_enum_has_all_classes() -> None:
    expected = {
        "NETWORK_FAILURE",
        "RATE_LIMIT",
        "TIMEOUT",
        "CRASH",
        "KEYBOARD_INTERRUPT",
        "UNEXPECTED_EXCEPTION",
        "MANUAL_STOP",
    }
    actual = {fc.name for fc in FailureClass}
    assert actual == expected


# ---------------------------------------------------------------------------
# FailureClass methods
# ---------------------------------------------------------------------------


def test_failure_class_is_retryable() -> None:
    assert FailureClass.NETWORK_FAILURE.is_retryable()
    assert FailureClass.RATE_LIMIT.is_retryable()
    assert FailureClass.TIMEOUT.is_retryable()
    assert FailureClass.UNEXPECTED_EXCEPTION.is_retryable()
    assert not FailureClass.CRASH.is_retryable()
    assert not FailureClass.KEYBOARD_INTERRUPT.is_retryable()
    assert not FailureClass.MANUAL_STOP.is_retryable()


def test_failure_class_needs_restore() -> None:
    assert FailureClass.CRASH.needs_restore()
    assert FailureClass.NETWORK_FAILURE.needs_restore()
    assert FailureClass.TIMEOUT.needs_restore()
    assert not FailureClass.RATE_LIMIT.needs_restore()
    assert not FailureClass.KEYBOARD_INTERRUPT.needs_restore()
    assert not FailureClass.MANUAL_STOP.needs_restore()


def test_failure_class_is_graceful_stop() -> None:
    assert FailureClass.KEYBOARD_INTERRUPT.is_graceful_stop()
    assert FailureClass.MANUAL_STOP.is_graceful_stop()
    assert not FailureClass.NETWORK_FAILURE.is_graceful_stop()


# ---------------------------------------------------------------------------
# RetryStrategy
# ---------------------------------------------------------------------------


def test_retry_strategy_defaults() -> None:
    rs = RetryStrategy()
    assert rs.max_retries == 3
    assert rs.base_delay == 2.0
    assert rs.multiplier == 2.0
    assert rs.max_delay == 60.0
    assert rs.jitter == 0.2


def test_retry_strategies_cover_all_failure_classes() -> None:
    for fc in FailureClass:
        assert fc in RETRY_STRATEGIES, f"Missing strategy for {fc}"


# ---------------------------------------------------------------------------
# _backoff_delay
# ---------------------------------------------------------------------------


def test_backoff_delay_zero_jitter() -> None:
    strategy = RetryStrategy(base_delay=2.0, multiplier=2.0, max_delay=60.0, jitter=0.0)
    assert _backoff_delay(strategy, 0) == 2.0
    assert _backoff_delay(strategy, 1) == 4.0
    assert _backoff_delay(strategy, 2) == 8.0


def test_backoff_delay_respects_max() -> None:
    strategy = RetryStrategy(base_delay=10.0, multiplier=10.0, max_delay=50.0, jitter=0.0)
    assert _backoff_delay(strategy, 2) == 50.0


def test_backoff_delay_with_jitter() -> None:
    strategy = RetryStrategy(base_delay=2.0, multiplier=2.0, max_delay=60.0, jitter=0.5)
    delay = _backoff_delay(strategy, 1)
    assert 2.0 <= delay <= 6.0  # 4.0 +/- 50%


# ---------------------------------------------------------------------------
# classify
# ---------------------------------------------------------------------------


def test_classify_rate_limit_status_code() -> None:
    assert classify("error", {"status_code": 429}) == FailureClass.RATE_LIMIT


def test_classify_rate_limit_string() -> None:
    assert classify("Too Many Requests") == FailureClass.RATE_LIMIT


def test_classify_network_by_status() -> None:
    assert classify("error", {"status_code": 503}) == FailureClass.NETWORK_FAILURE


def test_classify_connection_error() -> None:
    assert classify(ConnectionError("refused")) == FailureClass.NETWORK_FAILURE


def test_classify_timeout() -> None:
    assert classify(TimeoutError("timed out")) == FailureClass.TIMEOUT
    assert classify("timeout occurred") == FailureClass.TIMEOUT


def test_classify_keyboard_interrupt() -> None:
    assert classify(KeyboardInterrupt()) == FailureClass.KEYBOARD_INTERRUPT


def test_classify_manual_stop() -> None:
    assert classify("manual stop", {"manual_stop": True}) == FailureClass.MANUAL_STOP


def test_classify_crash_keyword() -> None:
    assert classify("segfault at 0x0") == FailureClass.CRASH


def test_classify_unknown_default() -> None:
    assert classify("random error") == FailureClass.UNEXPECTED_EXCEPTION
    assert classify(ValueError("bad value")) == FailureClass.UNEXPECTED_EXCEPTION


# ---------------------------------------------------------------------------
# restore
# ---------------------------------------------------------------------------


def test_restore_returns_consistent_on_missing_files(temp_core: Path) -> None:
    result = restore()
    assert "restored_at" in result
    assert result["consistent"] is False
    assert len(result["warnings"]) > 0


def test_restore_detects_mission_mismatch(temp_core: Path) -> None:
    core = temp_core
    (core / "CHECKPOINT.json").write_text(
        json.dumps({"current_mission": "MISSION_A", "stage": 3}), encoding="utf-8"
    )
    (core / "SESSION.json").write_text("{}", encoding="utf-8")
    (core / "QUEUE.json").write_text("[]", encoding="utf-8")
    (core / "STATE.json").write_text(
        json.dumps({"current_mission": {"id": "MISSION_B"}}), encoding="utf-8"
    )
    result = restore()
    assert not result["consistent"]
    assert any("mismatch" in w.lower() for w in result["warnings"])


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------


def test_report_produces_structured_dict() -> None:
    record = RecoveryRecord(
        recovery_id="test-id",
        timestamp="2026-07-01T00:00:00Z",
        failure_class=FailureClass.RATE_LIMIT,
        stage_number=9,
        error_message="429 Too Many Requests",
        retry_count=1,
        strategy=RETRY_STRATEGIES[FailureClass.RATE_LIMIT],
        resolved=True,
        resolution="Retry succeeded.",
    )
    rpt = report(record)
    assert rpt["recovery_id"] == "test-id"
    assert rpt["failure_class"] == "RATE_LIMIT"
    assert rpt["stage_number"] == 9
    assert rpt["resolved"] is True
    assert rpt["strategy"]["max_retries"] == 3


def test_report_handles_none_strategy() -> None:
    record = RecoveryRecord(
        recovery_id="test-id-2",
        timestamp="2026-07-01T00:00:00Z",
        failure_class=FailureClass.UNEXPECTED_EXCEPTION,
        stage_number=5,
        error_message="Something broke",
        retry_count=0,
        strategy=None,
        resolved=False,
        resolution="Could not recover.",
    )
    rpt = report(record)
    assert rpt["strategy"] is None


# ---------------------------------------------------------------------------
# log_recovery
# ---------------------------------------------------------------------------


def test_log_recovery_appends_to_state(temp_core: Path) -> None:
    core = temp_core
    state: dict[str, Any] = {
        "loop": {
            "artifacts": {"recovery_log": []},
        },
    }
    (core / "STATE.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

    record = RecoveryRecord(
        recovery_id="log-test",
        timestamp="2026-07-01T00:00:00Z",
        failure_class=FailureClass.NETWORK_FAILURE,
        stage_number=3,
        error_message="Connection refused",
        retry_count=0,
        strategy=RETRY_STRATEGIES[FailureClass.NETWORK_FAILURE],
        resolved=True,
        resolution="Retry succeeded on attempt 1.",
    )
    log_recovery(record)

    saved = json.loads((core / "STATE.json").read_text(encoding="utf-8"))
    logs = saved["loop"]["artifacts"]["recovery_log"]
    assert len(logs) == 1
    assert logs[0]["recovery_id"] == "log-test"


# ---------------------------------------------------------------------------
# log helper
# ---------------------------------------------------------------------------


def test_recovery_log_does_not_crash() -> None:
    log("Test recovery log message")
