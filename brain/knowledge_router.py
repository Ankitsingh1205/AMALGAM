from __future__ import annotations

import threading
from typing import Any

from brain.shared_context import SharedContext
from services.logger import get_logger


class KnowledgeRouter:
    """Topic-based semantic context routing.

    Prevents LLM context bloat by allowing agents to selectively load only
    the specific topics they care about, rather than the entire SharedContext.
    SharedContext remains the ultimate source of truth.

    Optimized (Mission 6.6.2):
    - Fast dictionary comprehension for O(k) filtered snapshot generation.
    - ``__slots__`` for memory efficiency.
    - Fine-grained locking for subscription management.
    """

    __slots__ = ("_shared_context", "_subscriptions", "_lock", "_logger")

    def __init__(self, shared_context: SharedContext) -> None:
        self._shared_context = shared_context
        # Maps agent_name -> set of subscribed topics
        self._subscriptions: dict[str, set[str]] = {}
        self._lock = threading.RLock()
        self._logger = get_logger("knowledge_router")

    def subscribe(self, agent_name: str, topic: str) -> None:
        """Subscribe an agent to a specific knowledge topic."""
        with self._lock:
            if agent_name not in self._subscriptions:
                self._subscriptions[agent_name] = set()
            self._subscriptions[agent_name].add(topic)
        self._logger.debug("agent subscribed to topic", agent=agent_name, topic=topic)

    def publish(self, topic: str, data: Any) -> None:
        """Publish data to a topic.

        Writes the data into the SharedContext which acts as the global
        source of truth.
        """
        self._shared_context.set(topic, data)
        self._logger.info("published knowledge to topic", topic=topic)

    def get_context(self, agent_name: str) -> dict[str, Any]:
        """Retrieve a filtered snapshot of context based on subscriptions."""
        with self._lock:
            # Create a shallow copy of the set to prevent race conditions
            topics = self._subscriptions.get(agent_name, set()).copy()

        if not topics:
            return {}

        # SharedContext snapshot is thread-safe
        full_state = self._shared_context.snapshot()

        # O(k) fast filter using dict comprehension
        return {topic: full_state[topic] for topic in topics if topic in full_state}
