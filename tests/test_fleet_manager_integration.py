from __future__ import annotations

import threading
import time
from unittest.mock import patch

import pytest

from agents.chief_agent import ChiefAgent
from brain.dependency_resolver import DependencyResolver
from brain.fleet_manager import FleetManager
from brain.messaging import Messaging
from brain.mission import Mission, MissionGraph, MissionID, MissionStatus
from brain.shared_context import SharedContext
from brain.work_pool import WorkPool


def _make_ready_mission(title: str = "M") -> Mission:
    return Mission(id=MissionID.generate(), title=title, status=MissionStatus.READY)


def _make_graph(*missions: Mission) -> MissionGraph:
    graph = MissionGraph()
    for m in missions:
        graph.add_mission(m)
    return graph


# ---------------------------------------------------------------------------
# Backward compatibility — existing run() unchanged
# ---------------------------------------------------------------------------


class TestChiefAgentBackwardCompatibility:
    def test_existing_run_unchanged(self):
        """run() must work exactly as before without FleetManager."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        ctx = SharedContext()
        ctx.set("task", "build website")

        chief = ChiefAgent(pool, resolver, ctx, msg)

        def simulate_workers():
            time.sleep(0.1)
            plan_task = pool.steal_task("planner_1", ["planner"])
            assert plan_task is not None
            assert plan_task["action"] == "plan"
            sub_tasks = [
                {"id": "t1", "depends_on": []},
            ]
            pool.complete_task(plan_task["id"], result=sub_tasks)
            time.sleep(0.1)
            t1 = pool.steal_task("engineer_1", ["llm"])
            assert t1 is not None
            pool.complete_task(t1["id"], result="done")

        worker_thread = threading.Thread(target=simulate_workers)
        worker_thread.start()
        result = chief.run(ctx)
        worker_thread.join(timeout=2.0)
        assert result["success"] is True

    def test_constructor_without_fleet_manager(self):
        """ChiefAgent must construct without FleetManager (backward compat)."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)
        assert chief._fleet_manager is None


# ---------------------------------------------------------------------------
# FleetManager registration
# ---------------------------------------------------------------------------


class TestChiefAgentFleetRegistration:
    def test_registers_with_fleet_manager_on_init(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        state = fm.get_agent_state("chief")
        assert state is not None
        assert "planning" in state["capabilities"]
        assert "orchestration" in state["capabilities"]
        assert state["status"] == "idle"

    def test_fleet_manager_optional(self):
        """FleetManager must be optional - no crash when not provided."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)
        assert chief._fleet_manager is None
        # Should not raise
        chief._send_heartbeat(status="test", load=0)


# ---------------------------------------------------------------------------
# Sequential fallback (no FleetManager)
# ---------------------------------------------------------------------------


class TestChiefAgentSequentialFallback:
    def test_execute_mission_without_fleet_manager(self):
        """Without FleetManager, execute_mission must use sequential path."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        # No fleet_manager
        chief = ChiefAgent(pool, resolver)

        graph = _make_graph(_make_ready_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 1, "skipped": 0, "results": {}}):
            result = chief.execute_mission(graph)

        assert result["success"] is True
        assert result["executed"] == 1

    def test_execute_mission_failure_sequential(self):
        """Sequential path must report failures correctly."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        graph = _make_graph(_make_ready_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": False, "executed": 1, "skipped": 0,
                                 "results": {}, "error": "crash"}):
            result = chief.execute_mission(graph)

        assert result["success"] is False
        assert "crash" in result["errors"]


# ---------------------------------------------------------------------------
# Distributed execution with FleetManager
# ---------------------------------------------------------------------------


class TestChiefAgentDistributedExecution:
    def test_distributed_single_mission(self):
        """A single mission is dispatched to WorkPool and completed by an agent."""
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
            assert task is not None, "No task available — race condition"
            assert task["action"] == "execute_mission"
            # Simulate execution: mark mission completed
            mission = task["data"]
            mission.transition(MissionStatus.RUNNING)
            mission.transition(MissionStatus.VERIFYING)
            mission.transition(MissionStatus.COMPLETED)
            pool.complete_task(task["id"], result={"success": True})

        t = threading.Thread(target=simulate_agent)
        t.start()
        result = chief.execute_mission(graph)
        t.join(timeout=2.0)

        assert result["success"] is True
        assert result["executed"] == 1
        assert m.status == MissionStatus.COMPLETED

    def test_distributed_dependency_ordering(self):
        """Missions with dependencies are gated until prerequisites complete."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        a = _make_ready_mission("A")
        b = _make_ready_mission("B")
        graph = _make_graph(a, b)
        graph.add_dependency(a, b)

        execution_order: list[str] = []

        def simulate_agent():
            time.sleep(0.5)
            # Only A should be available initially
            task1 = pool.steal_task("agent_1", ["llm"])
            assert task1 is not None, "No task1 available — race condition"
            execution_order.append(task1["data"].title)
            task1["data"].transition(MissionStatus.RUNNING)
            task1["data"].transition(MissionStatus.VERIFYING)
            task1["data"].transition(MissionStatus.COMPLETED)
            pool.complete_task(task1["id"], result={"success": True})

            time.sleep(0.1)
            # Now B should be available
            task2 = pool.steal_task("agent_1", ["llm"])
            assert task2 is not None, "No task2 available — dependency gate failed"
            execution_order.append(task2["data"].title)
            task2["data"].transition(MissionStatus.RUNNING)
            task2["data"].transition(MissionStatus.VERIFYING)
            task2["data"].transition(MissionStatus.COMPLETED)
            pool.complete_task(task2["id"], result={"success": True})

        t = threading.Thread(target=simulate_agent)
        t.start()
        result = chief.execute_mission(graph)
        t.join(timeout=2.0)

        assert result["success"] is True
        assert execution_order == ["A", "B"]
        assert a.status == MissionStatus.COMPLETED
        assert b.status == MissionStatus.COMPLETED

    def test_distributed_failure_handling(self):
        """When a mission fails, execution reports failure."""
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
            assert task is not None, "No task available — race condition"
            mission = task["data"]
            mission.transition(MissionStatus.RUNNING)
            mission.transition(MissionStatus.FAILED)
            pool.fail_task(task["id"], error="execution failed")

        t = threading.Thread(target=simulate_agent)
        t.start()
        result = chief.execute_mission(graph)
        t.join(timeout=2.0)

        assert result["success"] is False
        assert m.status == MissionStatus.FAILED

    def test_distributed_multiple_missions(self):
        """Multiple independent missions are all executed."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        a = _make_ready_mission("A")
        b = _make_ready_mission("B")
        c = _make_ready_mission("C")
        graph = _make_graph(a, b, c)

        completed: set[str] = set()

        def simulate_agent():
            for _ in range(3):
                time.sleep(0.1)
                task = pool.steal_task("agent_1", ["llm"])
                if task is None:
                    break
                mission = task["data"]
                mission.transition(MissionStatus.RUNNING)
                mission.transition(MissionStatus.VERIFYING)
                mission.transition(MissionStatus.COMPLETED)
                completed.add(mission.title)
                pool.complete_task(task["id"], result={"success": True})

        t = threading.Thread(target=simulate_agent)
        t.start()
        result = chief.execute_mission(graph)
        t.join(timeout=2.0)

        assert result["success"] is True
        assert completed == {"A", "B", "C"}


# ---------------------------------------------------------------------------
# Heartbeats during mission execution (via sequential path with FleetManager)
# ---------------------------------------------------------------------------


class TestChiefAgentHeartbeats:
    def test_heartbeat_on_execute_mission_start(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        graph = _make_graph(_make_ready_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 1, "skipped": 0, "results": {}}):
            chief.execute_mission(graph, force_sequential=True)

        # Check that heartbeats were sent
        state = fm.get_agent_state("chief")
        assert state is not None
        assert state["status"] == "completed"
        assert state["load"] == 0

    def test_heartbeat_on_execute_mission_failure(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        graph = _make_graph(_make_ready_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": False, "executed": 1, "skipped": 0,
                                 "results": {}, "error": "Task failed"}):
            result = chief.execute_mission(graph, force_sequential=True)

        assert result["success"] is False
        state = fm.get_agent_state("chief")
        assert state is not None
        assert state["status"] == "failed"

    def test_heartbeat_includes_mission_count_as_load(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        graph = _make_graph(_make_ready_mission("A"), _make_ready_mission("B"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 2, "skipped": 0, "results": {}}):
            chief.execute_mission(graph, force_sequential=True)

        state = fm.get_agent_state("chief")
        assert state is not None
        # load should be mission_count at start, 0 at end
        assert state["load"] == 0


# ---------------------------------------------------------------------------
# Reaping compatibility
# ---------------------------------------------------------------------------


class TestFleetManagerReaping:
    def test_reap_removes_stale_chief_agent(self):
        import time
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        # Manually age the agent
        with fm._lock:
            fm._agents["chief"]["last_seen"] = time.time() - 100

        dead = fm.reap_dead_agents(timeout_seconds=30.0)
        assert "chief" in dead
        assert fm.get_agent_state("chief") == {}

    def test_active_chief_not_reaped(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        dead = fm.reap_dead_agents(timeout_seconds=30.0)
        assert "chief" not in dead
        assert fm.get_agent_state("chief") != {}


# ---------------------------------------------------------------------------
# Result structure and API stability
# ---------------------------------------------------------------------------


class TestExecuteMissionResultStructure:
    def test_result_contains_all_expected_keys(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        graph = _make_graph(_make_ready_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 1, "skipped": 0, "results": {}}):
            result = chief.execute_mission(graph, force_sequential=True)

        for key in ("success", "results", "executed", "skipped", "errors"):
            assert key in result, f"Missing key: {key}"

    def test_empty_graph_returns_no_executed(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        graph = MissionGraph()

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 0, "skipped": 0, "results": {}}):
            result = chief.execute_mission(graph, force_sequential=True)

        assert result["executed"] == 0
        assert result["success"] is True


# ---------------------------------------------------------------------------
# Mission 7.3 — Heartbeat lifecycle for all ChiefAgent orchestration paths
# ---------------------------------------------------------------------------


class TestChiefAgentRunHeartbeats:
    def test_heartbeat_on_run_start_and_complete(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        ctx = SharedContext()
        ctx.set("task", "run heartbeat test")

        def simulate_workers():
            time.sleep(0.1)
            plan_task = pool.steal_task("planner_1", ["planner"])
            assert plan_task is not None
            sub_tasks = [{"id": "t1", "depends_on": []}]
            pool.complete_task(plan_task["id"], result=sub_tasks)
            time.sleep(0.1)
            t1 = pool.steal_task("engineer_1", ["llm"])
            assert t1 is not None
            pool.complete_task(t1["id"], result="done")

        worker_thread = threading.Thread(target=simulate_workers)
        worker_thread.start()
        result = chief.run(ctx)
        worker_thread.join(timeout=2.0)

        assert result["success"] is True

        # FleetManager should have received running and completed heartbeats
        state = fm.get_agent_state("chief")
        assert state is not None
        # Terminal status should be completed
        assert state["status"] == "completed"
        assert state["load"] == 0


class TestChiefAgentCancelExecutionHeartbeats:
    def test_heartbeat_on_cancel_execution(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        # Submit a dummy mission to create pending state
        graph = _make_graph(_make_ready_mission("A"))

        def simulate_agent():
            time.sleep(0.5)
            task = pool.steal_task("agent_1", ["llm"])
            assert task is not None
            mission = task["data"]
            mission.transition(MissionStatus.RUNNING)
            mission.transition(MissionStatus.VERIFYING)
            mission.transition(MissionStatus.COMPLETED)
            pool.complete_task(task["id"], result={"success": True})

        t = threading.Thread(target=simulate_agent)
        t.start()

        # Wait for task to be submitted
        time.sleep(0.2)

        # Cancel while execution is in progress
        cancel_result = chief.cancel_execution()

        t.join(timeout=2.0)

        assert cancel_result["success"] is True
        assert cancel_result["cancelled_count"] >= 0

        # FleetManager should have received cancelled heartbeat
        state = fm.get_agent_state("chief")
        assert state is not None
        # Terminal status should be cancelled
        assert state["status"] == "cancelled"
        assert state["load"] == 0
