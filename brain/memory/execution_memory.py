from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

from config import constants
from services.memory import MemoryService
from services.logger import get_logger


class ExecutionMemory:
    """Records every step of an autonomous execution for audit and replay.

    Uses the existing ``MemoryService`` for persistence, but structures
    entries into execution records. Each record captures a single step
    in the goal-plan-task-action pipeline.

    Records are kept in a local index for fast ``recall()`` without
    scanning the entire memory store. Writes are batched to reduce
    ``MemoryService`` I/O. Per-goal retention prevents unbounded growth.

    Attributes:
        _memory: Underlying ``MemoryService`` instance.
        _batch: Pending writes not yet flushed to ``MemoryService``.
        _batch_size: Number of records to buffer before flushing.
        _local_index: In-memory index ``goal_id -> list[records]``.
        _max_records_per_goal: Maximum records retained per goal.
        _logger: Structured logger instance.
    """

    def __init__(
        self,
        memory_service: Optional[MemoryService] = None,
        batch_size: int = 10,
        max_records_per_goal: int = 1000,
    ) -> None:
        self._memory = memory_service or MemoryService()
        self._batch: list[tuple[str, dict]] = []
        self._batch_size = batch_size
        self._local_index: dict[str, list[dict]] = {}
        self._max_records_per_goal = max_records_per_goal
        self._logger = get_logger("execution_memory")

    def record(
        self,
        goal_id: str,
        step: str,
        goal: Optional[dict] = None,
        plan: Optional[str] = None,
        task: Optional[dict] = None,
        action: Optional[str] = None,
        output: Any = None,
        error: Optional[str] = None,
        reflection: Optional[str] = None,
    ) -> bool:
        """Persist a single execution step.

        Args:
            goal_id: Identifier of the parent goal.
            step: Human-readable step name (e.g., ``"execute"``).
            goal: Serialized goal dictionary.
            plan: Plan text, if applicable.
            task: Serialized task dictionary.
            action: Action name string.
            output: Result payload.
            error: Error message, if any.
            reflection: Reflection text, if any.

        Returns:
            ``True`` if the record was saved successfully.
        """
        record = {
            "goal_id": goal_id,
            "step": step,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "goal": goal,
            "plan": plan,
            "task": task,
            "action": action,
            "output": self._serialize(output),
            "error": error,
            "reflection": reflection,
        }

        key = f"execution:{goal_id}:{step}:{record['timestamp']}"

        # Add to local index for fast recall
        self._local_index.setdefault(goal_id, []).append(record)

        # Prune oldest records if limit exceeded
        self._prune(goal_id)

        # Queue for persistence
        self._batch.append((key, record))
        if len(self._batch) >= self._batch_size:
            self._flush()

        self._logger.info("execution recorded", goal_id=goal_id, step=step)
        return True

    def recall(self, goal_id: str) -> list[dict]:
        """Retrieve all execution records for a given goal.

        Uses the local index; does not scan the entire ``MemoryService``.

        Args:
            goal_id: Goal identifier.

        Returns:
            List of execution records sorted by timestamp.
        """
        records = self._local_index.get(goal_id, [])
        return sorted(records, key=lambda r: r.get("timestamp", ""))

    def recall_latest(self, goal_id: str) -> Optional[dict]:
        """Return the most recent execution record for a goal.

        Args:
            goal_id: Goal identifier.

        Returns:
            The latest record, or ``None`` if none exist.
        """
        records = self.recall(goal_id)
        return records[-1] if records else None

    def flush(self) -> bool:
        """Flush all pending records to ``MemoryService``.

        Returns:
            ``True`` if all records were persisted.
        """
        return self._flush()

    def _flush(self) -> bool:
        """Internal flush implementation."""
        if not self._batch:
            return True

        all_saved = True
        for key, record in self._batch:
            saved = self._memory.remember(key, record)
            if not saved:
                all_saved = False
                self._logger.error("execution flush failed", key=key)

        self._batch.clear()
        return all_saved

    def _prune(self, goal_id: str) -> None:
        """Remove oldest records for a goal when the limit is exceeded.

        Prunes both the local index and the underlying ``MemoryService``.
        """
        records = self._local_index.get(goal_id, [])
        if len(records) <= self._max_records_per_goal:
            return

        to_remove = records[:-self._max_records_per_goal]
        self._local_index[goal_id] = records[-self._max_records_per_goal:]

        for old in to_remove:
            old_key = f"execution:{old['goal_id']}:{old['step']}:{old['timestamp']}"
            self._memory.forget(old_key)

        self._logger.info(
            "pruned old execution records",
            goal_id=goal_id,
            removed=len(to_remove),
            retained=len(self._local_index[goal_id]),
        )

    @staticmethod
    def _serialize(value: Any) -> Any:
        """Attempt to serialize a value for JSON storage.

        Falls back to string representation if serialization fails.
        """
        try:
            json.dumps(value)
            return value
        except (TypeError, ValueError):
            return str(value)
