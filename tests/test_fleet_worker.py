"""Tests for brain.fleet_worker (Mission 7.5)."""

import time

from brain.fleet_worker import FleetWorker
from brain.messaging import Messaging
from brain.work_pool import WorkPool


def _wait_for(predicate, timeout=3.0, interval=0.02):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return predicate()


def test_fleet_worker_executes_task_and_completes():
    msg = Messaging()
    pool = WorkPool(msg)
    completed = []
    msg.subscribe("*", lambda m: completed.append(m) if m.msg_type == "task_completed" else None)

    worker = FleetWorker("w1", ["llm"], pool, handler=lambda t: f"done:{t['data']}")
    worker.start()
    try:
        pool.submit_task({"data": "hello"}, "llm")
        assert _wait_for(lambda: len(completed) == 1)
    finally:
        worker.stop()
    assert not worker.running


def test_fleet_worker_reports_handler_failure():
    msg = Messaging()
    pool = WorkPool(msg)
    failed = []
    msg.subscribe("*", lambda m: failed.append(m) if m.msg_type == "task_failed" else None)

    def boom(task):
        raise RuntimeError("kaput")

    worker = FleetWorker("w1", ["llm"], pool, handler=boom)
    worker.start()
    try:
        pool.submit_task({"data": "x"}, "llm")
        assert _wait_for(lambda: len(failed) == 1)
    finally:
        worker.stop()


def test_fleet_worker_ignores_unmatched_capability():
    msg = Messaging()
    pool = WorkPool(msg)
    handled = []

    worker = FleetWorker("w1", ["files"], pool, handler=lambda t: handled.append(t))
    worker.start()
    try:
        pool.submit_task({"data": "x"}, "llm")
        time.sleep(0.2)
        assert handled == []
        # Task still stealable by a matching worker
        assert pool.steal_task("other", ["llm"]) is not None
    finally:
        worker.stop()


def test_fleet_worker_start_is_idempotent():
    msg = Messaging()
    pool = WorkPool(msg)
    worker = FleetWorker("w1", ["llm"], pool, handler=lambda t: None)
    worker.start()
    thread_before = worker._thread
    worker.start()
    assert worker._thread is thread_before
    worker.stop()
