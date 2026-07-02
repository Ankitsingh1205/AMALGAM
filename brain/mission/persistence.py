from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from brain.mission.epic import Epic
from brain.mission.graph import MissionGraph
from brain.mission.mission import Mission


class MissionPersistenceError(Exception):
    """Raised when a mission persistence operation fails."""


class MissionPersistence:
    """Persistent storage coordinator for Mission, Epic, and MissionGraph.

    Uses JSON for human-readable, deterministic output. All serialization
    logic is delegated to the domain objects themselves (``to_dict()`` /
    ``from_dict()``). This layer only coordinates file I/O.
    """

    @staticmethod
    def save_mission(mission: Mission, path: Path | str) -> None:
        """Serialize a Mission to a JSON file.

        Args:
            mission: The Mission to persist.
            path: Destination file path.

        Raises:
            MissionPersistenceError: If writing fails.
        """
        MissionPersistence._write_json(mission.to_dict(), path)

    @staticmethod
    def load_mission(path: Path | str) -> Mission:
        """Deserialize a Mission from a JSON file.

        Args:
            path: Source file path.

        Returns:
            The restored Mission.

        Raises:
            MissionPersistenceError: If the file is missing, empty, or
                contains invalid data.
        """
        data = MissionPersistence._read_json(path)
        if not isinstance(data, dict):
            raise MissionPersistenceError(
                f"Expected dict at {path!r}, got {type(data).__name__}."
            )
        try:
            return Mission.from_dict(data)
        except Exception as e:
            raise MissionPersistenceError(
                f"Failed to load mission from {path!r}: {e}"
            ) from e

    @staticmethod
    def save_epic(epic: Epic, path: Path | str) -> None:
        """Serialize an Epic to a JSON file.

        Args:
            epic: The Epic to persist.
            path: Destination file path.

        Raises:
            MissionPersistenceError: If writing fails.
        """
        MissionPersistence._write_json(epic.to_dict(), path)

    @staticmethod
    def load_epic(path: Path | str) -> Epic:
        """Deserialize an Epic from a JSON file.

        Args:
            path: Source file path.

        Returns:
            The restored Epic.

        Raises:
            MissionPersistenceError: If the file is missing, empty, or
                contains invalid data.
        """
        data = MissionPersistence._read_json(path)
        if not isinstance(data, dict):
            raise MissionPersistenceError(
                f"Expected dict at {path!r}, got {type(data).__name__}."
            )
        try:
            return Epic.from_dict(data)
        except Exception as e:
            raise MissionPersistenceError(
                f"Failed to load epic from {path!r}: {e}"
            ) from e

    @staticmethod
    def save_graph(graph: MissionGraph, path: Path | str) -> None:
        """Serialize a MissionGraph to a JSON file.

        Args:
            graph: The MissionGraph to persist.
            path: Destination file path.

        Raises:
            MissionPersistenceError: If writing fails.
        """
        MissionPersistence._write_json(graph.to_dict(), path)

    @staticmethod
    def load_graph(path: Path | str) -> MissionGraph:
        """Deserialize a MissionGraph from a JSON file.

        Args:
            path: Source file path.

        Returns:
            The restored MissionGraph.

        Raises:
            MissionPersistenceError: If the file is missing, empty, or
                contains invalid data.
        """
        data = MissionPersistence._read_json(path)
        if not isinstance(data, dict):
            raise MissionPersistenceError(
                f"Expected dict at {path!r}, got {type(data).__name__}."
            )
        try:
            return MissionGraph.from_dict(data)
        except Exception as e:
            raise MissionPersistenceError(
                f"Failed to load graph from {path!r}: {e}"
            ) from e

    @staticmethod
    def save_all(container: dict[str, Any], path: Path | str) -> None:
        """Serialize a collection of mission objects to a JSON file.

        The *container* dict should use keys such as ``missions``,
        ``epics``, ``graphs``. Each value is a list of domain objects.

        Example::

            MissionPersistence.save_all({
                "missions": [mission1, mission2],
                "epics": [epic1],
            }, path)

        Args:
            container: Dictionary of lists of domain objects.
            path: Destination file path.

        Raises:
            MissionPersistenceError: If writing fails.
        """
        serialised: dict[str, Any] = {}
        for key, values in container.items():
            if isinstance(values, list):
                serialised[key] = [
                    v.to_dict() if hasattr(v, "to_dict") else v
                    for v in values
                ]
            elif hasattr(values, "to_dict"):
                serialised[key] = values.to_dict()
            else:
                serialised[key] = values

        MissionPersistence._write_json(serialised, path)

    @staticmethod
    def load_all(path: Path | str) -> dict[str, Any]:
        """Deserialize a collection of mission objects from a JSON file.

        Returns a plain dictionary. Callers are responsible for converting
        nested dicts back to domain objects if needed.

        Args:
            path: Source file path.

        Returns:
            The restored dictionary.

        Raises:
            MissionPersistenceError: If the file is missing, empty, or
                contains invalid data.
        """
        return MissionPersistence._read_json(path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _write_json(data: Any, path: Path | str) -> None:
        """Write *data* as pretty-printed JSON to *path*."""
        target = Path(path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.write("\n")
        except (OSError, TypeError) as e:
            raise MissionPersistenceError(
                f"Failed to write to {target!r}: {e}"
            ) from e

    @staticmethod
    def _read_json(path: Path | str) -> Any:
        """Read and parse JSON from *path*.

        Returns an empty dict for missing or empty files.

        Raises:
            MissionPersistenceError: For malformed JSON or schema errors.
        """
        source = Path(path)
        if not source.exists():
            return {}

        try:
            with source.open("r", encoding="utf-8") as f:
                text = f.read().strip()
                if not text:
                    return {}
                return json.loads(text)
        except json.JSONDecodeError as e:
            raise MissionPersistenceError(
                f"Malformed JSON in {source!r}: {e}"
            ) from e
        except OSError as e:
            raise MissionPersistenceError(
                f"Failed to read {source!r}: {e}"
            ) from e
