from tools.file_tool import FileTool
from tools.python_executor import PythonExecutor
from brain.executor.autonomous_executor import AutonomousExecutor
from brain.goal.goal import Goal
from config import constants

try:
    from services.project_service import ProjectService
except Exception:
    ProjectService = None


class EngineerAgent:
    """Autonomous agent that executes engineering tasks through the AMALGAM pipeline.

    The agent wraps an ``AutonomousExecutor`` to run goals through the full
    lifecycle: analyze, plan, queue, execute, verify, reflect, and retry.

    Attributes:
        files: ``FileTool`` for direct filesystem operations.
        executor: ``PythonExecutor`` for direct code execution.
        project: ``ProjectService`` for project introspection, if available.
        autonomous: ``AutonomousExecutor`` for goal-driven execution.
    """

    def __init__(self, autonomous_executor: AutonomousExecutor = None) -> None:
        self.files = FileTool()
        self.executor = PythonExecutor()
        self.project = ProjectService() if ProjectService else None
        self.autonomous = autonomous_executor or AutonomousExecutor()

    def execute(self, task: str) -> dict:
        """Execute a task using the autonomous executor.

        This is the primary entry point. It delegates to the autonomous loop
        and returns a structured result dictionary.

        Args:
            task: Human-readable task description.

        Returns:
            Dictionary with ``success``, ``task``, ``goal``, and ``errors``.
        """
        result = {
            "success": True,
            "task": task,
            "goal": None,
            "errors": [],
        }

        try:
            goal = self.autonomous.run(task)
            result["goal"] = goal.as_dict()
            result["success"] = goal.status == constants.GOAL_STATUS_COMPLETED
            if goal.error:
                result["errors"].append(goal.error)
        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))

        if self.project:
            try:
                if hasattr(self.project, "summarize"):
                    result["project"] = self.project.summarize()
            except Exception as e:
                result["errors"].append(str(e))

        return result

    def run_goal(self, description: str, priority: int = constants.GOAL_PRIORITY_NORMAL) -> Goal:
        """Run a goal directly and return the ``Goal`` object.

        Args:
            description: Goal description.
            priority: Optional priority (default ``NORMAL``).

        Returns:
            The completed or failed ``Goal``.
        """
        return self.autonomous.run(description, priority=priority)

    def goal_progress(self, goal_id: str) -> dict:
        """Return progress for a goal.

        Args:
            goal_id: Goal identifier.

        Returns:
            Progress dictionary.
        """
        return self.autonomous.progress(goal_id)
