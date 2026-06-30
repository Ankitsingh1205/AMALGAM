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

    Attributes:
        _queue: Internal deque of pending tasks.
        _running: The currently executing task, if any.
        _paused: Whether the queue is paused.
        _history: Record of completed or failed tasks.
        _max_history: Maximum number of history entries to retain.
        _logger: Structured logger instance.
    """

    def __init__(self, max_history: int = 1000) -> None:
        self._queue: deque[dict] = deque()
        self._running: Optional[dict] = None
        self._paused: bool = False
        self._history: list[dict] = []
        self._max_history = max_history
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
            self._history.append(self._running)
            self._trim_history()
            self._running = None
            self._logger.info("running task cancelled")
            return True

        for i, task in enumerate(self._queue):
            if task.get("id") == task_id:
                task["status"] = constants.TASK_STATUS_CANCELLED
                self._history.append(task)
                self._trim_history()
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

        Returns:
            Dictionary with ``pending``, ``running``, ``completed``,
            ``failed``, ``cancelled``, and ``total`` counts.
        """
        completed = failed = cancelled = 0
        for t in self._history:
            status = t.get("status")
            if status == constants.TASK_STATUS_COMPLETED:
                completed += 1
            elif status == constants.TASK_STATUS_FAILED:
                failed += 1
            elif status == constants.TASK_STATUS_CANCELLED:
                cancelled += 1
        pending = len(self._queue)
        running = 1 if self._running else 0

        return {
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed,
            "cancelled": cancelled,
            "total": pending + running + completed + failed + cancelled,
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
        self._history.append(self._running)
        self._trim_history()
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
        self._history.append(self._running)
        self._trim_history()
        self._logger.error("task failed", task_id=self._running.get("id"), error=error)
        self._running = None

    def _trim_history(self) -> None:
        """Trim history to the configured maximum size."""
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

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
