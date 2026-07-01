from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from config import constants


_VALID_TRANSITIONS: dict[str, set[str]] = {
    constants.GOAL_STATUS_IDLE: {constants.GOAL_STATUS_NEW},
    constants.GOAL_STATUS_NEW: {constants.GOAL_STATUS_ANALYZING},
    constants.GOAL_STATUS_ANALYZING: {constants.GOAL_STATUS_PLANNING},
    constants.GOAL_STATUS_PLANNING: {constants.GOAL_STATUS_READY},
    constants.GOAL_STATUS_READY: {constants.GOAL_STATUS_RUNNING},
    constants.GOAL_STATUS_RUNNING: {
        constants.GOAL_STATUS_VERIFYING,
        constants.GOAL_STATUS_REFLECTING,
        constants.GOAL_STATUS_FAILED,
        constants.GOAL_STATUS_PAUSED,
    },
    constants.GOAL_STATUS_PAUSED: {
        constants.GOAL_STATUS_RUNNING,
        constants.GOAL_STATUS_FAILED,
    },
    constants.GOAL_STATUS_VERIFYING: {
        constants.GOAL_STATUS_COMPLETED,
        constants.GOAL_STATUS_FAILED,
    },
    constants.GOAL_STATUS_REFLECTING: {
        constants.GOAL_STATUS_REPLANNING,
        constants.GOAL_STATUS_RUNNING,
        constants.GOAL_STATUS_FAILED,
    },
    constants.GOAL_STATUS_REPLANNING: {
        constants.GOAL_STATUS_RUNNING,
        constants.GOAL_STATUS_FAILED,
    },
    constants.GOAL_STATUS_COMPLETED: set(),
    constants.GOAL_STATUS_FAILED: set(),
}


@dataclass
class Goal:
    """Represents an autonomous goal with lifecycle management.

    A goal progresses through a canonical state machine from creation
    through completion. Each state transition is recorded with a
    timestamp for auditability.

    Attributes:
        id: Unique identifier for the goal.
        description: Human-readable description of the goal.
        priority: Integer priority (higher is more urgent).
        status: Current lifecycle state of the goal.
        created_at: ISO timestamp when the goal was created.
        updated_at: ISO timestamp of the most recent state change.
        plan: Optional high-level plan derived from the goal.
        plan_version: Integer version of the current plan (increments on replan).
        result: Optional final result or summary.
        error: Optional error message if the goal failed.
        metadata: Optional dictionary for extensible context.
    """

    id: str
    description: str
    priority: int = constants.GOAL_PRIORITY_NORMAL
    status: str = constants.GOAL_STATUS_IDLE
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    plan: Optional[str] = None
    plan_version: int = 0
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def transition(self, new_status: str) -> None:
        """Transition the goal to a new status.

        Validates the transition against the canonical state machine.
        Transitions to ``FAILED`` are always permitted from non-terminal
        states. Idempotent transitions (same status) are silently ignored.

        Args:
            new_status: The target status string.

        Raises:
            ValueError: If the transition is invalid or the goal is already
                in a terminal state.
        """
        if self.status == new_status:
            return

        if self.is_terminal():
            raise ValueError(
                f"Cannot transition from terminal state {self.status!r} to {new_status!r}."
            )

        valid = _VALID_TRANSITIONS.get(self.status, set())
        if new_status not in valid and new_status != constants.GOAL_STATUS_FAILED:
            raise ValueError(
                f"Invalid transition: {self.status!r} -> {new_status!r}."
            )

        self.status = new_status
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def is_terminal(self) -> bool:
        """Return whether the goal has reached a terminal state.

        Terminal states are ``COMPLETED`` and ``FAILED``.
        """
        return self.status in {
            constants.GOAL_STATUS_COMPLETED,
            constants.GOAL_STATUS_FAILED,
        }

    def is_active(self) -> bool:
        """Return whether the goal is currently active.

        Active states are any non-terminal states that are not ``IDLE``.
        """
        return not self.is_terminal() and self.status != constants.GOAL_STATUS_IDLE

    def as_dict(self) -> dict:
        """Serialize the goal to a plain dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "plan": self.plan,
            "plan_version": self.plan_version,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Goal:
        """Deserialize a goal from a plain dictionary.

        Ignores unknown keys to support forward compatibility.
        """
        known = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)
