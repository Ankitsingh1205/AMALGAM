from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from brain.agent_context import AgentContext
from brain.messaging import Messaging, Message
from brain.shared_context import SharedContext
from services.logger import get_logger


class BaseAgent(ABC):
    """Abstract base class for all agents in the multi-agent framework.

    Every agent has:

    - A unique ``name``.
    - An isolated :class:`AgentContext` for private state.
    - Access to a :class:`SharedContext` for cross-agent communication.
    - Access to a :class:`Messaging` bus for inter-agent messaging.
    - A lifecycle: ``setup`` → ``run`` → ``teardown``.

    Concrete agents must implement :meth:`run`.
    """

    def __init__(
        self,
        name: str,
        shared_context: Optional[SharedContext] = None,
        messaging: Optional[Messaging] = None,
    ) -> None:
        self.name = name
        self._context = AgentContext(name)
        self._shared = shared_context or SharedContext()
        self._messaging = messaging or Messaging()
        self._logger = get_logger(name)
        self._status = "idle"

    @property
    def status(self) -> str:
        """Current lifecycle status (``idle``, ``ready``, ``running``,
        ``completed``, ``failed``)."""
        return self._status

    def setup(self) -> None:
        """Lifecycle hook called before the agent runs.

        Subclasses may override this to perform one-time initialisation.
        """
        self._status = "ready"
        self._logger.info("agent setup", agent=self.name)

    @abstractmethod
    def run(self, shared_context: SharedContext) -> Any:
        """Execute the agent's primary logic.

        Args:
            shared_context: The blackboard containing task data and
                intermediate results from upstream agents.

        Returns:
            The agent's result. It is good practice to return a dictionary
            with at least a ``success`` key.
        """
        raise NotImplementedError

    def teardown(self) -> None:
        """Lifecycle hook called after the agent runs.

        Subclasses may override this to release resources.
        """
        self._status = "idle"
        self._logger.info("agent teardown", agent=self.name)

    def send_message(self, recipient: str, msg_type: str, payload: Any = None) -> None:
        """Send a message to another agent via the messaging bus.

        Args:
            recipient: Target agent name or ``"*"`` for broadcast.
            msg_type: Message category.
            payload: Arbitrary payload.
        """
        msg = Message(
            sender=self.name,
            recipient=recipient,
            msg_type=msg_type,
            payload=payload,
        )
        self._messaging.send(msg)

    def receive_messages(self) -> list[Message]:
        """Retrieve and clear all pending messages for this agent.

        Returns:
            List of :class:`Message` objects.
        """
        return self._messaging.receive(self.name)

    def peek_messages(self) -> list[Message]:
        """Peek at pending messages without removing them.

        Returns:
            Shallow copy of pending messages.
        """
        return self._messaging.peek(self.name)

    def has_messages(self) -> bool:
        """Return whether this agent has unread messages."""
        return self._messaging.has_messages(self.name)

    def _record(self, event: str, data: Any = None) -> None:
        """Record an event in the agent's private context."""
        self._context.record({
            "event": event,
            "data": data,
            "agent": self.name,
        })
