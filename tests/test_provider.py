"""Regression tests for scripts/provider.py.

Covers provider registration, health tracking, priority-based selection,
failover, rate-limit/timeout detection, error recording, cooldown,
state persistence/restoration, and recovery delegation.

All tests operate on isolated per-test temp directories so STATE.json
is never modified in the real repository.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from scripts.provider import (
    PROVIDER_VERSION,
    DEFAULT_ERROR_THRESHOLD,
    ProviderStatus,
    ProviderError,
    ProviderRecord,
    ProviderManager,
    create_manager,
    resume_manager,
    _record_to_dict,
    _dict_to_record,
    log,
)
from scripts.recovery import FailureClass


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_core(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create an isolated .amalgam-core with seeded files."""
    with tempfile.TemporaryDirectory(prefix="amalgam_test_provider_") as tmp:
        root = Path(tmp)
        core = root / ".amalgam-core"
        core.mkdir()

        # Seed an empty STATE.json.
        (core / "STATE.json").write_text("{}", encoding="utf-8")

        monkeypatch.setattr("scripts.context.get_project_root", lambda _root=root: _root)
        monkeypatch.setattr("scripts.context.core_dir", lambda _core=core: _core)

        yield core


@pytest.fixture
def manager() -> ProviderManager:
    """Return a fresh ProviderManager with two test providers."""
    return ProviderManager([
        {"name": "openai", "priority": 0, "model": "gpt-4o"},
        {"name": "anthropic", "priority": 1, "model": "claude-opus-4"},
    ])


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_provider_version() -> None:
    assert PROVIDER_VERSION == "1.0"


def test_default_error_threshold_is_positive() -> None:
    assert DEFAULT_ERROR_THRESHOLD > 0


# ---------------------------------------------------------------------------
# ProviderStatus
# ---------------------------------------------------------------------------


def test_provider_status_healthy_is_selectable() -> None:
    assert ProviderStatus.HEALTHY.is_selectable()


def test_provider_status_degraded_is_selectable() -> None:
    assert ProviderStatus.DEGRADED.is_selectable()


def test_provider_status_unavailable_not_selectable() -> None:
    assert not ProviderStatus.UNAVAILABLE.is_selectable()


def test_provider_status_disabled_not_selectable() -> None:
    assert not ProviderStatus.DISABLED.is_selectable()


def test_provider_status_enum_values() -> None:
    expected = {"HEALTHY", "DEGRADED", "UNAVAILABLE", "DISABLED"}
    actual = {s.value for s in ProviderStatus}
    assert actual == expected


# ---------------------------------------------------------------------------
# ProviderRecord
# ---------------------------------------------------------------------------


def test_provider_record_defaults() -> None:
    rec = ProviderRecord(provider_id="test-id", name="test")
    assert rec.priority == 0
    assert rec.status == ProviderStatus.HEALTHY
    assert rec.total_requests == 0
    assert rec.total_errors == 0
    assert rec.total_timeouts == 0
    assert rec.total_rate_limits == 0


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------


def test_record_to_dict_and_back() -> None:
    rec = ProviderRecord(
        provider_id="abc", name="openai", priority=1,
        status=ProviderStatus.DEGRADED, model="gpt-4o",
    )
    d = _record_to_dict(rec)
    restored = _dict_to_record(d)
    assert restored.provider_id == "abc"
    assert restored.name == "openai"
    assert restored.priority == 1
    assert restored.status == ProviderStatus.DEGRADED
    assert restored.model == "gpt-4o"


def test_dict_to_record_handles_invalid_status() -> None:
    rec = _dict_to_record({"name": "test", "status": "INVALID_STATUS"})
    assert rec.status == ProviderStatus.HEALTHY  # Falls back to HEALTHY


def test_dict_to_record_handles_missing_fields() -> None:
    rec = _dict_to_record({"name": "minimal"})
    assert rec.name == "minimal"
    assert rec.priority == 0
    assert rec.endpoint == ""


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_register_basic(manager: ProviderManager) -> None:
    assert len(manager.all_providers()) == 2


def test_register_returns_record(manager: ProviderManager) -> None:
    rec = manager.register({"name": "google", "priority": 2, "model": "gemini"})
    assert rec.name == "google"
    assert rec.priority == 2
    assert rec.registered_at != ""


def test_register_requires_name() -> None:
    mgr = ProviderManager()
    with pytest.raises(ProviderError, match="name"):
        mgr.register({})


def test_register_empty_name_raises() -> None:
    mgr = ProviderManager()
    with pytest.raises(ProviderError, match="name"):
        mgr.register({"name": ""})


def test_unregister(manager: ProviderManager) -> None:
    providers = manager.all_providers()
    pid = providers[0].provider_id
    assert manager.unregister(pid) is True
    assert len(manager.all_providers()) == 1


def test_unregister_nonexistent(manager: ProviderManager) -> None:
    assert manager.unregister("nonexistent-id") is False


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------


def test_get_by_id(manager: ProviderManager) -> None:
    providers = manager.all_providers()
    rec = manager.get(providers[0].provider_id)
    assert rec is not None
    assert rec.name == providers[0].name


def test_get_nonexistent(manager: ProviderManager) -> None:
    assert manager.get("nonexistent") is None


def test_get_by_name(manager: ProviderManager) -> None:
    rec = manager.get_by_name("anthropic")
    assert rec is not None
    assert rec.name == "anthropic"


def test_get_by_name_not_found(manager: ProviderManager) -> None:
    assert manager.get_by_name("nonexistent") is None


# ---------------------------------------------------------------------------
# Selection
# ---------------------------------------------------------------------------


def test_select_returns_highest_priority(manager: ProviderManager) -> None:
    selected = manager.select()
    assert selected is not None
    assert selected.name == "openai"  # priority=0


def test_select_skips_unavailable(manager: ProviderManager) -> None:
    # Make highest-priority provider unavailable.
    openai = manager.get_by_name("openai")
    assert openai is not None
    manager.set_status(openai.provider_id, ProviderStatus.UNAVAILABLE)

    selected = manager.select()
    assert selected is not None
    assert selected.name == "anthropic"


def test_select_skips_disabled(manager: ProviderManager) -> None:
    openai = manager.get_by_name("openai")
    assert openai is not None
    manager.set_status(openai.provider_id, ProviderStatus.DISABLED)

    selected = manager.select()
    assert selected is not None
    assert selected.name == "anthropic"


def test_select_returns_none_when_all_unavailable(manager: ProviderManager) -> None:
    for p in manager.all_providers():
        manager.set_status(p.provider_id, ProviderStatus.UNAVAILABLE)
    assert manager.select() is None


def test_select_empty_manager() -> None:
    mgr = ProviderManager()
    assert mgr.select() is None


def test_select_excluding(manager: ProviderManager) -> None:
    openai = manager.get_by_name("openai")
    assert openai is not None
    selected = manager.select_excluding({openai.provider_id})
    assert selected is not None
    assert selected.name == "anthropic"


def test_select_excluding_all(manager: ProviderManager) -> None:
    all_ids = {p.provider_id for p in manager.all_providers()}
    assert manager.select_excluding(all_ids) is None


# ---------------------------------------------------------------------------
# Priority management
# ---------------------------------------------------------------------------


def test_set_priority(manager: ProviderManager) -> None:
    anthropic = manager.get_by_name("anthropic")
    assert anthropic is not None

    # Promote anthropic above openai.
    manager.set_priority(anthropic.provider_id, -1)
    selected = manager.select()
    assert selected is not None
    assert selected.name == "anthropic"


def test_set_priority_nonexistent(manager: ProviderManager) -> None:
    assert manager.set_priority("bad-id", 0) is False


# ---------------------------------------------------------------------------
# Status management
# ---------------------------------------------------------------------------


def test_set_status(manager: ProviderManager) -> None:
    openai = manager.get_by_name("openai")
    assert openai is not None
    assert manager.set_status(openai.provider_id, ProviderStatus.DEGRADED)
    assert openai.status == ProviderStatus.DEGRADED


def test_set_status_nonexistent(manager: ProviderManager) -> None:
    assert manager.set_status("bad-id", ProviderStatus.HEALTHY) is False


# ---------------------------------------------------------------------------
# Cooldown
# ---------------------------------------------------------------------------


def test_set_and_clear_cooldown(manager: ProviderManager) -> None:
    openai = manager.get_by_name("openai")
    assert openai is not None

    # Set cooldown far in the future.
    future = "2099-01-01T00:00:00+00:00"
    assert manager.set_cooldown(openai.provider_id, future)

    # Should skip openai during selection.
    selected = manager.select()
    assert selected is not None
    assert selected.name == "anthropic"

    # Clear cooldown.
    assert manager.clear_cooldown(openai.provider_id)
    selected = manager.select()
    assert selected is not None
    assert selected.name == "openai"


def test_cooldown_nonexistent(manager: ProviderManager) -> None:
    assert manager.set_cooldown("bad-id", "2099-01-01T00:00:00+00:00") is False
    assert manager.clear_cooldown("bad-id") is False


# ---------------------------------------------------------------------------
# Health tracking: record_success
# ---------------------------------------------------------------------------


def test_record_success_increments(manager: ProviderManager) -> None:
    openai = manager.get_by_name("openai")
    assert openai is not None
    manager.record_success(openai.provider_id)
    assert openai.total_requests == 1
    assert openai.last_success_at != ""


def test_record_success_recovers_from_degraded(manager: ProviderManager) -> None:
    openai = manager.get_by_name("openai")
    assert openai is not None
    openai.status = ProviderStatus.DEGRADED
    manager.record_success(openai.provider_id)
    assert openai.status == ProviderStatus.HEALTHY


def test_record_success_nonexistent(manager: ProviderManager) -> None:
    # Should not raise.
    manager.record_success("nonexistent-id")


# ---------------------------------------------------------------------------
# Health tracking: record_error
# ---------------------------------------------------------------------------


def test_record_error_classifies_rate_limit(manager: ProviderManager) -> None:
    openai = manager.get_by_name("openai")
    assert openai is not None
    fc = manager.record_error(openai.provider_id, "429 Too Many Requests")
    assert fc == FailureClass.RATE_LIMIT
    assert openai.total_rate_limits == 1
    assert openai.total_errors == 1


def test_record_error_classifies_timeout(manager: ProviderManager) -> None:
    openai = manager.get_by_name("openai")
    assert openai is not None
    fc = manager.record_error(openai.provider_id, TimeoutError("timed out"))
    assert fc == FailureClass.TIMEOUT
    assert openai.total_timeouts == 1


def test_record_error_classifies_network(manager: ProviderManager) -> None:
    openai = manager.get_by_name("openai")
    assert openai is not None
    fc = manager.record_error(openai.provider_id, ConnectionError("refused"))
    assert fc == FailureClass.NETWORK_FAILURE


def test_record_error_degrades_on_threshold(manager: ProviderManager) -> None:
    openai = manager.get_by_name("openai")
    assert openai is not None

    for i in range(DEFAULT_ERROR_THRESHOLD):
        manager.record_error(openai.provider_id, f"error {i}")

    assert openai.status == ProviderStatus.DEGRADED


def test_record_error_unavailable_after_double_threshold(
    manager: ProviderManager,
) -> None:
    openai = manager.get_by_name("openai")
    assert openai is not None

    # First threshold: HEALTHY -> DEGRADED.
    for i in range(DEFAULT_ERROR_THRESHOLD):
        manager.record_error(openai.provider_id, f"error {i}")
    assert openai.status == ProviderStatus.DEGRADED

    # Second threshold worth of errors: DEGRADED -> UNAVAILABLE.
    for i in range(DEFAULT_ERROR_THRESHOLD):
        manager.record_error(openai.provider_id, f"error2 {i}")
    assert openai.status == ProviderStatus.UNAVAILABLE


def test_record_error_nonexistent_returns_classification(
    manager: ProviderManager,
) -> None:
    fc = manager.record_error("nonexistent", "429 Too Many Requests")
    assert fc == FailureClass.RATE_LIMIT


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------


def test_reset_errors(manager: ProviderManager) -> None:
    openai = manager.get_by_name("openai")
    assert openai is not None

    for i in range(DEFAULT_ERROR_THRESHOLD):
        manager.record_error(openai.provider_id, f"error {i}")
    assert openai.status == ProviderStatus.DEGRADED

    assert manager.reset_errors(openai.provider_id)
    assert openai.total_errors == 0
    assert openai.total_timeouts == 0
    assert openai.total_rate_limits == 0
    assert openai.status == ProviderStatus.HEALTHY


def test_reset_errors_nonexistent(manager: ProviderManager) -> None:
    assert manager.reset_errors("bad-id") is False


# ---------------------------------------------------------------------------
# Failover
# ---------------------------------------------------------------------------


def test_failover_selects_next_provider(manager: ProviderManager) -> None:
    openai = manager.get_by_name("openai")
    assert openai is not None

    next_prov, _ = manager.failover(
        openai.provider_id, "connection refused"
    )
    assert next_prov is not None
    assert next_prov.name == "anthropic"


def test_failover_returns_none_when_only_one_provider() -> None:
    mgr = ProviderManager([{"name": "only-one", "priority": 0}])
    prov = mgr.get_by_name("only-one")
    assert prov is not None

    next_prov, _ = mgr.failover(prov.provider_id, "error")
    assert next_prov is None


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def test_save_and_load_state(temp_core: Path) -> None:
    mgr = ProviderManager([
        {"name": "openai", "priority": 0, "model": "gpt-4o"},
        {"name": "anthropic", "priority": 1, "model": "claude-opus-4"},
    ])
    mgr.save_state()

    # Load into a new manager.
    mgr2 = ProviderManager()
    loaded = mgr2.load_state()
    assert loaded == 2

    providers = mgr2.all_providers()
    assert providers[0].name == "openai"
    assert providers[1].name == "anthropic"


def test_save_state_updates_active_provider(temp_core: Path) -> None:
    mgr = ProviderManager([
        {"name": "openai", "priority": 0, "model": "gpt-4o"},
    ])
    mgr.save_state()

    state = json.loads((temp_core / "STATE.json").read_text(encoding="utf-8"))
    assert state["providers"]["active_provider"] is not None
    assert state["provider"]["name"] == "openai"
    assert state["provider"]["model"] == "gpt-4o"


def test_load_state_empty(temp_core: Path) -> None:
    mgr = ProviderManager()
    loaded = mgr.load_state()
    assert loaded == 0


def test_load_state_preserves_metrics(temp_core: Path) -> None:
    mgr = ProviderManager([{"name": "openai", "priority": 0}])
    openai = mgr.get_by_name("openai")
    assert openai is not None
    openai.total_requests = 42
    openai.total_errors = 3
    mgr.save_state()

    mgr2 = ProviderManager()
    mgr2.load_state()
    restored = mgr2.get_by_name("openai")
    assert restored is not None
    assert restored.total_requests == 42
    assert restored.total_errors == 3


# ---------------------------------------------------------------------------
# Session continuity
# ---------------------------------------------------------------------------


def test_resume_manager_loads_persisted(temp_core: Path) -> None:
    mgr = ProviderManager([
        {"name": "openai", "priority": 0},
        {"name": "anthropic", "priority": 1},
    ])
    mgr.save_state()

    resumed = resume_manager()
    assert len(resumed.all_providers()) == 2


def test_resume_manager_fresh_when_no_state(temp_core: Path) -> None:
    resumed = resume_manager()
    assert len(resumed.all_providers()) == 0


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def test_report_structure(manager: ProviderManager) -> None:
    rpt = manager.report()
    assert rpt["version"] == PROVIDER_VERSION
    assert rpt["total_providers"] == 2
    assert rpt["healthy"] == 2
    assert rpt["degraded"] == 0
    assert rpt["unavailable"] == 0
    assert rpt["active_provider"] == "openai"
    assert len(rpt["roster"]) == 2


def test_report_empty_manager() -> None:
    mgr = ProviderManager()
    rpt = mgr.report()
    assert rpt["total_providers"] == 0
    assert rpt["active_provider"] is None


# ---------------------------------------------------------------------------
# create_manager
# ---------------------------------------------------------------------------


def test_create_manager_with_providers() -> None:
    mgr = create_manager([{"name": "test", "priority": 5}])
    assert len(mgr.all_providers()) == 1
    assert mgr.all_providers()[0].name == "test"


def test_create_manager_empty() -> None:
    mgr = create_manager()
    assert len(mgr.all_providers()) == 0


# ---------------------------------------------------------------------------
# Log helper
# ---------------------------------------------------------------------------


def test_log_does_not_crash() -> None:
    log("Test provider log message")


# ---------------------------------------------------------------------------
# Priority ordering
# ---------------------------------------------------------------------------


def test_providers_sorted_by_priority() -> None:
    mgr = ProviderManager([
        {"name": "low", "priority": 10},
        {"name": "high", "priority": 0},
        {"name": "mid", "priority": 5},
    ])
    providers = mgr.all_providers()
    assert providers[0].name == "high"
    assert providers[1].name == "mid"
    assert providers[2].name == "low"


# ---------------------------------------------------------------------------
# Multiple failovers
# ---------------------------------------------------------------------------


def test_multiple_failovers_exhaust_providers() -> None:
    mgr = ProviderManager([
        {"name": "primary", "priority": 0},
        {"name": "secondary", "priority": 1},
        {"name": "tertiary", "priority": 2},
    ])

    failed_ids: set[str] = set()

    # Fail primary.
    primary = mgr.get_by_name("primary")
    assert primary is not None
    failed_ids.add(primary.provider_id)
    mgr.set_status(primary.provider_id, ProviderStatus.UNAVAILABLE)

    # Fail secondary.
    secondary = mgr.get_by_name("secondary")
    assert secondary is not None
    failed_ids.add(secondary.provider_id)
    mgr.set_status(secondary.provider_id, ProviderStatus.UNAVAILABLE)

    # Only tertiary should remain.
    selected = mgr.select()
    assert selected is not None
    assert selected.name == "tertiary"

    # Fail tertiary.
    mgr.set_status(selected.provider_id, ProviderStatus.UNAVAILABLE)
    assert mgr.select() is None


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_register_with_custom_id() -> None:
    mgr = ProviderManager()
    rec = mgr.register({"name": "custom", "provider_id": "my-custom-id"})
    assert rec.provider_id == "my-custom-id"
    assert mgr.get("my-custom-id") is not None


def test_select_skips_cooldown_in_future(manager: ProviderManager) -> None:
    openai = manager.get_by_name("openai")
    assert openai is not None
    manager.set_cooldown(openai.provider_id, "2099-12-31T23:59:59+00:00")

    selected = manager.select()
    assert selected is not None
    assert selected.name == "anthropic"


def test_select_allows_expired_cooldown(manager: ProviderManager) -> None:
    openai = manager.get_by_name("openai")
    assert openai is not None
    # Set cooldown in the past.
    manager.set_cooldown(openai.provider_id, "2020-01-01T00:00:00+00:00")

    selected = manager.select()
    assert selected is not None
    assert selected.name == "openai"
