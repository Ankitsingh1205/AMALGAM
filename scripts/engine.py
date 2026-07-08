#!/usr/bin/env python3
"""
AMALGAM Engine

The single public entry point for AMALGAM Core orchestration.

Responsibilities:
    - initialize:  bootstrap the .amalgam-core directory and runtime files
    - run:         execute the full 17-stage engineering loop
    - resume:      resume from the last checkpoint
    - checkpoint:  write a checkpoint snapshot
    - recover:     classify + retry a loop stage failure
    - audit:       validate all .amalgam-core files
    - rebuild:     regenerate derived markdown files from STATE.json
    - verify:      compare repository state against CHECKSUMS.json
    - complete:    mark the current mission complete and advance state

Engine coordinates.
Other scripts perform the work.
No duplicated logic.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.bootstrap import bootstrap as _bootstrap
from scripts.context import (
    cmd_audit as context_audit,
    cmd_checkpoint as context_checkpoint,
    cmd_complete as context_complete,
    cmd_rebuild as context_rebuild,
    cmd_resume as context_resume,
    cmd_status,
    get_project_root,
    load_json,
    save_json,
)
from scripts.fingerprint import cmd_build as fp_build, cmd_verify as fp_verify
from scripts.loop import run as loop_run, status as loop_status
from scripts.recovery import recover, log_recovery, report as recovery_report


ENGINE_VERSION = "1.0"


def log(message: str) -> None:
    """Print a structured log line with an ENGINE prefix."""
    print(f"[ENGINE] {message}")


# ---------------------------------------------------------------------------
# Commands — each delegates 100 % to the owning script
# ---------------------------------------------------------------------------


def cmd_initialize() -> None:
    """Delegate to bootstrap.py: create .amalgam-core/ and runtime JSON files."""
    log("Command: initialize")
    _bootstrap()
    log("Command complete: initialize")


def cmd_run() -> None:
    """Delegate to loop.py: execute the full 17-stage engineering loop."""
    log("Command: run")
    loop_run()
    loop_status()
    log("Command complete: run")


def cmd_resume() -> None:
    """Delegate to context.py + loop.py: resume from last checkpoint."""
    log("Command: resume")
    context_resume()
    log("Command complete: resume")


def cmd_checkpoint() -> None:
    """Delegate to context.py: write CHECKPOINT.json."""
    log("Command: checkpoint")
    context_checkpoint()
    log("Command complete: checkpoint")


def cmd_recover() -> None:
    """Delegate to recovery.py: classify and retry a loop stage failure.

    Usage: engine recover <stage_number> <error_message>
    """
    log("Command: recover")
    if len(sys.argv) < 4:
        print("ERROR: Usage: py scripts/engine.py recover <stage> <error_message>")
        sys.exit(1)
    try:
        stage = int(sys.argv[2])
    except ValueError:
        print(f"ERROR: Invalid stage number '{sys.argv[2]}'. Must be 1-17.")
        sys.exit(1)
    error_msg = " ".join(sys.argv[3:])
    log(f"Recovering stage {stage} from error: {error_msg}")
    rec = recover(stage, error_msg)
    log_recovery(rec)
    rpt = recovery_report(rec)
    if rec.resolved:
        print(f"Recovery result: resolved=True, resolution={rec.resolution}")
    else:
        print(f"Recovery result: resolved=False, resolution={rec.resolution}")
        sys.exit(1)
    log("Command complete: recover")


def cmd_audit() -> None:
    """Delegate to context.py: validate all .amalgam-core files."""
    log("Command: audit")
    context_audit()
    log("Command complete: audit")


def cmd_rebuild() -> None:
    """Delegate to context.py: regenerate MISSION.md, TASK.md, CONTEXT.md."""
    log("Command: rebuild")
    context_rebuild()
    log("Command complete: rebuild")


def cmd_verify() -> None:
    """Delegate to fingerprint.py: verify repository against CHECKSUMS.json."""
    log("Command: verify")
    fp_verify()
    log("Command complete: verify")


def cmd_complete() -> None:
    """Delegate to context.py: mark current mission complete and advance state."""
    log("Command: complete")
    context_complete()
    log("Command complete: complete")


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------

COMMAND_MAP: dict[str, str] = {
    "initialize": "cmd_initialize",
    "init": "cmd_initialize",
    "run": "cmd_run",
    "resume": "cmd_resume",
    "checkpoint": "cmd_checkpoint",
    "recover": "cmd_recover",
    "audit": "cmd_audit",
    "rebuild": "cmd_rebuild",
    "verify": "cmd_verify",
    "complete": "cmd_complete",
}


def print_help() -> None:
    """Print the available commands."""
    print("AMALGAM Engine v1.0")
    print()
    print("The single public entry point for AMALGAM Core orchestration.")
    print()
    print("Commands:")
    for _, func_name in sorted(
        (k, v) for k, v in COMMAND_MAP.items() if k != "init"
    ):
        print(f"  py scripts/engine.py {func_name[4:]}")
    print()
    print("  initialize  : Bootstrap .amalgam-core directory and runtime files")
    print("  run         : Execute the full 17-stage engineering loop")
    print("  resume      : Resume from the last checkpoint")
    print("  checkpoint  : Write a checkpoint snapshot")
    print("  recover     : Classify + retry a loop stage failure")
    print("  audit       : Validate all .amalgam-core files")
    print("  rebuild     : Regenerate MISSION.md, TASK.md, CONTEXT.md")
    print("  verify      : Compare repository state against CHECKSUMS.json")
    print("  complete    : Mark current mission complete and advance state")
    print()


def main() -> None:
    """Parse CLI arguments and dispatch to the requested command."""
    if len(sys.argv) < 2:
        print("Usage: py scripts/engine.py <command> [args]")
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
        start = time.time()
        func()
        elapsed = round(time.time() - start, 2)
        log(f"ENGINE COMPLETE ({elapsed}s)")
    except Exception as exc:
        print(f"ERROR: Command '{cmd}' failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
