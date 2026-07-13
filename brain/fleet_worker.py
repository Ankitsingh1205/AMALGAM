"""FleetWorker -- in-process worker loop for the WorkPool (Mission 7.5).

Prior to Mission 7.5 the ``WorkPool.steal_task`` API was only exercised
by tests, which simulated workers on ad-hoc threads.  ``FleetWorker``
provides the missing production worker loop: a daemon thread that
repeatedly steals tasks matching its capabilities, executes them through
a caller-supplied handler, and reports completion or failure back to the
pool so the ``ChiefAgent`` orchestration can make progress.

The worker is deliberately generic -- execution semantics live in the
``handler`` callable, keeping this module free of agent- or tool-
specific knowledge (Brain/Kernel separation, ADR-001).
"""

from __future__ import annotations

import threading
from typing import Any, Callable, Optional

from brain.work_pool import WorkPool
from services.logger import get_logger


class FleetWorker:
    """Background worker that steals and executes WorkPool tasks.

    Args:
        name: Worker identity used for task ownership and logging.
        capabilities: Capability names this worker can serve, in
            priority order (forwarded to ``WorkPool.steal_task``).
        work_pool: The shared ``WorkPool`` instance.
        handler: Callable invoked with the stolen task dict.  Its
            return value is reported via ``WorkPool.complete_task``.
            Exceptions are caught and reported via ``fail_task``.
        poll_interval: Seconds to sleep when no work is available.
    """

    def __init__(
        self,
        name: str,
        capabilities: list[str],
        work_pool: WorkPool,
        handler: Callable[[dict[str, Any]], Any],
        poll_interval: float = 0.05,
    ) -> None:
        self._name = name
        self._capabilities = list(capabilities)
        self._pool = work_pool
        self._handler = handler
        self._poll_interval = poll_interval
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._logger = get_logger(f"fleet_worker.{name}")

    @property
    def name(self) -> str:
        """Worker identity."""
        return self._name

    @property
    def running(self) -> bool:
        """``True`` while the worker thread is alive."""
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        """Start the worker loop on a daemon thread (idempotent)."""
        if self.running:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._loop,
            name=f"fleet-worker-{self._name}",
            daemon=True,
        )
        self._thread.start()
        self._logger.info("worker started", capabilities=self._capabilities)

    def stop(self, timeout: float = 2.0) -> None:
        """Signal the loop to stop and join the thread."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout)
            self._thread = None
        self._logger.info("worker stopped")

    def _loop(self) -> None:
        """Steal-execute-report loop until ``stop`` is requested."""
        while not self._stop_event.is_set():
            task = self._pool.steal_task(self._name, self._capabilities)
            if task is None:
                self._stop_event.wait(self._poll_interval)
                continue

            task_id = task["id"]
            try:
                result = self._handler(task)
            except Exception as e:  # noqa: BLE001 -- worker must never die
                self._logger.error("task handler failed", task_id=task_id, error=str(e))
                self._pool.fail_task(task_id, error=str(e))
            else:
                self._pool.complete_task(task_id, result=result)
