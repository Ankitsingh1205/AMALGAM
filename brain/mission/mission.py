from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from brain.mission.mission_id import MissionID
from brain.mission.mission_priority import MissionPriority
from brain.mission.mission_status import MissionStatus, _VALID_TRANSITIONS, _UNIVERSAL_SINKS


@dataclass
class Mission:
    """Pure metadata representation of a mission.

    A ``Mission`` is a self-contained data object. It never executes,
    schedules, or interacts with planners, schedulers, runtimes,
    executors, tools, or agents.

    Attributes:
        id: Unique identifier.
        title: Human-readable title.
        description: Detailed explanation.
        priority: Urgency level.
        status: Current lifecycle state.
        owner: Optional identifier of the owning entity.
        children: Nested sub-missions.
        dependencies: Missions that must precede this one.
        metadata: Extensible key-value context.
        created_at: ISO timestamp of creation.
        updated_at: ISO timestamp of the last mutation.
    """

    id: MissionID
    title: str
    description: str = ""
    priority: MissionPriority = MissionPriority.NORMAL
    status: MissionStatus = MissionStatus.CREATED
    owner: Optional[str] = None
    children: list[Mission] = field(default_factory=list)
    dependencies: list[Mission] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def transition(self, new_status: MissionStatus) -> None:
        """Move the mission to a new lifecycle state.

        Args:
            new_status: The target status.

        Raises:
            ValueError: If the transition is invalid or the mission is
                already in a terminal state.
        """
        if self.status == new_status:
            return

        if self.status.is_terminal():
            raise ValueError(
                f"Cannot transition from terminal state "
                f"{self.status.value!r} to {new_status.value!r}."
            )

        valid = _VALID_TRANSITIONS.get(self.status, set())
        if new_status not in valid and new_status not in _UNIVERSAL_SINKS:
            raise ValueError(
                f"Invalid transition: {self.status.value!r} -> {new_status.value!r}."
            )

        self.status = new_status
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def add_child(self, child: Mission) -> None:
        """Add a sub-mission if it is not already present."""
        if child not in self.children:
            self.children.append(child)

    def remove_child(self, child: Mission) -> None:
        """Remove a sub-mission if it is present."""
        if child in self.children:
            self.children.remove(child)

    def add_dependency(self, dependency: Mission) -> None:
        """Add a dependency if it is not already present."""
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)

    def remove_dependency(self, dependency: Mission) -> None:
        """Remove a dependency if it is present."""
        if dependency in self.dependencies:
            self.dependencies.remove(dependency)

    def to_dict(self) -> dict:
        """Serialize the mission to a plain dictionary.

        Children and dependencies are recursively serialized.
        """
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "owner": self.owner,
            "children": [child.to_dict() for child in self.children],
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Mission:
        """Deserialize a mission from a plain dictionary.

        Ignores unknown keys for forward compatibility.
        """
        mission_id = (
            MissionID(data["id"])
            if isinstance(data["id"], str)
            else data["id"]
        )

        raw_priority = data.get("priority", MissionPriority.NORMAL.value)
        priority = (
            MissionPriority(raw_priority)
            if isinstance(raw_priority, int)
            else MissionPriority.NORMAL
        )

        raw_status = data.get("status", MissionStatus.CREATED.value)
        status = (
            MissionStatus(raw_status)
            if isinstance(raw_status, str)
            else MissionStatus.CREATED
        )

        mission = cls(
            id=mission_id,
            title=data["title"],
            description=data.get("description", ""),
            priority=priority,
            status=status,
            owner=data.get("owner"),
            metadata=dict(data.get("metadata", {})),
            created_at=data.get(
                "created_at", datetime.now(timezone.utc).isoformat()
            ),
            updated_at=data.get(
                "updated_at", datetime.now(timezone.utc).isoformat()
            ),
        )

        for child_data in data.get("children", []):
            mission.children.append(cls.from_dict(child_data))

        for dep_data in data.get("dependencies", []):
            mission.dependencies.append(cls.from_dict(dep_data))

        return mission
