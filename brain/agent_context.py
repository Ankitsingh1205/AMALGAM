from __future__ import annotations

from typing import Any


class AgentContext:
    """Isolated execution context for a single agent.

    Each agent maintains its own ``AgentContext`` so that private state,
    configuration, and history do not leak to other agents.

    Attributes:
        _agent_name: Name of the owning agent.
        _state: Key-value store for agent-local data.
        _history: Ordered list of recorded events.
    """

    def __init__(self, agent_name: str) -> None:
        self._agent_name = agent_name
        self._state: dict[str, Any] = {}
        self._history: list[dict] = []

    @property
    def agent_name(self) -> str:
        return self._agent_name

    def get(self, key: str, default: Any = None) -> Any:
        """Return a value from the agent's private state."""
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Store a value in the agent's private state."""
        self._state[key] = value

    def update(self, updates: dict) -> None:
        """Merge a dictionary into the agent's private state."""
        self._state.update(updates)

    def snapshot(self) -> dict:
        """Return a shallow copy of the current state."""
        return dict(self._state)

    def record(self, event: dict) -> None:
        """Append an event to the agent's history.

        The event dictionary should include at least an ``event`` key.
        """
        self._history.append(event)

    def get_history(self) -> list[dict]:
        """Return a shallow copy of the recorded history."""
        return list(self._history)

    def clear_history(self) -> None:
        """Purge the agent's history."""
        self._history.clear()

    def clear(self) -> None:
        """Reset both state and history."""
        self._state.clear()
        self._history.clear()
