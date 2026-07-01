from __future__ import annotations

import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


@dataclass
class Message:
    """Inter-agent message for the multi-agent messaging bus.

    Attributes:
        sender: Name of the sending agent.
        recipient: Name of the target agent (or ``"*"`` for broadcast).
        msg_type: Message category (e.g., ``task``, ``plan``, ``research``,
            ``review``, ``result``, ``error``, ``notification``).
        payload: Arbitrary message payload.
        timestamp: ISO timestamp of creation.
        id: Unique message identifier.
    """

    sender: str
    recipient: str
    msg_type: str
    payload: Any = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


# Sentinel object used to detect a missing inbox key without raising KeyError.
_MISSING = object()


class Messaging:
    """In-memory message bus for inter-agent communication.

    Each agent has a private inbox. Messages can be sent directly or
    broadcast. Handlers can subscribe to receive real-time notifications.

    Optimizations (Mission 6.5.2):
    - ``has_messages`` uses ``dict.get`` instead of KeyError exception flow.
    - Broadcast avoids redundant ``setdefault`` by iterating existing inboxes
      directly; the inbox is guaranteed to exist since we only broadcast to
      already-known recipients.
    - ``subscribe`` pre-allocates the inbox for the subscribing agent so that
      future ``send`` calls skip the ``setdefault`` path.

    Attributes:
        _inboxes: Mapping of agent name to inbox deque.
        _handlers: Mapping of agent name to list of handler callbacks.
    """

    __slots__ = ("_inboxes", "_handlers")

    def __init__(self) -> None:
        self._inboxes: dict[str, deque[Message]] = {}
        self._handlers: dict[str, list[Callable[[Message], None]]] = {}

    def send(self, message: Message) -> None:
        """Deliver a message to the recipient's inbox.

        If the recipient is ``"*"``, the message is broadcast to all
        known inboxes. Subscribed handlers are also invoked.

        Args:
            message: The ``Message`` to deliver.
        """
        if message.recipient == "*":
            # Iterate over a snapshot of current keys to avoid mutation
            # issues if a handler causes a new inbox to be created.
            for name, inbox in list(self._inboxes.items()):
                inbox.append(message)
                self._notify(name, message)
        else:
            inbox = self._inboxes.get(message.recipient)
            if inbox is None:
                inbox = deque()
                self._inboxes[message.recipient] = inbox
            inbox.append(message)
            self._notify(message.recipient, message)

    def subscribe(self, agent_name: str, handler: Callable[[Message], None]) -> None:
        """Subscribe a handler to receive real-time messages for an agent.

        Pre-allocates an inbox for ``agent_name`` so that broadcast
        immediately reaches this agent.

        Args:
            agent_name: The agent whose messages the handler cares about.
            handler: Callable invoked with each incoming ``Message``.
        """
        if agent_name not in self._inboxes:
            self._inboxes[agent_name] = deque()
        handlers = self._handlers.get(agent_name)
        if handlers is None:
            self._handlers[agent_name] = [handler]
        else:
            handlers.append(handler)

    def receive(self, agent_name: str) -> list[Message]:
        """Retrieve and clear all pending messages for an agent.

        Args:
            agent_name: Name of the agent.

        Returns:
            List of pending ``Message`` objects.
        """
        inbox = self._inboxes.get(agent_name)
        if inbox is None:
            return []
        messages = list(inbox)
        inbox.clear()
        return messages

    def peek(self, agent_name: str) -> list[Message]:
        """Peek at pending messages without removing them.

        Args:
            agent_name: Name of the agent.

        Returns:
            Shallow copy of pending messages.
        """
        inbox = self._inboxes.get(agent_name)
        return list(inbox) if inbox else []

    def has_messages(self, agent_name: str) -> bool:
        """Return whether the agent has unread messages.

        Args:
            agent_name: Name of the agent.

        Returns:
            ``True`` if the inbox is non-empty.
        """
        inbox = self._inboxes.get(agent_name)
        return inbox is not None and bool(inbox)

    def clear_inbox(self, agent_name: str) -> None:
        """Clear an agent's inbox without reading.

        Args:
            agent_name: Name of the agent.
        """
        inbox = self._inboxes.get(agent_name)
        if inbox is not None:
            inbox.clear()

    def _notify(self, agent_name: str, message: Message) -> None:
        """Invoke subscribed handlers for a message."""
        handlers = self._handlers.get(agent_name)
        if handlers is None:
            return
        for handler in handlers:
            try:
                handler(message)
            except Exception:
                pass
