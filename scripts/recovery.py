#!/usr/bin/env python3
"""
AMALGAM Recovery Engine

Extends Checkpoint and Resume into automatic failure recovery.

Responsibilities:
    - Classify failures by type (network, rate-limit, timeout, crash, etc.).
    - Apply retry strategies with exponential backoff and jitter.
    - Restore execution state from CHECKPOINT.json, SESSION.json,
      QUEUE.json, and STATE.json.
    - Integrate with loop.py for automatic stage-level recovery.
    - Produce structured recovery reports.

Dependencies: Python standard library only.
Never imports agents/, brain/, kernel/, or services/.
"""

from __future__ import annotations

import json
import random
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.context import (  # noqa: E402
    core_dir,
    get_project_root,
    load_json,
    now_iso,
    save_json,
    new_uuid,
)
from scripts.loop import (  # noqa: E402
    StageResult,
    run_stage,
    STAGE_NAMES,
    ALL_STAGES,
    log as loop_log,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RECOVERY_VERSION = "1.0"

MAX_RETRIES_DEFAULT = 3


# ---------------------------------------------------------------------------
# Failure classification
# ---------------------------------------------------------------------------


class FailureClass(Enum):
    """Taxonomy of recoverable failures the engine can handle."""

    NETWORK_FAILURE = "NETWORK_FAILURE"
    RATE_LIMIT = "RATE_LIMIT"
    TIMEOUT = "TIMEOUT"
    CRASH = "CRASH"
    KEYBOARD_INTERRUPT = "KEYBOARD_INTERRUPT"
    UNEXPECTED_EXCEPTION = "UNEXPECTED_EXCEPTION"
    MANUAL_STOP = "MANUAL_STOP"

    def is_retryable(self) -> bool:
        """Return True if this failure class supports retry."""
        return self in (
            FailureClass.NETWORK_FAILURE,
            FailureClass.RATE_LIMIT,
            FailureClass.TIMEOUT,
            FailureClass.UNEXPECTED_EXCEPTION,
        )

    def needs_restore(self) -> bool:
        """Return True if state restore is needed before retry."""
        return self in (
            FailureClass.CRASH,
            FailureClass.NETWORK_FAILURE,
            FailureClass.TIMEOUT,
        )

    def is_graceful_stop(self) -> bool:
        """Return True if this failure should save state and stop."""
        return self in (
            FailureClass.KEYBOARD_INTERRUPT,
            FailureClass.MANUAL_STOP,
        )


# ---------------------------------------------------------------------------
# Retry strategy
# ---------------------------------------------------------------------------


@dataclass
class RetryStrategy:
    """Backoff parameters for a failure class.

    Attributes:
        max_retries: Maximum retry attempts before escalation.
        base_delay: Initial delay in seconds before first retry.
        multiplier: Exponential factor applied each retry.
        max_delay: Ceiling on delay in seconds.
        jitter: Fraction of jitter to add (0.0 = none, 0.2 = +/-20%).
    """

    max_retries: int = 3
    base_delay: float = 2.0
    multiplier: float = 2.0
    max_delay: float = 60.0
    jitter: float = 0.2


RETRY_STRATEGIES: dict[FailureClass, RetryStrategy] = {
    FailureClass.NETWORK_FAILURE: RetryStrategy(
        max_retries=5, base_delay=2.0, multiplier=2.0, max_delay=60.0, jitter=0.2
    ),
    FailureClass.RATE_LIMIT: RetryStrategy(
        max_retries=3, base_delay=5.0, multiplier=2.0, max_delay=60.0, jitter=0.2
    ),
    FailureClass.TIMEOUT: RetryStrategy(
        max_retries=3, base_delay=3.0, multiplier=2.0, max_delay=60.0, jitter=0.2
    ),
    FailureClass.CRASH: RetryStrategy(
        max_retries=2, base_delay=1.0, multiplier=1.0, max_delay=5.0, jitter=0.0
    ),
    FailureClass.KEYBOARD_INTERRUPT: RetryStrategy(
        max_retries=1, base_delay=0.0, multiplier=1.0, max_delay=0.0, jitter=0.0
    ),
    FailureClass.UNEXPECTED_EXCEPTION: RetryStrategy(
        max_retries=2, base_delay=2.0, multiplier=2.0, max_delay=30.0, jitter=0.2
    ),
    FailureClass.MANUAL_STOP: RetryStrategy(
        max_retries=1, base_delay=0.0, multiplier=1.0, max_delay=0.0, jitter=0.0
    ),
}


# ---------------------------------------------------------------------------
# Recovery record
# ---------------------------------------------------------------------------


@dataclass
class RecoveryRecord:
    """A single recovery attempt with full context.

    Attributes:
        recovery_id: Unique identifier for this recovery attempt.
        timestamp: When the recovery was initiated.
        failure_class: Classified failure type.
        stage_number: The loop stage that was executing when the failure occurred.
        error_message: Original error description.
        retry_count: Which retry attempt this is (0-indexed).
        strategy: The RetryStrategy used.
        delay_applied: Actual delay in seconds before retry (with jitter).
        resolved: Whether this recovery attempt succeeded.
        resolution: Description of how it was resolved.
        restored_state: Whether state was restored from checkpoint files.
    """

    recovery_id: str
    timestamp: str
    failure_class: FailureClass
    stage_number: int
    error_message: str
    retry_count: int
    strategy: RetryStrategy | None = None
    delay_applied: float = 0.0
    resolved: bool = False
    resolution: str = ""
    restored_state: bool = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def log(message: str) -> None:
    """Print a structured log line with a RECOVERY prefix."""
    print(f"[RECOVERY] {message}")


def _backoff_delay(strategy: RetryStrategy, attempt: int) -> float:
    """Compute the delay in seconds for a given retry attempt.

    Applies exponential backoff with optional jitter.

    Args:
        strategy: The RetryStrategy defining base_delay, multiplier, max_delay.
        attempt: Zero-based retry attempt number.

    Returns:
        Delay in seconds to wait before retrying.
    """
    delay = strategy.base_delay * (strategy.multiplier ** attempt)
    delay = min(delay, strategy.max_delay)
    if strategy.jitter > 0.0:
        jitter_amount = delay * strategy.jitter
        delay += random.uniform(-jitter_amount, jitter_amount)
        delay = max(0.0, delay)
    return round(delay, 2)


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def classify(error: Any, context: dict[str, Any] | None = None) -> FailureClass:
    """Classify an error into a FailureClass.

    Inspects the error type, string representation, and optional context to
    determine which failure class applies.

    Args:
        error: The error object or string to classify.
        context: Optional dict with additional clues (e.g. ``{"status_code": 429}``).

    Returns:
        The best-matching FailureClass.
    """
    ctx = context or {}
    error_str = str(error).lower()
    error_type = type(error).__name__

    status = ctx.get("status_code", ctx.get("status", 0))

    if status == 429 or "429" in error_str or "too many requests" in error_str:
        return FailureClass.RATE_LIMIT

    if status in (502, 503, 504):
        return FailureClass.NETWORK_FAILURE

    if isinstance(error, TimeoutError) or "timeout" in error_str:
        return FailureClass.TIMEOUT

    if isinstance(error, ConnectionError) or "connection" in error_str:
        return FailureClass.NETWORK_FAILURE

    if isinstance(error, OSError):
        return FailureClass.NETWORK_FAILURE

    net_keywords = (
        "network", "connection", "dns", "socket", "refused", "reset",
        "unreachable", "resolve", "eof", "broken pipe",
    )
    if any(kw in error_str for kw in net_keywords):
        return FailureClass.NETWORK_FAILURE

    rate_keywords = ("rate limit", "quota", "exhausted", "resource_exhausted")
    if any(kw in error_str for kw in rate_keywords):
        return FailureClass.RATE_LIMIT

    if isinstance(error, KeyboardInterrupt):
        return FailureClass.KEYBOARD_INTERRUPT

    if ctx.get("manual_stop") or "manual" in error_str:
        return FailureClass.MANUAL_STOP

    crash_keywords = ("crash", "segfault", "segmentation", "abort", "killed")
    if any(kw in error_str for kw in crash_keywords):
        return FailureClass.CRASH

    if ctx.get("crash") or ctx.get("process_exit"):
        return FailureClass.CRASH

    return FailureClass.UNEXPECTED_EXCEPTION


# ---------------------------------------------------------------------------
# State restore
# ---------------------------------------------------------------------------


def restore() -> dict[str, Any]:
    """Restore execution state from all four checkpoint files.

    Reads CHECKPOINT.json, SESSION.json, QUEUE.json, and STATE.json.
    Validates consistency and returns a consolidated restore report.

    Returns:
        Dict with keys:
          - checkpoint: parsed CHECKPOINT.json content (or empty dict).
          - session: parsed SESSION.json content (or empty dict).
          - queue: parsed QUEUE.json content (or empty list).
          - state: parsed STATE.json content (or empty dict).
          - restored_at: ISO 8601 timestamp.
          - consistent: True if all available files parse successfully.
          - warnings: list of any issues found.
    """
    warnings: list[str] = []
    cdir = core_dir()

    checkpoint_raw = load_json("CHECKPOINT.json")
    if not isinstance(checkpoint_raw, dict):
        warnings.append("CHECKPOINT.json is not a dict or is missing.")
        checkpoint = {}
    else:
        checkpoint = checkpoint_raw

    session = load_json("SESSION.json")
    if not isinstance(session, dict):
        warnings.append("SESSION.json is not a dict or is missing.")
        session = {}

    queue = load_json("QUEUE.json")
    if not isinstance(queue, list):
        warnings.append("QUEUE.json is not a list or is missing.")
        queue = []

    state = load_json("STATE.json")
    if not isinstance(state, dict):
        warnings.append("STATE.json is not a dict or is missing.")
        state = {}

    cp_mission = checkpoint.get("current_mission")
    st_mission = None
    st_mission_obj = state.get("current_mission")
    if isinstance(st_mission_obj, dict):
        st_mission = st_mission_obj.get("id")
    if cp_mission and st_mission and cp_mission != st_mission:
        warnings.append(
            f"Mission mismatch: checkpoint={cp_mission}, state={st_mission}."
        )

    result = {
        "checkpoint": checkpoint,
        "session": session,
        "queue": queue,
        "state": state,
        "restored_at": now_iso(),
        "consistent": len(warnings) == 0,
        "warnings": warnings,
    }

    if warnings:
        for w in warnings:
            log(f"  Restore warning: {w}")

    return result


def _save_checkpoint_from_state(state: dict[str, Any]) -> dict[str, Any]:
    """Generate and persist a CHECKPOINT.json from the current STATE.json.

    Used during graceful-stop failures (keyboard interrupt, manual stop) to
    ensure the next invocation can resume.

    Args:
        state: Current STATE.json content.

    Returns:
        The checkpoint dict that was written.
    """
    loop = state.get("loop", {})
    stage = loop.get("stage", 1)
    stage_name = loop.get("stage_name", STAGE_NAMES.get(stage, "Unknown"))
    checkpoints = loop.get("checkpoints", {})
    completed = [
        s for s in ALL_STAGES
        if checkpoints.get(f"stage_{s}") == "completed"
    ]
    remaining = [
        s for s in ALL_STAGES
        if checkpoints.get(f"stage_{s}") != "completed"
    ]

    mission_id = None
    mission_obj = state.get("current_mission")
    if isinstance(mission_obj, dict):
        mission_id = mission_obj.get("id")

    ck = {
        "checkpoint_id": str(uuid.uuid4()),
        "generated_at": now_iso(),
        "stage": stage,
        "stage_name": stage_name,
        "completed_stages": completed,
        "remaining_stages": remaining,
        "current_mission": mission_id,
        "current_task": None,
        "branch": state.get("current_branch", ""),
        "session_id": state.get("session_id", ""),
        "timestamp": now_iso(),
        "recovery_checkpoint": True,
    }

    save_json("CHECKPOINT.json", ck)
    return ck


# ---------------------------------------------------------------------------
# Retry
# ---------------------------------------------------------------------------


def retry(
    stage_number: int,
    failure_class: FailureClass,
    context: dict[str, Any] | None = None,
) -> StageResult | None:
    """Retry a failed stage with exponential backoff.

    Applies the RetryStrategy for the given FailureClass, sleeps for the
    computed backoff delay, then calls loop.run_stage(stage_number).

    Args:
        stage_number: The loop stage number to retry.
        failure_class: The classified failure type.
        context: Optional context dict (may contain "retry_count" override).

    Returns:
        StageResult if the retry succeeded, or None if retries are exhausted.
    """
    ctx = context or {}
    strategy = RETRY_STRATEGIES.get(failure_class, RETRY_STRATEGIES[FailureClass.UNEXPECTED_EXCEPTION])
    attempt = ctx.get("retry_count", 0)

    if attempt >= strategy.max_retries:
        log(f"  Retry {attempt + 1}/{strategy.max_retries} exhausted for "
            f"stage {stage_number} ({failure_class.value}). Escalating.")
        return None

    delay = _backoff_delay(strategy, attempt)
    log(f"  Backoff delay: {delay}s (attempt {attempt + 1}/{strategy.max_retries}, "
        f"base={strategy.base_delay}s, mult={strategy.multiplier}x).")

    time.sleep(delay)

    log(f"  Retrying stage {stage_number} ({STAGE_NAMES.get(stage_number, '?')})...")
    try:
        result = run_stage(stage_number)
        if result.success:
            log(f"  Retry {attempt + 1} succeeded.")
        else:
            log(f"  Retry {attempt + 1} failed: {result.message}")
        return result
    except Exception as exc:
        log(f"  Retry {attempt + 1} raised exception: {exc}")
        return None


# ---------------------------------------------------------------------------
# Recovery
# ---------------------------------------------------------------------------


def recover(
    stage_number: int,
    error: Any,
    context: dict[str, Any] | None = None,
) -> RecoveryRecord:
    """Attempt to recover from a failure during a loop stage.

    This is the main recovery entry point.  It classifies the error, restores
    state if needed, applies backoff retry, and produces a RecoveryRecord
    documenting the outcome.

    Args:
        stage_number: The loop stage that was executing.
        error: The error object or string.
        context: Optional dict with additional clues (status_code, retry_count,
            manual_stop, etc.).

    Returns:
        A RecoveryRecord with the full recovery outcome.
    """
    ctx = context or {}
    fc = classify(error, ctx)
    record = RecoveryRecord(
        recovery_id=str(uuid.uuid4()),
        timestamp=now_iso(),
        failure_class=fc,
        stage_number=stage_number,
        error_message=str(error),
        retry_count=ctx.get("retry_count", 0),
    )

    log(f"Recovery initiated: stage={stage_number}, "
        f"failure={fc.value}, retry={record.retry_count}.")

    if fc.is_graceful_stop():
        state = load_json("STATE.json")
        if isinstance(state, dict):
            _save_checkpoint_from_state(state)
            log("  Checkpoint saved for graceful stop.")
        record.resolved = True
        record.resolution = f"Graceful stop ({fc.value}). State saved."
        log(f"  Resolution: {record.resolution}")
        return record

    if fc.needs_restore():
        restore_result = restore()
        record.restored_state = restore_result["consistent"]
        if not restore_result["consistent"]:
            log(f"  State restore had warnings: {restore_result['warnings']}")
        else:
            log("  State restored successfully.")
    else:
        record.restored_state = False

    attempt = record.retry_count
    strategy = RETRY_STRATEGIES.get(fc, RETRY_STRATEGIES[FailureClass.UNEXPECTED_EXCEPTION])
    record.strategy = strategy

    while attempt < strategy.max_retries:
        ctx["retry_count"] = attempt
        result = retry(stage_number, fc, ctx)

        if result is None:
            attempt += 1
            continue

        if result.success:
            record.resolved = True
            record.resolution = (
                f"Recovered on retry {attempt + 1}/{strategy.max_retries}."
            )
            log(f"  Resolution: {record.resolution}")
            return record

        attempt += 1
        record.retry_count = attempt

    record.resolved = False
    record.resolution = (
        f"Retries exhausted ({strategy.max_retries}). "
        f"Escalating {fc.value} failure."
    )
    log(f"  Resolution: {record.resolution}")
    return record


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def report(record: RecoveryRecord) -> dict[str, Any]:
    """Produce a structured recovery report from a RecoveryRecord.

    Args:
        record: The RecoveryRecord to report on.

    Returns:
        Dict with recovery metadata suitable for logging or storing in
        STATE.json loop.artifacts.recovery_log.
    """
    report_data = {
        "recovery_id": record.recovery_id,
        "timestamp": record.timestamp,
        "failure_class": record.failure_class.value,
        "stage_number": record.stage_number,
        "stage_name": STAGE_NAMES.get(record.stage_number, "?"),
        "error_message": record.error_message,
        "retry_count": record.retry_count,
        "resolved": record.resolved,
        "resolution": record.resolution,
        "restored_state": record.restored_state,
        "strategy": {
            "max_retries": record.strategy.max_retries if record.strategy else 0,
            "base_delay": record.strategy.base_delay if record.strategy else 0.0,
        } if record.strategy else None,
    }

    log(f"Recovery Report: {record.recovery_id}")
    log(f"  Failure Class : {record.failure_class.value}")
    log(f"  Stage         : {record.stage_number} "
        f"({STAGE_NAMES.get(record.stage_number, '?')})")
    log(f"  Retry Count   : {record.retry_count}")
    log(f"  Resolved      : {record.resolved}")
    log(f"  Resolution    : {record.resolution}")

    return report_data


# ---------------------------------------------------------------------------
# Log recovery record to file
# ---------------------------------------------------------------------------


def log_recovery(record: RecoveryRecord) -> None:
    """Append a recovery record to a recovery log in STATE.json.

    The record is appended to STATE.json loop.artifacts.recovery_log so the
    loop engine can track recovery history.

    Args:
        record: The RecoveryRecord to persist.
    """
    state = load_json("STATE.json")
    if not isinstance(state, dict):
        return
    loop = state.get("loop")
    if not isinstance(loop, dict):
        return
    artifacts = loop.get("artifacts")
    if not isinstance(artifacts, dict):
        return
    rlog = artifacts.get("recovery_log")
    if not isinstance(rlog, list):
        rlog = []
        artifacts["recovery_log"] = rlog
    rlog.append(report(record))
    state["last_updated"] = now_iso()
    save_json("STATE.json", state)


# ---------------------------------------------------------------------------
# Wrapper for loop stage with automatic recovery
# ---------------------------------------------------------------------------


def recoverable_stage(
    stage_number: int,
    context: dict[str, Any] | None = None,
) -> StageResult:
    """Execute a loop stage with automatic recovery on failure.

    Wraps ``loop.run_stage(stage_number)``.  If the stage fails, the recovery
    engine classifies the error, restores state if needed, retries with
    exponential backoff, and logs the recovery attempt.

    Args:
        stage_number: The loop stage to execute.
        context: Optional context dict for recovery hints.

    Returns:
        A StageResult indicating success or final failure after all retries.
    """
    ctx = context or {}
    log(f"Recoverable stage {stage_number} ({STAGE_NAMES.get(stage_number, '?')}).")

    try:
        result = run_stage(stage_number)
    except Exception as exc:
        log(f"  Stage {stage_number} raised exception: {exc}")
        rec = recover(stage_number, exc, ctx)
        log_recovery(rec)
        if rec.resolved:
            return StageResult(True, f"Recovered from {rec.failure_class.value}.")
        return StageResult(False, f"Unrecoverable: {rec.resolution}.")

    if result.success:
        return result

    log(f"  Stage {stage_number} returned failure: {result.message}")
    rec = recover(stage_number, result.message, ctx)
    log_recovery(rec)
    if rec.resolved:
        return StageResult(True, f"Recovered from {rec.failure_class.value}.")
    return StageResult(False, f"Unrecoverable: {rec.resolution}.")


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------


COMMAND_MAP: dict[str, str] = {
    "recover": "cmd_recover",
    "retry": "cmd_retry",
    "classify": "cmd_classify",
    "restore": "cmd_restore",
    "report": "cmd_report",
}


def print_help() -> None:
    """Print the available commands."""
    print("AMALGAM Recovery Engine")
    print()
    print("Commands:")
    for cmd in COMMAND_MAP:
        print(f"  py scripts/recovery.py {cmd} [args]")
    print()
    print("  recover <stage> <error>     : Classify and recover from a failure.")
    print("  retry <stage> <failure>     : Retry a stage with backoff.")
    print("  classify <error>            : Classify an error string.")
    print("  restore                     : Restore state from checkpoint files.")
    print("  report <recovery_id>        : Generate a recovery report.")
    print()


def cmd_recover() -> None:
    """CLI handler for the 'recover' command."""
    if len(sys.argv) < 4:
        print("ERROR: Usage: py scripts/recovery.py recover <stage> <error_message>")
        sys.exit(1)
    try:
        stage = int(sys.argv[2])
    except ValueError:
        print(f"ERROR: Invalid stage number '{sys.argv[2]}'. Must be 1-17.")
        sys.exit(1)
    error_msg = sys.argv[3]
    rec = recover(stage, error_msg)
    log_recovery(rec)
    rpt = report(rec)
    print(f"Recovery result: resolved={rpt['resolved']}, resolution={rpt['resolution']}")
    if not rec.resolved:
        sys.exit(1)


def cmd_retry() -> None:
    """CLI handler for the 'retry' command."""
    if len(sys.argv) < 4:
        print("ERROR: Usage: py scripts/recovery.py retry <stage> <failure_class>")
        sys.exit(1)
    try:
        stage = int(sys.argv[2])
    except ValueError:
        print(f"ERROR: Invalid stage number '{sys.argv[2]}'. Must be 1-17.")
        sys.exit(1)
    fc_name = sys.argv[3].upper()
    try:
        fc = FailureClass[fc_name]
    except KeyError:
        valid = ", ".join(fc.value for fc in FailureClass)
        print(f"ERROR: Invalid failure class '{fc_name}'. Valid: {valid}")
        sys.exit(1)
    result = retry(stage, fc)
    if result is None:
        print("Retry exhausted. Escalating.")
        sys.exit(1)
    print(f"Retry result: success={result.success}, message='{result.message}'")
    if not result.success:
        sys.exit(1)


def cmd_classify() -> None:
    """CLI handler for the 'classify' command."""
    if len(sys.argv) < 3:
        print("ERROR: Usage: py scripts/recovery.py classify <error_string>")
        sys.exit(1)
    error_str = " ".join(sys.argv[2:])
    fc = classify(error_str)
    print(f"Classification: {fc.value}")


def cmd_restore() -> None:
    """CLI handler for the 'restore' command."""
    result = restore()
    print()
    print("AMALGAM STATE RESTORE")
    print("-" * 40)
    print(f"Restored at  : {result['restored_at']}")
    print(f"Consistent   : {result['consistent']}")
    print(f"Checkpoint   : {'present' if result['checkpoint'] else 'missing/empty'}")
    print(f"Session      : {'present' if result['session'] else 'missing/empty'}")
    print(f"Queue        : {'present' if isinstance(result['queue'], list) and len(result['queue']) > 0 else 'empty'}")
    print(f"State        : {'present' if result['state'] else 'missing/empty'}")
    if result['warnings']:
        print(f"Warnings     : {len(result['warnings'])}")
        for w in result['warnings']:
            print(f"  - {w}")
    if result['checkpoint']:
        cp = result['checkpoint']
        print(f"  Checkpoint stage: {cp.get('stage', '?')}")
        print(f"  Mission         : {cp.get('current_mission') or 'none'}")
    print()


def cmd_report() -> None:
    """CLI handler for the 'report' command."""
    if len(sys.argv) < 3:
        print("ERROR: Usage: py scripts/recovery.py report <recovery_id>")
        sys.exit(1)
    rec_id = sys.argv[2]
    state = load_json("STATE.json")
    if not isinstance(state, dict):
        print("ERROR: STATE.json not available.")
        sys.exit(1)
    loop = state.get("loop", {})
    artifacts = loop.get("artifacts", {})
    rlog = artifacts.get("recovery_log", [])
    if not isinstance(rlog, list):
        rlog = []
    for entry in rlog:
        if isinstance(entry, dict) and entry.get("recovery_id") == rec_id:
            print(json.dumps(entry, indent=2))
            return
    print(f"Recovery ID '{rec_id}' not found in recovery_log.")


def main() -> None:
    """Parse CLI arguments and dispatch to the requested command."""
    if len(sys.argv) < 2:
        print("Usage: py scripts/recovery.py <command> [args]")
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
    except Exception as exc:
        print(f"ERROR: Command '{cmd}' failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
