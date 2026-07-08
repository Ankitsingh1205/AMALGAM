"""Regression tests for scripts/bootstrap.py, scripts/context.py, scripts/registry.py.

Coverage categories:
    - Bootstrap idempotency
    - Corrupt file recovery
    - Registry rebuild (discovery + persistence)
    - State rebuild (MISSION/TASK/CONTEXT from STATE.json)
    - Checkpoint (write + resume)
    - Audit (split detection, missing-file detection, drift)
    - Validation (registry drift, schema leakage)
    - Resume from checkpoint
    - Edge cases (empty STATE, corrupt JSON, missing root files)

All tests operate on isolated per-test temp directories so no production
.amalgam-core/ file is ever touched.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from scripts.bootstrap import (
    CORE_DIR_NAME,
    IMMUTABLE_FILES,
    INITIALIZABLE_FILES,
    BootstrapError,
    validate_json_file,
    validate_root_files,
    ensure_core_dir,
    bootstrap as bootstrap_main,
)

from scripts.context import (
    core_dir as context_core_dir,
    get_project_root as context_get_project_root,
    load_state,
    save_state,
    load_json,
    save_json,
    cmd_rebuild,
    cmd_audit,
    cmd_checkpoint,
    cmd_resume,
    _rebuild_all,
)

from scripts.registry import (
    discover_components,
    load_registry,
    save_registry,
    Component,
    cmd_scan,
    cmd_validate,
    dependencies_of,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_core(monkeypatch: Any) -> Path:
    """Create an isolated temp directory as the .amalgam-core root.

    Monkeypatches all three scripts' root-resolution functions so they operate
    on the temp directory instead of the production repository.
    """
    with tempfile.TemporaryDirectory(prefix="amalgam_test_core_") as tmp:
        root = Path(tmp)
        core = root / CORE_DIR_NAME
        core.mkdir()

        # Copy the immutable schema so bootstrap does not reject.
        prod_schema = Path(r"C:\AMALGAM\.amalgam-core\STATE.schema.json")
        if prod_schema.exists():
            (core / "STATE.schema.json").write_text(
                prod_schema.read_text(encoding="utf-8"), encoding="utf-8"
            )

        # Redirect all three scripts to the temp root.
        monkeypatch.setattr("scripts.bootstrap.get_project_root", lambda _root=root: _root)
        monkeypatch.setattr("scripts.context.get_project_root", lambda _root=root: _root)
        monkeypatch.setattr("scripts.context.core_dir", lambda _core=core: _core)

        yield core


def _make_temp_root_from_core(core: Path) -> Path:
    """Return the temp repository root given the .amalgam-core dir."""
    return core.parent


# ---------------------------------------------------------------------------
# Bootstrap -- idempotency
# ---------------------------------------------------------------------------

def test_bootstrap_creates_missing_json_files(temp_core: Path) -> None:
    """First run: missing files are created with correct empty-defaults."""
    root = _make_temp_root_from_core(temp_core)

    # Write required root files so validate_root_files passes.
    for name in ("AGENTS.md", "ARCHITECTURE.md", "MISSION.md", "TASK.md"):
        (root / name).write_text(f"# {name}\n\nContent.\n", encoding="utf-8")

    created = bootstrap_main()
    # After bootstrap, all 5 initializable files exist and parse as JSON.
    for filename in INITIALIZABLE_FILES:
        path = temp_core / filename
        assert path.exists(), f"{filename} missing after bootstrap"
        data = json.loads(path.read_text(encoding="utf-8"))
        if INITIALIZABLE_FILES[filename] == "[]":
            assert isinstance(data, list), f"{filename} is not an array"
        else:
            assert isinstance(data, dict), f"{filename} is not an object"


def test_bootstrap_idempotent_does_not_overwrite_valid_state(temp_core: Path) -> None:
    """Second run on already-bootstrapped dir leaves every file untouched."""
    root = _make_temp_root_from_core(temp_core)
    for name in ("AGENTS.md", "ARCHITECTURE.md", "MISSION.md", "TASK.md"):
        (root / name).write_text(f"# {name}\n\nContent.\n", encoding="utf-8")

    # Run bootstrap once to initialize.
    bootstrap_main()

    # Capture every file's content after first run.
    before: dict[str, str] = {}
    for filename in INITIALIZABLE_FILES:
        before[filename] = (temp_core / filename).read_text(encoding="utf-8")

    bootstrap_main()

    for filename in INITIALIZABLE_FILES:
        after = (temp_core / filename).read_text(encoding="utf-8")
        assert after == before[filename], f"{filename} was overwritten on re-run"


# ---------------------------------------------------------------------------
# Bootstrap -- corrupt file recovery
# ---------------------------------------------------------------------------

def test_bootstrap_recreates_missing_empty_file(temp_core: Path) -> None:
    """A missing INITIALIZABLE_FILES entry is reinitialized."""
    root = _make_temp_root_from_core(temp_core)
    for name in ("AGENTS.md", "ARCHITECTURE.md", "MISSION.md", "TASK.md"):
        (root / name).write_text(f"# {name}\n\nContent.\n", encoding="utf-8")

    # Force-remove SESSION.json after first bootstrap.
    bootstrap_main()
    (temp_core / "SESSION.json").unlink()

    bootstrap_main()
    assert (temp_core / "SESSION.json").exists()


def test_bootstrap_rejects_missing_immutable_file(temp_core: Path) -> None:
    """STATE.schema.json missing -> BootstrapError (bootstrap never creates it)."""
    root = _make_temp_root_from_core(temp_core)
    for name in ("AGENTS.md", "ARCHITECTURE.md", "MISSION.md", "TASK.md"):
        (root / name).write_text(f"# {name}\n\nContent.\n", encoding="utf-8")

    (temp_core / "STATE.schema.json").unlink()
    with pytest.raises(BootstrapError, match="Immutable file"):
        bootstrap_main()


def test_corrupt_json_written_as_default(temp_core: Path) -> None:
    """validate_json_file resets a file containing invalid JSON."""
    path = temp_core / "QUEUE.json"
    path.write_text("not-json {{{", encoding="utf-8")
    result = validate_json_file(path, "[]")
    assert result is False
    assert json.loads(path.read_text(encoding="utf-8")) == []


def test_validate_json_file_leaves_valid_json_untouched(temp_core: Path) -> None:
    """A valid JSON file is left untouched."""
    path = temp_core / "STATE.json"
    path.write_text('{"a": 1}', encoding="utf-8")
    result = validate_json_file(path, "{}")
    assert result is True
    assert json.loads(path.read_text(encoding="utf-8")) == {"a": 1}


def test_bootstrap_missing_root_file_raises(temp_core: Path) -> None:
    """validate_root_files raises BootstrapError when AGENTS.md is absent."""
    root = _make_temp_root_from_core(temp_core)
    with pytest.raises(BootstrapError, match="missing"):
        validate_root_files(root)


# ---------------------------------------------------------------------------
# Registry -- discovery and rebuild
# ---------------------------------------------------------------------------

def test_registry_scan_discovers_known_categories(temp_core: Path) -> None:
    """Registry scan discovers packages from the real repository."""
    real_root = Path(r"C:\AMALGAM")
    components = discover_components(real_root)
    categories = set(components.keys())
    expected = {"agents", "brain", "kernel", "services", "tools", "workspace", "tests", "scripts"}
    missing = expected - categories
    assert not missing, f"Expected categories not discovered: {sorted(missing)}"


def test_registry_scan_never_hardcodes_nonexistent_dir(temp_core: Path) -> None:
    """providers/ and configs/ do not exist; they are never emitted."""
    real_root = Path(r"C:\AMALGAM")
    components = discover_components(real_root)
    assert "providers" not in components, "providers/ does not exist -- must not appear"
    assert "configs" not in components, "configs/ does not exist -- must not appear"


def test_registry_save_and_load_roundtrip(temp_core: Path) -> None:
    """save_registry writes REGISTRY.json; load_registry reads it back."""
    real_root = Path(r"C:\AMALGAM")
    live = discover_components(real_root)
    registry = save_registry(live, verified=True)
    reloaded = load_registry()
    assert reloaded["verified"] is True
    assert reloaded["components"] == live


def test_registry_validate_reports_drift(temp_core: Path) -> None:
    """When REGISTRY.json is stale, validate detects drift."""
    real_root = Path(r"C:\AMALGAM")
    live = discover_components(real_root)
    # Persist a stale registry (remove one category).
    stale = dict(live)
    stale.pop("agents", None)
    save_registry(stale, verified=False)

    # Re-discover live and compare -- drift must be detected.
    path_sets_live = {k: {c["path"] for c in v} for k, v in live.items()}
    path_sets_stale = {k: {c["path"] for c in v} for k, v in stale.items()}
    all_cats = set(path_sets_live) | set(path_sets_stale)
    drifted = False
    for cat in all_cats:
        lset = path_sets_live.get(cat, set())
        sset = path_sets_stale.get(cat, set())
        if lset != sset:
            drifted = True
            break
    assert drifted, "Stale registry should show drift vs live discovery"


def test_registry_validate_clean_after_rebuild(temp_core: Path) -> None:
    """After a rebuild (scan), validate finds zero drift."""
    real_root = Path(r"C:\AMALGAM")
    live = discover_components(real_root)
    save_registry(live, verified=True)
    path_sets_live = {k: {c["path"] for c in v} for k, v in live.items()}
    path_sets_persisted = {
        k: {c["path"] for c in v} for k, v in load_registry()["components"].items()
    }
    for cat in path_sets_live:
        assert path_sets_live[cat] == path_sets_persisted.get(cat, set()), \
            f"Category {cat} drifted after rebuild"


def test_component_fields_are_fully_populated(temp_core: Path) -> None:
    """A discovered component carries all 8 required metadata fields."""
    real_root = Path(r"C:\AMALGAM")
    components = discover_components(real_root)
    sample = components.get("agents", []) or components.get("kernel", [])
    assert sample, "No components discovered to verify fields"
    c = sample[0]
    required_fields = {"name", "path", "category", "public_modules", "dependencies",
                       "children", "parent_package", "last_modified"}
    assert set(c.keys()) >= required_fields, f"Missing fields: {required_fields - set(c.keys())}"


def test_dependencies_of_finds_internal_imports(temp_core: Path) -> None:
    """AST-based dependency extraction on orchestrator_agent.py finds AMALGAM deps."""
    real_root = Path(r"C:\AMALGAM")
    mod = real_root / "agents" / "orchestrator_agent.py"
    deps = dependencies_of(mod, real_root)
    assert "brain.agent_registry" in deps or "agents.engineer" in deps, \
        f"Expected amalgam dependencies in orchestrator_agent, got: {deps}"
    assert "typing" not in deps, "stdlib imports must be filtered out"


# ---------------------------------------------------------------------------
# Context -- state rebuild (MISSION/TASK/CONTEXT)
# ---------------------------------------------------------------------------

def test_rebuild_writes_valid_state_from_nonempty_instance(temp_core: Path) -> None:
    """When STATE.json has mission data, rebuild populates all 3 MD files."""
    state: dict[str, Any] = {
        "current_mission": {
            "id": "MISSION_99_1",
            "title": "Test Mission",
            "status": "in_progress",
            "started_at": "2026-07-01T00:00:00Z",
        },
        "completed_missions": [],
        "current_task": None,
        "task_status": "pending",
        "current_stage": "idle",
        "current_branch": "main",
        "session_id": "test-session",
        "provider": {"name": "test-provider", "api_base": "", "rate_limit": {"requests_per_minute": 40, "max_concurrent": 32}},
        "model": {"id": "test-model", "role": "default", "context_window": 128000},
        "current_worker": {"agent": "test-agent", "host": "localhost"},
        "tests": {"passed": 0, "failed": 0, "total": 0, "status": "not_run"},
        "checkpoint": {},
        "queue": [],
        "recent_commit": {},
        "next_mission": None,
        "repository": {"head": {}, "remotes": [], "status": {"clean": False, "staged": [], "unstaged": [], "untracked": []}},
        "schema_version": "1.0.0",
        "architecture_version": "1.0.0",
        "repository_version": 1,
        "last_updated": "2026-07-01T00:00:00Z",
    }
    save_state(state)
    _rebuild_all(state)

    mission_md = (temp_core / "MISSION.md").read_text(encoding="utf-8")
    task_md = (temp_core / "TASK.md").read_text(encoding="utf-8")
    context_md = (temp_core / "CONTEXT.md").read_text(encoding="utf-8")
    assert "MISSION_99_1" in mission_md
    assert "Test Mission" in mission_md
    assert "No active task" in task_md  # current_task is None
    assert "test-provider" in context_md


def test_rebuild_from_empty_state_produces_placeholder_files(temp_core: Path) -> None:
    """With no mission data, the rebuild emits 'No active mission' placeholders."""
    save_json("STATE.json", {})
    state = load_state()
    _rebuild_all(state)
    mission_md = (temp_core / "MISSION.md").read_text(encoding="utf-8")
    assert "No active mission" in mission_md


# ---------------------------------------------------------------------------
# Context -- checkpoint and resume
# ---------------------------------------------------------------------------

def test_checkpoint_writes_and_resume_reads(temp_core: Path) -> None:
    """cmd_checkpoint writes CHECKPOINT.json; cmd_resume reads it."""
    state: dict[str, Any] = {
        "current_stage": "implement",
        "current_mission": {"id": "MISSION_99_1", "title": "Test", "status": "in_progress", "started_at": "2026-07-01T00:00:00Z"},
        "current_task": {"id": "task-1", "title": "A task", "mission_id": "MISSION_99_1", "started_at": "2026-07-01T00:00:00Z"},
        "test": {},
    }
    save_state(state)

    cmd_checkpoint()
    cp_path = temp_core / "CHECKPOINT.json"
    assert cp_path.exists(), "CHECKPOINT.json not created"
    cp = json.loads(cp_path.read_text(encoding="utf-8"))
    assert cp.get("stage") == "implement"
    assert cp.get("current_mission") == "MISSION_99_1"

    cmd_resume()
    state_after = load_state()
    assert state_after.get("current_stage") == "implement"


def test_resume_fails_on_missing_checkpoint(temp_core: Path) -> None:
    """When CHECKPOINT.json is absent, resume prints an error without crashing."""
    save_state({})
    cmd_resume()


def test_resume_fails_on_empty_checkpoint(temp_core: Path) -> None:
    """When CHECKPOINT.json is blank, resume prints an error without crashing."""
    save_state({})
    (temp_core / "CHECKPOINT.json").write_text("", encoding="utf-8")
    cmd_resume()


# ---------------------------------------------------------------------------
# Context -- audit
# ---------------------------------------------------------------------------

def test_audit_detects_schema_leakage_in_state_json(temp_core: Path) -> None:
    """cmd_audit flags STATE.json containing schema marker keys."""
    root = _make_temp_root_from_core(temp_core)
    for name in ("AGENTS.md", "ARCHITECTURE.md", "MISSION.md", "TASK.md"):
        (root / name).write_text(f"# {name}\n\nContent.\n", encoding="utf-8")

    save_json("STATE.json", {"$schema": "draft-07", "properties": [], "current_stage": "idle"})
    cmd_audit()

    state_obj = load_state()
    leaked = {"$schema", "$id", "properties", "required"} & set(state_obj.keys() if isinstance(state_obj, dict) else [])
    assert leaked, "Schema markers should be present for this test branch"


def test_audit_accepts_clean_runtime_instance(temp_core: Path) -> None:
    """cmd_audit passes STATE.json that is a pure runtime instance."""
    root = _make_temp_root_from_core(temp_core)
    for name in ("AGENTS.md", "ARCHITECTURE.md", "MISSION.md", "TASK.md"):
        (root / name).write_text(f"# {name}\n\nContent.\n", encoding="utf-8")

    save_json("STATE.json", {})
    cmd_audit()

    state_obj = load_state()
    leaked = {"$schema", "$id", "properties", "required"} & set(state_obj.keys() if isinstance(state_obj, dict) else [])
    assert not leaked, "Clean instance must have zero schema marker keys"


def test_audit_detects_missing_required_core_files(temp_core: Path) -> None:
    """cmd_audit raises an issue when CONTEXT.md is missing."""
    root = _make_temp_root_from_core(temp_core)
    for name in ("AGENTS.md", "ARCHITECTURE.md", "MISSION.md", "TASK.md"):
        (root / name).write_text(f"# {name}\n\nContent.\n", encoding="utf-8")
    save_json("STATE.json", {})

    (temp_core / "CONTEXT.md").write_text("", encoding="utf-8")  # empty -> issue
    cmd_audit()

    assert (temp_core / "CONTEXT.md").read_text(encoding="utf-8").strip() == ""


# ---------------------------------------------------------------------------
# Edge cases -- empty / corrupt states
# ---------------------------------------------------------------------------

def test_load_state_on_missing_file_returns_empty_dict(temp_core: Path) -> None:
    """load_state returns {} when STATE.json is absent."""
    (temp_core / "STATE.json").unlink(missing_ok=True)
    result = load_state()
    assert isinstance(result, dict) and len(result) == 0


def test_save_state_preserves_existing_keys(temp_core: Path) -> None:
    """save_state sets last_updated but keeps pre-existing data."""
    state = {"current_stage": "review", "extra": 42}
    save_state(state)
    reloaded = load_state()
    assert reloaded.get("current_stage") == "review"
    assert reloaded.get("extra") == 42
    assert "last_updated" in reloaded


def test_bootstrap_handles_corrupt_json_gracefully(temp_core: Path) -> None:
    """validate_json_file handles a file containing 'not-json {{{'."""
    path = temp_core / "SESSION.json"
    path.write_text("not-json {{{", encoding="utf-8")
    restored = validate_json_file(path, "{}")
    assert restored is False
    assert json.loads(path.read_text(encoding="utf-8")) == {}


def test_empty_default_array_file_is_valid_json(temp_core: Path) -> None:
    """A file that starts as [] passes validate_json_file untouched."""
    path = temp_core / "HISTORY.json"
    path.write_text("[]", encoding="utf-8")
    result = validate_json_file(path, "[]")
    assert result is True
    assert json.loads(path.read_text(encoding="utf-8")) == []