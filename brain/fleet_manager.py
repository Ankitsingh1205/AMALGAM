from __future__ import annotations

import threading
import time
from typing import Any

from brain.messaging import Messaging, Message
from services.logger import get_logger


class FleetManager:
    """Oversees health, lifecycle, and load of the multi-agent fleet.

    Maintains a registry of active agents, their capabilities, and current
    load metrics. Listens for asynchronous heartbeats over the Messaging bus
    to avoid blocking agent execution.

    Optimized (Mission 6.6.2):
    - Uses ``__slots__`` for memory efficiency.
    - Employs ``threading.RLock()`` lock batching for fast concurrent updates.
    """

    __slots__ = ("_messaging", "_agents", "_lock", "_logger")

    def __init__(self, messaging: Messaging) -> None:
        self._messaging = messaging
        self._agents: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._logger = get_logger("fleet_manager")

        # Subscribe to the messaging bus as 'fleet_manager'
        self._messaging.subscribe("fleet_manager", self._on_message)

    def _on_message(self, message: Message) -> None:
        """Handle incoming asynchronous health and registry events."""
        if message.msg_type == "heartbeat":
            self.report_health(message.sender, message.payload or {})
        elif message.msg_type == "register":
            payload = message.payload or {}
            caps = payload.get("capabilities", [])
            self.register(message.sender, caps)

    def register(self, agent_name: str, capabilities: list[str]) -> None:
        """Register an agent with the fleet."""
        with self._lock:
            self._agents[agent_name] = {
                "capabilities": set(capabilities),
                "last_seen": time.time(),
                "status": "idle",
                "load": 0,
                "consecutive_failures": 0,
            }
        self._logger.info("agent registered with fleet manager", agent=agent_name)

    def report_health(self, agent_name: str, metrics: dict[str, Any]) -> None:
        """Update the health and load metrics for an agent."""
        with self._lock:
            agent = self._agents.get(agent_name)
            if agent:
                agent["last_seen"] = time.time()
                if "status" in metrics:
                    agent["status"] = metrics["status"]
                if "load" in metrics:
                    agent["load"] = metrics["load"]
                if "consecutive_failures" in metrics:
                    agent["consecutive_failures"] = metrics["consecutive_failures"]

    def get_fleet_state(self) -> dict[str, dict[str, Any]]:
        """Return a point-in-time snapshot of the entire fleet."""
        with self._lock:
            # Shallow copy of the agent dicts is sufficient here since values are primitives/sets
            return {name: data.copy() for name, data in self._agents.items()}

    def get_agent_state(self, agent_name: str) -> dict[str, Any]:
        """Return the state of a specific agent, or empty dict if unknown."""
        with self._lock:
            agent = self._agents.get(agent_name)
            return agent.copy() if agent else {}

    def unregister(self, agent_name: str) -> None:
        """Remove an agent from the fleet.

        Called during graceful shutdown. No-op if the agent is unknown.
        """
        with self._lock:
            removed = self._agents.pop(agent_name, None)
        if removed is not None:
            self._logger.info("agent unregistered from fleet", agent=agent_name)
        else:
            self._logger.debug("unregister for unknown agent (no-op)", agent=agent_name)

    def increment_failures(self, agent_name: str) -> int:
        """Increment the consecutive failure count for an agent.

        Returns the new count, or 0 if the agent is unknown.
        """
        with self._lock:
            agent = self._agents.get(agent_name)
            if agent is None:
                return 0
            agent["consecutive_failures"] = agent.get("consecutive_failures", 0) + 1
            new_count = agent["consecutive_failures"]
        self._logger.debug("failure incremented", agent=agent_name, consecutive_failures=new_count)
        return new_count

    def clear_failures(self, agent_name: str) -> None:
        """Reset consecutive failure count to zero for an agent.

        No-op if the agent is unknown.
        """
        with self._lock:
            agent = self._agents.get(agent_name)
            if agent is None:
                return
            agent["consecutive_failures"] = 0
        self._logger.debug("failures cleared", agent=agent_name)

    def reap_dead_agents(self, timeout_seconds: float = 60.0) -> list[str]:
        """Remove agents that haven't sent a heartbeat within the timeout."""
        now = time.time()
        dead_agents = []

        with self._lock:
            for name, data in list(self._agents.items()):
                if now - data["last_seen"] > timeout_seconds:
                    dead_agents.append(name)
                    del self._agents[name]

        for name in dead_agents:
            self._logger.warning("agent reaped due to heartbeat timeout", agent=name)

        return dead_agents
