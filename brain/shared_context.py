from __future__ import annotations

from collections import deque
from threading import Lock
from typing import Any


class SharedContext:
    """Thread-safe context shared across all agents in a pipeline.

    The ``SharedContext`` acts as a blackboard where agents publish and
    read intermediate results. Access is synchronised with a lock so that
    concurrent agents can safely mutate the state.

    Optimizations (Mission 6.5.2):
    - ``__slots__`` eliminates the per-instance ``__dict__`` overhead.
    - History stored as ``deque`` for O(1) append; copies still O(n) but
      only on explicit ``get_history()`` call.
    - ``update()`` batches all dict mutations inside a single lock section,
      then records history in one pass — avoiding repeated lock acquisitions.

    Attributes:
        _state: Key-value store for shared data.
        _history: Ordered audit trail of mutations.
        _lock: Lock protecting all operations.
    """

    __slots__ = ("_state", "_history", "_lock")

    def __init__(self) -> None:
        self._state: dict[str, Any] = {}
        self._history: deque[dict] = deque()
        self._lock = Lock()

    def get(self, key: str, default: Any = None) -> Any:
        """Return a value from the shared state."""
        with self._lock:
            return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Store a value in the shared state and record the mutation."""
        with self._lock:
            self._state[key] = value
            self._history.append({"op": "set", "key": key, "value": value})

    def update(self, updates: dict) -> None:
        """Merge a dictionary into the shared state."""
        with self._lock:
            self._state.update(updates)
            # Build all history entries in a single pass inside the lock
            # to avoid repeated lock overhead.
            hist = self._history
            for key, value in updates.items():
                hist.append({"op": "update", "key": key, "value": value})

    def snapshot(self) -> dict:
        """Return a shallow copy of the current shared state."""
        with self._lock:
            return dict(self._state)

    def record(self, event: dict) -> None:
        """Append an arbitrary audit event to the history."""
        with self._lock:
            self._history.append(event)

    def get_history(self) -> list[dict]:
        """Return a shallow copy of the recorded history."""
        with self._lock:
            return list(self._history)

    def clear(self) -> None:
        """Reset both state and history."""
        with self._lock:
            self._state.clear()
            self._history.clear()
