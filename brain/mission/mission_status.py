from __future__ import annotations

from enum import Enum


class MissionStatus(str, Enum):
    """Canonical lifecycle states for a Mission.

    A Mission progresses through a directed state machine from creation
    through completion. Terminal states are ``COMPLETED``, ``FAILED``,
    and ``CANCELLED``.
    """

    CREATED = "created"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    RECOVERING = "recovering"
    CANCELLED = "cancelled"

    def is_terminal(self) -> bool:
        """Return whether the state is terminal."""
        return self in {
            MissionStatus.COMPLETED,
            MissionStatus.FAILED,
            MissionStatus.CANCELLED,
        }


_VALID_TRANSITIONS: dict[MissionStatus, set[MissionStatus]] = {
    MissionStatus.CREATED: {
        MissionStatus.ANALYZING,
        MissionStatus.CANCELLED,
    },
    MissionStatus.ANALYZING: {
        MissionStatus.PLANNING,
        MissionStatus.FAILED,
        MissionStatus.CANCELLED,
    },
    MissionStatus.PLANNING: {
        MissionStatus.READY,
        MissionStatus.FAILED,
        MissionStatus.CANCELLED,
    },
    MissionStatus.READY: {
        MissionStatus.RUNNING,
        MissionStatus.FAILED,
        MissionStatus.CANCELLED,
    },
    MissionStatus.RUNNING: {
        MissionStatus.VERIFYING,
        MissionStatus.FAILED,
        MissionStatus.RECOVERING,
        MissionStatus.CANCELLED,
    },
    MissionStatus.VERIFYING: {
        MissionStatus.COMPLETED,
        MissionStatus.FAILED,
        MissionStatus.RECOVERING,
        MissionStatus.CANCELLED,
    },
    MissionStatus.COMPLETED: set(),
    MissionStatus.FAILED: set(),
    MissionStatus.RECOVERING: {
        MissionStatus.ANALYZING,
        MissionStatus.PLANNING,
        MissionStatus.READY,
        MissionStatus.RUNNING,
        MissionStatus.FAILED,
        MissionStatus.CANCELLED,
    },
    MissionStatus.CANCELLED: set(),
}


_UNIVERSAL_SINKS: set[MissionStatus] = {
    MissionStatus.FAILED,
    MissionStatus.CANCELLED,
}
