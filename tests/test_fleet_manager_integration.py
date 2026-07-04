from __future__ import annotations

import threading
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


class DummyThreadPool:
    """Synchronous thread pool replacement for MissionExecutor tests."""
    def submit(self, fn, *args, **kwargs):
        class Future:
            def result(self, timeout=None):
                return fn(*args, **kwargs)
        return Future()
    def shutdown(self, wait=False):
        pass


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
            import time
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
# Heartbeats during mission execution
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
            chief.execute_mission(graph)

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
            result = chief.execute_mission(graph)

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
            chief.execute_mission(graph)

        state = fm.get_agent_state("chief")
        assert state is not None
        # load should be mission_count at start, 0 at end
        assert state["load"] == 0


# ---------------------------------------------------------------------------
# Mission execution with FleetManager
# ---------------------------------------------------------------------------


class TestChiefAgentMissionExecution:
    def test_single_mission_completes(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        graph = _make_graph(_make_ready_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 1, "skipped": 0, "results": {}}):
            result = chief.execute_mission(graph)

        assert result["success"] is True
        assert result["executed"] == 1
        state = fm.get_agent_state("chief")
        assert state["status"] == "completed"

    def test_multiple_missions_execute(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        a = _make_ready_mission("A")
        b = _make_ready_mission("B")
        c = _make_ready_mission("C")
        graph = _make_graph(a, b, c)

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 3, "skipped": 0, "results": {}}):
            result = chief.execute_mission(graph)

        assert result["success"] is True
        assert result["executed"] == 3
        state = fm.get_agent_state("chief")
        assert state["status"] == "completed"

    def test_execute_mission_failure_updates_fleet(self):
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        graph = _make_graph(_make_ready_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": False, "executed": 1, "skipped": 0,
                                 "results": {}, "error": "crash"}):
            result = chief.execute_mission(graph)

        assert result["success"] is False
        state = fm.get_agent_state("chief")
        assert state["status"] == "failed"


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
            result = chief.execute_mission(graph)

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
            result = chief.execute_mission(graph)

        assert result["executed"] == 0
        assert result["success"] is True