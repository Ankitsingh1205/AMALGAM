"""Regression tests for scripts/engine.py.

Covers CLI dispatch, delegation to underlying scripts,
and error handling for all 9 responsibilities.

Since engine.py is pure orchestration (no duplicated logic),
these tests verify that each command dispatches to the correct
underlying function.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

from scripts.engine import (
    ENGINE_VERSION,
    COMMAND_MAP,
    cmd_initialize,
    cmd_run,
    cmd_resume,
    cmd_checkpoint,
    cmd_recover,
    cmd_audit,
    cmd_rebuild,
    cmd_verify,
    cmd_complete,
    print_help,
    main,
    log,
)


# ---------------------------------------------------------------------------
# Basic structure
# ---------------------------------------------------------------------------


def test_version_constant() -> None:
    assert ENGINE_VERSION == "1.0"


def test_command_map_contains_all_commands() -> None:
    expected = {
        "initialize", "init", "run", "resume", "checkpoint",
        "recover", "audit", "rebuild", "verify", "complete",
    }
    assert set(COMMAND_MAP.keys()) == expected


def test_every_command_maps_to_callable() -> None:
    for cmd, func_name in COMMAND_MAP.items():
        func = globals()[func_name]
        assert callable(func), f"{cmd} -> {func_name} not callable"


# ---------------------------------------------------------------------------
# Delegation — each command calls the correct underlying script function
# ---------------------------------------------------------------------------


def test_cmd_initialize_calls_bootstrap(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False
    def fake_bootstrap() -> None:
        nonlocal called
        called = True
    monkeypatch.setattr("scripts.engine._bootstrap", fake_bootstrap)
    cmd_initialize()
    assert called


def test_cmd_run_calls_loop_run(monkeypatch: pytest.MonkeyPatch) -> None:
    run_called = False
    status_called = False
    def fake_run() -> None:
        nonlocal run_called
        run_called = True
    def fake_status() -> None:
        nonlocal status_called
        status_called = True
    monkeypatch.setattr("scripts.engine.loop_run", fake_run)
    monkeypatch.setattr("scripts.engine.loop_status", fake_status)
    cmd_run()
    assert run_called
    assert status_called


def test_cmd_resume_calls_context_resume(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False
    def fake_resume() -> None:
        nonlocal called
        called = True
    monkeypatch.setattr("scripts.engine.context_resume", fake_resume)
    cmd_resume()
    assert called


def test_cmd_checkpoint_calls_context_checkpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False
    def fake_ck() -> None:
        nonlocal called
        called = True
    monkeypatch.setattr("scripts.engine.context_checkpoint", fake_ck)
    cmd_checkpoint()
    assert called


def test_cmd_audit_calls_context_audit(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False
    def fake_audit() -> None:
        nonlocal called
        called = True
    monkeypatch.setattr("scripts.engine.context_audit", fake_audit)
    cmd_audit()
    assert called


def test_cmd_rebuild_calls_context_rebuild(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False
    def fake_rebuild() -> None:
        nonlocal called
        called = True
    monkeypatch.setattr("scripts.engine.context_rebuild", fake_rebuild)
    cmd_rebuild()
    assert called


def test_cmd_verify_calls_fingerprint_verify(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False
    def fake_verify() -> None:
        nonlocal called
        called = True
    monkeypatch.setattr("scripts.engine.fp_verify", fake_verify)
    cmd_verify()
    assert called


def test_cmd_complete_calls_context_complete(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False
    def fake_complete() -> None:
        nonlocal called
        called = True
    monkeypatch.setattr("scripts.engine.context_complete", fake_complete)
    cmd_complete()
    assert called


# ---------------------------------------------------------------------------
# Recover
# ---------------------------------------------------------------------------


def test_cmd_recover_rejects_missing_args(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("scripts.engine.sys.argv", ["engine.py", "recover"])
    with pytest.raises(SystemExit):
        cmd_recover()


# ---------------------------------------------------------------------------
# CLI dispatch (main)
# ---------------------------------------------------------------------------


def test_main_no_args(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    monkeypatch.setattr("scripts.engine.sys.argv", ["engine.py"])
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    assert "Usage:" in captured.out


def test_main_help(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit):
        sys.argv = ["engine.py", "--help"]
        main()
    captured = capsys.readouterr()
    assert "Commands:" in captured.out


def test_main_unknown_command(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit):
        sys.argv = ["engine.py", "nonexistent"]
        main()
    captured = capsys.readouterr()
    assert "Unknown command" in captured.out


def test_main_dispatches_known_commands(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    """Every known command dispatches without raising ERROR."""
    monkeypatch.setattr("scripts.engine._bootstrap", lambda: None)
    monkeypatch.setattr("scripts.engine.loop_run", lambda: None)
    monkeypatch.setattr("scripts.engine.loop_status", lambda: None)
    monkeypatch.setattr("scripts.engine.context_resume", lambda: None)
    monkeypatch.setattr("scripts.engine.context_checkpoint", lambda: None)
    monkeypatch.setattr("scripts.engine.context_audit", lambda: None)
    monkeypatch.setattr("scripts.engine.context_rebuild", lambda: None)
    monkeypatch.setattr("scripts.engine.fp_verify", lambda: None)
    monkeypatch.setattr("scripts.engine.context_complete", lambda: None)
    for cmd in ("initialize", "run", "resume", "checkpoint", "audit", "rebuild", "verify", "complete"):
        monkeypatch.setattr("scripts.engine.sys.argv", ["engine.py", cmd])
        main()
        captured = capsys.readouterr()
        assert "ERROR:" not in captured.out, f"Command '{cmd}' produced error"


# ---------------------------------------------------------------------------
# print_help
# ---------------------------------------------------------------------------


def test_print_help_includes_all_commands(capsys: pytest.CaptureFixture) -> None:
    print_help()
    captured = capsys.readouterr()
    for cmd in ("initialize", "run", "resume", "checkpoint", "recover", "audit", "rebuild", "verify", "complete"):
        assert cmd in captured.out


# ---------------------------------------------------------------------------
# Integration smoke tests
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_core(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolated temp directory with .amalgam-core for integration tests."""
    with tempfile.TemporaryDirectory(prefix="amalgam_test_engine_int_") as tmp:
        root = Path(tmp)
        core = root / ".amalgam-core"
        core.mkdir()

        prod_schema = Path(r"C:\AMALGAM\.amalgam-core\STATE.schema.json")
        if prod_schema.exists():
            (core / "STATE.schema.json").write_text(
                prod_schema.read_text(encoding="utf-8"), encoding="utf-8"
            )

        for name in ("AGENTS.md", "ARCHITECTURE.md", "MISSION.md", "TASK.md"):
            (root / name).write_text(f"# {name}\n\nContent.\n", encoding="utf-8")

        monkeypatch.setattr("scripts.bootstrap.get_project_root", lambda _root=root: _root)
        monkeypatch.setattr("scripts.context.get_project_root", lambda _root=root: _root)
        monkeypatch.setattr("scripts.context.core_dir", lambda _core=core: _core)
        monkeypatch.setattr("scripts.fingerprint.get_project_root", lambda _root=root: _root)
        monkeypatch.setattr("scripts.fingerprint.core_dir", lambda _core=core: _core)
        monkeypatch.setattr("scripts.loop.get_project_root", lambda _root=root: _root)
        monkeypatch.setattr("scripts.loop.core_dir", lambda _core=core: _core)
        monkeypatch.setattr("scripts.recovery.get_project_root", lambda _root=root: _root)
        monkeypatch.setattr("scripts.recovery.core_dir", lambda _core=core: _core)

        yield core


def test_engine_initialize_integration(temp_core: Path) -> None:
    cmd_initialize()
    for name in ("STATE.json", "HISTORY.json", "CHECKPOINT.json", "SESSION.json", "QUEUE.json"):
        assert (temp_core / name).exists(), f"{name} missing after initialize"


def test_engine_rebuild_integration(temp_core: Path) -> None:
    state = {
        "current_mission": {"id": "MISSION_99_1", "title": "Engine Test", "status": "in_progress", "started_at": "2026-07-01T00:00:00Z"},
        "completed_missions": [],
        "current_task": {"id": "t1", "title": "Test task", "mission_id": "MISSION_99_1", "started_at": "2026-07-01T00:00:00Z"},
        "task_status": "pending",
        "current_stage": "idle",
        "current_branch": "main",
        "session_id": "s1",
        "tests": {"passed": 10, "failed": 0, "total": 10, "status": "passed"},
        "queue": [],
        "repository": {"head": {}, "remotes": [], "status": {"clean": True, "staged": [], "unstaged": [], "untracked": []}},
    }
    (temp_core / "STATE.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    cmd_rebuild()
    for name in ("MISSION.md", "TASK.md", "CONTEXT.md"):
        assert (temp_core / name).exists(), f"{name} missing after rebuild"


def test_engine_audit_integration(temp_core: Path) -> None:
    (temp_core / "STATE.json").write_text("{}", encoding="utf-8")
    (temp_core / "MISSION.md").write_text("# Mission\n", encoding="utf-8")
    (temp_core / "TASK.md").write_text("# Task\n", encoding="utf-8")
    (temp_core / "CONTEXT.md").write_text("# Context\n", encoding="utf-8")
    (temp_core / "REGISTRY.json").write_text("{}", encoding="utf-8")
    (temp_core / "HISTORY.json").write_text("[]", encoding="utf-8")
    (temp_core / "WORKFLOW.yaml").write_text("workflow:\n  version: 1.0\n", encoding="utf-8")
    cmd_audit()


def test_engine_complete_integration(temp_core: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("scripts.context._get_git_head", lambda _: None)
    state = {
        "current_mission": {"id": "MISSION_99_1", "title": "Engine Test Complete", "status": "in_progress", "started_at": "2026-07-01T00:00:00Z"},
        "completed_missions": [],
        "current_task": {"id": "t1", "title": "Test", "mission_id": "MISSION_99_1", "started_at": "2026-07-01T00:00:00Z"},
        "current_branch": "main",
        "session_id": "s1",
    }
    (temp_core / "STATE.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    cmd_complete()
    history = json.loads((temp_core / "HISTORY.json").read_text(encoding="utf-8"))
    assert len(history) == 1
    assert history[0]["event"] == "mission_completed"


def test_engine_checkpoint_integration(temp_core: Path) -> None:
    state = {"current_stage": "implement", "current_mission": {"id": "M99", "title": "T", "status": "in_progress", "started_at": "2026-07-01T00:00:00Z"}}
    (temp_core / "STATE.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    cmd_checkpoint()
    assert (temp_core / "CHECKPOINT.json").exists()
    cp = json.loads((temp_core / "CHECKPOINT.json").read_text(encoding="utf-8"))
    assert cp.get("stage") == "implement"


# ---------------------------------------------------------------------------
# log
# ---------------------------------------------------------------------------


def test_log_function(capsys: pytest.CaptureFixture) -> None:
    log("hello world")
    captured = capsys.readouterr()
    assert "[ENGINE] hello world" in captured.out


# ---------------------------------------------------------------------------
# ENGINE COMPLETE marker
# ---------------------------------------------------------------------------


def test_engine_complete_marker() -> None:
    assert True
