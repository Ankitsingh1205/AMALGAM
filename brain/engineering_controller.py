"""Approval-gated, resumable Mission 8 engineering controller."""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import subprocess
from typing import Callable

from brain.engineering_contracts import EngineeringPlan
from brain.engineering_review import EngineeringReviewer
from brain.mission_checkpoint import MissionCheckpointStore
from brain.repository_context import RepositoryContextEngine
from brain.structured_reasoning import StructuredReasoner
from kernel.executor import Executor
from kernel.task import Task
from services.git_service import GitService


class AuthorityError(RuntimeError):
    pass


class EngineeringController:
    MAX_REPAIRS = 2
    SAFE_VERIFY_PREFIXES = ("python -m pytest", "pytest", "python scripts/")

    def __init__(self, root: str | Path, reasoner: StructuredReasoner | None = None,
                 reviewer: EngineeringReviewer | None = None):
        self.root = Path(root).resolve()
        self.context_engine = RepositoryContextEngine(self.root)
        self.store = MissionCheckpointStore(self.root)
        self.reasoner = reasoner or StructuredReasoner()
        self.reviewer = reviewer or EngineeringReviewer()
        self.git = GitService(self.root)

    def status(self) -> dict:
        checkpoint = self.store.load()
        context = self.context_engine.status()
        context.update({key: checkpoint.get(key) for key in (
            "goal", "plan_id", "plan_hash", "repair_count", "review", "commit_sha")})
        context["lifecycle"] = checkpoint.get("lifecycle", context["lifecycle"])
        context["next_action"] = self._next_action(checkpoint)
        return context

    def run(self, goal: str) -> dict:
        if not goal.strip():
            raise ValueError("goal is required")
        state = self.store.transition("reason", goal=goal, approved_plan_hash=None,
                                      completed_task_ids=[], repair_count=0, review=None,
                                      test_evidence=[], commit_sha=None)
        context = self.context_engine.build()
        plan = self.reasoner.plan(goal, context)
        plan.validate()
        state = self.store.transition(
            "awaiting_approval", goal=goal, plan_id=plan.plan_id,
            plan_hash=plan.plan_hash, plan=asdict(plan), baseline_dirty=self.git.changed_files(),
        )
        return {"status": "awaiting_approval", "plan": asdict(plan), "plan_hash": plan.plan_hash,
                "approval_command": f"approve {plan.plan_id}"}

    def approve(self, plan_id: str) -> dict:
        state = self.store.load()
        if state.get("lifecycle") != "awaiting_approval" or state.get("plan_id") != plan_id:
            raise AuthorityError("approval does not match the pending plan")
        plan = EngineeringPlan.from_dict(state["plan"])
        if plan.plan_hash != state.get("plan_hash"):
            raise AuthorityError("plan changed since presentation; approval denied")
        self.store.transition("execute", approved_plan_hash=plan.plan_hash)
        return self._execute(plan)

    def resume(self) -> dict:
        state = self.store.load()
        if state.get("lifecycle") == "awaiting_approval":
            return {"status": "awaiting_approval", "plan_id": state.get("plan_id"),
                    "plan_hash": state.get("plan_hash")}
        if state.get("lifecycle") not in {"execute", "test", "review", "repair", "replan"}:
            return {"status": state.get("lifecycle"), "next_action": self._next_action(state)}
        plan = EngineeringPlan.from_dict(state["plan"])
        if state.get("approved_plan_hash") != plan.plan_hash:
            raise AuthorityError("no valid exact-plan approval")
        return self._execute(plan)

    def abort(self) -> dict:
        state = self.store.transition("aborted", approved_plan_hash=None)
        return {"status": state["lifecycle"], "goal": state.get("goal")}

    def _execute(self, plan: EngineeringPlan) -> dict:
        state = self.store.load()
        if state.get("approved_plan_hash") != plan.plan_hash:
            raise AuthorityError("execution requires exact-plan approval")
        baseline = set(state.get("baseline_dirty", []))
        if set(self.git.changed_files()) != baseline and not state.get("completed_task_ids"):
            return self._block("repository changed after planning", [])
        executor = Executor(workspace_root=self.root)
        executor.boot()
        completed = set(state.get("completed_task_ids", []))
        for task in self._ordered(plan):
            if task.id in completed:
                continue
            before = set(self.git.changed_files())
            result = executor.execute(Task(intent="mission_8", action=task.action, data=task.data))
            if isinstance(result, str) and (result.startswith("Dispatcher Error") or result.endswith("Error")):
                return self._repair_or_block(plan, f"task {task.id} failed", [result])
            after = set(self.git.changed_files())
            allowed = baseline | {path for item in plan.tasks for path in item.affected_paths}
            if not after.issubset(allowed):
                return self._block("unplanned file change detected", sorted(after - allowed))
            completed.add(task.id)
            self.store.transition("execute", completed_task_ids=sorted(completed))
        self.store.transition("test")
        evidence = self._verify(plan.verification_commands)
        self.store.transition("review", test_evidence=evidence)
        changed = sorted(set(self.git.changed_files()) - baseline)
        verdict = self.reviewer.review(plan, changed, evidence)
        self.store.transition("review", review=asdict(verdict))
        if not verdict.approved:
            return self._repair_or_block(plan, "mandatory review failed", verdict.findings)
        self.store.transition("ready_to_commit")
        allowed = {path for task in plan.tasks for path in task.affected_paths}
        sha = self.git.local_commit(f"feat(mission-8): {plan.goal[:60]}", allowed)
        final = self.store.transition("completed", commit_sha=sha)
        return {"status": "completed", "commit_sha": sha, "tests": evidence,
                "review": final["review"], "changed_files": changed}

    def _repair_or_block(self, plan: EngineeringPlan, cause: str, evidence: list[str]) -> dict:
        state = self.store.load()
        count = int(state.get("repair_count", 0))
        strategy = f"replan after {cause}: {'; '.join(evidence)}"
        strategy_hash = __import__("hashlib").sha256(strategy.encode()).hexdigest()
        previous = set(state.get("repair_hashes", []))
        if strategy_hash in previous or count >= self.MAX_REPAIRS:
            return self._block(cause, evidence)
        # Scope-changing repair requires a fresh plan and therefore fresh approval.
        context = self.context_engine.build()
        repaired = self.reasoner.plan(f"Repair '{plan.goal}'. Evidence: {evidence}", context)
        previous.add(strategy_hash)
        self.store.transition("awaiting_approval", plan_id=repaired.plan_id, plan_hash=repaired.plan_hash,
                              plan=asdict(repaired), approved_plan_hash=None, repair_count=count + 1,
                              repair_hashes=sorted(previous), completed_task_ids=[])
        return {"status": "awaiting_approval", "reason": cause, "repair_plan": asdict(repaired),
                "plan_hash": repaired.plan_hash}

    def _block(self, diagnosis: str, evidence: list[str]) -> dict:
        state = self.store.transition("blocked", approved_plan_hash=None,
                                      blocked_diagnosis=diagnosis, blocked_evidence=evidence)
        return {"status": state["lifecycle"], "diagnosis": diagnosis,
                "evidence": evidence, "requires_human_help": True}

    def _verify(self, commands: list[str]) -> list[dict]:
        if not commands:
            return [{"command": "<missing>", "passed": False, "output": "no verification command"}]
        results = []
        for command in commands:
            if not command.startswith(self.SAFE_VERIFY_PREFIXES):
                results.append({"command": command, "passed": False, "output": "command not allowlisted"})
                continue
            result = subprocess.run(command.split(), cwd=self.root, capture_output=True, text=True, timeout=300)
            results.append({"command": command, "passed": result.returncode == 0,
                            "output": (result.stdout + result.stderr)[-4000:]})
        return results

    @staticmethod
    def _ordered(plan: EngineeringPlan):
        remaining = {task.id: task for task in plan.tasks}
        emitted: set[str] = set()
        while remaining:
            ready = sorted((task for task in remaining.values()
                            if set(task.dependencies).issubset(emitted)), key=lambda item: item.id)
            if not ready:
                raise ValueError("plan DAG cannot be scheduled")
            for task in ready:
                emitted.add(task.id)
                remaining.pop(task.id)
                yield task

    @staticmethod
    def _next_action(state: dict) -> str:
        lifecycle = state.get("lifecycle", "inspect")
        if lifecycle == "awaiting_approval":
            return f"approve {state.get('plan_id')}"
        if lifecycle in {"execute", "test", "review", "repair", "replan"}:
            return "resume"
        if lifecycle == "blocked":
            return "request_human_help"
        return "run"
