#!/usr/bin/env python3
"""
AMALGAM Bootstrap Script

Responsibilities:
    - Create the .amalgam-core directory.
    - Validate required project root files.
    - Initialize the five runtime JSON files:
      STATE.json, HISTORY.json, CHECKPOINT.json, SESSION.json, QUEUE.json.
    - Verify (never create, never modify) STATE.schema.json.

State split contract:
    STATE.json        -- runtime instance written here by bootstrap/context.
    STATE.schema.json -- immutable Draft-07 schema for STATE.json. Created
                         once out-of-band; bootstrap only asserts its presence
                         and never overwrites it.

Bootstrap never generates MISSION.md, TASK.md, CONTEXT.md, or REGISTRY.json.
Those are owned by the context engine (scripts/context.py) and the registry
discovery module (scripts/registry.py).

Idempotent: repeated execution is safe. Existing non-empty files are never
overwritten. Python standard library only.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CORE_DIR_NAME = ".amalgam-core"

REQUIRED_ROOT_FILES: list[str] = [
    "AGENTS.md",
    "ARCHITECTURE.md",
    "MISSION.md",
    "TASK.md",
]

# Files bootstrap owns. Each maps to its empty (zero-state) initializer.
# These are the only files bootstrap will touch on disk.
INITIALIZABLE_FILES: dict[str, str] = {
    "STATE.json": "{}",
    "HISTORY.json": "[]",
    "CHECKPOINT.json": "{}",
    "SESSION.json": "{}",
    "QUEUE.json": "[]",
}

# Immutable files bootstrap must NEVER create or overwrite. Their presence is
# asserted as a final validation step only. STATE.schema.json is the Draft-07
# schema for STATE.json; it is authored once and is the permanent contract for
# every runtime instance that context.py writes.
IMMUTABLE_FILES: list[str] = [
    "STATE.schema.json",
]


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class BootstrapError(Exception):
    """Raised when a bootstrap validation or initialization step fails."""
    pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_project_root() -> Path:
    """Return the repository root directory.

    scripts/bootstrap.py lives one level below the repository root, so the
    parent of this file's directory is the project root.
    """
    return Path(__file__).resolve().parent.parent


def log(message: str) -> None:
    """Print a structured log line to stdout."""
    print(f"[BOOTSTRAP] {message}")


def now_iso() -> str:
    """Return current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_root_files(root: Path) -> None:
    """Validate that every required root-level file exists and is non-empty.

    Args:
        root: Repository root directory.

    Raises:
        BootstrapError: If any required file is missing or empty.
    """
    log("Validating required root files...")
    missing: list[str] = []
    empty: list[str] = []
    for filename in REQUIRED_ROOT_FILES:
        path = root / filename
        if not path.exists():
            missing.append(filename)
            continue
        if not path.read_text(encoding="utf-8").strip():
            empty.append(filename)

    if missing or empty:
        detail: list[str] = []
        if missing:
            detail.append(f"missing: {', '.join(missing)}")
        if empty:
            detail.append(f"empty: {', '.join(empty)}")
        raise BootstrapError(
            "Required root files invalid (" + "; ".join(detail) + "). "
            "Create or populate them before bootstrapping."
        )

    log(f"Validated {len(REQUIRED_ROOT_FILES)} required root files.")


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def ensure_core_dir(root: Path) -> Path:
    """Create the .amalgam-core directory if missing. Return its path.

    Args:
        root: Repository root directory.

    Returns:
        The .amalgam-core directory path.
    """
    core = root / CORE_DIR_NAME
    core.mkdir(exist_ok=True)
    log(f"Core directory: {core}")
    return core


def is_empty_file(path: Path) -> bool:
    """Return True if a file is missing or contains only whitespace."""
    if not path.exists():
        return True
    return not path.read_text(encoding="utf-8").strip()


def validate_json_file(path: Path, default: str) -> bool:
    """Return True if path parses as JSON; otherwise repair it to default.

    A corrupt (unparseable) JSON file is reset to the provided default so the
    runtime never blocks on invalid state. A non-empty, parseable file is left
    untouched (idempotency).

    Args:
        path: Target JSON file.
        default: Fallback JSON text to write if the file is corrupt.

    Returns:
        True if the file was already valid and was left unchanged.
        False if it was missing, empty, or corrupt and had to be (re)initialized.
    """
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        path.write_text(default, encoding="utf-8")
        return False
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except json.JSONDecodeError:
        log(f"Warning: {path.name} was corrupt JSON; resetting to empty default.")
        path.write_text(default, encoding="utf-8")
        return False


def initialize_json_files(core_dir: Path) -> list[str]:
    """Initialize the five runtime JSON files. Never overwrite valid data.

    For each file in INITIALIZABLE_FILES:
      - If the file is missing, empty, or corrupt JSON: write the empty default.
      - If the file is valid JSON: leave it untouched.

    Args:
        core_dir: The .amalgam-core directory.

    Returns:
        List of file names that were created or repaired.
    """
    created: list[str] = []
    for filename, default in INITIALIZABLE_FILES.items():
        path = core_dir / filename
        untouched = validate_json_file(path, default)
        if untouched:
            log(f"{filename}: present and valid; skipping.")
        else:
            log(f"{filename}: initialized.")
            created.append(filename)
    return created


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def bootstrap() -> None:
    """Run the AMALGAM bootstrap process.

    Steps:
        1. Locate project root.
        2. Validate required root-level files.
        3. Create .amalgam-core/ if missing.
        4. Initialize STATE.json, HISTORY.json, CHECKPOINT.json,
           SESSION.json, QUEUE.json (idempotent).
    """
    actions: list[str] = []

    log("Starting AMALGAM bootstrap...")

    root = get_project_root()
    log(f"Project root: {root}")
    actions.append(f"Project root: {root}")

    validate_root_files(root)
    actions.append(f"Validated {len(REQUIRED_ROOT_FILES)} required root files")

    core_dir = ensure_core_dir(root)
    actions.append(f"Core directory: {core_dir}")

    created = initialize_json_files(core_dir)
    if created:
        actions.append(f"Initialized: {', '.join(created)}")
    else:
        actions.append("All runtime JSON files already present and valid")

    # Final validation: every bootstrap-owned file must exist and be valid JSON.
    for filename in INITIALIZABLE_FILES:
        path = core_dir / filename
        if not path.exists():
            raise BootstrapError(f"{filename} missing after bootstrap.")
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise BootstrapError(f"{filename} is not valid JSON: {exc}") from exc
    actions.append("Final validation passed -- all runtime JSON files present and valid")

    # Immutable files: assert presence, never write. STATE.schema.json is the
    # Draft-07 contract for STATE.json and must pre-exist; bootstrap does not
    # author the schema.
    missing_immutable = [
        name for name in IMMUTABLE_FILES if not (core_dir / name).exists()
    ]
    if missing_immutable:
        raise BootstrapError(
            "Immutable file missing: " + ", ".join(missing_immutable) +
            ". Create the schema before bootstrapping."
        )
    actions.append(
        "Verified immutable files present: " + ", ".join(IMMUTABLE_FILES)
    )

    # Required output sections -------------------------------------------------
    print()
    print("Architecture Summary")
    print()
    print("  Layer: scripts/ (leaf -- standard library only).")
    print("  Responsibility: Create .amalgam-core/ and initialize the five")
    print("  runtime JSON files (STATE, HISTORY, CHECKPOINT, SESSION, QUEUE).")
    print("  Verifies (never creates) STATE.schema.json -- the immutable")
    print("  Draft-07 contract for STATE.json.")
    print("  Does NOT generate MISSION.md, TASK.md, CONTEXT.md, or REGISTRY.json")
    print("  -- those are owned by scripts/context.py and scripts/registry.py.")
    print("  Dependencies: Python standard library only.")
    print("  Idempotent and safe to rerun.")
    print()
    print("Responsibilities")
    print()
    print("  1. Create folders: .amalgam-core/.")
    print("  2. Validate required files: AGENTS.md, ARCHITECTURE.md,")
    print("     MISSION.md, TASK.md at the repository root.")
    print("  3. Initialize runtime JSON files: STATE.json, HISTORY.json,")
    print("     CHECKPOINT.json, SESSION.json, QUEUE.json.")
    print("  Never: generate MISSION.md, TASK.md, CONTEXT.md, REGISTRY.json.")
    print()
    print("Initialization Flow")
    print()
    for i, action in enumerate(actions, start=1):
        print(f"  {i}. {action}")
    print()
    log("BOOTSTRAP COMPLETE")


if __name__ == "__main__":
    try:
        bootstrap()
    except BootstrapError as exc:
        log(f"FAILED: {exc}")
        sys.exit(1)
    except Exception as exc:
        log(f"UNEXPECTED FAILURE: {exc}")
        sys.exit(1)
