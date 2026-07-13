"""Atomic, resumable Mission 8 checkpoint storage."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from brain.engineering_contracts import LIFECYCLE_STATES


class MissionCheckpointStore:
    def __init__(self, root: str | Path):
        self.path = Path(root).resolve() / ".amalgam-core" / "MISSION_8_STATE.json"

    def load(self) -> dict[str, Any]:
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                raise ValueError("checkpoint must be an object")
            return value
        except FileNotFoundError:
            return self.initial()

    def save(self, state: dict[str, Any]) -> dict[str, Any]:
        lifecycle = state.get("lifecycle")
        if lifecycle not in LIFECYCLE_STATES:
            raise ValueError(f"invalid lifecycle: {lifecycle}")
        state = dict(state)
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(self.path)
        return state

    def transition(self, lifecycle: str, **updates: Any) -> dict[str, Any]:
        state = self.load()
        state.update(updates)
        state["lifecycle"] = lifecycle
        return self.save(state)

    @staticmethod
    def initial() -> dict[str, Any]:
        return {
            "version": "8.0", "mission": "Mission 8", "lifecycle": "inspect",
            "goal": None, "plan_id": None, "plan_hash": None,
            "approved_plan_hash": None, "completed_task_ids": [], "repair_count": 0,
            "repair_hashes": [], "review": None, "test_evidence": [], "commit_sha": None,
        }
