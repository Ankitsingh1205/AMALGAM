from __future__ import annotations

from typing import Optional

from config import constants
from services.logger import get_logger


class RetryManager:
    """Manages retry logic with bounded retries and strategy fallback.

    Tracks per-goal retry counts and prevents infinite loops. When the
    maximum retry count is exceeded, it recommends an alternative strategy
    or user escalation.

    Attributes:
        _max_retries: Maximum retry attempts per goal.
        _attempts: Mapping of goal_id to retry count.
        _logger: Structured logger instance.
    """

    def __init__(self, max_retries: int = constants.MAX_RETRY_COUNT) -> None:
        self._max_retries = max_retries
        self._attempts: dict[str, int] = {}
        self._logger = get_logger("retry_manager")

    def can_retry(self, goal_id: str) -> bool:
        """Return whether the given goal is still eligible for retry.

        Args:
            goal_id: Goal identifier.

        Returns:
            ``True`` if retries remain, ``False`` otherwise.
        """
        return self._attempts.get(goal_id, 0) < self._max_retries

    def record_attempt(self, goal_id: str) -> int:
        """Increment the retry count for a goal and return the new count.

        Args:
            goal_id: Goal identifier.

        Returns:
            The updated retry count.
        """
        self._attempts[goal_id] = self._attempts.get(goal_id, 0) + 1
        self._logger.info(
            "retry recorded",
            goal_id=goal_id,
            attempt=self._attempts[goal_id],
            max_retries=self._max_retries,
        )
        return self._attempts[goal_id]

    def attempts_left(self, goal_id: str) -> int:
        """Return the number of retry attempts remaining.

        Args:
            goal_id: Goal identifier.

        Returns:
            Remaining retry count (never negative).
        """
        used = self._attempts.get(goal_id, 0)
        return max(0, self._max_retries - used)

    def decide_next_step(
        self,
        goal_id: str,
        strategy: str,
    ) -> dict:
        """Decide the next recovery step based on retry state.

        If retries remain, the recommended step is ``retry`` with the
        same strategy. If retries are exhausted, the strategy is
        escalated to ``alternative`` and finally ``user``.

        Args:
            goal_id: Goal identifier.
            strategy: Current reflection strategy.

        Returns:
            A dictionary with ``next_step`` and ``message``.
        """
        if self.can_retry(goal_id):
            remaining = self.attempts_left(goal_id)
            return {
                "next_step": constants.REFLECTION_STRATEGY_RETRY,
                "message": f"Retrying ({remaining} attempt(s) left).",
                "strategy": strategy,
            }

        if strategy == constants.REFLECTION_STRATEGY_RETRY:
            return {
                "next_step": constants.REFLECTION_STRATEGY_ALTERNATIVE,
                "message": "Retries exhausted. Trying an alternative strategy.",
                "strategy": constants.REFLECTION_STRATEGY_ALTERNATIVE,
            }

        if strategy == constants.REFLECTION_STRATEGY_ALTERNATIVE:
            return {
                "next_step": constants.REFLECTION_STRATEGY_REPLAN,
                "message": "Alternative strategy failed. Replanning the goal.",
                "strategy": constants.REFLECTION_STRATEGY_REPLAN,
            }

        if strategy == constants.REFLECTION_STRATEGY_REPLAN:
            return {
                "next_step": constants.REFLECTION_STRATEGY_USER,
                "message": "All automated strategies exhausted. Escalating to user.",
                "strategy": constants.REFLECTION_STRATEGY_USER,
            }

        return {
            "next_step": constants.REFLECTION_STRATEGY_GIVE_UP,
            "message": "Goal cannot be recovered automatically.",
            "strategy": constants.REFLECTION_STRATEGY_GIVE_UP,
        }

    def reset(self, goal_id: str) -> None:
        """Reset the retry count for a goal.

        Useful when a goal is replanned and the retry budget should be
        refreshed.

        Args:
            goal_id: Goal identifier.
        """
        self._attempts.pop(goal_id, None)
        self._logger.info("retry count reset", goal_id=goal_id)

    def reset_all(self) -> None:
        """Reset all retry counts."""
        self._attempts.clear()
        self._logger.info("all retry counts reset")
