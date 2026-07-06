#!/usr/bin/env python3
"""
AMALGAM Context Engine

Responsibilities:
    - Read STATE.json as the single source of truth.
    - Execute context commands: status, complete, next, checkpoint,
      resume, audit, rebuild.
    - Regenerate derived artifacts (MISSION.md, TASK.md, CONTEXT.md)
      from STATE.json data.
    - Validate all .amalgam-core files for consistency.

Python standard library only.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CORE_DIR_NAME = ".amalgam-core"
CORE_FILES = [
    "AGENTS.md", "CONTEXT.md", "HISTORY.json", "LOOP.md",
    "MISSION.md", "REGISTRY.json", "STATE.json", "TASK.md", "WORKFLOW.yaml",
]

STAGE_ORDER = [
    "understand", "plan", "implement", "verify",
    "test", "review", "report",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_project_root() -> Path:
    """Return the repository root directory."""
    return Path(__file__).resolve().parent.parent


def core_dir() -> Path:
    """Return the .amalgam-core directory path."""
    return get_project_root() / CORE_DIR_NAME


def now_iso() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def new_uuid() -> str:
    """Return a new UUID4 string."""
    return str(uuid.uuid4())


def load_state() -> dict[str, Any]:
    """Load the runtime STATE.json instance from .amalgam-core."""
    path = core_dir() / "STATE.json"
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return {}
    return json.loads(raw)


def save_state(state: dict[str, Any]) -> None:
    """Write the runtime STATE.json instance atomically."""
    state["last_updated"] = now_iso()
    path = core_dir() / "STATE.json"
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def load_json(file_name: str) -> Any:
    """Load a JSON file from .amalgam-core, returning parsed data or a safe default."""
    path = core_dir() / file_name
    if not path.exists():
        return {} if file_name != "HISTORY.json" else []
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return {} if file_name != "HISTORY.json" else []
    return json.loads(raw)


def save_json(file_name: str, data: Any) -> None:
    """Write a JSON file to .amalgam-core."""
    path = core_dir() / file_name
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _safe_str(value: Any, default: str = "—") -> str:
    """Return a safe string representation of any value."""
    if value is None:
        return default
    return str(value)


def _format_timestamp(ts: str | None) -> str:
    """Return a human-readable timestamp or placeholder."""
    if not ts:
        return "—"
    try:
        return ts[:19].replace("T", " ")
    except Exception:
        return ts


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def cmd_status() -> None:
    """Display the current AMALGAM runtime status from STATE.json."""
    state = load_state()
    print()
    print("AMALGAM STATUS")
    print("-" * 40)

    mission = state.get("current_mission")
    if mission and mission is not None:
        print(f"Current Mission  : {mission.get('id','?')} — {mission.get('title','?')}")
        print(f"Mission Status   : {mission.get('status','?')}")
    else:
        print("Current Mission  : None")

    task = state.get("current_task")
    if task and task is not None:
        print(f"Current Task     : {task.get('id','?')} — {task.get('title','?')}")
    else:
        print("Current Task     : None")

    print(f"Task Status      : {_safe_str(state.get('task_status'))}")
    print(f"Current Stage    : {_safe_str(state.get('current_stage'))}")
    print(f"Branch           : {_safe_str(state.get('current_branch'))}")

    print("-" * 40)
    print("Completed Missions")
    completed = state.get("completed_missions", [])
    if completed:
        for m in completed:
            print(f"  {m.get('id','?')} — {m.get('title','?')}  ({_format_timestamp(m.get('completed_at'))})")
    else:
        print("  None")

    print("-" * 40)
    next_m = state.get("next_mission")
    if next_m and next_m is not None:
        print(f"Next Mission     : {next_m.get('id','?')} — {next_m.get('title','?')}")
    else:
        print("Next Mission     : None")

    print("-" * 40)
    checkpoint = state.get("checkpoint")
    if checkpoint:
        print(f"Checkpoint       : stage={_safe_str(checkpoint.get('stage'))} "
              f"seq={_safe_str(checkpoint.get('sequence'))} "
              f"at={_format_timestamp(checkpoint.get('at'))}")
    else:
        print("Checkpoint       : None")

    worker = state.get("current_worker")
    if worker:
        print(f"Worker           : {_safe_str(worker.get('agent'))} @ {_safe_str(worker.get('host'))}")
    model = state.get("model")
    if model:
        print(f"Model            : {_safe_str(model.get('id'))} ({_safe_str(model.get('role'))})")

    print("-" * 40)
    print("Session")
    print(f"  ID             : {_safe_str(state.get('session_id'))}")
    print(f"  Last Updated   : {_format_timestamp(state.get('last_updated'))}")
    provider = state.get("provider")
    if provider:
        rl = provider.get("rate_limit", {})
        print(f"  Provider       : {_safe_str(provider.get('name'))} "
              f"(rpm={rl.get('requests_per_minute','?')}, "
              f"concurrent={rl.get('max_concurrent','?')})")

    print("-" * 40)
    queue = state.get("queue", [])
    if queue:
        print(f"Queue            : {len(queue)} items pending")
        for item in sorted(queue, key=lambda x: x.get("priority", 0)):
            print(f"  [{item.get('priority','?')}] {item.get('kind','?')} "
                  f"— {item.get('id','?')} (stage={_safe_str(item.get('stage'))})")
    else:
        print("Queue            : Empty")

    tests = state.get("tests")
    if tests:
        print("-" * 40)
        print(f"Tests            : {tests.get('passed',0)} passed, "
              f"{tests.get('failed',0)} failed, "
              f"{tests.get('total',0)} total "
              f"({_safe_str(tests.get('status'))})")

    print()


# ---------------------------------------------------------------------------
# Complete
# ---------------------------------------------------------------------------

def cmd_complete() -> None:
    """Mark the current mission as complete and advance state."""
    state = load_state()
    mission = state.get("current_mission")
    if not mission or mission is None:
        print("ERROR: No active mission to complete.")
        return

    completed_at = now_iso()

    completed_entry = {
        "id": mission.get("id", "UNKNOWN"),
        "title": mission.get("title", "Unknown"),
        "completed_at": completed_at,
    }

    completed_list: list[dict[str, Any]] = state.get("completed_missions", [])
    if not completed_list or not isinstance(completed_list, list):
        completed_list = []
    completed_list.append(completed_entry)
    state["completed_missions"] = completed_list

    history: list[dict[str, Any]] = load_json("HISTORY.json")
    if not isinstance(history, list):
        history = []
    history.append({
        "entry_id": new_uuid(),
        "timestamp": completed_at,
        "event": "mission_completed",
        "mission_id": completed_entry["id"],
        "mission_title": completed_entry["title"],
    })
    save_json("HISTORY.json", history)

    next_m = state.get("next_mission")
    if next_m and next_m is not None:
        next_m["status"] = "in_progress"
        next_m["started_at"] = completed_at
        state["current_mission"] = next_m
        state["next_mission"] = None
        state["current_task"] = None
        state["task_status"] = "pending"
        state["current_stage"] = "idle"
        state["checkpoint"] = {}
        state["queue"] = []
    else:
        state["current_mission"] = None
        state["current_task"] = None
        state["task_status"] = "pending"
        state["current_stage"] = "idle"
        state["checkpoint"] = {}
        state["queue"] = []

    save_state(state)
    _rebuild_all(state)
    print(f"Mission {completed_entry['id']} — {completed_entry['title']} marked COMPLETE.")
    if next_m:
        print(f"Advanced to next mission: {next_m.get('id')} — {next_m.get('title')}.")


# ---------------------------------------------------------------------------
# Next
# ---------------------------------------------------------------------------

def cmd_next() -> None:
    """Advance to the next queued mission, preserving current one if complete."""
    state = load_state()
    current = state.get("current_mission")
    if current and current is not None:
        current_status = current.get("status", "")
        if current_status != "completed":
            print(f"ERROR: Current mission {current.get('id','?')} is not completed "
                  f"(status={current_status}). Use 'complete' first.")
            return

    next_m = state.get("next_mission")
    if not next_m or next_m is None:
        print("ERROR: No next_mission queued in STATE.json.")
        return

    next_m["status"] = "in_progress"
    next_m["started_at"] = now_iso()
    state["current_mission"] = next_m
    state["next_mission"] = None
    state["current_task"] = None
    state["task_status"] = "pending"
    state["current_stage"] = "idle"
    state["checkpoint"] = {}
    state["queue"] = []

    save_state(state)
    _rebuild_all(state)
    print(f"Advanced to mission: {next_m['id']} — {next_m['title']}.")


# ---------------------------------------------------------------------------
# Checkpoint
# ---------------------------------------------------------------------------

def cmd_checkpoint() -> None:
    """Generate CHECKPOINT.json recording the current stage and state."""
    state = load_state()
    current_stage = state.get("current_stage", "idle")
    completed_stages: list[str] = []
    remaining_stages: list[str] = []

    idx = STAGE_ORDER.index(current_stage) if current_stage in STAGE_ORDER else -1
    if idx >= 0:
        completed_stages = STAGE_ORDER[:idx]
        remaining_stages = STAGE_ORDER[idx:]
    elif current_stage == "idle":
        completed_stages = []
        remaining_stages = STAGE_ORDER[:]
    else:
        remaining_stages = STAGE_ORDER[:]

    checkpoint_data: dict[str, Any] = {
        "checkpoint_id": new_uuid(),
        "generated_at": now_iso(),
        "stage": current_stage,
        "completed_stages": completed_stages,
        "remaining_stages": remaining_stages,
        "current_mission": (
            state["current_mission"].get("id") if state.get("current_mission") else None
        ),
        "current_task": (
            state["current_task"].get("id") if state.get("current_task") else None
        ),
        "branch": state.get("current_branch", ""),
        "session_id": state.get("session_id", ""),
        "timestamp": now_iso(),
    }

    path = core_dir() / "CHECKPOINT.json"
    path.write_text(json.dumps(checkpoint_data, indent=2), encoding="utf-8")

    state["checkpoint"] = {
        "sequence": state.get("checkpoint", {}).get("sequence", 0) + 1,
        "stage": current_stage,
        "at": now_iso(),
        "by": {
            "worker": (
                state["current_worker"].get("agent", "context_engine")
                if state.get("current_worker")
                else "context_engine"
            ),
        },
    }
    save_state(state)

    print(f"Checkpoint {checkpoint_data['checkpoint_id']} saved to CHECKPOINT.json.")
    print(f"  Stage           : {current_stage}")
    print(f"  Completed       : {', '.join(completed_stages) if completed_stages else 'none'}")
    print(f"  Remaining       : {', '.join(remaining_stages)}")
    print(f"  Current Mission : {checkpoint_data['current_mission'] or 'none'}")


# ---------------------------------------------------------------------------
# Resume
# ---------------------------------------------------------------------------

def cmd_resume() -> None:
    """Resume from the latest CHECKPOINT.json. Never repeat completed work."""
    checkpoint_path = core_dir() / "CHECKPOINT.json"
    if not checkpoint_path.exists():
        print("ERROR: No CHECKPOINT.json found. Nothing to resume.")
        return

    raw = checkpoint_path.read_text(encoding="utf-8").strip()
    if not raw:
        print("ERROR: CHECKPOINT.json is empty.")
        return

    cp = json.loads(raw)
    current_stage = cp.get("stage", "idle")
    completed_stages = cp.get("completed_stages", [])
    remaining_stages = cp.get("remaining_stages", [])

    print(f"Resuming from checkpoint: stage={current_stage}")
    print(f"  Completed stages : {', '.join(completed_stages) if completed_stages else 'none'}")
    print(f"  Remaining stages : {', '.join(remaining_stages)}")
    print(f"  Mission          : {cp.get('current_mission') or 'none'}")
    print(f"  Task             : {cp.get('current_task') or 'none'}")
    print(f"  Branch           : {cp.get('branch') or 'none'}")

    state = load_state()
    state["current_stage"] = current_stage
    save_state(state)

    if remaining_stages:
        print()
        print("Next stage to execute:")
        print(f"  => {remaining_stages[0]}")
    print()
    print("State restored. Resume from current stage. Do NOT repeat completed stages.")


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

def cmd_audit() -> None:
    """Validate all .amalgam-core files and report inconsistencies."""
    issues: list[str] = []
    ok: list[str] = []

    cdir = core_dir()

    state_path = cdir / "STATE.json"
    schema_path = cdir / "STATE.schema.json"
    state_raw = state_path.read_text(encoding="utf-8").strip() if state_path.exists() else ""
    if not state_raw:
        issues.append("STATE.json is missing or empty.")
    else:
        try:
            state_obj = json.loads(state_raw)
            if isinstance(state_obj, list):
                issues.append("STATE.json is an array, expected an object.")
            elif isinstance(state_obj, dict):
                # After the schema/instance split, STATE.json must be a runtime
                # instance only. Schema-marker keys indicate the legacy mixed
                # file was never split out into STATE.schema.json.
                leaked_schema_keys = {
                    k for k in ("$schema", "$id", "properties", "required")
                    if k in state_obj
                }
                if leaked_schema_keys:
                    issues.append(
                        "STATE.json contains schema keys "
                        f"({', '.join(sorted(leaked_schema_keys))}); "
                        "split them into STATE.schema.json."
                    )
                else:
                    ok.append("STATE.json is a runtime instance (no schema keys).")
        except json.JSONDecodeError as exc:
            issues.append(f"STATE.json is not valid JSON: {exc}")

    # STATE.schema.json is the immutable Draft-07 contract for STATE.json.
    if not schema_path.exists():
        issues.append("STATE.schema.json is missing (immutable state contract).")
    else:
        try:
            schema_obj = json.loads(schema_path.read_text(encoding="utf-8"))
            if not isinstance(schema_obj, dict):
                issues.append("STATE.schema.json is not a JSON object.")
            elif "$schema" not in schema_obj or "properties" not in schema_obj:
                issues.append("STATE.schema.json is not a valid Draft-07 schema.")
            else:
                ok.append("STATE.schema.json present (Draft-07 contract).")
        except json.JSONDecodeError as exc:
            issues.append(f"STATE.schema.json is not valid JSON: {exc}")

    workflow_path = cdir / "WORKFLOW.yaml"
    if not workflow_path.exists():
        issues.append("WORKFLOW.yaml is missing.")
    else:
        yaml_raw = workflow_path.read_text(encoding="utf-8").strip()
        if not yaml_raw:
            issues.append("WORKFLOW.yaml is empty.")
        elif "workflow:" not in yaml_raw:
            issues.append("WORKFLOW.yaml is missing the 'workflow:' key.")
        else:
            ok.append("WORKFLOW.yaml present and non-empty.")

    reg = load_json("REGISTRY.json")
    if isinstance(reg, dict):
        components = reg.get("components", {})
        all_empty = all(
            isinstance(v, list) and len(v) == 0 for v in components.values()
        ) if components else True
        if all_empty and not reg.get("verified"):
            issues.append("REGISTRY.json has empty components and is not verified.")
        elif not all_empty:
            ok.append(f"REGISTRY.json has {sum(len(v) for v in components.values() if isinstance(v, list))} registered components.")
        if reg.get("verified"):
            ok.append("REGISTRY.json is marked verified.")
    else:
        issues.append("REGISTRY.json is not a valid object.")

    history = load_json("HISTORY.json")
    if isinstance(history, list):
        if len(history) == 0:
            issues.append("HISTORY.json is empty (no recorded history).")
        else:
            ok.append(f"HISTORY.json contains {len(history)} entries.")
    else:
        issues.append("HISTORY.json is not a valid array.")

    for md_file in ["MISSION.md", "TASK.md", "CONTEXT.md"]:
        md_path = cdir / md_file
        if not md_path.exists():
            issues.append(f"{md_file} is missing.")
        else:
            content = md_path.read_text(encoding="utf-8").strip()
            if not content:
                issues.append(f"{md_file} is empty.")
            else:
                ok.append(f"{md_file} present and non-empty ({len(content.splitlines())} lines).")

    for core_file in CORE_FILES:
        fpath = cdir / core_file
        if not fpath.exists():
            issues.append(f"Required core file {core_file} is missing.")
        elif fpath.read_text(encoding="utf-8").strip() == "":
            issues.append(f"Required core file {core_file} is empty.")

    print("AMALGAM AUDIT")
    print("=" * 40)
    if issues:
        print(f"\nISSUES ({len(issues)}):")
        for i, iss in enumerate(issues, 1):
            print(f"  {i}. {iss}")
    else:
        print("\nISSUES: None")

    print(f"\nOK ({len(ok)}):")
    for item in ok:
        print(f"  - {item}")

    if not issues:
        print("\nVERDICT: CLEAN — All files consistent.")
    else:
        print(f"\nVERDICT: {len(issues)} inconsistencies found. Run 'rebuild' to regenerate.")


# ---------------------------------------------------------------------------
# Rebuild
# ---------------------------------------------------------------------------

def cmd_rebuild() -> None:
    """Regenerate MISSION.md, TASK.md, and CONTEXT.md from STATE.json."""
    state = load_state()
    if not state:
        print("ERROR: STATE.json is empty or missing. Cannot rebuild.")
        return
    _rebuild_all(state)
    print("Rebuilt MISSION.md, TASK.md, and CONTEXT.md from STATE.json.")


def _rebuild_all(state: dict[str, Any]) -> None:
    """Internal: regenerate all three derived markdown files."""
    _write_mission_md(state)
    _write_task_md(state)
    _write_context_md(state)


def _write_mission_md(state: dict[str, Any]) -> None:
    """Generate MISSION.md from STATE.json current_mission and completed_missions."""
    current = state.get("current_mission")
    completed = state.get("completed_missions") or []
    mission = state.get("current_mission")

    lines: list[str] = []
    lines.append("# MISSION")
    lines.append("")

    if current and current is not None:
        lines.append("## Current Mission")
        lines.append("")
        lines.append(f"- **ID**: {current.get('id', '—')}")
        lines.append(f"- **Title**: {current.get('title', '—')}")
        lines.append(f"- **Status**: {current.get('status', '—')}")
        lines.append(f"- **Started**: {_format_timestamp(current.get('started_at'))}")
        lines.append(f"- **Spec Path**: {current.get('spec_path', '—')}")
    else:
        lines.append("## Current Mission")
        lines.append("")
        lines.append("No active mission.")
        lines.append("")

    next_m = state.get("next_mission")
    if next_m and next_m is not None:
        lines.append("")
        lines.append("## Next Mission")
        lines.append("")
        lines.append(f"- **ID**: {next_m.get('id', '—')}")
        lines.append(f"- **Title**: {next_m.get('title', '—')}")
        lines.append(f"- **Spec Path**: {next_m.get('spec_path', '—')}")
    lines.append("")

    if completed:
        lines.append("## Completed Missions")
        lines.append("")
        for i, m in enumerate(completed, 1):
            lines.append(f"### {i}. {m.get('id', '?')} — {m.get('title', '?')}")
            lines.append(f"- Completed at: {_format_timestamp(m.get('completed_at'))}")
            lines.append("")
    else:
        lines.append("## Completed Missions")
        lines.append("")
        lines.append("None.")
        lines.append("")

    if mission:
        lines.append("## Mission State")
        lines.append("")
        stage = state.get("current_stage", "idle")
        task_status = state.get("task_status", "pending")
        task = state.get("current_task")
        lines.append(f"- **Current Stage**: {stage}")
        lines.append(f"- **Task Status**: {task_status}")
        lines.append(f"- **Branch**: {state.get('current_branch', '—')}")
        if task and task is not None:
            lines.append(f"- **Current Task**: {task.get('id','?')} — {task.get('title','?')}")

    content = "\n".join(lines) + "\n"
    (core_dir() / "MISSION.md").write_text(content, encoding="utf-8")


def _write_task_md(state: dict[str, Any]) -> None:
    """Generate TASK.md from STATE.json current_task and queue."""
    task = state.get("current_task")
    lines: list[str] = []
    lines.append("# Current Task")
    lines.append("")

    if task and task is not None:
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        lines.append(f"| Task ID | {task.get('id', '—')} |")
        lines.append(f"| Title | {task.get('title', '—')} |")
        lines.append(f"| Mission ID | {task.get('mission_id', '—')} |")
        lines.append(f"| Started | {_format_timestamp(task.get('started_at'))} |")
    else:
        lines.append("No active task.")
        lines.append("")

    lines.append("")
    lines.append("# Task State")
    lines.append("")
    lines.append(f"- **Status**: {state.get('task_status', 'pending')}")
    lines.append(f"- **Stage**: {state.get('current_stage', 'idle')}")
    lines.append(f"- **Branch**: {state.get('current_branch', '—')}")

    tests = state.get("tests")
    if tests:
        lines.append("")
        lines.append("# Test Baseline")
        lines.append("")
        lines.append(f"- **Passed**: {tests.get('passed', 0)}")
        lines.append(f"- **Failed**: {tests.get('failed', 0)}")
        lines.append(f"- **Total**: {tests.get('total', 0)}")
        lines.append(f"- **Status**: {tests.get('status', 'not_run')}")

    queue = state.get("queue", [])
    if queue:
        lines.append("")
        lines.append("# Queue")
        lines.append("")
        for item in sorted(queue, key=lambda x: x.get("priority", 0)):
            lines.append(f"- [{item.get('priority','?')}] {item.get('kind','?')}: "
                         f"{item.get('id','?')} (stage={item.get('stage','—')})")

    mission = state.get("current_mission")
    if mission and mission is not None:
        lines.append("")
        lines.append("# Linked Mission")
        lines.append("")
        lines.append(f"- **{mission.get('id', '?')}**: {mission.get('title', '?')}")
        lines.append(f"- **Status**: {mission.get('status', '?')}")

    content = "\n".join(lines) + "\n"
    (core_dir() / "TASK.md").write_text(content, encoding="utf-8")


def _write_context_md(state: dict[str, Any]) -> None:
    """Generate CONTEXT.md from STATE.json runtime data."""
    timestamp = now_iso()
    lines: list[str] = []
    lines.append("# AMALGAM Runtime Context")
    lines.append("")
    lines.append(f"Generated: {timestamp}")
    lines.append("Version: 1.0")
    lines.append("Status: Active")
    lines.append("")
    lines.append("## Session")
    lines.append("")
    lines.append(f"- **Session ID**: {state.get('session_id', '—')}")
    lines.append(f"- **Last Updated**: {_format_timestamp(state.get('last_updated'))}")
    lines.append(f"- **Architecture Version**: {state.get('architecture_version', '—')}")
    lines.append(f"- **Repository Version**: {state.get('repository_version', '—')}")
    lines.append("")
    lines.append("## Active Mission")
    lines.append("")
    mission = state.get("current_mission")
    if mission and mission is not None:
        lines.append(f"- **ID**: {mission.get('id', '—')}")
        lines.append(f"- **Title**: {mission.get('title', '—')}")
        lines.append(f"- **Status**: {mission.get('status', '—')}")
        lines.append(f"- **Started**: {_format_timestamp(mission.get('started_at'))}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Active Task")
    lines.append("")
    task = state.get("current_task")
    if task and task is not None:
        lines.append(f"- **ID**: {task.get('id', '—')}")
        lines.append(f"- **Title**: {task.get('title', '—')}")
        lines.append(f"- **Status**: {state.get('task_status', 'pending')}")
        lines.append(f"- **Stage**: {state.get('current_stage', 'idle')}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Repository")
    lines.append("")
    repo = state.get("repository", {})
    head = repo.get("head", {})
    lines.append(f"- **Branch**: {state.get('current_branch', '—')}")
    lines.append(f"- **HEAD**: {head.get('short_sha', '—')}")
    lines.append(f"- **Clean**: {'yes' if repo.get('status', {}).get('clean', False) else 'no'}")
    recent = state.get("recent_commit")
    if recent:
        lines.append(f"- **Recent Commit**: {recent.get('sha', '—')[:7]} — {recent.get('subject', '—')}")
    lines.append("")
    lines.append("## Infrastructure")
    lines.append("")
    lines.append(f"- **Provider**: {state.get('provider', {}).get('name', '—')}")
    lines.append(f"- **Model**: {state.get('model', {}).get('id', '—')} ({state.get('model', {}).get('role', '—')})")
    lines.append(f"- **Worker**: {state.get('current_worker', {}).get('agent', '—')} @ {state.get('current_worker', {}).get('host', '—')}")
    lines.append("")
    lines.append("## Tests")
    lines.append("")
    tests = state.get("tests", {})
    lines.append(f"- **Last Run**: {_format_timestamp(tests.get('run_at'))}")
    lines.append(f"- **Passed**: {tests.get('passed', 0)}")
    lines.append(f"- **Failed**: {tests.get('failed', 0)}")
    lines.append(f"- **Total**: {tests.get('total', 0)}")
    lines.append(f"- **Status**: {tests.get('status', 'not_run')}")
    lines.append("")
    lines.append("## Active Documents")
    lines.append("")
    lines.append("- AGENTS.md")
    lines.append("- ARCHITECTURE.md")
    lines.append("- MISSION.md")
    lines.append("- TASK.md")
    lines.append("- WORKFLOW.yaml")

    content = "\n".join(lines) + "\n"
    (core_dir() / "CONTEXT.md").write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI Dispatch
# ---------------------------------------------------------------------------

COMMAND_MAP: dict[str, str] = {
    "status": "cmd_status",
    "complete": "cmd_complete",
    "next": "cmd_next",
    "checkpoint": "cmd_checkpoint",
    "resume": "cmd_resume",
    "audit": "cmd_audit",
    "rebuild": "cmd_rebuild",
}


def print_help() -> None:
    """Print the available commands."""
    print("AMALGAM Context Engine")
    print()
    print("Commands:")
    for cmd in COMMAND_MAP:
        print(f"  py scripts/context.py {cmd}")
    print()


def main() -> None:
    """Parse CLI arguments and dispatch to the appropriate command."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: py scripts/context.py <command>")
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