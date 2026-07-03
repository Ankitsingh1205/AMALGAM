from __future__ import annotations

from typing import Any

from brain.executor.autonomous_executor import AutonomousExecutor
from brain.mission.event import MissionEvent
from brain.mission.event_types import MissionEventType
from brain.mission.graph import MissionGraph
from brain.mission.mission import Mission
from brain.mission.mission_status import MissionStatus
from services.logger import get_logger


class MissionExecutionError(Exception):
    """Raised when mission execution encounters an unrecoverable failure."""


class MissionExecutor:
    """Bridge between Mission planning and the existing execution infrastructure.

    ``MissionExecutor`` takes a ``MissionGraph``, resolves the execution
    order via the existing ``Planner.plan_missions()``, and executes each
    mission through the existing ``AutonomousExecutor`` goal lifecycle.

    This component is an orchestration layer only. It does NOT duplicate
    scheduling logic, replace the ``Scheduler``, or redesign the execution
    pipeline. Execution remains owned by ``AutonomousExecutor``.

    Attributes:
        _planner: ``Planner`` for mission ordering and filtering.
        _executor: ``AutonomousExecutor`` for per-mission execution.
        _logger: Structured logger instance.
    """

    def __init__(self) -> None:
        from brain.planner.planner import Planner
        self._planner = Planner()
        self._executor = AutonomousExecutor()
        self._logger = get_logger("mission_executor")

    def execute(
        self,
        graph: MissionGraph,
        halt_on_failure: bool = True,
    ) -> dict[str, Any]:
        """Execute all executable missions in a graph.

        Missions are executed in topological dependency order as determined
        by ``Planner.plan_missions()``. Terminal missions (COMPLETED,
        FAILED, CANCELLED) are skipped. Each executable mission is
        dispatched through the ``AutonomousExecutor`` goal lifecycle.

        Args:
            graph: The ``MissionGraph`` containing missions to execute.
            halt_on_failure: If ``True`` (default), stop on the first
                mission failure. If ``False``, continue executing
                independent missions.

        Returns:
            Dictionary with ``success``, ``results`` (per-mission dict),
            ``executed`` count, ``skipped`` count, and optionally
            ``failed_at`` and ``error``.
        """
        plan = self._planner.plan_missions(graph)
        
        # Calculate total missions in graph to determine skipped count
        total_missions = len(graph)
        
        results: dict[str, dict[str, Any]] = {}
        executed: list[Mission] = []
        skipped: list[Mission] = []
        failures: list[str] = []

        for mission in plan:
            if not self._is_currently_executable(mission):
                skipped.append(mission)
                continue
    
            # Ensure mission is in a state that can transition to RUNNING.
            # For the bridge, we assume missions are pre-analyzed/planned
            # or we move them through the pipeline.
            if mission.status == MissionStatus.CREATED:
                mission.transition(MissionStatus.ANALYZING)
                mission.transition(MissionStatus.PLANNING)
                mission.transition(MissionStatus.READY)
            elif mission.status == MissionStatus.ANALYZING:
                mission.transition(MissionStatus.PLANNING)
                mission.transition(MissionStatus.READY)
            elif mission.status == MissionStatus.PLANNING:
                mission.transition(MissionStatus.READY)

            mission.transition(MissionStatus.RUNNING)

            result = self._execute_one(mission)
            results[str(mission.id)] = result
            executed.append(mission)

            if result.get("success"):
                # Avoid double transition if status_observer already moved mission to COMPLETED
                if mission.status != MissionStatus.COMPLETED:
                    mission.transition(MissionStatus.VERIFYING)
                    mission.transition(MissionStatus.COMPLETED)
            else:
                mission.transition(MissionStatus.FAILED)
                mission.error = result.get("error", "Mission execution failed")
                failures.append(str(mission.id))

                if halt_on_failure:
                    self._logger.warning(
                        "halting on mission failure",
                        failed_mission=str(mission.id),
                        error=mission.error,
                    )
                    return {
                        "success": False,
                        "results": results,
                        "executed": len(executed),
                        "skipped": len(skipped) + len(plan) - len(executed),
                        "failed_at": str(mission.id),
                        "error": mission.error,
                    }

        return {
            "success": len(failures) == 0,
            "results": results,
            "executed": len(executed),
            "skipped": total_missions - len(executed),
        }

    def _execute_one(self, mission: Mission) -> dict[str, Any]:
        """Execute a single mission through the AutonomousExecutor.

        The mission's title and description are combined into the goal
        description. The AutonomousExecutor runs the full lifecycle
        (analyze → plan → queue → execute → verify) and returns the
        terminal Goal.

        A ``status_observer`` callback maps Goal status changes to
        ``Mission`` transitions in real time. Invalid transitions are
        silently skipped (e.g. ``RUNNING → ANALYZING`` is not allowed
        by the mission state machine).

        Args:
            mission: The mission to execute.

        Returns:
            Dictionary with ``success``, ``goal_id``, and optionally
            ``error`` and ``final_status``.
        """
        description = f"{mission.title}: {mission.description}".strip()
        if description.endswith(":"):
            description = mission.title

        self._logger.info(
            "executing mission",
            mission_id=str(mission.id),
            title=mission.title,
        )

        # Status observer bridges AutonomousExecutor goal lifecycle
        # to Mission lifecycle without violating layer boundaries.
        _GOAL_TO_MISSION_STATUS = {
            "analyzing": MissionStatus.ANALYZING,
            "planning": MissionStatus.PLANNING,
            "ready": MissionStatus.READY,
            "running": MissionStatus.RUNNING,
            "verifying": MissionStatus.VERIFYING,
            "completed": MissionStatus.COMPLETED,
            "failed": MissionStatus.FAILED,
            "reflecting": MissionStatus.RECOVERING,
            "replanning": MissionStatus.RECOVERING,
        }

        def _status_mapper(status: str) -> None:
            mapped = _GOAL_TO_MISSION_STATUS.get(status)
            if mapped is None or mapped == mission.status:
                return
            try:
                mission.transition(mapped)
            except ValueError:
                pass  # Invalid transition for current state — skip silently

        goal = self._executor.run(
            description=description,
            priority=mission.priority.value,
            status_observer=_status_mapper,
        )

        success = goal.status == "completed"
        error = goal.error

        self._logger.info(
            "mission execution complete",
            mission_id=str(mission.id),
            success=success,
            goal_status=goal.status,
        )

        result: dict[str, Any] = {
            "success": success,
            "goal_id": goal.id,
            "final_status": goal.status,
        }
        if error:
            result["error"] = error

        return result

    @staticmethod
    def _is_currently_executable(mission: Mission) -> bool:
        """Return whether a mission is currently in an executable state.

        A mission is executable if it is not in a terminal state and
        is not already RUNNING.

        Args:
            mission: The mission to evaluate.

        Returns:
            ``True`` if the mission can be executed now.
        """
        if mission.status == MissionStatus.RUNNING:
            return True
        return not mission.status.is_terminal()