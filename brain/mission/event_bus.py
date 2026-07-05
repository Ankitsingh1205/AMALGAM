from __future__ import annotations

from collections import deque
from collections.abc import Callable
from typing import Optional

from brain.mission.event import MissionEvent


class MissionEventBus:
    """Lightweight synchronous event bus for the Mission subsystem.

    The Event Bus supports multiple subscribers, prevents duplicate
    subscription, dispatches events synchronously in deterministic
    subscription order, isolates subscriber exceptions, and enforces
    strongly-typed event objects.

    Event history is maintained in deterministic insertion order,
    with an optional bounded capacity (oldest evicted first).

    This component belongs entirely to the Mission layer. It is
    independent from the Planner, Scheduler, Runtime, AutonomousExecutor,
    Tool System, and Memory System.
    """

    def __init__(self, history_limit: Optional[int] = None) -> None:
        self._subscribers: list[Callable[[MissionEvent], None]] = []
        self._history: deque[MissionEvent] = deque()
        self._history_limit: int | None = (
            history_limit if history_limit and history_limit > 0 else None
        )

    def subscribe(self, callback: Callable[[MissionEvent], None]) -> None:
        """Register a callback to receive future events.

        Callbacks are stored in subscription order (FIFO) for
        deterministic dispatch. Duplicate subscriptions are silently
        ignored.

        Args:
            callback: A callable accepting a ``MissionEvent`` argument.
        """
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[MissionEvent], None]) -> None:
        """Remove a previously registered callback.

        If the callback is not currently subscribed this is a no-op.

        Args:
            callback: The callable to remove.
        """
        try:
            self._subscribers.remove(callback)
        except ValueError:
            pass

    def publish(self, event: MissionEvent) -> int:
        """Dispatch an event to all subscribers synchronously.

        Subscribers are called in deterministic subscription order.
        If a subscriber raises an exception the exception is isolated
        and does not prevent remaining subscribers from receiving the
        event.

        Published events are appended to the history buffer. If a
        history limit is configured the oldest event is evicted when
        the limit is exceeded.

        Args:
            event: The typed ``MissionEvent`` to dispatch.

        Returns:
            The number of subscribers that received the event.

        Raises:
            TypeError: If *event* is not a ``MissionEvent`` instance.
        """
        if not isinstance(event, MissionEvent):
            raise TypeError(
                f"Expected MissionEvent, got {type(event).__name__}."
            )

        delivered = 0
        for subscriber in self._subscribers:
            try:
                subscriber(event)
                delivered += 1
            except Exception:
                continue

        self._record(event)

        return delivered

    def clear(self) -> None:
        """Remove all subscribers and clear event history."""
        self._subscribers.clear()
        self._history.clear()

    def subscriber_count(self) -> int:
        """Return the number of registered subscribers."""
        return len(self._subscribers)

    def event_history(self) -> list[MissionEvent]:
        """Return all recorded events in deterministic insertion order.

        The returned list is a shallow copy — the caller may mutate it
        without affecting the internal history buffer.

        If a history limit is configured via the constructor the buffer
        never exceeds that limit (oldest events are evicted first).
        """
        return list(self._history)

    def _record(self, event: MissionEvent) -> None:
        """Append *event* to the history buffer with optional FIFO eviction."""
        if self._history_limit is not None and len(self._history) >= self._history_limit:
            self._history.popleft()
        self._history.append(event)