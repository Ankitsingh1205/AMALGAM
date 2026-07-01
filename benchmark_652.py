#!/usr/bin/env python3
"""Mission 6.5.2 — Post-Optimization Benchmark.

Covers:
- SharedContext throughput (single-threaded + concurrent)
- Messaging throughput (direct send, broadcast, subscribe)
- Scheduler pipeline + parallel
- TaskQueue ops (enqueue/dequeue/complete/progress)
- ReflectionEngine classification
- ExecutionMemory record + flush (with mocked MemoryService)
- Router model selection
- IntentAnalyzer classification
- Goal lifecycle

NOTE: MemoryService is mocked to avoid disk I/O during the benchmark.
"""
from __future__ import annotations

import time
import tracemalloc
import threading
import sys
from unittest.mock import MagicMock

# ── Mock everything that would cause disk/network I/O ────────────────────
mock_logger = MagicMock()
for _lvl in ("info", "debug", "error", "warning", "warn", "critical"):
    setattr(mock_logger, _lvl, MagicMock())

import types as _types
_mock_logger_mod = _types.ModuleType("services.logger")
_mock_logger_mod.get_logger = lambda name: mock_logger
sys.modules["services.logger"] = _mock_logger_mod

# Mock MemoryService to avoid disk I/O
_mock_memory_mod = _types.ModuleType("services.memory")


class _FakeMemoryService:
    def __init__(self):
        self.memories = {}
    def remember(self, k, v): self.memories[k] = v; return True
    def recall(self, k): return self.memories.get(k)
    def forget(self, k): self.memories.pop(k, None); return True


_mock_memory_mod.MemoryService = _FakeMemoryService
sys.modules["services.memory"] = _mock_memory_mod

# Now import the actual modules under test
from brain.shared_context import SharedContext
from brain.messaging import Message, Messaging
from brain.agent_registry import AgentRegistry
from brain.scheduler import Scheduler
from brain.queue.task_queue import TaskQueue
from brain.reflection.reflection_engine import ReflectionEngine
from brain.memory.execution_memory import ExecutionMemory
from brain.router import Router
from brain.intent.intent import IntentAnalyzer
from brain.goal.goal import Goal
from config import constants


SEP = "=" * 68


def bench(label: str, fn, iterations: int = 10_000) -> float:
    """Run *fn* for *iterations* and print throughput.  Returns ops/sec."""
    start = time.perf_counter()
    for _ in range(iterations):
        fn()
    elapsed = time.perf_counter() - start
    ops = iterations / elapsed
    us = elapsed / iterations * 1_000_000
    print(f"  {label:<50} {ops:>10,.0f} ops/s  ({us:.2f} µs/op)")
    return ops


def fmt_bytes(b: int) -> str:
    return f"{b / 1024:.1f} KiB"


print(SEP)
print("Mission 6.5.2  |  Post-Optimization Benchmark")
print(SEP)

# ── 1. SharedContext ──────────────────────────────────────────────────────
print("\n[1] SharedContext")
ctx = SharedContext()
bench("set()", lambda: ctx.set("k", "v"))
bench("get()", lambda: ctx.get("k"))
bench("update({3 keys})", lambda: ctx.update({"a": 1, "b": 2, "c": 3}))
bench("snapshot()", lambda: ctx.snapshot())
bench("record(event)", lambda: ctx.record({"op": "test"}))
bench("get_history()", lambda: ctx.get_history())

# Concurrent write stress
errors: list = []

def _ctx_writer():
    for i in range(500):
        ctx.set("counter", i)
        ctx.update({"x": i, "y": i * 2})

threads = [threading.Thread(target=_ctx_writer) for _ in range(8)]
t0 = time.perf_counter()
for t in threads:
    t.start()
for t in threads:
    t.join()
ct = time.perf_counter() - t0
print(f"  {'concurrent write (8 threads x 500 ops)':<50} {8*500/ct:>10,.0f} ops/s")

# ── 2. Messaging ──────────────────────────────────────────────────────────
print("\n[2] Messaging")
bus = Messaging()
msg = Message(sender="a", recipient="b", msg_type="t", payload="data")
bench("send() direct", lambda: bus.send(msg))
bench("receive()", lambda: bus.receive("b"))
bench("has_messages()", lambda: bus.has_messages("b"))
bench("peek()", lambda: bus.peek("b"))

# Broadcast with 10 subscribers
bcast_bus = Messaging()
for i in range(10):
    bcast_bus.send(Message(sender="x", recipient=f"agent{i}", msg_type="ping"))
bcast_msg = Message(sender="x", recipient="*", msg_type="alert", payload="all")
bench("broadcast (*) to 10 agents", lambda: bcast_bus.send(bcast_msg), iterations=1_000)

# Subscribe + handler
sub_bus = Messaging()
sub_bus.subscribe("a1", lambda m: None)
send_msg = Message(sender="x", recipient="a1", msg_type="t")
bench("send() with 1 handler", lambda: sub_bus.send(send_msg))

# ── 3. Scheduler ──────────────────────────────────────────────────────────
print("\n[3] Scheduler")


class _OkAgent:
    def run(self, ctx):
        return {"success": True}


reg = AgentRegistry()
for i in range(4):
    reg.register(f"agent{i}", _OkAgent())
sched = Scheduler(reg)


def _run_pipeline():
    c = SharedContext()
    sched.run_pipeline(["agent0", "agent1", "agent2", "agent3"], c)


def _run_parallel():
    c = SharedContext()
    sched.run_parallel(["agent0", "agent1", "agent2", "agent3"], c)


bench("run_pipeline (4 agents)", _run_pipeline, iterations=500)
bench("run_parallel (4 agents)", _run_parallel, iterations=200)

# ── 4. TaskQueue ──────────────────────────────────────────────────────────
print("\n[4] TaskQueue")
q = TaskQueue()


def _queue_cycle():
    q.enqueue({"id": "t1", "action": "x"})
    q.dequeue()
    q.complete_current(result="ok")


bench("enqueue+dequeue+complete", _queue_cycle)
bench("progress() (O(1))", lambda: q.progress())
bench("list_history()", lambda: q.list_history())

# ── 5. ReflectionEngine ───────────────────────────────────────────────────
print("\n[5] ReflectionEngine")
engine = ReflectionEngine()
bench("reflect (missing dep)", lambda: engine.reflect(error="No module named 'foo'"))
bench("reflect (runtime exc)", lambda: engine.reflect(error="ValueError: bad input"))
bench("reflect (unknown)", lambda: engine.reflect(error="something weird"))

# ── 6. ExecutionMemory (mocked MemoryService — no disk I/O) ──────────────
print("\n[6] ExecutionMemory (mocked)")
mem = ExecutionMemory(batch_size=50)


def _em_record():
    mem.record("g1", "step", goal={"id": "g1"})


bench("record (batch_size=50)", _em_record, iterations=5_000)
mem.flush()

tracemalloc.start()
mem2 = ExecutionMemory(batch_size=100)
for i in range(500):
    mem2.record("g1", f"step{i}", goal={"id": "g1"})
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"  {'Memory peak (500 records)':<50} {fmt_bytes(peak):>14}")
print(f"  {'Memory current':<50} {fmt_bytes(current):>14}")

# ── 7. Router + Intent ────────────────────────────────────────────────────
print("\n[7] Router & IntentAnalyzer")
router = Router()
bench("Router.choose_model (coding path)", lambda: router.choose_model("write python code for me"))
bench("Router.choose_model (general path)", lambda: router.choose_model("what is the weather"))

ia = IntentAnalyzer()
bench("IntentAnalyzer.detect (math)", lambda: ia.detect("2 + 2"))
bench("IntentAnalyzer.detect (remember)", lambda: ia.detect("remember key=value"))
bench("IntentAnalyzer.detect (search)", lambda: ia.detect("search web for python tips"))
bench("IntentAnalyzer.detect (general)", lambda: ia.detect("tell me a joke"))

# ── 8. Goal lifecycle ─────────────────────────────────────────────────────
print("\n[8] Goal lifecycle")


def _goal_lifecycle():
    g = Goal(id="g1", description="test", priority=1)
    g.transition(constants.GOAL_STATUS_NEW)
    g.transition(constants.GOAL_STATUS_ANALYZING)
    g.transition(constants.GOAL_STATUS_PLANNING)
    g.transition(constants.GOAL_STATUS_READY)
    g.transition(constants.GOAL_STATUS_RUNNING)
    g.transition(constants.GOAL_STATUS_VERIFYING)
    g.transition(constants.GOAL_STATUS_COMPLETED)


bench("Goal full lifecycle (7 transitions)", _goal_lifecycle, iterations=5_000)
bench(
    "Goal.is_terminal()",
    lambda: Goal(
        id="x", description="y", status=constants.GOAL_STATUS_COMPLETED
    ).is_terminal(),
    iterations=50_000,
)

print(f"\n{SEP}")
print("Benchmark complete.")
print(SEP)
