"""Regression tests for scripts/bootstrap.py.

All tests operate on isolated per-test temp directories so no production
.amalgam-core/ file is ever touched.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

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


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_core(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create an isolated temp directory as the .amalgam-core root."""
    with tempfile.TemporaryDirectory(prefix="amalgam_test_bootstrap_") as tmp:
        root = Path(tmp)
        core = root / CORE_DIR_NAME
        core.mkdir()

        prod_schema = Path(__file__).resolve().parents[1] / ".amalgam-core" / "STATE.schema.json"
        if prod_schema.exists():
            (core / "STATE.schema.json").write_text(
                prod_schema.read_text(encoding="utf-8"), encoding="utf-8"
            )

        monkeypatch.setattr("scripts.bootstrap.get_project_root", lambda _root=root: _root)

        yield core


def _root(core: Path) -> Path:
    return core.parent


# ---------------------------------------------------------------------------
# Bootstrap -- idempotency
# ---------------------------------------------------------------------------


def test_bootstrap_creates_missing_json_files(temp_core: Path) -> None:
    """First run: missing files are created with correct empty-defaults."""
    r = _root(temp_core)
    for name in ("AGENTS.md", "ARCHITECTURE.md", "MISSION.md", "TASK.md"):
        (r / name).write_text(f"# {name}\n\nContent.\n", encoding="utf-8")

    created = bootstrap_main()

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
    r = _root(temp_core)
    for name in ("AGENTS.md", "ARCHITECTURE.md", "MISSION.md", "TASK.md"):
        (r / name).write_text(f"# {name}\n\nContent.\n", encoding="utf-8")

    bootstrap_main()

    before: dict[str, str] = {}
    for filename in INITIALIZABLE_FILES:
        before[filename] = (temp_core / filename).read_text(encoding="utf-8")

    bootstrap_main()

    for filename in INITIALIZABLE_FILES:
        after = (temp_core / filename).read_text(encoding="utf-8")
        assert after == before[filename], f"{filename} was overwritten on re-run"


# ---------------------------------------------------------------------------
# Bootstrap -- corrupt / missing file recovery
# ---------------------------------------------------------------------------


def test_bootstrap_recreates_missing_initializable_file(temp_core: Path) -> None:
    """A missing INITIALIZABLE_FILES entry is reinitialized."""
    r = _root(temp_core)
    for name in ("AGENTS.md", "ARCHITECTURE.md", "MISSION.md", "TASK.md"):
        (r / name).write_text(f"# {name}\n\nContent.\n", encoding="utf-8")

    bootstrap_main()
    (temp_core / "SESSION.json").unlink()
    bootstrap_main()

    assert (temp_core / "SESSION.json").exists()


def test_bootstrap_rejects_missing_immutable_file(temp_core: Path) -> None:
    """STATE.schema.json missing -> BootstrapError."""
    r = _root(temp_core)
    for name in ("AGENTS.md", "ARCHITECTURE.md", "MISSION.md", "TASK.md"):
        (r / name).write_text(f"# {name}\n\nContent.\n", encoding="utf-8")

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
    r = _root(temp_core)
    with pytest.raises(BootstrapError, match="missing"):
        validate_root_files(r)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


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


def test_ensure_core_dir_creates_directory(monkeypatch: pytest.MonkeyPatch) -> None:
    """ensure_core_dir creates the .amalgam-core dir if missing."""
    import tempfile as tmp_mod
    with tmp_mod.TemporaryDirectory(prefix="amalgam_test_coredir_") as tmp:
        root = Path(tmp)
        monkeypatch.setattr("scripts.bootstrap.get_project_root", lambda _root=root: _root)
        core_path = root / ".amalgam-core"
        assert not core_path.exists()
        ensure_core_dir(root)
        assert core_path.is_dir()


def test_immutable_files_constant_is_nonempty() -> None:
    """IMMUTABLE_FILES must contain at least STATE.schema.json."""
    assert "STATE.schema.json" in IMMUTABLE_FILES


def test_core_dir_name_is_correct() -> None:
    """CORE_DIR_NAME must be .amalgam-core."""
    assert CORE_DIR_NAME == ".amalgam-core"
