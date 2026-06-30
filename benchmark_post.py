#!/usr/bin/env python3
"""Quick post-optimization benchmark — core components only."""

import time

# Silence the custom logger by pre-injecting a mock
import sys
from unittest.mock import MagicMock

mock_logger = MagicMock()
for level in ("info", "debug", "error", "warning", "warn", "critical"):
    setattr(mock_logger, level, MagicMock())

import types
mock_logger_mod = types.ModuleType("services.logger")
mock_logger_mod.get_logger = lambda name: mock_logger
sys.modules["services.logger"] = mock_logger_mod

from brain.goal.goal import Goal
from brain.queue.task_queue import TaskQueue
from brain.reflection.reflection_engine import ReflectionEngine
from brain.memory.execution_memory import ExecutionMemory
from config import constants


def benchmark(name, fn, iterations=1000):
    start = time.perf_counter()
    for _ in range(iterations):
        fn()
    elapsed = time.perf_counter() - start
    ops_per_sec = iterations / elapsed
    print(f"{name}: {elapsed:.4f}s ({ops_per_sec:.0f} ops/sec)")
    return elapsed


def main():
    print("=" * 60)
    print("Mission 6.4.2 | Post-Optimization Benchmark")
    print("=" * 60)

    # 1. Goal transitions
    def run_transitions():
        g = Goal(id="g1", description="test", priority=1)
        g.transition(constants.GOAL_STATUS_NEW)
        g.transition(constants.GOAL_STATUS_ANALYZING)
        g.transition(constants.GOAL_STATUS_PLANNING)
        g.transition(constants.GOAL_STATUS_READY)
        g.transition(constants.GOAL_STATUS_RUNNING)
        g.transition(constants.GOAL_STATUS_VERIFYING)
        g.transition(constants.GOAL_STATUS_COMPLETED)

    benchmark("Goal transitions (full lifecycle)", run_transitions, iterations=5000)

    # 2. TaskQueue operations
    def run_queue_ops():
        q = TaskQueue()
        q.enqueue({"id": "t1", "action": "test"})
        q.dequeue()
        q.complete_current()
        q.progress()

    benchmark("TaskQueue enqueue+dequeue+complete+progress", run_queue_ops, iterations=5000)

    # 3. ReflectionEngine classification
    refl = ReflectionEngine()
    benchmark("ReflectionEngine.classify (missing dep)",
              lambda: refl.reflect(error="No module named 'xxx'"), iterations=10000)
    benchmark("ReflectionEngine.classify (runtime exc)",
              lambda: refl.reflect(error="ValueError: invalid input"), iterations=10000)
    benchmark("ReflectionEngine.classify (unknown)",
              lambda: refl.reflect(error="something weird happened"), iterations=10000)

    # 4. ExecutionMemory batching
    mem = ExecutionMemory(batch_size=5)
    benchmark("ExecutionMemory.record (batched)",
              lambda: mem.record("g1", "test", goal={"id": "g1"}), iterations=5000)
    mem.flush()

    print("=" * 60)
    print("Benchmark complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
