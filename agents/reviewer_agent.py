from __future__ import annotations

from typing import Any, Optional

from agents.base_agent import BaseAgent
from brain.shared_context import SharedContext
from config import constants
from services.logger import get_logger


class ReviewerAgent(BaseAgent):
    """Agent that reviews plans and execution results for quality and safety.

    The reviewer performs deterministic checks on the task, plan, and
    research findings. It returns an ``approved`` / ``rejected`` verdict
    with a reason.
    """

    def __init__(
        self,
        shared_context: Optional[SharedContext] = None,
        messaging: Optional[Any] = None,
    ) -> None:
        super().__init__("reviewer", shared_context, messaging)

    def run(self, shared_context: SharedContext) -> dict:
        """Review the current task, plan, and research.

        Returns:
            Dictionary with ``success``, ``approved``, ``reason``,
            and ``issues``.
        """
        self._status = "running"
        self._record("review_start")

        task = shared_context.get("task", "")
        plan = shared_context.get("plan", "")
        research = shared_context.get("research", {})
        issues: list[str] = []

        # Check 1: task must be non-empty
        if not task or not task.strip():
            issues.append("Task is empty.")

        # Check 2: plan must exist and have steps
        if not plan or not plan.strip():
            issues.append("Plan is missing.")
        elif "." not in plan and "\n" not in plan:
            issues.append("Plan appears to have no steps.")

        # Check 3: task type must be supported
        supported_types = [
            "calculate", "math", "compute", "sum",
            "read", "file", "open", "content",
            "write", "save", "create file",
            "list", "show files", "directory", "ls",
            "python", "run code", "execute script",
            "search", "web", "find online",
            "remember", "store", "save data",
            "recall", "retrieve", "fetch memory",
            "project", "repository", "summarize", "overview",
            "+", "-", "*", "/",
        ]
        text = task.lower()
        if not any(keyword in text for keyword in supported_types):
            issues.append("Task type is not in the supported heuristic set.")

        # Check 4: research should exist for complex tasks
        if any(word in text for word in ["project", "repository", "summarize", "overview"]):
            if not research or not research.get("project"):
                issues.append("Complex task (project) lacks research findings.")

        # Check 5: safety — reject known dangerous patterns
        dangerous_patterns = [
            "__import__", "os.system", "subprocess", "eval(", "exec(",
            "rm -rf", "rmtree", "shutil.rmtree",
        ]
        if any(pattern in task for pattern in dangerous_patterns):
            issues.append("Task contains potentially dangerous patterns.")

        approved = len(issues) == 0
        reason = "Plan approved." if approved else f"Plan rejected: {'; '.join(issues)}"

        verdict = {
            "approved": approved,
            "reason": reason,
            "issues": issues,
        }

        shared_context.set("review", verdict)

        self._record("review_complete", verdict)
        self._status = "completed"

        return {
            "success": approved,
            "approved": approved,
            "reason": reason,
            "issues": issues,
        }
