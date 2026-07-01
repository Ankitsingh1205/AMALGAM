from __future__ import annotations

from typing import Any, Optional

from services.logger import get_logger


class AgentRegistry:
    """Central registry for agent discovery and lookup.

    The registry holds agent instances keyed by their logical name. It is
    intentionally stateless regarding agent execution — it only manages
    references.

    Attributes:
        _agents: Mapping of agent name to agent instance.
        _logger: Structured logger instance.
    """

    def __init__(self) -> None:
        self._agents: dict[str, Any] = {}
        self._logger = get_logger("agent_registry")

    def register(self, name: str, agent: Any) -> None:
        """Register an agent under a logical name.

        Args:
            name: Unique identifier for the agent.
            agent: The agent instance.
        """
        self._agents[name] = agent
        self._logger.info("agent registered", name=name, agent_type=type(agent).__name__)

    def get(self, name: str) -> Optional[Any]:
        """Retrieve an agent by name.

        Args:
            name: Agent identifier.

        Returns:
            The agent instance, or ``None`` if not found.
        """
        return self._agents.get(name)

    def list_all(self) -> list[str]:
        """Return all registered agent names."""
        return list(self._agents.keys())

    def unregister(self, name: str) -> None:
        """Remove an agent from the registry.

        Args:
            name: Agent identifier.
        """
        if name in self._agents:
            del self._agents[name]
            self._logger.info("agent unregistered", name=name)

    def reset(self) -> None:
        """Clear all registrations."""
        self._agents.clear()
        self._logger.info("agent registry reset")

    def __contains__(self, name: str) -> bool:
        return name in self._agents
