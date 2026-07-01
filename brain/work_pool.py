from __future__ import annotations

import threading
import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Any, Optional

from brain.messaging import Messaging, Message
from services.logger import get_logger


class WorkPool:
    """Capability-aware distributed task queue for work stealing.

    Instead of pushing tasks to specific agents, tasks are submitted to
    capability-specific queues. Agents 'steal' work matching their capabilities
    when idle.

    Optimized (Mission 6.6.2):
    - Deques for O(1) queue operations.
    - Lock batching via RLock to minimize contention.
    """

    __slots__ = ("_messaging", "_queues", "_active_tasks", "_lock", "_logger")

    def __init__(self, messaging: Messaging) -> None:
        self._messaging = messaging
        # Maps capability (str) -> deque of task dicts
        self._queues: dict[str, deque[dict[str, Any]]] = {}
        # Maps task_id -> task dict (tracking ownership)
        self._active_tasks: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._logger = get_logger("work_pool")

    def submit_task(self, task: dict[str, Any], required_capability: str) -> str:
        """Submit a task to the pool for a specific capability."""
        task_id = task.get("id") or str(uuid.uuid4())
        task["id"] = task_id
        task["status"] = "pending"
        task["required_capability"] = required_capability
        task["submitted_at"] = datetime.now(timezone.utc).isoformat()

        with self._lock:
            if required_capability not in self._queues:
                self._queues[required_capability] = deque()
            self._queues[required_capability].append(task)

        self._logger.info("task submitted to work pool", task_id=task_id, capability=required_capability)

        # Broadcast availability so idle agents can wake up and steal it
        self._messaging.send(Message(
            sender="work_pool",
            recipient="*",
            msg_type="work_available",
            payload={"capability": required_capability}
        ))

        return task_id

    def steal_task(self, agent_name: str, capabilities: list[str]) -> Optional[dict[str, Any]]:
        """Attempt to steal a task matching one of the provided capabilities.

        Capabilities are checked in the order provided (priority order).
        """
        with self._lock:
            for cap in capabilities:
                queue = self._queues.get(cap)
                if queue:
                    task = queue.popleft()
                    task["status"] = "running"
                    task["owner"] = agent_name
                    task["started_at"] = datetime.now(timezone.utc).isoformat()
                    self._active_tasks[task["id"]] = task
                    self._logger.info("task stolen", task_id=task["id"], agent=agent_name, capability=cap)
                    return task
        return None

    def requeue_task(self, task_id: str) -> bool:
        """Return an active task back to its capability queue (e.g. if agent dies)."""
        with self._lock:
            task = self._active_tasks.pop(task_id, None)
            if task:
                task["status"] = "pending"
                task.pop("owner", None)
                task.pop("started_at", None)
                cap = task.get("required_capability", "default")
                
                if cap not in self._queues:
                    self._queues[cap] = deque()
                # Put it at the front for immediate retry
                self._queues[cap].appendleft(task)
                
                self._logger.warning("task requeued", task_id=task_id)
                return True
        return False

    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """Mark a stolen task as completed and notify observers."""
        with self._lock:
            task = self._active_tasks.pop(task_id, None)
            if task:
                self._logger.info("task completed in work pool", task_id=task_id)
                self._messaging.send(Message(
                    sender="work_pool",
                    recipient="*",
                    msg_type="task_completed",
                    payload={"task_id": task_id, "result": result}
                ))
                return True
        return False

    def fail_task(self, task_id: str, error: str = "") -> bool:
        """Mark a stolen task as failed and notify observers."""
        with self._lock:
            task = self._active_tasks.pop(task_id, None)
            if task:
                self._logger.error("task failed in work pool", task_id=task_id, error=error)
                self._messaging.send(Message(
                    sender="work_pool",
                    recipient="*",
                    msg_type="task_failed",
                    payload={"task_id": task_id, "error": error}
                ))
                return True
        return False

    def get_progress(self) -> dict[str, Any]:
        """Return O(1) snapshot of work pool progress."""
        with self._lock:
            pending = sum(len(q) for q in self._queues.values())
            running = len(self._active_tasks)
            return {
                "pending": pending,
                "running": running,
                "total_active": pending + running
            }
