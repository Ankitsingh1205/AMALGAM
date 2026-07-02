from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from brain.mission.mission import Mission
from brain.mission.mission_id import MissionID


@dataclass
class Epic:
    """Organizational container that groups related Mission objects.

    An ``Epic`` is a pure metadata object. It never executes, schedules,
    or interacts with planners, schedulers, runtimes, executors, tools,
    or agents.

    Attributes:
        id: Unique identifier.
        title: Human-readable title.
        description: Detailed explanation.
        missions: Ordered list of Mission objects belonging to this epic.
        metadata: Extensible key-value context.
        created_at: ISO timestamp of creation.
        updated_at: ISO timestamp of the last mutation.
    """

    id: MissionID
    title: str
    description: str = ""
    missions: list[Mission] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def _touch(self) -> None:
        """Update the ``updated_at`` timestamp."""
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def add_mission(self, mission: Mission) -> None:
        """Add a mission to the epic if its ID is not already present.

        Args:
            mission: The Mission to add.

        Raises:
            ValueError: If a mission with the same ID already exists.
        """
        if self.find_mission(mission.id) is not None:
            raise ValueError(
                f"Mission with ID {str(mission.id)!r} already exists in epic."
            )
        self.missions.append(mission)
        self._touch()

    def remove_mission(self, mission: Mission) -> None:
        """Remove a mission from the epic if it is present.

        Args:
            mission: The Mission to remove.
        """
        if mission in self.missions:
            self.missions.remove(mission)
            self._touch()

    def find_mission(self, mission_id: MissionID | str) -> Optional[Mission]:
        """Find a mission by its ID.

        Args:
            mission_id: The MissionID or its string representation.

        Returns:
            The matching Mission, or ``None`` if not found.
        """
        target = str(mission_id)
        for m in self.missions:
            if str(m.id) == target:
                return m
        return None

    def to_dict(self) -> dict:
        """Serialize the epic to a plain dictionary.

        Missions are serialized in their current insertion order.
        """
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "missions": [m.to_dict() for m in self.missions],
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Epic:
        """Deserialize an epic from a plain dictionary.

        Ignores unknown keys for forward compatibility.
        """
        epic_id = (
            MissionID(data["id"])
            if isinstance(data["id"], str)
            else data["id"]
        )

        epic = cls(
            id=epic_id,
            title=data["title"],
            description=data.get("description", ""),
            metadata=dict(data.get("metadata", {})),
            created_at=data.get(
                "created_at", datetime.now(timezone.utc).isoformat()
            ),
            updated_at=data.get(
                "updated_at", datetime.now(timezone.utc).isoformat()
            ),
        )

        for mission_data in data.get("missions", []):
            epic.missions.append(Mission.from_dict(mission_data))

        return epic
