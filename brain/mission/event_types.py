from __future__ import annotations

from enum import Enum


class MissionEventType(str, Enum):
    """Typed event categories for the Mission lifecycle.

    Every event dispatched through the Mission Event Bus must carry
    exactly one of these types. The type determines what lifecycle
    transition or mutation occurred.
    """

    MISSION_CREATED = "mission_created"
    MISSION_UPDATED = "mission_updated"
    MISSION_STATUS_CHANGED = "mission_status_changed"
    MISSION_COMPLETED = "mission_completed"
    MISSION_FAILED = "mission_failed"
    MISSION_CANCELLED = "mission_cancelled"
    MISSION_DELETED = "mission_deleted"