"""Benchmark for Mission 6.4.2 optimization sprint.

Measures boot time, goal execution, queue ops, and memory usage.
Run before and after optimization. Save results for comparison.
"""
from __future__ import annotations

import time
import tracemalloc

from brain.executor.autonomous_executor import AutonomousExecutor
from brain.goal.goal import Goal
from brain.queue.task_queue import TaskQueue
from brain.evaluator.evaluator import Evaluator
from brain.reflection.reflection_engine import ReflectionEngine
from brain.retry.retry_manager import RetryManager
from brain.memory.execution_memory import ExecutionMemory
from config import constants


def fmt_us(t: float) -> str:
    return f"{t * 1_000_000:.1f} µs"


def fmt_bytes(b: int) -> str:
    return f"{b / 1024:.1f} KiB"


# ── 1. Boot time ──
start = time.perf_counter()
for _ in range(100):
    executor = AutonomousExecutor()
boot_time = (time.perf_counter() - start) / 100


# ── 2. Goal execution time (success) ──
class FakeKernel:
    def execute(self, task):
        return getattr(task, "data", None)


executor = AutonomousExecutor(kernel_executor=FakeKernel())
start = time.perf_counter()
for _ in range(50):
    goal = executor.run("2 + 2")
exec_success = (time.perf_counter() - start) / 50


# ── 3. Goal execution time (failure + retry) ──
class FakeFailingThenSuccess:
    def __init__(self):
        self.calls = 0

    def execute(self, task):
        self.calls += 1
        if self.calls % 2 == 1:
            raise RuntimeError("fail")
        return "ok"


executor = AutonomousExecutor(kernel_executor=FakeFailingThenSuccess())
start = time.perf_counter()
for _ in range(20):
    goal = executor.run("2 + 2")
exec_retry = (time.perf_counter() - start) / 20


# ── 4. Queue performance ──
q = TaskQueue()
start = time.perf_counter()
for i in range(1000):
    q.enqueue({"id": f"t{i}", "plan_version": 0})
    t = q.dequeue()
    q.complete_current(result="ok")
queue_ops = (time.perf_counter() - start) / 1000


# ── 5. Reflection engine classification ──
engine = ReflectionEngine()
start = time.perf_counter()
for _ in range(10000):
    engine.reflect(error="ValueError: bad input")
reflect_time = (time.perf_counter() - start) / 10000


# ── 6. Execution memory recording ──
mem = ExecutionMemory()
mem._memory.memories = {}
start = time.perf_counter()
for i in range(500):
    mem.record("g1", f"step{i}")
mem_time = (time.perf_counter() - start) / 500


# ── 7. Memory allocations during execution memory ──
tracemalloc.start()
mem2 = ExecutionMemory()
mem2._memory.memories = {}
for i in range(200):
    mem2.record("g1", f"step{i}")
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()


print("=" * 60)
print("AMALGAM Mission 6.4.2 Benchmark (Pre-Optimization)")
print("=" * 60)
print(f"Boot time (100x)        : {fmt_us(boot_time)}")
print(f"Goal exec success (50x)  : {fmt_us(exec_success)}")
print(f"Goal exec retry (20x)    : {fmt_us(exec_retry)}")
print(f"Queue ops (1000x)        : {fmt_us(queue_ops)}")
print(f"Reflect classify (10000x): {fmt_us(reflect_time)}")
print(f"ExecMemory record (500x) : {fmt_us(mem_time)}")
print(f"Memory peak (200 records): {fmt_bytes(peak)}")
print(f"Memory current           : {fmt_bytes(current)}")
print("=" * 60)
