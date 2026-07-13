"""Typed Mission 8 contracts and deterministic validators."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
from typing import Any

LIFECYCLE_STATES = {
    "inspect", "reason", "plan", "awaiting_approval", "execute", "test",
    "review", "repair", "replan", "ready_to_commit", "completed", "blocked", "aborted",
}


@dataclass(frozen=True)
class RepositoryContext:
    root: str
    branch: str
    dirty_files: list[str]
    mission: str
    lifecycle: str
    next_action: str
    recent_commits: list[str]
    summaries: dict[str, str]
    provenance: dict[str, str]
    generated_at: str


@dataclass
class PlanTask:
    id: str
    description: str
    action: str
    capability: str
    dependencies: list[str] = field(default_factory=list)
    affected_paths: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    data: Any = None


@dataclass
class EngineeringPlan:
    plan_id: str
    goal: str
    tasks: list[PlanTask]
    verification_commands: list[str]
    risks: list[str] = field(default_factory=list)
    requires_approval: bool = True

    def canonical(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))

    @property
    def plan_hash(self) -> str:
        return sha256(self.canonical().encode("utf-8")).hexdigest()

    def validate(self, allowed_actions: set[str] | None = None) -> None:
        if not self.plan_id or not self.goal or not self.tasks:
            raise ValueError("plan_id, goal and tasks are required")
        ids = [task.id for task in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("task IDs must be unique")
        known = set(ids)
        for task in self.tasks:
            if not task.description or not task.action or not task.capability:
                raise ValueError(f"task {task.id} is incomplete")
            if allowed_actions is not None and task.action not in allowed_actions:
                raise ValueError(f"unknown action: {task.action}")
            if any(dep not in known for dep in task.dependencies):
                raise ValueError(f"task {task.id} has unknown dependency")
            if task.id in task.dependencies:
                raise ValueError(f"task {task.id} depends on itself")
        self._assert_acyclic()

    def _assert_acyclic(self) -> None:
        graph = {task.id: task.dependencies for task in self.tasks}
        active: set[str] = set()
        complete: set[str] = set()
        def visit(node: str) -> None:
            if node in active:
                raise ValueError("plan contains a dependency cycle")
            if node in complete:
                return
            active.add(node)
            for dep in graph[node]:
                visit(dep)
            active.remove(node)
            complete.add(node)
        for node in graph:
            visit(node)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "EngineeringPlan":
        tasks = [PlanTask(**task) for task in value.get("tasks", [])]
        return cls(
            plan_id=str(value.get("plan_id", "")), goal=str(value.get("goal", "")),
            tasks=tasks, verification_commands=list(value.get("verification_commands", [])),
            risks=list(value.get("risks", [])),
            requires_approval=bool(value.get("requires_approval", True)),
        )


@dataclass(frozen=True)
class ReviewVerdict:
    approved: bool
    findings: list[str]
    evidence: list[str]
    checks: dict[str, bool]


@dataclass(frozen=True)
class RepairStrategy:
    failure_class: str
    root_cause: str
    evidence: list[str]
    changed_strategy: str
    actions: list[str]

    @property
    def strategy_hash(self) -> str:
        raw = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return sha256(raw.encode()).hexdigest()
