#!/usr/bin/env python3
"""
AMALGAM Fingerprint Engine

Repository integrity verification via SHA256 content hashing.

Responsibilities:
    - Generate CHECKSUMS.json: a snapshot of the repository with SHA256
      hashes for every managed file, plus git branch and HEAD.
    - Verify current repository state against stored CHECKSUMS.
    - Report detailed differences on any mismatch.
    - Never silently resume after repository changes.

Standard library only (hashlib for SHA256, no subprocess).
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.context import (  # noqa: E402
    core_dir,
    get_project_root,
    load_json,
    now_iso,
    save_json,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FINGERPRINT_VERSION = "1.0"
CHECKSUMS_FILE = "CHECKSUMS.json"

# Directories and files always excluded from fingerprinting.
EXCLUDED_DIRS: set[str] = {
    ".git",
    "__pycache__",
    ".venv",
    ".pytest_cache",
    ".amalgam-core",
    ".claude",
    ".idea",
    ".vscode",
    "node_modules",
    "logs",
    "data",
    "assets",
    "storage",
    ".mypy_cache",
    ".ruff_cache",
    ".eggs",
    "*.egg-info",
    ".tox",
    ".nox",
    ".coverage",
    "htmlcov",
    ".hypothesis",
}

EXCLUDED_FILES: set[str] = {
    ".DS_Store",
    "Thumbs.db",
    "*.pyc",
    "*.pyo",
    "*.so",
    "*.dll",
    "*.dylib",
}

HASH_BLOCK_SIZE = 65536


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class FingerprintError(Exception):
    """Raised when fingerprint build, verify, or diff fails."""

    pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def log(message: str) -> None:
    """Print a structured log line with a FINGERPRINT prefix."""
    print(f"[FINGERPRINT] {message}")


def _git_branch(root: Path) -> str:
    """Return the current git branch name by parsing .git/HEAD.

    Returns '—' when .git/HEAD is missing or unparseable.
    """
    head_file = root / ".git" / "HEAD"
    if not head_file.exists():
        return "\u2014"
    try:
        raw = head_file.read_text(encoding="utf-8", errors="replace").strip()
        if raw.startswith("ref: "):
            ref = raw[5:]
            return ref.replace("refs/heads/", "")
        return raw[:40]
    except OSError:
        return "\u2014"


def _git_head(root: Path) -> str:
    """Return the full git commit hash by resolving .git/HEAD.

    Returns '\u2014' when the commit hash cannot be determined.
    """
    head_file = root / ".git" / "HEAD"
    if not head_file.exists():
        return "\u2014"
    try:
        raw = head_file.read_text(encoding="utf-8", errors="replace").strip()
        if raw.startswith("ref: "):
            ref_path = root / ".git" / raw[5:]
            if ref_path.exists():
                return ref_path.read_text(encoding="utf-8",
                                          errors="replace").strip()[:40]
            return "\u2014"
        return raw[:40]
    except OSError:
        return "\u2014"


def _sha256(file_path: Path) -> str:
    """Return the hex SHA256 digest of a file's contents.

    Reads the file in fixed-size blocks to handle large files without
    loading the entire content into memory.

    Args:
        file_path: Path to the file to hash.

    Returns:
        64-character hex SHA256 digest.

    Raises:
        FingerprintError: If the file cannot be read.
    """
    hasher = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while True:
                block = f.read(HASH_BLOCK_SIZE)
                if not block:
                    break
                hasher.update(block)
    except OSError as exc:
        raise FingerprintError(f"Cannot read {file_path}: {exc}") from exc
    return hasher.hexdigest()


def _should_exclude(path: Path, root: Path) -> bool:
    """Return True if a file or directory should be excluded from fingerprinting.

    Args:
        path: The file or directory to check.
        root: Repository root used to compute relative paths.

    Returns:
        True if the path matches any exclusion pattern.
    """
    try:
        rel = path.relative_to(root)
    except ValueError:
        return True
    parts = rel.parts
    for part in parts:
        if part in EXCLUDED_DIRS:
            return True
        if part.startswith(".") and part not in (".",):
            return True
    if path.is_file():
        name = path.name
        if name in EXCLUDED_FILES:
            return True
        if name.endswith((".pyc", ".pyo", ".so", ".dll", ".dylib", ".exe")):
            return True
    return False


# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------


def _collect_files(root: Path) -> list[Path]:
    """Walk the repository tree and return all non-excluded file paths.

    Args:
        root: Repository root directory.

    Returns:
        Sorted list of file paths relative to root.
    """
    files: list[Path] = []
    for entry in sorted(root.rglob("*")):
        if not entry.is_file():
            continue
        if _should_exclude(entry, root):
            continue
        files.append(entry)
    return files


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def cmd_build() -> dict[str, Any]:
    """Walk the repository, compute SHA256 hashes, write CHECKSUMS.json.

    Returns:
        The CHECKSUMS.json dict that was written.

    Raises:
        FingerprintError: If the repository root cannot be read.
    """
    root = get_project_root()
    log(f"Building fingerprint for repository: {root}")

    files = _collect_files(root)
    log(f"Found {len(files)} files to fingerprint.")

    file_map: dict[str, str] = {}
    total = len(files)
    for i, fpath in enumerate(files):
        try:
            rel = fpath.relative_to(root).as_posix()
            file_map[rel] = _sha256(fpath)
        except (FingerprintError, OSError) as exc:
            log(f"  WARNING: Skipping {fpath}: {exc}")
        if (i + 1) % 100 == 0 or i + 1 == total:
            log(f"  Hashed {i + 1}/{total} files.")

    branch = _git_branch(root)
    head = _git_head(root)

    checksums: dict[str, Any] = {
        "version": FINGERPRINT_VERSION,
        "generated_at": now_iso(),
        "repository_root": str(root.resolve()),
        "branch": branch,
        "head": head,
        "file_count": len(file_map),
        "files": file_map,
    }

    save_json(CHECKSUMS_FILE, checksums)
    log(f"Wrote CHECKSUMS.json with {len(file_map)} file hashes.")
    log(f"  Branch: {branch}")
    log(f"  HEAD:   {head}")

    return checksums


# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------


def cmd_verify() -> None:
    """Verify current repository state against stored CHECKSUMS.json.

    Compares every file in CHECKSUMS.json against the live repository.
    Reports:
      - Unchanged files (matches stored hash)
      - Modified files (hash mismatch)
      - Missing files (in CHECKSUMS but not on disk)
      - New files (on disk but not in CHECKSUMS)

    Exits with code 1 if ANY difference is found (modified, missing, or new).
    """
    checksums = load_json(CHECKSUMS_FILE)
    if not isinstance(checksums, dict) or "files" not in checksums:
        print("ERROR: CHECKSUMS.json is missing, empty, or invalid. Run 'build' first.")
        print()
        sys.exit(1)

    root = get_project_root()
    stored_files: dict[str, str] = checksums.get("files", {})
    stored_branch = checksums.get("branch", "\u2014")
    stored_head = checksums.get("head", "\u2014")

    current_branch = _git_branch(root)
    current_head = _git_head(root)

    print()
    print("AMALGAM FINGERPRINT VERIFY")
    print("-" * 50)

    changes: list[str] = []

    # Check branch
    if current_branch != stored_branch:
        changes.append(f"  BRANCH   : {stored_branch} -> {current_branch}")

    # Check HEAD
    if current_head != stored_head and current_head != "\u2014":
        changes.append(f"  HEAD     : {stored_head[:12]}... -> {current_head[:12]}...")

    # Verify each stored file
    modified: list[str] = []
    missing: list[str] = []
    unchanged_count = 0
    for rel_path, stored_hash in stored_files.items():
        abs_path = root / rel_path
        if not abs_path.exists():
            missing.append(rel_path)
            continue
        try:
            current_hash = _sha256(abs_path)
        except FingerprintError:
            missing.append(rel_path)
            continue
        if current_hash == stored_hash:
            unchanged_count += 1
        else:
            modified.append(rel_path)

    # Detect new files (present on disk, not in CHECKSUMS)
    live_files = _collect_files(root)
    live_relative = set()
    for fp in live_files:
        try:
            live_relative.add(fp.relative_to(root).as_posix())
        except ValueError:
            pass
    stored_relative = set(stored_files.keys())
    new_files = sorted(live_relative - stored_relative)

    total_changed = len(modified) + len(missing) + len(new_files) + (len(changes) - len(changes))

    print(f"Stored branch : {stored_branch}")
    print(f"Current branch: {current_branch}")
    print(f"Stored HEAD   : {stored_head[:16] if stored_head != '\u2014' else stored_head}...")
    print(f"Current HEAD  : {current_head[:16] if current_head != '\u2014' else current_head}...")
    print(f"Total files   : {len(stored_files)} stored, {len(live_files)} live")
    print(f"Unchanged     : {unchanged_count}")
    print()

    if changes:
        print("REPOSITORY CHANGES DETECTED:")
        print()
        for c in changes:
            print(c)
        print()

    if modified:
        print(f"MODIFIED FILES ({len(modified)}):")
        for f in modified[:20]:
            print(f"  M  {f}")
        if len(modified) > 20:
            print(f"  ... and {len(modified) - 20} more")
        print()

    if missing:
        print(f"MISSING FILES ({len(missing)}):")
        for f in missing[:20]:
            print(f"  D  {f}")
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")
        print()

    if new_files:
        print(f"NEW FILES ({len(new_files)}):")
        for f in new_files[:20]:
            print(f"  A  {f}")
        if len(new_files) > 20:
            print(f"  ... and {len(new_files) - 20} more")
        print()

    verdict = "CLEAN"
    if changes or modified or missing or new_files:
        total_issues = len(changes) + len(modified) + len(missing) + len(new_files)
        print(f"VERDICT: {total_issues} difference(s) detected.")
        print("  Repository has changed since CHECKSUMS.json was built.")
        print("  Rebuild CHECKSUMS.json before resuming work.")
        print()
        sys.exit(1)
    else:
        print("VERDICT: CLEAN — All files match stored checksums.")
        print()


# ---------------------------------------------------------------------------
# Diff
# ---------------------------------------------------------------------------


def cmd_diff() -> None:
    """Print differences between current repository and CHECKSUMS.json.

    Works like verify but only prints changes (no pass/fail exit code).
    Returns a structured diff dict that can be used programmatically.
    """
    checksums = load_json(CHECKSUMS_FILE)
    if not isinstance(checksums, dict) or "files" not in checksums:
        print("ERROR: CHECKSUMS.json is missing, empty, or invalid. Run 'build' first.")
        print()
        return

    root = get_project_root()
    stored_files: dict[str, str] = checksums.get("files", {})
    stored_branch = checksums.get("branch", "\u2014")
    stored_head = checksums.get("head", "\u2014")
    current_branch = _git_branch(root)
    current_head = _git_head(root)

    print()
    print("AMALGAM FINGERPRINT DIFF")
    print("-" * 50)

    has_diff = False

    if current_branch != stored_branch:
        has_diff = True
        print(f"  BRANCH   : {stored_branch} -> {current_branch}")

    if current_head != stored_head and current_head != "\u2014":
        has_diff = True
        print(f"  HEAD     : {stored_head[:12]}... -> {current_head[:12]}...")

    modified = []
    missing = []
    for rel_path, stored_hash in stored_files.items():
        abs_path = root / rel_path
        if not abs_path.exists():
            missing.append(rel_path)
            continue
        try:
            current_hash = _sha256(abs_path)
        except FingerprintError:
            missing.append(rel_path)
            continue
        if current_hash != stored_hash:
            modified.append(rel_path)

    live_files = _collect_files(root)
    live_relative = set()
    for fp in live_files:
        try:
            live_relative.add(fp.relative_to(root).as_posix())
        except ValueError:
            pass
    stored_relative = set(stored_files.keys())
    new_files = sorted(live_relative - stored_relative)

    if modified:
        has_diff = True
        print(f"\nMODIFIED ({len(modified)}):")
        for f in modified:
            print(f"  {f}")

    if missing:
        has_diff = True
        print(f"\nMISSING ({len(missing)}):")
        for f in missing:
            print(f"  {f}")

    if new_files:
        has_diff = True
        print(f"\nNEW ({len(new_files)}):")
        for f in new_files:
            print(f"  {f}")

    if not has_diff:
        print("  No differences found.")
    print()


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------


def cmd_status() -> None:
    """Print a summary of the current CHECKSUMS.json contents."""
    checksums = load_json(CHECKSUMS_FILE)
    if not isinstance(checksums, dict):
        print()
        print("AMALGAM FINGERPRINT STATUS")
        print("-" * 50)
        print("CHECKSUMS.json is missing or invalid. Run 'build' first.")
        print()
        return

    files = checksums.get("files", {})
    file_count = checksums.get("file_count", len(files))

    print()
    print("AMALGAM FINGERPRINT STATUS")
    print("-" * 50)
    print(f"Version       : {checksums.get('version', '\u2014')}")
    print(f"Generated At  : {checksums.get('generated_at', '\u2014')}")
    print(f"Repository    : {checksums.get('repository_root', '\u2014')}")
    print(f"Branch        : {checksums.get('branch', '\u2014')}")
    print(f"HEAD          : {checksums.get('head', '\u2014')[:20]}...")
    print(f"File Count    : {file_count}")
    print("-" * 50)

    if files:
        py_count = sum(1 for f in files if f.endswith(".py"))
        md_count = sum(1 for f in files if f.endswith(".md"))
        json_count = sum(1 for f in files if f.endswith(".json"))
        yaml_count = sum(1 for f in files if f.endswith((".yaml", ".yml")))
        other = file_count - py_count - md_count - json_count - yaml_count
        print(f"Python files  : {py_count}")
        print(f"Markdown files: {md_count}")
        print(f"JSON files    : {json_count}")
        print(f"YAML files    : {yaml_count}")
        print(f"Other files   : {other}")
    print()


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------

COMMAND_MAP: dict[str, str] = {
    "build": "cmd_build",
    "verify": "cmd_verify",
    "diff": "cmd_diff",
    "status": "cmd_status",
}


def print_help() -> None:
    """Print the available commands."""
    print("AMALGAM Fingerprint Engine")
    print()
    print("Commands:")
    for cmd in COMMAND_MAP:
        print(f"  py scripts/fingerprint.py {cmd}")
    print()
    print("  build    : Walk repository, compute SHA256 hashes, write CHECKSUMS.json.")
    print("  verify   : Compare current repository against CHECKSUMS.json.")
    print("  diff     : Show differences (same as verify, no exit code).")
    print("  status   : Print CHECKSUMS.json summary.")
    print()


def main() -> None:
    """Parse CLI arguments and dispatch to the requested command."""
    if len(sys.argv) < 2:
        print("Usage: py scripts/fingerprint.py <command>")
        print()
        print_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd in ("help", "--help", "-h"):
        print_help()
        sys.exit(0)

    func_name = COMMAND_MAP.get(cmd)
    if func_name is None:
        print(f"ERROR: Unknown command '{cmd}'.")
        print_help()
        sys.exit(1)

    func = globals().get(func_name)
    if func is None:
        print(f"ERROR: Internal dispatch failure for '{cmd}' -> '{func_name}'.")
        sys.exit(1)

    try:
        func()
    except FingerprintError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Command '{cmd}' failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
