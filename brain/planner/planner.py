from __future__ import annotations

from typing import Optional

from brain.mission import Mission, MissionGraph, MissionStatus
from kernel.task import Task
from models.registry import ModelRegistry
from config import constants


class Planner:
    """Unified planner that produces execution plans for both Goals and Missions.

    The Planner is a pure planning component. It never executes, schedules,
    or interacts with runtimes, executors, tools, or agents.
    """

    def __init__(self) -> None:
        self.registry = ModelRegistry()

    # ------------------------------------------------------------------
    # Goal planning (existing, unchanged)
    # ------------------------------------------------------------------

    def create_task(self, intent: str, user_input: str) -> Task:
        """Create a concrete Task from an intent and user input."""
        if intent == constants.INTENT_MATH:
            return Task(
                intent=intent,
                action=constants.ACTION_CALCULATE,
                data=user_input,
            )

        if intent == constants.INTENT_MEMORY:
            if user_input.lower().startswith("remember "):
                payload = user_input[9:]
                if "=" in payload:
                    key, value = payload.split("=", 1)
                    return Task(
                        intent=intent,
                        action=constants.ACTION_REMEMBER,
                        data=(key.strip(), value.strip()),
                    )
            if user_input.lower().startswith("recall "):
                return Task(
                    intent=intent,
                    action=constants.ACTION_RECALL,
                    data=user_input[7:].strip(),
                )

        if intent == constants.INTENT_FILES:
            return Task(
                intent=intent,
                action=constants.ACTION_LIST_FILES,
                data=".",
            )

        if intent == constants.INTENT_INTERNET:
            query = (
                user_input
                .replace("search web", "")
                .replace("search", "")
                .replace("google", "")
                .replace("find online", "")
                .strip()
            )
            return Task(
                intent=intent,
                action=constants.ACTION_SEARCH_WEB,
                data=query,
            )

        if intent == constants.INTENT_PYTHON:
            code = (
                user_input
                .replace("run python", "")
                .replace("execute python", "")
                .replace("python:", "")
                .strip()
            )
            return Task(
                intent=intent,
                action=constants.ACTION_RUN_PYTHON,
                data=code,
            )

        if intent == constants.INTENT_PROJECT:
            return Task(
                intent=intent,
                action=constants.ACTION_PROJECT_SUMMARY,
                data=user_input,
            )

        if intent == constants.INTENT_CODING:
            return Task(
                intent=intent,
                action=constants.ACTION_GENERATE_CODE,
                model=self.registry.get("coding"),
                data=user_input,
            )

        return Task(
            intent=constants.INTENT_GENERAL,
            action=constants.ACTION_CHAT,
            model=self.registry.get("general"),
            data=user_input,
        )

    # ------------------------------------------------------------------
    # Mission planning (additive)
    # ------------------------------------------------------------------

    def plan_missions(self, graph: MissionGraph) -> list[Mission]:
        """Validate a MissionGraph and return executable missions in order.

        Uses the graph's topological sort to produce a deterministic
        execution plan. Missions in terminal states (``COMPLETED``,
        ``FAILED``, ``CANCELLED``) are excluded from the plan.

        Args:
            graph: The MissionGraph to plan.

        Returns:
            List of executable missions in dependency order.

        Raises:
            ValueError: If the graph is invalid or contains a cycle.
        """
        if graph.has_cycle():
            raise ValueError("Mission graph contains a cycle.")

        if not graph.validate():
            raise ValueError("Invalid mission graph.")

        order = graph.topological_sort()
        return [m for m in order if self._is_executable(m)]

    def plan_mission(self, mission: Mission) -> Optional[Mission]:
        """Return the mission if it is in an executable state.

        Args:
            mission: The mission to evaluate.

        Returns:
            The mission if executable, ``None`` otherwise.
        """
        if self._is_executable(mission):
            return mission
        return None

    def _is_executable(self, mission: Mission) -> bool:
        """Return whether a mission is in an executable state.

        Executable states are all non-terminal states: ``CREATED``,
        ``ANALYZING``, ``PLANNING``, ``READY``, ``RUNNING``,
        ``VERIFYING``, and ``RECOVERING``.
        """
        return mission.status not in {
            MissionStatus.COMPLETED,
            MissionStatus.FAILED,
            MissionStatus.CANCELLED,
        }
