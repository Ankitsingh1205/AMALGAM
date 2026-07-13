"""Deterministic read-only repository reconstruction for Mission 8."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

from brain.engineering_contracts import RepositoryContext


class RepositoryContextEngine:
    """Build bounded, provenance-carrying context without chat history."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def build(self) -> RepositoryContext:
        state_path = self.root / ".amalgam-core" / "STATE.json"
        state = self._json(state_path)
        branch = self._git("branch", "--show-current") or "unknown"
        dirty = [line[3:] for line in self._git("status", "--porcelain").splitlines() if len(line) > 3]
        commits = self._git("log", "-5", "--pretty=%h %s").splitlines()
        lifecycle = str(state.get("lifecycle", state.get("phase", "inspect")))
        mission = str(state.get("mission", "Mission 8"))
        next_action = self._next_action(lifecycle, state, dirty)
        docs = {
            "roadmap": self._bounded(self.root / "docs" / "00_START_HERE" / "ROADMAP_CANON.md"),
            "architecture": self._bounded(self.root / "docs" / "00_START_HERE" / "MISSION_8_MASTER_ARCHITECTURE.md"),
        }
        return RepositoryContext(
            root=str(self.root), branch=branch, dirty_files=dirty, mission=mission,
            lifecycle=lifecycle, next_action=next_action, recent_commits=commits,
            summaries=docs,
            provenance={"state": str(state_path), "git": "git status/log", "docs": "canonical bounded excerpts"},
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    def status(self) -> dict:
        context = self.build()
        return {
            "mission": context.mission, "lifecycle": context.lifecycle,
            "branch": context.branch, "dirty_files": context.dirty_files,
            "next_action": context.next_action,
        }

    def _next_action(self, lifecycle: str, state: dict, dirty: list[str]) -> str:
        if lifecycle == "awaiting_approval":
            return f"approve {state.get('plan_id', '<plan-id>')}"
        if lifecycle in {"blocked", "aborted", "completed"}:
            return "human_decision" if lifecycle == "blocked" else "start_new_goal"
        if lifecycle in {"execute", "test", "review", "repair", "replan"}:
            return "resume"
        if dirty:
            return "inspect_dirty_state"
        return "run"

    def _git(self, *args: str) -> str:
        result = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() if result.returncode == 0 else ""

    @staticmethod
    def _json(path: Path) -> dict:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            return value if isinstance(value, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    @staticmethod
    def _bounded(path: Path, limit: int = 4000) -> str:
        try:
            return path.read_text(encoding="utf-8")[:limit]
        except OSError:
            return ""
