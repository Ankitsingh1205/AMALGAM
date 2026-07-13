"""Repository-aware structured reasoning using the existing local model."""
from __future__ import annotations

from dataclasses import asdict
import json
import uuid

from brain.engineering_contracts import EngineeringPlan, RepositoryContext
from services.llm import LLMService

DEFAULT_MODEL = "qwen2.5-coder:7b"
ENGINEERING_ACTIONS = {"write_file", "replace_text", "run_python", "list_files"}


class StructuredReasoner:
    def __init__(self, llm: LLMService | None = None, model: str = DEFAULT_MODEL):
        self.llm = llm or LLMService()
        self.model = model

    def classify(self, request: str, context: RepositoryContext) -> dict:
        exact = request.strip().lower()
        if exact in {"status", "resume", "abort"}:
            return {"intent": "mission_control", "action": exact, "confidence": 1.0,
                    "rationale": "deterministic command", "requires_plan": False}
        prompt = json.dumps({"request": request, "repository": asdict(context)}, default=str)
        return self.llm.ask_structured(
            prompt, self.model,
            "Classify an AMALGAM engineering request. Fields: intent, action, confidence (0..1), rationale, requires_plan.",
            self._validate_intent,
        )

    def plan(self, goal: str, context: RepositoryContext) -> EngineeringPlan:
        action_contract = {
            "write_file": "create or fully replace one approved workspace file; data requires path/content",
            "replace_text": "replace exact old text with new text in one approved workspace file",
            "run_python": "run a bounded Python verification command through the sandbox",
            "list_files": "read-only directory listing",
        }
        prompt = json.dumps({
            "goal": goal, "repository": asdict(context), "allowed_actions": action_contract,
            "requirements": [
                "Every modifying task must list affected_paths.",
                "Use dependencies to form an acyclic DAG.",
                "Include verification commands and acceptance criteria.",
                "Never plan deletion, dependency changes, remote Git, secrets or external side effects.",
            ],
            "plan_id": str(uuid.uuid4()),
        }, default=str)
        value = self.llm.ask_structured(
            prompt, self.model,
            "You are AMALGAM's planner. Produce a minimal repository-aware EngineeringPlan JSON with plan_id, goal, tasks, verification_commands, risks, requires_approval. Each task has id, description, action, capability, dependencies, affected_paths, acceptance_criteria, and action-specific data. write_file data is {path,content}; replace_text data is {path,old,new}; read-only actions use their normal argument.",
            self._validate_plan_dict,
        )
        value.pop("_meta", None)
        plan = EngineeringPlan.from_dict(value)
        plan.validate(ENGINEERING_ACTIONS)
        return plan

    @staticmethod
    def _validate_intent(value: dict) -> None:
        required = {"intent", "action", "confidence", "rationale", "requires_plan"}
        if not required.issubset(value):
            raise ValueError(f"missing fields: {sorted(required - set(value))}")
        confidence = float(value["confidence"])
        if confidence < 0 or confidence > 1:
            raise ValueError("confidence outside 0..1")

    @staticmethod
    def _validate_plan_dict(value: dict) -> None:
        value = {k: v for k, v in value.items() if k != "_meta"}
        EngineeringPlan.from_dict(value).validate(ENGINEERING_ACTIONS)
