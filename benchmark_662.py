#!/usr/bin/env python3
"""Mission 6.6.2 — Adaptive Layer Benchmark."""

import time
import uuid
import threading
import sys
from collections import deque
from unittest.mock import MagicMock

# Mock logger to avoid console spam
mock_logger = MagicMock()
for _lvl in ("info", "debug", "error", "warning", "warn", "critical"):
    setattr(mock_logger, _lvl, MagicMock())

import types as _types
_mock_logger_mod = _types.ModuleType("services.logger")
_mock_logger_mod.get_logger = lambda name: mock_logger
sys.modules["services.logger"] = _mock_logger_mod

from brain.dependency_resolver import DependencyResolver
from brain.fleet_manager import FleetManager
from brain.work_pool import WorkPool
from brain.knowledge_router import KnowledgeRouter
from brain.capability_router import CapabilityRouter
from brain.shared_context import SharedContext
from brain.messaging import Messaging, Message

SEP = "=" * 68

def bench(label: str, fn, iterations: int = 10_000) -> float:
    start = time.perf_counter()
    for _ in range(iterations):
        fn()
    elapsed = time.perf_counter() - start
    ops = iterations / elapsed
    us = elapsed / iterations * 1_000_000
    print(f"  {label:<50} {ops:>10,.0f} ops/s  ({us:.2f} µs/op)")
    return ops

print(SEP)
print("Mission 6.6.2  |  Adaptive Layer Benchmark")
print(SEP)

# 1. DependencyResolver
print("\n[1] DependencyResolver")
resolver = DependencyResolver()
tasks = []
for i in range(100):
    tasks.append({"id": f"t{i}", "depends_on": [f"t{i-1}"] if i > 0 else []})

bench("resolve() 100-node linear DAG", lambda: resolver.resolve(tasks), iterations=1_000)

# 2. FleetManager
print("\n[2] FleetManager")
msg = Messaging()
fm = FleetManager(msg)
fm.register("agent1", ["files", "llm"])
bench("report_health()", lambda: fm.report_health("agent1", {"load": 5}))
bench("get_fleet_state()", lambda: fm.get_fleet_state())

# 3. WorkPool
print("\n[3] WorkPool")
wp_msg = Messaging()
wp = WorkPool(wp_msg)
wp_msg.subscribe("*", lambda m: None)

def _submit_steal_cycle():
    tid = wp.submit_task({"action": "x"}, "files")
    wp.steal_task("a", ["files"])
    wp.complete_task(tid)

bench("submit + steal + complete", _submit_steal_cycle, iterations=5_000)

def _concurrent_work_pool():
    def _worker():
        for _ in range(1000):
            wp.submit_task({"action": "x"}, "parallel")
            tid = wp.steal_task("a", ["parallel"])
            if tid:
                wp.complete_task(tid["id"])
    threads = [threading.Thread(target=_worker) for _ in range(4)]
    t0 = time.perf_counter()
    for t in threads: t.start()
    for t in threads: t.join()
    t_elapsed = time.perf_counter() - t0
    ops = 4000 / t_elapsed
    print(f"  {'concurrent WorkPool (4 threads x 1000 ops)':<50} {ops:>10,.0f} ops/s")

_concurrent_work_pool()

# 4. KnowledgeRouter
print("\n[4] KnowledgeRouter")
ctx = SharedContext()
kr = KnowledgeRouter(ctx)
for i in range(50):
    kr.publish(f"topic_{i}", {"data": i})
kr.subscribe("agent_test", "topic_42")
kr.subscribe("agent_test", "topic_7")

bench("get_context() filtered snapshot", lambda: kr.get_context("agent_test"), iterations=50_000)

# 5. CapabilityRouter (Extended)
print("\n[5] CapabilityRouter (Dynamic)")
cr = CapabilityRouter()
fm_cr = FleetManager(Messaging())
for i in range(20):
    fm_cr.register(f"agent{i}", ["knowledge"])
    fm_cr.report_health(f"agent{i}", {"load": i % 5, "consecutive_failures": 0})

bench("route() load-aware over 20 agents", lambda: cr.route({"data": "class architecture"}, fleet_manager=fm_cr), iterations=10_000)

print(f"\n{SEP}")
print("Benchmark complete.")
print(SEP)
