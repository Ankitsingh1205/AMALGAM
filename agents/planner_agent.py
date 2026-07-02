from __future__ import annotations

import uuid
from typing import Any, Optional

from agents.base_agent import BaseAgent
from brain.goal.goal import Goal
from brain.mission import MissionGraph
from brain.shared_context import SharedContext
from config import constants
from services.logger import get_logger


class PlannerAgent(BaseAgent):
    """Agent responsible for creating high-level plans from user tasks.

    The planner inspects the task description, creates a structured plan,
    and publishes a :class:`Goal` or Mission plan into the shared context.
    """

    def __init__(
        self,
        shared_context: Optional[SharedContext] = None,
        messaging: Optional[Any] = None,
    ) -> None:
        super().__init__("planner", shared_context, messaging)

    def run(self, shared_context: SharedContext) -> dict:
        """Create a plan from the task in the shared context.

        Returns:
            Dictionary with ``success``, ``goal_id``, and ``plan``.
        """
        self._status = "running"
        self._record("plan_start")

        task = shared_context.get("task")
        if not task:
            error = "No task provided in shared context"
            self._logger.error(error)
            shared_context.set("error", error)
            self._status = "failed"
            return {"success": False, "error": error}

        priority = shared_context.get("priority", constants.GOAL_PRIORITY_NORMAL)

        goal = Goal(
            id=str(uuid.uuid4()),
            description=task,
            priority=priority,
            status=constants.GOAL_STATUS_NEW,
        )
        goal.transition(constants.GOAL_STATUS_ANALYZING)
        goal.transition(constants.GOAL_STATUS_PLANNING)

        plan = self._generate_plan(task)
        goal.plan = plan
        goal.transition(constants.GOAL_STATUS_READY)

        shared_context.set("goal", goal.as_dict())
        shared_context.set("plan", plan)

        self._record("plan_complete", {"goal_id": goal.id, "plan": plan})
        self._status = "completed"

        return {"success": True, "goal_id": goal.id, "plan": plan}

    def run_missions(self, graph: MissionGraph, shared_context: SharedContext, plan_only: bool = False) -> dict:
        """Plan missions from a MissionGraph, optionally executing them through MissionExecutor.

        Validates the graph, performs a topological sort, and filters out
        terminal missions. The resulting execution plan is stored in the
        shared context under ``mission_plan``.

        When ``plan_only`` is ``False`` (default), the missions are also
        executed via ``MissionExecutor`` and results are stored under
        ``mission_results``.

        Args:
            graph: The MissionGraph to plan and optionally execute.
            shared_context: The shared context to publish results into.
            plan_only: If ``True``, only plan without executing.

        Returns:
            Dictionary with ``success``, ``mission_count``, ``plan``,
            and optionally ``execution_result`` and ``results``.
        """
        self._status = "running"
        self._record("mission_plan_start")

        try:
            from brain.planner.planner import Planner
            planner = Planner()
            plan = planner.plan_missions(graph)
        except ValueError as e:
            self._logger.error("mission planning failed", error=str(e))
            shared_context.set("error", str(e))
            self._status = "failed"
            return {"success": False, "error": str(e)}

        shared_context.set("mission_plan", plan)
        shared_context.set("mission_count", len(plan))

        self._record(
            "mission_plan_complete",
            {"mission_count": len(plan)},
        )

        if plan_only:
            self._status = "completed"
            return {
                "success": True,
                "mission_count": len(plan),
                "plan": [m.title for m in plan],
            }

        try:
            from brain.mission import MissionExecutor
            executor = MissionExecutor()
            execution_result = executor.execute(graph)
        except Exception as e:
            self._logger.error("mission execution failed", error=str(e))
            shared_context.set("error", str(e))
            self._status = "failed"
            return {
                "success": False,
                "error": str(e),
                "mission_count": len(plan),
                "plan": [m.title for m in plan],
            }

        shared_context.set("mission_results", execution_result)

        self._record(
            "mission_execution_complete",
            {"executed": execution_result.get("executed", 0)},
        )
        self._status = "completed"

        return {
            "success": execution_result.get("success", False),
            "mission_count": len(plan),
            "plan": [m.title for m in plan],
            "execution_result": execution_result.get("success", False),
            "results": execution_result.get("results", {}),
        }

    @staticmethod
    def _generate_plan(description: str) -> str:
        """Heuristic planner that maps keywords to canonical plans.

        Matches the logic used by :class:`AutonomousExecutor` to ensure
        plan consistency.
        """
        text = description.lower()

        if any(word in text for word in ["calculate", "math", "compute", "sum"]):
            return "1. Extract the mathematical expression. 2. Execute calculator."

        if any(word in text for word in ["read", "file", "open", "content"]):
            return "1. Identify the file path. 2. Read the file. 3. Return contents."

        if any(word in text for word in ["write", "save", "create file"]):
            return "1. Identify target path. 2. Write content. 3. Verify file exists."

        if any(word in text for word in ["list", "show files", "directory", "ls"]):
            return "1. Identify target directory. 2. List files."

        if any(word in text for word in ["python", "run code", "execute script"]):
            return "1. Extract the Python code. 2. Execute via PythonExecutor. 3. Return output."

        if any(word in text for word in ["search", "web", "find online"]):
            return "1. Extract search query. 2. Search the web. 3. Return results."

        if any(word in text for word in ["remember", "store", "save data"]):
            return "1. Extract key and value. 2. Store in memory."

        if any(word in text for word in ["recall", "retrieve", "fetch memory"]):
            return "1. Extract key. 2. Recall from memory. 3. Return value."

        if any(word in text for word in ["project", "repository", "summarize", "overview"]):
            return "1. Analyze workspace. 2. Build knowledge graph. 3. Summarize results."

        return "1. Analyze user request. 2. Select appropriate tool or model. 3. Execute and return result."
