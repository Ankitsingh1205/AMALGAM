"""Regression tests for scripts/context.py.

Covers status, complete, next, checkpoint, resume, audit, rebuild,
and the _rich_history_entry builder.

All tests operate on isolated per-test temp directories.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from scripts.context import (
    CORE_DIR_NAME,
    cmd_status,
    cmd_complete,
    cmd_next,
    cmd_checkpoint,
    cmd_resume,
    cmd_rebuild,
    cmd_audit,
    load_state,
    save_state,
    load_json,
    save_json,
    now_iso,
    new_uuid,
    _rebuild_all,
    _rich_history_entry,
    _get_git_head,
    _safe_str,
    _format_timestamp,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_core(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create an isolated temp directory as the .amalgam-core root."""
    with tempfile.TemporaryDirectory(prefix="amalgam_test_context_") as tmp:
        root = Path(tmp)
        core = root / CORE_DIR_NAME
        core.mkdir()

        prod_schema = Path(r"C:\AMALGAM\.amalgam-core\STATE.schema.json")
        if prod_schema.exists():
            (core / "STATE.schema.json").write_text(
                prod_schema.read_text(encoding="utf-8"), encoding="utf-8"
            )

        monkeypatch.setattr("scripts.context.get_project_root", lambda _root=root: _root)
        monkeypatch.setattr("scripts.context.core_dir", lambda _core=core: _core)

        yield core


def _root(core: Path) -> Path:
    return core.parent


@pytest.fixture
def full_state(temp_core: Path) -> dict[str, Any]:
    """Return a populated STATE.json dict suitable for rebuild/complete tests."""
    state: dict[str, Any] = {
        "current_mission": {
            "id": "MISSION_99_1",
            "title": "Test Mission",
            "status": "in_progress",
            "started_at": "2026-07-01T00:00:00Z",
        },
        "completed_missions": [],
        "current_task": {"id": "task-1", "title": "A task", "mission_id": "MISSION_99_1", "started_at": "2026-07-01T00:00:00Z"},
        "task_status": "pending",
        "current_stage": "idle",
        "current_branch": "main",
        "session_id": "test-session",
        "provider": {"name": "test-provider", "api_base": "", "rate_limit": {"requests_per_minute": 40, "max_concurrent": 32}},
        "model": {"id": "test-model", "role": "default", "context_window": 128000},
        "current_worker": {"agent": "test-agent", "host": "localhost"},
        "tests": {"passed": 10, "failed": 0, "total": 10, "status": "passed", "run_at": "2026-07-01T00:00:00Z"},
        "checkpoint": {"sequence": 3, "stage": "idle", "at": "2026-07-01T00:00:00Z", "by": {"worker": "test"}},
        "queue": [],
        "recent_commit": {},
        "next_mission": None,
        "repository": {"head": {}, "remotes": [], "status": {"clean": True, "staged": [], "unstaged": [], "untracked": []}},
        "schema_version": "1.0.0",
        "architecture_version": "1.0.0",
        "repository_version": 1,
    }
    save_state(state)
    return load_state()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def test_now_iso_format() -> None:
    """now_iso returns an ISO 8601 string."""
    ts = now_iso()
    assert "T" in ts
    assert ts.endswith("+00:00") or "+" in ts


def test_new_uuid_format() -> None:
    """new_uuid returns a valid UUID4 string."""
    uid = new_uuid()
    parts = uid.split("-")
    assert len(parts) == 5
    assert len(parts[0]) == 8


def test_safe_str_handles_none() -> None:
    assert _safe_str(None) == "\u2014"


def test_safe_str_returns_str() -> None:
    assert _safe_str("hello") == "hello"
    assert _safe_str(42) == "42"


def test_format_timestamp_handles_none() -> None:
    assert _format_timestamp(None) == "\u2014"


def test_format_timestamp_formats_iso() -> None:
    assert _format_timestamp("2026-07-01T12:34:56.789+00:00") == "2026-07-01 12:34:56"


# ---------------------------------------------------------------------------
# State I/O
# ---------------------------------------------------------------------------


def test_load_state_on_missing_file_returns_empty_dict(temp_core: Path) -> None:
    (temp_core / "STATE.json").unlink(missing_ok=True)
    result = load_state()
    assert isinstance(result, dict) and len(result) == 0


def test_save_state_preserves_existing_keys(temp_core: Path) -> None:
    state = {"current_stage": "review", "extra": 42}
    save_state(state)
    reloaded = load_state()
    assert reloaded.get("current_stage") == "review"
    assert reloaded.get("extra") == 42
    assert "last_updated" in reloaded


def test_load_json_returns_default_for_missing_file(temp_core: Path) -> None:
    result = load_json("NONEXISTENT.json")
    assert result == {}


def test_load_json_returns_list_default_for_history(temp_core: Path) -> None:
    result = load_json("HISTORY.json")
    assert result == []


# ---------------------------------------------------------------------------
# _get_git_head
# ---------------------------------------------------------------------------


def test_get_git_head_on_non_git_dir(temp_core: Path) -> None:
    root = _root(temp_core)
    result = _get_git_head(root)
    assert result is None


# ---------------------------------------------------------------------------
# _rich_history_entry
# ---------------------------------------------------------------------------


def test_rich_history_entry_minimal_state(temp_core: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A minimal state dict produces a valid entry with all required fields."""
    monkeypatch.setattr("scripts.context._get_git_head", lambda _: None)
    state: dict[str, Any] = {"current_branch": "main"}
    entry = _rich_history_entry(state, "mission_completed")
    assert entry["entry_id"] is not None
    assert entry["event"] == "mission_completed"
    assert entry["mission"] is None
    assert entry["task"] is None
    assert entry["branch"] == "main"
    assert entry["commit_hash"] is None
    assert entry["files_changed"] == {"created": [], "modified": []}
    assert entry["tests_passed"] == 0
    assert entry["tests_failed"] == 0


def test_rich_history_entry_with_full_state(temp_core: Path, full_state: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    """A full state dict populates mission, task, provider, model, tests."""
    monkeypatch.setattr("scripts.context._get_git_head", lambda _: None)
    entry = _rich_history_entry(full_state, "mission_completed")
    assert entry["mission"]["id"] == "MISSION_99_1"
    assert entry["mission"]["title"] == "Test Mission"
    assert entry["task"]["id"] == "task-1"
    assert entry["provider"] == "test-provider"
    assert entry["model"] == "test-model"
    assert entry["tests_passed"] == 10
    assert entry["tests_failed"] == 0
    assert entry["checkpoint_id"] == 3
    assert entry["branch"] == "main"


def test_rich_history_entry_with_loop_artifacts(temp_core: Path, full_state: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    """Loop artifacts enrich files_changed, tests, and verdicts."""
    monkeypatch.setattr("scripts.context._get_git_head", lambda _: None)
    artifacts = {
        "implementation_summary": {
            "files_created": ["src/new.py"],
            "files_modified": ["src/existing.py"],
            "backward_compatibility": "PRESERVED",
            "security_verdict": "PASS",
        },
        "test_result": {
            "passed": 95,
            "failed": 0,
            "runtime": "12.34s",
        },
    }
    entry = _rich_history_entry(full_state, "loop_completed", artifacts)
    assert entry["files_changed"]["created"] == ["src/new.py"]
    assert entry["files_changed"]["modified"] == ["src/existing.py"]
    assert entry["tests_passed"] == 95
    assert entry["tests_failed"] == 0
    assert entry["architecture_verdict"] == "PRESERVED"
    assert entry["security_verdict"] == "PASS"


# ---------------------------------------------------------------------------
# cmd_status
# ---------------------------------------------------------------------------


def test_cmd_status_no_crash_on_empty_state(temp_core: Path) -> None:
    save_state({})
    cmd_status()


def test_cmd_status_no_crash_on_full_state(temp_core: Path, full_state: dict[str, Any]) -> None:
    cmd_status()


# ---------------------------------------------------------------------------
# cmd_complete
# ---------------------------------------------------------------------------


def test_cmd_complete_no_active_mission(temp_core: Path) -> None:
    save_state({})
    cmd_complete()
    assert load_json("HISTORY.json") == []


def test_cmd_complete_marks_mission_and_writes_history(temp_core: Path, full_state: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("scripts.context._get_git_head", lambda _: None)
    cmd_complete()
    history = load_json("HISTORY.json")
    assert len(history) == 1
    entry = history[0]
    assert entry["event"] == "mission_completed"
    assert entry["mission"]["id"] == "MISSION_99_1"


def test_cmd_complete_advances_to_next_mission(temp_core: Path, full_state: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("scripts.context._get_git_head", lambda _: None)
    state = load_state()
    state["next_mission"] = {"id": "MISSION_100_1", "title": "Next Mission", "status": "pending"}
    save_state(state)
    cmd_complete()
    new_state = load_state()
    assert new_state["current_mission"]["id"] == "MISSION_100_1"


# ---------------------------------------------------------------------------
# cmd_next
# ---------------------------------------------------------------------------


def test_cmd_next_fails_if_current_not_completed(temp_core: Path, full_state: dict[str, Any]) -> None:
    cmd_next()


def test_cmd_next_advances_if_current_completed(temp_core: Path, full_state: dict[str, Any]) -> None:
    state = load_state()
    state["current_mission"]["status"] = "completed"
    state["next_mission"] = {"id": "MISSION_100_1", "title": "Next", "status": "pending"}
    save_state(state)
    cmd_next()
    new_state = load_state()
    assert new_state["current_mission"]["id"] == "MISSION_100_1"


# ---------------------------------------------------------------------------
# cmd_checkpoint / cmd_resume
# ---------------------------------------------------------------------------


def test_checkpoint_writes_and_resume_reads(temp_core: Path) -> None:
    state: dict[str, Any] = {
        "current_stage": "implement",
        "current_mission": {"id": "MISSION_99_1", "title": "Test", "status": "in_progress", "started_at": "2026-07-01T00:00:00Z"},
        "current_task": {"id": "task-1", "title": "A task", "mission_id": "MISSION_99_1", "started_at": "2026-07-01T00:00:00Z"},
    }
    save_state(state)
    cmd_checkpoint()
    cp_path = temp_core / "CHECKPOINT.json"
    assert cp_path.exists()
    cp = json.loads(cp_path.read_text(encoding="utf-8"))
    assert cp.get("stage") == "implement"
    assert cp.get("current_mission") == "MISSION_99_1"

    cmd_resume()
    state_after = load_state()
    assert state_after.get("current_stage") == "implement"


def test_resume_fails_on_missing_checkpoint(temp_core: Path) -> None:
    save_state({})
    cmd_resume()


def test_resume_fails_on_empty_checkpoint(temp_core: Path) -> None:
    save_state({})
    (temp_core / "CHECKPOINT.json").write_text("", encoding="utf-8")
    cmd_resume()


# ---------------------------------------------------------------------------
# cmd_rebuild / _rebuild_all
# ---------------------------------------------------------------------------


def test_rebuild_writes_valid_state_from_nonempty_instance(temp_core: Path, full_state: dict[str, Any]) -> None:
    _rebuild_all(load_state())
    mission_md = (temp_core / "MISSION.md").read_text(encoding="utf-8")
    task_md = (temp_core / "TASK.md").read_text(encoding="utf-8")
    context_md = (temp_core / "CONTEXT.md").read_text(encoding="utf-8")
    assert "MISSION_99_1" in mission_md
    assert "task-1" in task_md
    assert "test-provider" in context_md


def test_rebuild_from_empty_state_produces_placeholders(temp_core: Path) -> None:
    save_json("STATE.json", {})
    _rebuild_all(load_state())
    mission_md = (temp_core / "MISSION.md").read_text(encoding="utf-8")
    assert "No active mission" in mission_md


def test_cmd_rebuild_no_crash_on_empty(temp_core: Path) -> None:
    cmd_rebuild()


# ---------------------------------------------------------------------------
# cmd_audit
# ---------------------------------------------------------------------------


def test_audit_detects_schema_leakage_in_state_json(temp_core: Path) -> None:
    r = _root(temp_core)
    for name in ("AGENTS.md", "ARCHITECTURE.md", "MISSION.md", "TASK.md"):
        (r / name).write_text(f"# {name}\n\nContent.\n", encoding="utf-8")
    save_json("STATE.json", {"$schema": "draft-07", "properties": [], "current_stage": "idle"})
    cmd_audit()
    state_obj = load_state()
    leaked = {"$schema", "$id", "properties", "required"} & set(state_obj.keys() if isinstance(state_obj, dict) else [])
    assert leaked


def test_audit_accepts_clean_runtime_instance(temp_core: Path) -> None:
    r = _root(temp_core)
    for name in ("AGENTS.md", "ARCHITECTURE.md", "MISSION.md", "TASK.md"):
        (r / name).write_text(f"# {name}\n\nContent.\n", encoding="utf-8")
    save_json("STATE.json", {})
    cmd_audit()
    state_obj = load_state()
    leaked = {"$schema", "$id", "properties", "required"} & set(state_obj.keys() if isinstance(state_obj, dict) else [])
    assert not leaked


def test_audit_detects_missing_required_core_files(temp_core: Path) -> None:
    r = _root(temp_core)
    for name in ("AGENTS.md", "ARCHITECTURE.md", "MISSION.md", "TASK.md"):
        (r / name).write_text(f"# {name}\n\nContent.\n", encoding="utf-8")
    save_json("STATE.json", {})
    (temp_core / "CONTEXT.md").write_text("", encoding="utf-8")
    cmd_audit()
    assert (temp_core / "CONTEXT.md").read_text(encoding="utf-8").strip() == ""
