"""Regression tests for scripts/fingerprint.py.

Covers git HEAD parsing, SHA256 hashing, exclusion logic,
file collection, build, verify, diff, and status commands.

All tests operate on isolated per-test temp directories.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from scripts.fingerprint import (
    FINGERPRINT_VERSION,
    CHECKSUMS_FILE,
    EXCLUDED_DIRS,
    EXCLUDED_FILES,
    HASH_BLOCK_SIZE,
    FingerprintError,
    cmd_build,
    cmd_verify,
    cmd_diff,
    cmd_status,
    _git_branch,
    _git_head,
    _sha256,
    _should_exclude,
    _collect_files,
    log,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_repo(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create an isolated temp directory as the repository root."""
    with tempfile.TemporaryDirectory(prefix="amalgam_test_fingerprint_") as tmp:
        root = Path(tmp)
        core = root / ".amalgam-core"
        core.mkdir()

        monkeypatch.setattr("scripts.context.get_project_root", lambda _root=root: _root)
        monkeypatch.setattr("scripts.context.core_dir", lambda _core=core: _core)
        monkeypatch.setattr("scripts.fingerprint.get_project_root", lambda _root=root: _root)

        yield root


@pytest.fixture
def repo_with_files(temp_repo: Path) -> Path:
    """Create a small repo with a few files and a simulated .git directory."""
    root = temp_repo

    # Create a fake .git with HEAD pointing to main
    git_dir = root / ".git"
    git_dir.mkdir()
    refs_heads = git_dir / "refs" / "heads"
    refs_heads.mkdir(parents=True)
    (refs_heads / "main").write_text("abc123def456abc123def456abc123def456abc1\n", encoding="utf-8")
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")

    # Create some repo files
    (root / "README.md").write_text("# Test Repo\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
    (root / "docs").mkdir()
    (root / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")

    # Create an excluded dir
    excluded = root / "__pycache__"
    excluded.mkdir()
    (excluded / "cache.pyc").write_text("cache", encoding="utf-8")

    return root


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_fingerprint_version() -> None:
    assert FINGERPRINT_VERSION == "1.0"


def test_checksums_file_name() -> None:
    assert CHECKSUMS_FILE == "CHECKSUMS.json"


def test_excluded_dirs_nonempty() -> None:
    assert ".git" in EXCLUDED_DIRS
    assert "__pycache__" in EXCLUDED_DIRS


def test_hash_block_size_positive() -> None:
    assert HASH_BLOCK_SIZE > 0


# ---------------------------------------------------------------------------
# _git_branch / _git_head
# ---------------------------------------------------------------------------


def test_git_branch_returns_unknown_on_no_git(temp_repo: Path) -> None:
    result = _git_branch(temp_repo)
    assert result == "\u2014"


def test_git_head_returns_unknown_on_no_git(temp_repo: Path) -> None:
    result = _git_head(temp_repo)
    assert result == "\u2014"


def test_git_branch_reads_from_head(temp_repo: Path) -> None:
    root = temp_repo
    git_dir = root / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    result = _git_branch(root)
    assert result == "main"


def test_git_head_resolves_from_ref(temp_repo: Path) -> None:
    root = temp_repo
    git_dir = root / ".git"
    git_dir.mkdir()
    refs_heads = git_dir / "refs" / "heads"
    refs_heads.mkdir(parents=True)
    (refs_heads / "main").write_text("abc123def456abc123def456abc123def456abc1\n", encoding="utf-8")
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    result = _git_head(root)
    assert result == "abc123def456abc123def456abc123def456abc1"


# ---------------------------------------------------------------------------
# _sha256
# ---------------------------------------------------------------------------


def test_sha256_known_content(temp_repo: Path) -> None:
    path = temp_repo / "test.txt"
    path.write_text("hello\n", encoding="utf-8")
    digest = _sha256(path)
    assert isinstance(digest, str)
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


def test_sha256_raises_on_missing_file(temp_repo: Path) -> None:
    path = temp_repo / "nonexistent.txt"
    with pytest.raises(FingerprintError, match="Cannot read"):
        _sha256(path)


# ---------------------------------------------------------------------------
# _should_exclude
# ---------------------------------------------------------------------------


def test_should_exclude_dot_git(temp_repo: Path) -> None:
    git_path = temp_repo / ".git" / "HEAD"
    assert _should_exclude(git_path, temp_repo)


def test_should_exclude_pycache(temp_repo: Path) -> None:
    path = temp_repo / "__pycache__" / "foo.pyc"
    assert _should_exclude(path, temp_repo)


def test_should_not_exclude_regular_file(temp_repo: Path) -> None:
    path = temp_repo / "README.md"
    path.write_text("content", encoding="utf-8")
    assert not _should_exclude(path, temp_repo)


def test_should_exclude_pyc_extension(temp_repo: Path) -> None:
    path = temp_repo / "module.pyc"
    path.write_text("", encoding="utf-8")
    assert _should_exclude(path, temp_repo)


# ---------------------------------------------------------------------------
# _collect_files
# ---------------------------------------------------------------------------


def test_collect_files_counts_excluded(repo_with_files: Path) -> None:
    files = _collect_files(repo_with_files)
    paths = [f.relative_to(repo_with_files).as_posix() for f in files]
    # .git/* and __pycache__/* should be excluded
    assert ".git/HEAD" not in paths
    assert "__pycache__/cache.pyc" not in paths
    # Regular files should be present
    assert "README.md" in paths
    assert "src/main.py" in paths
    assert "docs/guide.md" in paths


# ---------------------------------------------------------------------------
# cmd_build
# ---------------------------------------------------------------------------


def test_build_creates_checksums_json(repo_with_files: Path) -> None:
    core = repo_with_files / ".amalgam-core"
    checksums = cmd_build()
    assert isinstance(checksums, dict)
    assert checksums["version"] == FINGERPRINT_VERSION
    assert checksums["file_count"] >= 3  # README.md, src/main.py, docs/guide.md

    saved = json.loads((core / CHECKSUMS_FILE).read_text(encoding="utf-8"))
    assert saved["file_count"] == checksums["file_count"]


# ---------------------------------------------------------------------------
# cmd_verify
# ---------------------------------------------------------------------------


def test_verify_reports_clean_when_unchanged(repo_with_files: Path) -> None:
    cmd_build()

    # Verify on the same repo - should pass (exit 0)
    try:
        cmd_verify()
    except SystemExit as exc:
        assert exc.code != 1, "Verify should pass on unchanged repo"


def test_verify_reports_changes_when_file_modified(repo_with_files: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    checksums = cmd_build()

    # Modify a file
    (repo_with_files / "README.md").write_text("# Modified\n", encoding="utf-8")

    with pytest.raises(SystemExit) as excinfo:
        cmd_verify()
    assert excinfo.value.code == 1


def test_verify_reports_changes_when_file_added(repo_with_files: Path) -> None:
    cmd_build()

    # Add a new file
    (repo_with_files / "NEW.md").write_text("# New file\n", encoding="utf-8")

    with pytest.raises(SystemExit) as excinfo:
        cmd_verify()
    assert excinfo.value.code == 1


def test_verify_reports_changes_when_file_deleted(repo_with_files: Path) -> None:
    cmd_build()

    # Delete a file
    (repo_with_files / "src" / "main.py").unlink()

    with pytest.raises(SystemExit) as excinfo:
        cmd_verify()
    assert excinfo.value.code == 1


def test_verify_exits_on_missing_checksums(repo_with_files: Path) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cmd_verify()
    assert excinfo.value.code == 1


# ---------------------------------------------------------------------------
# cmd_diff
# ---------------------------------------------------------------------------


def test_diff_no_changes_when_unchanged(repo_with_files: Path) -> None:
    cmd_build()
    cmd_diff()  # Should not raise


def test_diff_detects_changes(repo_with_files: Path) -> None:
    cmd_build()
    (repo_with_files / "README.md").write_text("# Changed\n", encoding="utf-8")
    cmd_diff()  # Should not raise


def test_diff_handles_missing_checksums(repo_with_files: Path) -> None:
    cmd_diff()  # Should not raise


# ---------------------------------------------------------------------------
# cmd_status
# ---------------------------------------------------------------------------


def test_status_reports_missing_checksums(repo_with_files: Path) -> None:
    cmd_status()


def test_status_shows_build_info(repo_with_files: Path) -> None:
    cmd_build()
    cmd_status()


# ---------------------------------------------------------------------------
# log
# ---------------------------------------------------------------------------


def test_fingerprint_log_does_not_crash() -> None:
    log("Test fingerprint log message")
