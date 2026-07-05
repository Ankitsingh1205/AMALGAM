"""Regression tests for Mission 7.1.6 Scheduler Integration.

Covers:
- Sequential execution with FleetManager (force_sequential)
- Distributed execution with WorkPool + FleetManager
- Dependency ordering (gated dispatch)
- Parallel-ready scheduling (multiple independent missions)
- Failure propagation (worker/mission/dependency failure)
- Timeout and graceful shutdown
- Recovery (requeue after worker failure)
- Heartbeat updates
- Result aggregation
- Deterministic execution order
- API stability
"""
from __future__ import annotations

import threading
import time
from unittest.mock import patch

import pytest

from agents.chief_agent import ChiefAgent
from brain.dependency_resolver import DependencyResolver
from brain.fleet_manager import FleetManager
from brain.messaging import Messaging
from brain.mission import (
    Mission,
    MissionEventBus,
    MissionEventType,
    MissionGraph,
    MissionID,
    MissionStatus,
)
from brain.shared_context import SharedContext
from brain.work_pool import WorkPool


def _make_ready_mission(title: str = "M") -> Mission:
    return Mission(id=MissionID.generate(), title=title, status=MissionStatus.READY)


def _make_graph(*missions: Mission) -> MissionGraph:
    graph = MissionGraph()
    for m in missions:
        graph.add_mission(m)
    return graph


def _complete_mission(mission: Mission) -> None:
    """Transition a READY mission through to COMPLETED."""
    mission.transition(MissionStatus.RUNNING)
    mission.transition(MissionStatus.VERIFYING)
    mission.transition(MissionStatus.COMPLETED)


def _fail_mission(mission: Mission) -> None:
    """Transition a READY mission to FAILED."""
    mission.transition(MissionStatus.RUNNING)
    mission.transition(MissionStatus.FAILED)


# ---------------------------------------------------------------------------
# Sequential execution with FleetManager (force_sequential)
# ---------------------------------------------------------------------------


class TestSequentialExecutionWithFleet:
    def test_force_sequential_with_fleet_manager(self):
        """force_sequential=True uses sequential path even with FleetManager."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        graph = _make_graph(_make_ready_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 1, "skipped": 0, "results": {}}):
            result = chief.execute_mission(graph, force_sequential=True)

        assert result["success"] is True
        assert result["executed"] == 1

    def test_sequential_default_without_fleet_manager(self):
        """Without FleetManager, sequential is the default path."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        graph = _make_graph(_make_ready_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 1, "skipped": 0, "results": {}}):
            result = chief.execute_mission(graph)

        assert result["success"] is True

    def test_sequential_reports_errors(self):
        """Sequential path must surface MissionExecutor errors."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        graph = _make_graph(_make_ready_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": False, "executed": 1, "skipped": 0,
                                 "results": {}, "error": "boom"}):
            result = chief.execute_mission(graph)

        assert result["success"] is False
        assert "boom" in result["errors"]


# ---------------------------------------------------------------------------
# Distributed execution — dependency ordering
# ---------------------------------------------------------------------------


class TestDistributedDependencyOrdering:
    def test_chain_dependency_order(self):
        """A -> B -> C: B waits for A, C waits for B."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        a = _make_ready_mission("A")
        b = _make_ready_mission("B")
        c = _make_ready_mission("C")
        graph = _make_graph(a, b, c)
        graph.add_dependency(a, b)
        graph.add_dependency(b, c)

        order: list[str] = []

        def simulate_agent():
            for _ in range(3):
                time.sleep(0.3)
                task = pool.steal_task("agent_1", ["llm"])
                if task is None:
                    continue
                order.append(task["data"].title)
                _complete_mission(task["data"])
                pool.complete_task(task["id"], result={"success": True})

        t = threading.Thread(target=simulate_agent)
        t.start()
        result = chief.execute_mission(graph, timeout=30.0)
        t.join(timeout=5.0)

        assert result["success"] is True
        assert order == ["A", "B", "C"]

    def test_parallel_ready_missions(self):
        """Independent missions are all submitted immediately."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        a = _make_ready_mission("A")
        b = _make_ready_mission("B")
        c = _make_ready_mission("C")
        graph = _make_graph(a, b, c)

        stolen: list[str] = []

        def simulate_agent():
            time.sleep(0.5)
            for _ in range(3):
                task = pool.steal_task("agent_1", ["llm"])
                if task is None:
                    break
                stolen.append(task["data"].title)
                _complete_mission(task["data"])
                pool.complete_task(task["id"], result={"success": True})

        t = threading.Thread(target=simulate_agent)
        t.start()
        result = chief.execute_mission(graph, timeout=30.0)
        t.join(timeout=5.0)

        assert result["success"] is True
        assert len(stolen) == 3
        assert set(stolen) == {"A", "B", "C"}

    def test_blocked_mission_waits(self):
        """A mission with unmet dependencies is NOT submitted."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        a = _make_ready_mission("A")
        b = _make_ready_mission("B")
        graph = _make_graph(a, b)
        graph.add_dependency(a, b)

        def simulate_agent():
            time.sleep(0.5)
            # Only A should be available
            task1 = pool.steal_task("agent_1", ["llm"])
            assert task1 is not None
            assert task1["data"].title == "A"
            # B should NOT be available yet
            task_none = pool.steal_task("agent_1", ["llm"])
            assert task_none is None

            _complete_mission(task1["data"])
            pool.complete_task(task1["id"], result={"success": True})

            time.sleep(0.2)
            # Now B should be available
            task2 = pool.steal_task("agent_1", ["llm"])
            assert task2 is not None
            assert task2["data"].title == "B"
            _complete_mission(task2["data"])
            pool.complete_task(task2["id"], result={"success": True})

        t = threading.Thread(target=simulate_agent)
        t.start()
        result = chief.execute_mission(graph, timeout=30.0)
        t.join(timeout=5.0)

        assert result["success"] is True
        assert a.status == MissionStatus.COMPLETED
        assert b.status == MissionStatus.COMPLETED


# ---------------------------------------------------------------------------
# Failure propagation
# ---------------------------------------------------------------------------


class TestFailurePropagation:
    def test_mission_failure_reports_error(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        m = _make_ready_mission("A")
        m.error = "execution crashed"
        graph = _make_graph(m)

        def simulate_agent():
            time.sleep(0.5)
            task = pool.steal_task("agent_1", ["llm"])
            assert task is not None
            _fail_mission(task["data"])
            task["data"].error = "execution crashed"
            pool.fail_task(task["id"], error="execution crashed")

        t = threading.Thread(target=simulate_agent)
        t.start()
        result = chief.execute_mission(graph, timeout=15.0)
        t.join(timeout=3.0)

        assert result["success"] is False
        assert m.status == MissionStatus.FAILED
        assert "execution crashed" in result["errors"]

    def test_dependency_failure_stops_dependent(self):
        """When A fails, B (which depends on A) is never executed."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        a = _make_ready_mission("A")
        b = _make_ready_mission("B")
        graph = _make_graph(a, b)
        graph.add_dependency(a, b)

        b_was_executed = threading.Event()

        def simulate_agent():
            time.sleep(0.5)
            task = pool.steal_task("agent_1", ["llm"])
            assert task is not None
            assert task["data"].title == "A"
            _fail_mission(task["data"])
            task["data"].error = "A failed"
            pool.fail_task(task["id"], error="A failed")

        t = threading.Thread(target=simulate_agent)
        t.start()
        result = chief.execute_mission(graph, timeout=15.0)
        t.join(timeout=3.0)

        assert result["success"] is False
        assert a.status == MissionStatus.FAILED
        assert b.status == MissionStatus.READY  # never executed
        assert not b_was_executed.is_set()


# ---------------------------------------------------------------------------
# Timeout and graceful shutdown
# ---------------------------------------------------------------------------


class TestTimeoutAndGracefulShutdown:
    def test_timeout_returns_failure(self):
        """When no worker picks up a task, execute_mission times out gracefully."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        m = _make_ready_mission("A")
        graph = _make_graph(m)

        # No simulate_agent — nothing steals the task.
        result = chief.execute_mission(graph, timeout=1.0)

        assert result["success"] is False
        assert "timed out" in result["errors"][0].lower()
        assert result["executed"] == 0

    def test_timeout_does_not_crash(self):
        """Timeout must never raise an exception."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        graph = _make_graph(_make_ready_mission("A"))

        try:
            result = chief.execute_mission(graph, timeout=0.5)
        except Exception as e:
            pytest.fail(f"execute_mission raised {e} on timeout")

        assert result["success"] is False

    def test_zero_subscribers_no_deadlock(self):
        """Distributed path with zero agents must not deadlock — it times out."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        graph = _make_graph(_make_ready_mission("A"), _make_ready_mission("B"))
        result = chief.execute_mission(graph, timeout=0.5)

        assert result["success"] is False
        assert "timed out" in result["errors"][0].lower()


# ---------------------------------------------------------------------------
# Recovery — requeue after worker failure
# ---------------------------------------------------------------------------


class TestRecovery:
    def test_work_pool_requeue(self):
        """A failed task can be requeued and retried."""
        msg = Messaging()
        pool = WorkPool(msg)

        pool.submit_task({"id": "t1", "action": "test"}, "llm")

        # First steal succeeds
        task = pool.steal_task("agent_1", ["llm"])
        assert task is not None
        assert task["id"] == "t1"

        # Requeue (simulating agent death)
        assert pool.requeue_task("t1") is True

        # Second steal retrieves the requeued task
        task2 = pool.steal_task("agent_2", ["llm"])
        assert task2 is not None
        assert task2["id"] == "t1"

    def test_requeue_nonexistent_task(self):
        """Requeuing a task that was never stolen returns False."""
        msg = Messaging()
        pool = WorkPool(msg)

        assert pool.requeue_task("nonexistent") is False


# ---------------------------------------------------------------------------
# Heartbeat updates
# ---------------------------------------------------------------------------


class TestHeartbeatUpdates:
    def test_heartbeat_status_completed_on_success(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        graph = _make_graph(_make_ready_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 1, "skipped": 0, "results": {}}):
            chief.execute_mission(graph, force_sequential=True)

        state = fm.get_agent_state("chief")
        assert state["status"] == "completed"

    def test_heartbeat_status_failed_on_failure(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        graph = _make_graph(_make_ready_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": False, "executed": 1, "skipped": 0,
                                 "results": {}, "error": "fail"}):
            chief.execute_mission(graph, force_sequential=True)

        state = fm.get_agent_state("chief")
        assert state["status"] == "failed"

    def test_heartbeat_load_reset_to_zero(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        graph = _make_graph(
            _make_ready_mission("A"),
            _make_ready_mission("B"),
            _make_ready_mission("C"),
        )

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 3, "skipped": 0, "results": {}}):
            chief.execute_mission(graph, force_sequential=True)

        state = fm.get_agent_state("chief")
        assert state["load"] == 0


# ---------------------------------------------------------------------------
# Result aggregation
# ---------------------------------------------------------------------------


class TestResultAggregation:
    def test_distributed_results_collected(self):
        """Distributed execution collects per-mission results."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        a = _make_ready_mission("A")
        b = _make_ready_mission("B")
        graph = _make_graph(a, b)

        def simulate_agent():
            time.sleep(0.5)
            for _ in range(2):
                task = pool.steal_task("agent_1", ["llm"])
                if task is None:
                    break
                _complete_mission(task["data"])
                pool.complete_task(
                    task["id"],
                    result={"success": True, "mission": task["data"].title},
                )

        t = threading.Thread(target=simulate_agent)
        t.start()
        result = chief.execute_mission(graph, timeout=30.0)
        t.join(timeout=5.0)

        assert result["success"] is True
        assert result["executed"] == 2
        assert len(result["results"]) == 2

    def test_result_keys_always_present(self):
        """Every result dict must have all 5 expected keys."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        graph = _make_graph(_make_ready_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 1, "skipped": 0, "results": {}}):
            result = chief.execute_mission(graph)

        for key in ("success", "results", "executed", "skipped", "errors"):
            assert key in result


# ---------------------------------------------------------------------------
# Deterministic execution
# ---------------------------------------------------------------------------


class TestDeterministicExecution:
    def test_same_graph_same_plan_order(self):
        """Planner produces the same topological order for the same graph."""
        from brain.planner.planner import Planner

        planner = Planner()
        a = _make_ready_mission("A")
        b = _make_ready_mission("B")
        c = _make_ready_mission("C")
        graph = _make_graph(a, b, c)
        graph.add_dependency(a, b)
        graph.add_dependency(b, c)

        plan1 = planner.plan_missions(graph)
        plan2 = planner.plan_missions(graph)

        assert [m.title for m in plan1] == [m.title for m in plan2]

    def test_empty_graph_deterministic(self):
        """Empty graph produces empty plan — deterministically."""
        from brain.planner.planner import Planner

        planner = Planner()
        graph = MissionGraph()

        plan = planner.plan_missions(graph)
        assert plan == []


# ---------------------------------------------------------------------------
# Event bus integration during distributed execution
# ---------------------------------------------------------------------------


class TestEventBusDistributedIntegration:
    def test_event_bus_receives_dispatch_event(self):
        """execute_mission publishes a status_changed event before dispatch."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        bus = MissionEventBus()
        events: list = []
        bus.subscribe(events.append)

        m = _make_ready_mission("A")
        graph = _make_graph(m)

        def simulate_agent():
            time.sleep(0.5)
            task = pool.steal_task("agent_1", ["llm"])
            if task is None:
                return
            _complete_mission(task["data"])
            pool.complete_task(task["id"], result={"success": True})

        t = threading.Thread(target=simulate_agent)
        t.start()
        result = chief.execute_mission(graph, event_bus=bus, timeout=30.0)
        t.join(timeout=5.0)

        assert result["success"] is True
        # At least one status_changed event was published
        status_events = [e for e in events
                         if e.event_type == MissionEventType.MISSION_STATUS_CHANGED]
        assert len(status_events) >= 1

    def test_event_bus_optional_distributed(self):
        """Distributed path works without an event bus."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        m = _make_ready_mission("A")
        graph = _make_graph(m)

        def simulate_agent():
            time.sleep(0.5)
            task = pool.steal_task("agent_1", ["llm"])
            if task is None:
                return
            _complete_mission(task["data"])
            pool.complete_task(task["id"], result={"success": True})

        t = threading.Thread(target=simulate_agent)
        t.start()
        result = chief.execute_mission(graph, event_bus=None, timeout=30.0)
        t.join(timeout=5.0)

        assert result["success"] is True


# ---------------------------------------------------------------------------
# API stability — backward-compatible constructor and method signatures
# ---------------------------------------------------------------------------


class TestAPIStability:
    def test_constructor_accepts_required_args(self):
        """ChiefAgent(pool, resolver) must work without optional args."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)
        assert chief.name == "chief"

    def test_constructor_with_shared_context_and_messaging(self):
        """ChiefAgent(pool, resolver, ctx, msg) must work as before."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        ctx = SharedContext()
        chief = ChiefAgent(pool, resolver, ctx, msg)
        assert chief.name == "chief"
        assert chief._shared is ctx

    def test_execute_mission_returns_dict(self):
        """execute_mission must always return a dict — never None."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        graph = _make_graph(_make_ready_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 1, "skipped": 0, "results": {}}):
            result = chief.execute_mission(graph)

        assert isinstance(result, dict)

    def test_run_method_still_works(self):
        """run(ctx) backward compatibility — WorkPool pipeline unchanged."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        ctx = SharedContext()
        ctx.set("task", "test task")
        chief = ChiefAgent(pool, resolver, ctx, msg)

        def simulate_workers():
            time.sleep(0.1)
            plan_task = pool.steal_task("planner_1", ["planner"])
            assert plan_task is not None
            pool.complete_task(plan_task["id"], result=[{"id": "t1", "depends_on": []}])
            time.sleep(0.1)
            t1 = pool.steal_task("engineer_1", ["llm"])
            assert t1 is not None
            pool.complete_task(t1["id"], result="done")

        t = threading.Thread(target=simulate_workers)
        t.start()
        result = chief.run(ctx)
        t.join(timeout=3.0)

        assert result["success"] is True
