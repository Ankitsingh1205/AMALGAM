from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any, Optional

from config import constants
from services.logger import get_logger


class TaskQueue:
    """Sequential task queue with lifecycle controls.

    Tasks are executed one at a time in FIFO order. The queue supports
    pausing, resuming, and cancelling individual or all tasks.

    Optimizations (Mission 6.5.2):
    - History stored as a ``deque`` with ``maxlen`` so that trimming is O(1)
      (automatic eviction by the deque) rather than the previous O(n) list
      slice.  ``_trim_history`` is retained as a no-op for API compatibility.
    - ``progress()`` maintains running counters (``_completed``,
      ``_failed``, ``_cancelled``) updated at mutation sites, eliminating
      the O(n) history scan on every call.
    - ``cancel()`` iterates the deque using ``enumerate`` — same complexity
      as before but avoids creating an intermediate list copy.

    Attributes:
        _queue: Internal deque of pending tasks.
        _running: The currently executing task, if any.
        _paused: Whether the queue is paused.
        _history: Record of completed or failed tasks (bounded deque).
        _max_history: Maximum number of history entries to retain.
        _completed: Count of completed tasks.
        _failed: Count of failed tasks.
        _cancelled: Count of cancelled tasks.
        _logger: Structured logger instance.
    """

    def __init__(self, max_history: int = 1000) -> None:
        self._queue: deque[dict] = deque()
        self._running: Optional[dict] = None
        self._paused: bool = False
        # Use a bounded deque — eviction is O(1) with no explicit trim call.
        self._history: deque[dict] = deque(maxlen=max_history)
        self._max_history = max_history
        # Counters kept in sync with history mutations for O(1) progress().
        self._completed: int = 0
        self._failed: int = 0
        self._cancelled: int = 0
        self._logger = get_logger("task_queue")

    def enqueue(self, task: dict) -> None:
        """Add a task to the back of the queue.

        The task dictionary must contain at least an ``id`` key.
        A ``status`` field of ``pending`` is added if absent.

        Args:
            task: Dictionary representing the task to enqueue.
        """
        task.setdefault("status", constants.TASK_STATUS_PENDING)
        task.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        self._queue.append(task)
        self._logger.info("task enqueued", task_id=task.get("id"), queue_size=len(self._queue))

    def dequeue(self) -> Optional[dict]:
        """Remove and return the next task from the front of the queue.

        Returns ``None`` if the queue is empty or paused.

        Returns:
            The next task dictionary, or ``None``.
        """
        if self._paused:
            self._logger.debug("dequeue skipped: queue is paused")
            return None

        if not self._queue:
            return None

        task = self._queue.popleft()
        task["status"] = constants.TASK_STATUS_RUNNING
        self._running = task
        self._logger.info("task dequeued", task_id=task.get("id"))
        return task

    def pause(self) -> None:
        """Pause the queue so that ``dequeue()`` returns ``None``."""
        self._paused = True
        self._logger.info("queue paused")

    def resume(self) -> None:
        """Resume the queue so that ``dequeue()`` may return tasks."""
        self._paused = False
        self._logger.info("queue resumed")

    def cancel(self, task_id: Optional[str] = None) -> bool:
        """Cancel a task by ID or the current running task.

        If ``task_id`` is ``None`` and a task is currently running,
        that running task is cancelled.

        Args:
            task_id: Optional identifier of the task to cancel.

        Returns:
            ``True`` if a task was found and cancelled, ``False`` otherwise.
        """
        if task_id is None and self._running is not None:
            self._running["status"] = constants.TASK_STATUS_CANCELLED
            self._cancelled += 1
            self._append_history(self._running)
            self._running = None
            self._logger.info("running task cancelled")
            return True

        for i, task in enumerate(self._queue):
            if task.get("id") == task_id:
                task["status"] = constants.TASK_STATUS_CANCELLED
                self._cancelled += 1
                self._append_history(task)
                del self._queue[i]
                self._logger.info("pending task cancelled", task_id=task_id)
                return True

        return False

    def clear_pending(self) -> None:
        """Clear all pending tasks without affecting history."""
        self._queue.clear()
        self._running = None
        self._logger.info("queue cleared")

    def progress(self) -> dict:
        """Return a snapshot of queue progress.

        O(1) — counters are maintained incrementally.

        Returns:
            Dictionary with ``pending``, ``running``, ``completed``,
            ``failed``, ``cancelled``, and ``total`` counts.
        """
        pending = len(self._queue)
        running = 1 if self._running else 0

        return {
            "pending": pending,
            "running": running,
            "completed": self._completed,
            "failed": self._failed,
            "cancelled": self._cancelled,
            "total": pending + running + self._completed + self._failed + self._cancelled,
        }

    def complete_current(self, result: Any = None) -> None:
        """Mark the currently running task as completed.

        Args:
            result: Optional result payload to attach to the task.
        """
        if self._running is None:
            return

        self._running["status"] = constants.TASK_STATUS_COMPLETED
        self._running["result"] = result
        self._running["completed_at"] = datetime.now(timezone.utc).isoformat()
        self._completed += 1
        self._append_history(self._running)
        self._logger.info("task completed", task_id=self._running.get("id"))
        self._running = None

    def fail_current(self, error: Optional[str] = None) -> None:
        """Mark the currently running task as failed.

        Args:
            error: Optional error message to attach to the task.
        """
        if self._running is None:
            return

        self._running["status"] = constants.TASK_STATUS_FAILED
        self._running["error"] = error
        self._running["failed_at"] = datetime.now(timezone.utc).isoformat()
        self._failed += 1
        self._append_history(self._running)
        self._logger.error("task failed", task_id=self._running.get("id"), error=error)
        self._running = None

    def _append_history(self, task: dict) -> None:
        """Append to the bounded history deque.

        When ``maxlen`` is reached the oldest entry is silently evicted by
        the deque — no explicit trim is required.
        """
        self._history.append(task)

    def _trim_history(self) -> None:
        """No-op: history is bounded by the deque's ``maxlen``."""

    def is_empty(self) -> bool:
        """Return ``True`` if no tasks are pending or running."""
        return len(self._queue) == 0 and self._running is None

    def is_paused(self) -> bool:
        """Return ``True`` if the queue is paused."""
        return self._paused

    def list_pending(self) -> list[dict]:
        """Return a shallow copy of the pending task list."""
        return list(self._queue)

    def list_history(self) -> list[dict]:
        """Return a shallow copy of the task history."""
        return list(self._history)
