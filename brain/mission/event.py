from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid

from brain.mission.event_types import MissionEventType


@dataclass(frozen=True)
class MissionEvent:
    """Immutable, strongly-typed lifecycle event for the Mission subsystem.

    Every event published through the Mission Event Bus must be an
    instance of ``MissionEvent``.  String-based events, dictionary-based
    events, and untyped events are prohibited.

    The frozen dataclass guarantees that events are immutable facts:
    once created they cannot be mutated, making them safe for logging,
    persistence, audit trails, replay, and future distributed transport.

    Attributes:
        event_id: Unique event identifier (UUID4 string).
        event_type: Canonical lifecycle event type.
        mission_id: String representation of the Mission's ID.
        timestamp: ISO-8601 UTC timestamp of event creation.
        payload: Structured metadata specific to the event type.
    """

    event_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )
    event_type: MissionEventType = MissionEventType.MISSION_STATUS_CHANGED
    mission_id: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    payload: dict[str, Any] = field(
        default_factory=dict, hash=False
    )