from __future__ import annotations

from typing import Any, Optional

from agents.base_agent import BaseAgent
from agents.engineer import EngineerAgent
from agents.planner_agent import PlannerAgent
from agents.research_agent import ResearchAgent
from agents.reviewer_agent import ReviewerAgent
from brain.agent_registry import AgentRegistry
from brain.messaging import Messaging
from brain.scheduler import Scheduler
from brain.shared_context import SharedContext
from services.logger import get_logger


class OrchestratorAgent(BaseAgent):
    """Top-level coordinator for the multi-agent pipeline.

    The orchestrator receives a user task, bootstraps the shared context,
    registers all downstream agents, and executes the deterministic pipeline:

    ``PlannerAgent → ResearchAgent → ReviewerAgent → EngineerAgent``

    Results from each stage are stored in the shared context so that
    downstream agents can inspect upstream output.
    """

    # Default pipeline order. Override via constructor for custom routing.
    DEFAULT_PIPELINE = [
        "planner",
        "researcher",
        "reviewer",
        "engineer",
    ]

    def __init__(
        self,
        shared_context: Optional[SharedContext] = None,
        messaging: Optional[Messaging] = None,
        registry: Optional[AgentRegistry] = None,
        scheduler: Optional[Scheduler] = None,
        pipeline: Optional[list[str]] = None,
    ) -> None:
        super().__init__("orchestrator", shared_context, messaging)
        self._registry = registry or AgentRegistry()
        self._scheduler = scheduler
        self._pipeline = pipeline or list(self.DEFAULT_PIPELINE)
        self._engineer: Optional[EngineerAgent] = None

    def _bootstrap(self) -> None:
        """Register the default agent fleet if not already present."""
        if "planner" not in self._registry:
            self._registry.register(
                "planner",
                PlannerAgent(self._shared, self._messaging),
            )
        if "researcher" not in self._registry:
            self._registry.register(
                "researcher",
                ResearchAgent(self._shared, self._messaging),
            )
        if "reviewer" not in self._registry:
            self._registry.register(
                "reviewer",
                ReviewerAgent(self._shared, self._messaging),
            )
        if "engineer" not in self._registry:
            self._engineer = EngineerAgent()
            self._registry.register("engineer", self._engineer)

        # Lazy-create scheduler if not injected
        if self._scheduler is None:
            self._scheduler = Scheduler(self._registry, self._messaging)

    def run(self, shared_context: SharedContext) -> dict:
        """Execute the multi-agent pipeline for the task in shared context.

        The shared context must contain a ``task`` key. After execution it
        will contain ``goal``, ``plan``, ``research``, ``review``, and
        ``result_engineer``.

        Returns:
            Structured result with ``success``, ``task``, ``goal``, and
            ``errors``.
        """
        self._status = "running"
        self._record("orchestrator_start")
        self._logger.info("orchestrator started", task=shared_context.get("task"))

        self._bootstrap()

        task = shared_context.get("task")
        if not task:
            error = "No task provided in shared context"
            self._logger.error(error)
            shared_context.set("error", error)
            self._status = "failed"
            return {"success": False, "task": None, "goal": None, "errors": [error]}

        try:
            pipeline_result = self._scheduler.run_pipeline(
                self._pipeline,
                shared_context,
            )
        except Exception as e:
            self._logger.error("orchestrator exception", error=str(e))
            shared_context.set("error", str(e))
            self._status = "failed"
            return {"success": False, "task": task, "goal": None, "errors": [str(e)]}

        if not pipeline_result.get("success"):
            error = pipeline_result.get("error", "Pipeline failed")
            failed_agent = pipeline_result.get("failed_agent", "unknown")
            self._logger.error("pipeline failure", agent=failed_agent, error=error)
            shared_context.set("error", error)
            self._status = "failed"
            return {
                "success": False,
                "task": task,
                "goal": shared_context.get("goal"),
                "errors": [error],
                "failed_agent": failed_agent,
            }

        # Extract engineer result, or fall back to pipeline success
        engineer_result = pipeline_result.get("results", {}).get("engineer", {})
        goal = engineer_result.get("goal")
        success = engineer_result.get("success", pipeline_result.get("success", False))
        errors = engineer_result.get("errors", [])

        self._record("orchestrator_complete", {"success": success, "goal_id": goal.get("id") if goal else None})
        self._status = "completed"
        self._logger.info("orchestrator completed", success=success)

        return {
            "success": success,
            "task": task,
            "goal": goal,
            "errors": errors,
        }

    def execute(self, task: str, priority: int = 5) -> dict:
        """Convenience method that creates a fresh shared context and runs the pipeline.

        Args:
            task: Human-readable task description.
            priority: Optional priority (default 5 = NORMAL).

        Returns:
            Structured result dictionary.
        """
        ctx = SharedContext()
        ctx.set("task", task)
        ctx.set("priority", priority)
        return self.run(ctx)

    def get_progress(self) -> dict:
        """Return the current state of the shared context."""
        return self._shared.snapshot()
