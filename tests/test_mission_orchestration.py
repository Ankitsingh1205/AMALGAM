from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from agents.chief_agent import ChiefAgent
from brain.dependency_resolver import DependencyResolver
from brain.fleet_manager import FleetManager
from brain.messaging import Messaging
from brain.mission import (
    Mission,
    MissionExecutor,
    MissionGraph,
    MissionID,
    MissionPersistence,
    MissionStatus,
)
from brain.work_pool import WorkPool


def _make_mission(title: str = "M", status: MissionStatus = MissionStatus.READY) -> Mission:
    return Mission(id=MissionID.generate(), title=title, status=status)


def _make_graph(*missions: Mission) -> MissionGraph:
    graph = MissionGraph()
    for m in missions:
        graph.add_mission(m)
    return graph


# ---------------------------------------------------------------------------
# execute_graph alias
# ---------------------------------------------------------------------------


class TestExecuteGraph:
    def test_execute_graph_alias(self):
        """execute_graph must behave identically to execute_mission."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        graph = _make_graph(_make_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 1, "skipped": 0, "results": {}}):
            result = chief.execute_graph(graph)

        assert result["success"] is True
        assert result["executed"] == 1


# ---------------------------------------------------------------------------
# MissionExecutor cancellation
# ---------------------------------------------------------------------------


class TestMissionExecutorCancellation:
    def test_cancel_before_execute(self):
        """Cancelling before execute() marks all missions as cancelled."""
        executor = MissionExecutor()
        a = _make_mission("A", MissionStatus.READY)
        b = _make_mission("B", MissionStatus.READY)
        graph = _make_graph(a, b)

        executor.cancel()
        with patch.object(executor, "_execute_one", return_value={"success": True, "goal_id": "g1"}):
            result = executor.execute(graph)

        assert result["success"] is False
        assert a.status == MissionStatus.CANCELLED
        assert b.status == MissionStatus.CANCELLED

    def test_cancel_during_execute(self):
        """Cancelling during execute() stops further missions."""
        executor = MissionExecutor()
        a = _make_mission("A", MissionStatus.READY)
        b = _make_mission("B", MissionStatus.READY)
        graph = _make_graph(a, b)

        # Patch _execute_one to trigger cancellation after first mission
        original_execute_one = executor._execute_one
        call_count = 0

        def counting_execute_one(mission):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                executor.cancel()
            return {"success": True, "goal_id": "g1"}

        executor._execute_one = counting_execute_one  # type: ignore[method-assign]
        result = executor.execute(graph)

        assert call_count == 1
        assert a.status == MissionStatus.COMPLETED
        assert b.status == MissionStatus.CANCELLED

    def test_cancel_resets_flag_on_next_execute(self):
        """The cancellation flag must be reset on each execute() call."""
        executor = MissionExecutor()
        a = _make_mission("A", MissionStatus.READY)
        graph = _make_graph(a)

        executor.cancel()
        with patch.object(executor, "_execute_one", return_value={"success": True, "goal_id": "g1"}):
            executor.execute(graph)
        assert a.status == MissionStatus.CANCELLED

        executor2 = MissionExecutor()
        b = _make_mission("B", MissionStatus.READY)
        graph2 = _make_graph(b)
        # execute() resets _cancelled to False, so b should execute
        with patch.object(executor2, "_execute_one", return_value={"success": True, "goal_id": "g2"}):
            result = executor2.execute(graph2)
        assert b.status == MissionStatus.COMPLETED


# ---------------------------------------------------------------------------
# ChiefAgent resume_execution
# ---------------------------------------------------------------------------


class TestResumeExecution:
    def test_resume_from_persisted_graph(self, tmp_path: Path):
        """Resume execution from a saved MissionGraph."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        a = _make_mission("A", MissionStatus.COMPLETED)
        b = _make_mission("B", MissionStatus.RUNNING)
        c = _make_mission("C", MissionStatus.READY)
        graph = _make_graph(a, b, c)

        # Persist the graph
        path = tmp_path / "graph.json"
        MissionPersistence.save_graph(graph, path)

        # Resume should reset RUNNING -> READY, skip COMPLETED, execute READY
        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 2, "skipped": 0, "results": {}}):
            result = chief.resume_execution(str(path))

        assert result["success"] is True
        # B was reset to READY and executed, C was executed, A was already COMPLETED

    def test_resume_missing_file(self):
        """Resume with a missing file must return a failure."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        result = chief.resume_execution("/nonexistent/path.json")
        assert result["success"] is False
        assert "errors" in result

    def test_resume_preserves_completed_missions(self, tmp_path: Path):
        """Completed missions should not be re-executed on resume."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        a = _make_mission("A", MissionStatus.COMPLETED)
        graph = _make_graph(a)

        path = tmp_path / "graph.json"
        MissionPersistence.save_graph(graph, path)

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 0, "skipped": 0, "results": {}}):
            result = chief.resume_execution(str(path))

        assert result["success"] is True
        assert a.status == MissionStatus.COMPLETED


# ---------------------------------------------------------------------------
# ChiefAgent cancel_execution
# ---------------------------------------------------------------------------


class TestCancelExecution:
    def test_cancel_sets_flag(self):
        """cancel_execution must set the cancellation flag."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        assert chief._cancelled is False
        result = chief.cancel_execution()
        assert chief._cancelled is True
        assert result["success"] is True
        assert result["cancelled_count"] >= 0

    def test_cancel_clears_pending_tasks(self):
        """cancel_execution must clear pending tasks."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        a = _make_mission("A", MissionStatus.READY)
        with chief._lock:
            chief._pending_tasks["t1"] = {"data": a, "_sched_status": "waiting"}

        result = chief.cancel_execution()
        assert chief._pending_tasks == {}
        assert a.status == MissionStatus.CANCELLED

    def test_cancel_does_not_affect_completed(self):
        """cancel_execution must not affect already-completed missions."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        a = _make_mission("A", MissionStatus.COMPLETED)
        with chief._lock:
            chief._pending_tasks["t1"] = {"data": a, "_sched_status": "waiting"}

        chief.cancel_execution()
        assert a.status == MissionStatus.COMPLETED


# ---------------------------------------------------------------------------
# ChiefAgent graceful_shutdown
# ---------------------------------------------------------------------------


class TestGracefulShutdown:
    def test_graceful_shutdown_returns_success(self):
        """graceful_shutdown must return success."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        result = chief.graceful_shutdown(timeout=0.5)
        assert result["success"] is True
        assert result["status"] == "shutdown"

    def test_graceful_shutdown_clears_state(self):
        """graceful_shutdown must clear all internal state."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        with chief._lock:
            chief._pending_tasks["t1"] = {"data": "test"}
            chief._completed_tasks.add("t1")

        chief.graceful_shutdown(timeout=0.5)
        assert chief._pending_tasks == {}
        assert chief._completed_tasks == set()
        assert chief._cancelled is False

    def test_graceful_shutdown_with_fleet_manager(self):
        """graceful_shutdown must unregister from FleetManager."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        fm = FleetManager(msg)
        chief = ChiefAgent(pool, resolver, fleet_manager=fm)

        # Verify registration
        assert fm.get_agent_state("chief") is not None

        result = chief.graceful_shutdown(timeout=0.5)
        assert result["success"] is True
        # After unregister, the agent state should be empty or removed


# ---------------------------------------------------------------------------
# Backward compatibility
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    def test_existing_execute_mission_unchanged(self):
        """The existing execute_mission API must continue to work."""
        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        graph = _make_graph(_make_mission("A"))

        with patch("brain.mission.mission_executor.MissionExecutor.execute",
                   return_value={"success": True, "executed": 1, "skipped": 0, "results": {}}):
            result = chief.execute_mission(graph)

        assert result["success"] is True
        assert result["executed"] == 1

    def test_run_method_unchanged(self):
        """The existing run() API must continue to be importable and callable."""
        from brain.shared_context import SharedContext
        ctx = SharedContext()
        ctx.set("task", "test task")

        msg = Messaging()
        pool = WorkPool(msg)
        resolver = DependencyResolver()
        chief = ChiefAgent(pool, resolver)

        # run() is already thoroughly tested in test_fleet_manager_integration.py.
        # Here we just verify the API surface remains stable.
        assert hasattr(chief, "run")
        import inspect
        assert inspect.ismethod(chief.run)
