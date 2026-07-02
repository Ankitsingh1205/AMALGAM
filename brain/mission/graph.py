from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Optional

from brain.mission.mission import Mission
from brain.mission.mission_id import MissionID


class MissionNode:
    """Node in a Mission dependency graph.

    Wraps a :class:`Mission` with parent (dependency) and child
    (dependent) references. Parent and child IDs are stored as strings
    for fast set-based lookup.
    """

    __slots__ = ("mission", "parents", "children")

    def __init__(self, mission: Mission) -> None:
        self.mission = mission
        self.parents: set[str] = set()   # IDs this mission depends on
        self.children: set[str] = set()  # IDs that depend on this mission

    @property
    def mission_id(self) -> str:
        return str(self.mission.id)

    def __hash__(self) -> int:
        return hash(self.mission_id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, MissionNode):
            return self.mission_id == other.mission_id
        return False

    def __repr__(self) -> str:
        return (
            f"MissionNode({self.mission_id!r}, "
            f"parents={sorted(self.parents)}, "
            f"children={sorted(self.children)})"
        )


@dataclass(frozen=True)
class MissionDependency:
    """Directed edge: ``source -> target`` means *target* depends on *source*."""

    source: str  # MissionID string
    target: str  # MissionID string

    def __repr__(self) -> str:
        return f"MissionDependency({self.source!r} -> {self.target!r})"


class MissionGraph:
    """Directed acyclic graph (DAG) for Mission dependency management.

    A ``MissionGraph`` is a pure metadata container. It never executes,
    schedules, or interacts with planners, schedulers, runtimes,
    executors, tools, or agents.

    Attributes:
        _nodes: Mapping from MissionID string to :class:`MissionNode`.
        _edges: Set of :class:`MissionDependency` edges.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, MissionNode] = {}
        self._edges: set[MissionDependency] = set()

    # ------------------------------------------------------------------
    # Node management
    # ------------------------------------------------------------------

    def add_mission(self, mission: Mission) -> None:
        """Add a mission to the graph.

        Args:
            mission: The Mission to add.

        Raises:
            ValueError: If a mission with the same ID already exists.
        """
        mid = str(mission.id)
        if mid in self._nodes:
            raise ValueError(f"Mission with ID {mid!r} already exists in graph.")
        self._nodes[mid] = MissionNode(mission)

    def remove_mission(self, mission: Mission) -> None:
        """Remove a mission and all connected edges from the graph.

        Args:
            mission: The Mission to remove.
        """
        mid = str(mission.id)
        if mid not in self._nodes:
            return

        node = self._nodes[mid]

        # Remove incoming edges
        for parent_id in list(node.parents):
            parent = self._nodes.get(parent_id)
            if parent:
                parent.children.discard(mid)
                self._edges.discard(MissionDependency(parent_id, mid))

        # Remove outgoing edges
        for child_id in list(node.children):
            child = self._nodes.get(child_id)
            if child:
                child.parents.discard(mid)
                self._edges.discard(MissionDependency(mid, child_id))

        del self._nodes[mid]

    # ------------------------------------------------------------------
    # Edge management
    # ------------------------------------------------------------------

    def add_dependency(self, source: Mission, target: Mission) -> None:
        """Add a dependency: *target* depends on *source* (edge ``source -> target``).

        Args:
            source: The prerequisite mission.
            target: The mission that depends on *source*.

        Raises:
            ValueError: If either mission is not in the graph, the
                dependency already exists, or adding it would create a
                cycle.
        """
        source_id = str(source.id)
        target_id = str(target.id)

        if source_id not in self._nodes:
            raise ValueError(f"Source mission {source_id!r} not in graph.")
        if target_id not in self._nodes:
            raise ValueError(f"Target mission {target_id!r} not in graph.")

        edge = MissionDependency(source_id, target_id)
        if edge in self._edges:
            raise ValueError(
                f"Dependency {source_id!r} -> {target_id!r} already exists."
            )

        if self._can_reach(target_id, source_id):
            raise ValueError(
                f"Adding dependency {source_id!r} -> {target_id!r} "
                f"would create a cycle."
            )

        self._edges.add(edge)
        self._nodes[source_id].children.add(target_id)
        self._nodes[target_id].parents.add(source_id)

    def remove_dependency(self, source: Mission, target: Mission) -> None:
        """Remove a dependency if it exists.

        Args:
            source: The prerequisite mission.
            target: The dependent mission.
        """
        source_id = str(source.id)
        target_id = str(target.id)
        edge = MissionDependency(source_id, target_id)
        if edge not in self._edges:
            return

        self._edges.discard(edge)
        self._nodes[source_id].children.discard(target_id)
        self._nodes[target_id].parents.discard(source_id)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_dependencies(self, mission: Mission) -> list[Mission]:
        """Return missions that the given mission depends on (parents).

        Args:
            mission: The mission whose dependencies to retrieve.

        Returns:
            List of prerequisite missions in deterministic order.
        """
        mid = str(mission.id)
        node = self._nodes.get(mid)
        if not node:
            return []
        return [
            self._nodes[pid].mission
            for pid in sorted(node.parents)
            if pid in self._nodes
        ]

    def get_dependents(self, mission: Mission) -> list[Mission]:
        """Return missions that depend on the given mission (children).

        Args:
            mission: The mission whose dependents to retrieve.

        Returns:
            List of dependent missions in deterministic order.
        """
        mid = str(mission.id)
        node = self._nodes.get(mid)
        if not node:
            return []
        return [
            self._nodes[cid].mission
            for cid in sorted(node.children)
            if cid in self._nodes
        ]

    def roots(self) -> list[Mission]:
        """Return missions with no dependencies (no parents)."""
        return [
            node.mission for node in self._nodes.values() if not node.parents
        ]

    def leaves(self) -> list[Mission]:
        """Return missions with no dependents (no children)."""
        return [
            node.mission for node in self._nodes.values() if not node.children
        ]

    # ------------------------------------------------------------------
    # Algorithms
    # ------------------------------------------------------------------

    def _can_reach(self, start: str, target: str) -> bool:
        """Return whether *start* can reach *target* via existing edges."""
        if start == target:
            return True

        visited: set[str] = {start}
        queue: deque[str] = deque([start])

        while queue:
            current = queue.popleft()
            if current == target:
                return True
            node = self._nodes.get(current)
            if node:
                for child in node.children:
                    if child not in visited:
                        visited.add(child)
                        queue.append(child)

        return False

    def topological_sort(self) -> list[Mission]:
        """Return missions in topological order using Kahn's algorithm.

        The sort is deterministic: roots are processed in insertion order,
        and children are processed in sorted order by MissionID.

        Returns:
            List of missions in dependency order (prerequisites first).

        Raises:
            ValueError: If the graph contains a cycle.
        """
        if not self._nodes:
            return []

        in_degree: dict[str, int] = {
            node.mission_id: len(node.parents) for node in self._nodes.values()
        }

        # Process roots in insertion order, children in sorted order for determinism.
        queue = deque([
            node.mission_id
            for node in self._nodes.values()
            if in_degree[node.mission_id] == 0
        ])
        result: list[Mission] = []

        while queue:
            current_id = queue.popleft()
            result.append(self._nodes[current_id].mission)

            for child_id in sorted(self._nodes[current_id].children):
                in_degree[child_id] -= 1
                if in_degree[child_id] == 0:
                    queue.append(child_id)

        if len(result) != len(self._nodes):
            raise ValueError(
                "Graph contains a cycle; topological sort is impossible."
            )

        return result

    def has_cycle(self) -> bool:
        """Return ``True`` if the graph contains a cycle."""
        if not self._nodes:
            return False

        in_degree: dict[str, int] = {
            node.mission_id: len(node.parents) for node in self._nodes.values()
        }

        queue = deque([
            node.mission_id
            for node in self._nodes.values()
            if in_degree[node.mission_id] == 0
        ])
        processed = 0

        while queue:
            current_id = queue.popleft()
            processed += 1
            for child_id in self._nodes[current_id].children:
                in_degree[child_id] -= 1
                if in_degree[child_id] == 0:
                    queue.append(child_id)

        return processed != len(self._nodes)

    def validate(self) -> bool:
        """Validate graph consistency.

        Checks that all edges reference existing nodes, that parent/child
        references are bidirectionally consistent, and that the graph is
        acyclic.
        """
        # All edges reference existing nodes
        for edge in self._edges:
            if edge.source not in self._nodes or edge.target not in self._nodes:
                return False

        # Node-edge consistency
        for node in self._nodes.values():
            for parent_id in node.parents:
                if parent_id not in self._nodes:
                    return False
                parent = self._nodes[parent_id]
                if node.mission_id not in parent.children:
                    return False
                if MissionDependency(parent_id, node.mission_id) not in self._edges:
                    return False

            for child_id in node.children:
                if child_id not in self._nodes:
                    return False
                child = self._nodes[child_id]
                if node.mission_id not in child.parents:
                    return False
                if MissionDependency(node.mission_id, child_id) not in self._edges:
                    return False

        # Acyclic
        return not self.has_cycle()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize the graph to a deterministic plain dictionary."""
        return {
            "missions": [node.mission.to_dict() for node in self._nodes.values()],
            "dependencies": [
                {"source": e.source, "target": e.target}
                for e in sorted(self._edges, key=lambda d: (d.source, d.target))
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> MissionGraph:
        """Deserialize a graph from a plain dictionary.

        Ignores unknown keys for forward compatibility.
        """
        graph = cls()

        for mission_data in data.get("missions", []):
            graph.add_mission(Mission.from_dict(mission_data))

        for dep_data in data.get("dependencies", []):
            source_id = dep_data["source"]
            target_id = dep_data["target"]
            graph.add_dependency(
                graph._nodes[source_id].mission,
                graph._nodes[target_id].mission,
            )

        return graph

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._nodes)

    def __contains__(self, mission: Mission) -> bool:
        return str(mission.id) in self._nodes
