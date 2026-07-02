from __future__ import annotations

from enum import Enum


class MissionPriority(int, Enum):
    """Priority levels for a Mission.

    Higher integer values indicate greater urgency.
    """

    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20
