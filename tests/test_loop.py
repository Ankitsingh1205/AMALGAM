"""Regression tests for scripts/loop.py.

Covers stage dispatch, checkpoint management, run/resume/abort flows,
and the upgraded _stage_16_history_update.

All tests operate on isolated per-test temp directories.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from scripts.loop import (
    LOOP_VERSION,
    STAGE_NAMES,
    PHASE_NAMES,
    ALL_STAGES,
    MAX_RETRIES,
    StageResult,
    LoopError,
    run_stage,
    run,
    resume,
    abort,
    status,
    _default_loop_block,
    _load_loop_state,
    _full_state,
    _mark_completed,
    _next_stage,
    _elapsed,
    log,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_core(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create isolated .amalgam-core with a default loop block in STATE.json."""
    with tempfile.TemporaryDirectory(prefix="amalgam_test_loop_") as tmp:
        root = Path(tmp)
        core = root / ".amalgam-core"
        core.mkdir()

        prod_schema = Path(__file__).resolve().parents[1] / ".amalgam-core" / "STATE.schema.json"
        if prod_schema.exists():
            (core / "STATE.schema.json").write_text(
                prod_schema.read_text(encoding="utf-8"), encoding="utf-8"
            )

        # Seed STATE.json with a default loop block so _load_loop_state works.
        loop = _default_loop_block()
        state: dict[str, Any] = {"loop": loop, "last_updated": "2026-07-01T00:00:00Z"}
        (core / "STATE.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

        monkeypatch.setattr("scripts.context.get_project_root", lambda _root=root: _root)
        monkeypatch.setattr("scripts.context.core_dir", lambda _core=core: _core)
        monkeypatch.setattr("scripts.loop.core_dir", lambda _core=core: _core)
        monkeypatch.setattr("scripts.loop.get_project_root", lambda _root=root: _root)
        monkeypatch.setattr("scripts.context._get_git_head", lambda _: None)

        yield core


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_loop_version_constant() -> None:
    assert LOOP_VERSION == "1.0"


def test_max_retries_constant() -> None:
    assert MAX_RETRIES == 3


def test_all_stages_has_17_entries() -> None:
    assert ALL_STAGES == list(range(1, 18))


def test_stage_names_has_17_entries() -> None:
    assert len(STAGE_NAMES) == 17


def test_phase_names_has_17_entries() -> None:
    assert len(PHASE_NAMES) == 17


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def test_log_does_not_crash() -> None:
    log("Test log message")


def test_elapsed_returns_zero_for_invalid() -> None:
    assert _elapsed("not-a-date") == 0.0


def test_elapsed_returns_float_for_valid() -> None:
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).isoformat()
    result = _elapsed(ts)
    assert isinstance(result, float)
    assert result >= 0.0


# ---------------------------------------------------------------------------
# _default_loop_block
# ---------------------------------------------------------------------------


def test_default_loop_block_has_all_stages_pending() -> None:
    block = _default_loop_block()
    assert block["version"] == LOOP_VERSION
    assert block["phase"] == "UNDERSTAND"
    assert block["stage"] == 1
    for s in ALL_STAGES:
        assert block["checkpoints"][f"stage_{s}"] == "pending"
    assert block["verdict"] is None


# ---------------------------------------------------------------------------
# _next_stage
# ---------------------------------------------------------------------------


def test_next_stage_returns_none_past_17() -> None:
    assert _next_stage(17) is None


def test_next_stage_increments() -> None:
    assert _next_stage(1) == 2
    assert _next_stage(16) == 17


# ---------------------------------------------------------------------------
# _mark_completed
# ---------------------------------------------------------------------------


def test_mark_completed_advances_stage(temp_core: Path) -> None:
    loop = _load_loop_state()
    _mark_completed(1, loop)
    assert loop["checkpoints"]["stage_1"] == "completed"
    assert loop["stage"] == 2


def test_mark_completed_stops_at_17(temp_core: Path) -> None:
    loop = _load_loop_state()
    _mark_completed(17, loop)
    assert loop["stage"] == 17
    assert loop["phase"] == "COMPLETE"


# ---------------------------------------------------------------------------
# run_stage dispatch
# ---------------------------------------------------------------------------


def test_run_stage_invalid_number_raises() -> None:
    with pytest.raises(LoopError, match="Invalid stage number"):
        run_stage(99)


def test_run_stage_valid_dispatch(temp_core: Path) -> None:
    result = run_stage(1)
    assert result.success
    assert "Stage 1" in result.message


def test_run_stage_16_writes_rich_history_entry(temp_core: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Stage 16 appends a rich entry to HISTORY.json."""

    # Simulate stages 1-15 completed so stage 16 preconditions are met.
    loop = _load_loop_state()
    for s in range(1, 16):
        loop["checkpoints"][f"stage_{s}"] = "completed"
    state = _full_state()
    state["loop"] = loop
    (temp_core / "STATE.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

    # Initialize HISTORY.json as empty array.
    (temp_core / "HISTORY.json").write_text("[]", encoding="utf-8")

    result = run_stage(16)
    assert result.success
    history = json.loads((temp_core / "HISTORY.json").read_text(encoding="utf-8"))
    assert len(history) == 1
    entry = history[0]
    assert entry["event"] == "loop_completed"
    assert "entry_id" in entry
    assert "stages" in entry
    assert entry["verdict"] == "COMPLETE"


# ---------------------------------------------------------------------------
# run()
# ---------------------------------------------------------------------------


def test_run_does_nothing_on_completed_verdict(temp_core: Path) -> None:
    loop = _load_loop_state()
    loop["verdict"] = "LOOP_COMPLETE"
    state = _full_state()
    state["loop"] = loop
    (temp_core / "STATE.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    run()


def test_run_does_nothing_on_failed_verdict(temp_core: Path) -> None:
    loop = _load_loop_state()
    loop["verdict"] = "LOOP_FAILED"
    state = _full_state()
    state["loop"] = loop
    (temp_core / "STATE.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    run()


def test_run_does_nothing_on_terminated_phase(temp_core: Path) -> None:
    loop = _load_loop_state()
    loop["phase"] = "TERMINATED"
    state = _full_state()
    state["loop"] = loop
    (temp_core / "STATE.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    run()


def test_run_executes_stages_from_current_state(temp_core: Path) -> None:
    """Run from Stage 1 executes a few stages before hitting the test baseline."""
    run()
    loop = _load_loop_state()
    assert loop["stage"] >= 2


# ---------------------------------------------------------------------------
# resume()
# ---------------------------------------------------------------------------


def test_resume_starts_fresh_after_terminated(temp_core: Path) -> None:
    loop = _load_loop_state()
    loop["phase"] = "TERMINATED"
    loop["verdict"] = "LOOP_FAILED"
    state = _full_state()
    state["loop"] = loop
    (temp_core / "STATE.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    resume()
    new_loop = _load_loop_state()
    assert new_loop["phase"] == "UNDERSTAND"
    assert new_loop["stage"] >= 1


# ---------------------------------------------------------------------------
# abort()
# ---------------------------------------------------------------------------


def test_abort_marks_terminated(temp_core: Path) -> None:
    abort()
    loop = _load_loop_state()
    assert loop["phase"] == "TERMINATED"
    assert loop["verdict"] == "LOOP_FAILED"


# ---------------------------------------------------------------------------
# status()
# ---------------------------------------------------------------------------


def test_status_does_not_crash(temp_core: Path) -> None:
    status()


# ---------------------------------------------------------------------------
# Stage dispatch table completeness
# ---------------------------------------------------------------------------


def test_all_stages_have_function_in_dispatch() -> None:
    from scripts.loop import STAGE_FUNCTIONS
    for s in ALL_STAGES:
        assert s in STAGE_FUNCTIONS, f"Stage {s} missing from STAGE_FUNCTIONS"
