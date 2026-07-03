from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from brain.executor.autonomous_executor import AutonomousExecutor
from brain.mission import (
    Mission,
    MissionEvent,
    MissionEventBus,
    MissionEventType,
    MissionExecutor,
    MissionGraph,
    MissionID,
    MissionStatus,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mission(title: str = "M", status: MissionStatus = MissionStatus.READY) -> Mission:
    return Mission(id=MissionID.generate(), title=title, status=status)


def _mock_run_success(*args, **kwargs):
    """Return a completed goal mock."""
    return MagicMock(status="completed", error="", id="g-success")


def _mock_run_failure(*args, **kwargs):
    """Return a failed goal mock."""
    return MagicMock(status="failed", error="mock failure", id="g-fail")


# ---------------------------------------------------------------------------
# AutonomousExecutor backward compatibility
# ---------------------------------------------------------------------------


class TestAutonomousExecutorBackwardCompatibility:
    def test_run_without_observer(self):
        """AutonomousExecutor must work exactly as before without observer."""
        ae = AutonomousExecutor()
        with patch.object(ae._executor, "submit", return_value=MagicMock(result=lambda *_: "ok")):
            goal = ae.run("Calculate 2+2")
        assert goal.status in {"completed", "failed"}

    def test_run_with_observer(self):
        """AutonomousExecutor must accept an observer and invoke it."""
        recorded: list[str] = []
        ae = AutonomousExecutor()
        with patch.object(ae._executor, "submit", return_value=MagicMock(result=lambda *_: "ok")):
            goal = ae.run("Calculate 2+2", status_observer=recorded.append)
        assert goal.status in {"completed", "failed"}
        assert len(recorded) > 0
        assert "running" in recorded

    def test_observer_exception_isolated(self):
        """Observer exceptions must not break execution."""
        def bad_observer(_):
            raise RuntimeError("boom")

        ae = AutonomousExecutor()
        with patch.object(ae._executor, "submit", return_value=MagicMock(result=lambda *_: "ok")):
            goal = ae.run("Calculate 2+2", status_observer=bad_observer)
        assert goal.status in {"completed", "failed"}


# ---------------------------------------------------------------------------
# MissionExecutor — successful execution
# ---------------------------------------------------------------------------


class TestMissionExecutorSuccess:
    def test_execute_single_mission_success(self):
        graph = MissionGraph()
        m = _make_mission("Math", MissionStatus.READY)
        graph.add_mission(m)
        executor = MissionExecutor()
        with patch.object(executor._executor, "run", side_effect=_mock_run_success):
            result = executor.execute(graph)
        assert result["success"] is True
        assert result["executed"] == 1
        assert m.status == MissionStatus.COMPLETED

    def test_execute_multiple_missions_in_order(self):
        graph = MissionGraph()
        a = _make_mission("A", MissionStatus.READY)
        b = _make_mission("B", MissionStatus.READY)
        c = _make_mission("C", MissionStatus.READY)
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, b)
        graph.add_dependency(b, c)
        executor = MissionExecutor()
        with patch.object(executor._executor, "run", side_effect=_mock_run_success):
            result = executor.execute(graph)
        assert result["success"] is True
        assert result["executed"] == 3
        assert a.status == MissionStatus.COMPLETED
        assert b.status == MissionStatus.COMPLETED
        assert c.status == MissionStatus.COMPLETED

    def test_execute_skips_completed_missions(self):
        graph = MissionGraph()
        a = _make_mission("A", MissionStatus.COMPLETED)
        b = _make_mission("B", MissionStatus.READY)
        graph.add_mission(a)
        graph.add_mission(b)
        executor = MissionExecutor()
        with patch.object(executor._executor, "run", side_effect=_mock_run_success):
            result = executor.execute(graph)
        assert result["success"] is True
        assert result["executed"] == 1
        assert a.status == MissionStatus.COMPLETED
        assert b.status == MissionStatus.COMPLETED

    def test_execute_skips_failed_missions(self):
        graph = MissionGraph()
        a = _make_mission("A", MissionStatus.FAILED)
        b = _make_mission("B", MissionStatus.READY)
        graph.add_mission(a)
        graph.add_mission(b)
        executor = MissionExecutor()
        with patch.object(executor._executor, "run", side_effect=_mock_run_success):
            result = executor.execute(graph)
        assert result["success"] is True
        assert result["executed"] == 1
        assert a.status == MissionStatus.FAILED


# ---------------------------------------------------------------------------
# MissionExecutor — failure handling
# ---------------------------------------------------------------------------


class TestMissionExecutorFailure:
    def test_execute_halt_on_failure(self):
        graph = MissionGraph()
        a = _make_mission("A", MissionStatus.READY)
        b = _make_mission("B", MissionStatus.READY)
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_dependency(a, b)
        executor = MissionExecutor()

        with patch.object(
            executor._executor,
            "run",
            side_effect=[
                MagicMock(status="failed", error="Mock failure", id="g1"),
            ],
        ):
            result = executor.execute(graph, halt_on_failure=True)

        assert result["success"] is False
        assert a.status == MissionStatus.FAILED
        assert a.error == "Mock failure"
        assert b.status == MissionStatus.READY  # never reached

    def test_execute_continue_on_failure(self):
        graph = MissionGraph()
        a = _make_mission("A", MissionStatus.READY)
        b = _make_mission("B", MissionStatus.READY)
        graph.add_mission(a)
        graph.add_mission(b)
        executor = MissionExecutor()

        with patch.object(
            executor._executor,
            "run",
            side_effect=[
                MagicMock(status="failed", error="Mock failure", id="g1"),
                MagicMock(status="completed", error="", id="g2"),
            ],
        ):
            result = executor.execute(graph, halt_on_failure=False)

        assert result["success"] is False
        assert a.status == MissionStatus.FAILED
        assert b.status == MissionStatus.COMPLETED


# ---------------------------------------------------------------------------
# Mission status transitions during execution
# ---------------------------------------------------------------------------


class TestMissionStatusTransitions:
    def test_created_to_completed(self):
        graph = MissionGraph()
        m = _make_mission("M", MissionStatus.CREATED)
        graph.add_mission(m)
        executor = MissionExecutor()
        with patch.object(executor._executor, "run", side_effect=_mock_run_success):
            executor.execute(graph)
        assert m.status == MissionStatus.COMPLETED

    def test_ready_to_completed(self):
        graph = MissionGraph()
        m = _make_mission("M", MissionStatus.READY)
        graph.add_mission(m)
        executor = MissionExecutor()
        with patch.object(executor._executor, "run", side_effect=_mock_run_success):
            executor.execute(graph)
        assert m.status == MissionStatus.COMPLETED

    def test_running_to_completed(self):
        graph = MissionGraph()
        m = _make_mission("M", MissionStatus.RUNNING)
        graph.add_mission(m)
        executor = MissionExecutor()
        with patch.object(executor._executor, "run", side_effect=_mock_run_success):
            executor.execute(graph)
        assert m.status == MissionStatus.COMPLETED

    def test_verify_state_reached(self):
        """Mission must pass through VERIFYING before COMPLETED."""
        graph = MissionGraph()
        m = _make_mission("M", MissionStatus.READY)
        graph.add_mission(m)
        executor = MissionExecutor()

        transitions: list[MissionStatus] = []
        original_transition = m.transition

        def tracking_transition(new_status):
            transitions.append(new_status)
            original_transition(new_status)

        m.transition = tracking_transition  # type: ignore[method-assign]
        with patch.object(executor._executor, "run", side_effect=_mock_run_success):
            executor.execute(graph)

        assert MissionStatus.VERIFYING in transitions
        assert m.status == MissionStatus.COMPLETED

    def test_failed_state(self):
        graph = MissionGraph()
        m = _make_mission("M", MissionStatus.READY)
        graph.add_mission(m)
        executor = MissionExecutor()

        with patch.object(
            executor._executor,
            "run",
            return_value=MagicMock(status="failed", error="fail", id="g1"),
        ):
            executor.execute(graph)

        assert m.status == MissionStatus.FAILED
        assert m.error == "fail"


# ---------------------------------------------------------------------------
# RECOVERING state
# ---------------------------------------------------------------------------


class TestMissionRecoveringState:
    def test_mission_can_transition_to_recovering(self):
        m = _make_mission("M", MissionStatus.RUNNING)
        m.transition(MissionStatus.RECOVERING)
        assert m.status == MissionStatus.RECOVERING

    def test_mission_can_transition_from_recovering_to_ready(self):
        m = _make_mission("M", MissionStatus.RECOVERING)
        m.transition(MissionStatus.READY)
        assert m.status == MissionStatus.READY

    def test_mission_can_transition_from_recovering_to_running(self):
        m = _make_mission("M", MissionStatus.RECOVERING)
        m.transition(MissionStatus.RUNNING)
        assert m.status == MissionStatus.RUNNING

    def test_mission_can_transition_from_recovering_to_failed(self):
        m = _make_mission("M", MissionStatus.RECOVERING)
        m.transition(MissionStatus.FAILED)
        assert m.status == MissionStatus.FAILED


# ---------------------------------------------------------------------------
# Event emission
# ---------------------------------------------------------------------------


class TestMissionEventEmission:
    def test_transition_emits_status_changed_event(self):
        bus = MissionEventBus()
        events: list[MissionEvent] = []
        bus.subscribe(events.append)

        m = Mission(id=MissionID.generate(), title="M", event_bus=bus)
        m.transition(MissionStatus.ANALYZING)

        status_changes = [e for e in events if e.event_type == MissionEventType.MISSION_STATUS_CHANGED]
        assert len(status_changes) == 1
        assert status_changes[0].payload["old_status"] == "created"
        assert status_changes[0].payload["new_status"] == "analyzing"

    def test_transition_emits_completed_event(self):
        bus = MissionEventBus()
        events: list[MissionEvent] = []
        bus.subscribe(lambda e: events.append(e) if e.event_type == MissionEventType.MISSION_COMPLETED else None)

        m = Mission(id=MissionID.generate(), title="M", event_bus=bus)
        m.transition(MissionStatus.ANALYZING)
        m.transition(MissionStatus.PLANNING)
        m.transition(MissionStatus.READY)
        m.transition(MissionStatus.RUNNING)
        m.transition(MissionStatus.VERIFYING)
        m.transition(MissionStatus.COMPLETED)

        assert len(events) == 1
        assert events[0].event_type == MissionEventType.MISSION_COMPLETED

    def test_transition_emits_failed_event(self):
        bus = MissionEventBus()
        events: list[MissionEvent] = []
        bus.subscribe(lambda e: events.append(e) if e.event_type == MissionEventType.MISSION_FAILED else None)

        m = Mission(id=MissionID.generate(), title="M", event_bus=bus)
        m.transition(MissionStatus.ANALYZING)
        m.transition(MissionStatus.PLANNING)
        m.transition(MissionStatus.READY)
        m.transition(MissionStatus.RUNNING)
        m.transition(MissionStatus.FAILED)

        assert len(events) == 1
        assert events[0].event_type == MissionEventType.MISSION_FAILED

    def test_no_events_when_event_bus_none(self):
        m = Mission(id=MissionID.generate(), title="M", event_bus=None)
        m.transition(MissionStatus.ANALYZING)
        m.transition(MissionStatus.PLANNING)
        m.transition(MissionStatus.READY)
        m.transition(MissionStatus.RUNNING)
        # Should not raise
        assert m.status == MissionStatus.RUNNING

    def test_event_bus_integration_with_executor(self):
        bus = MissionEventBus()
        events: list[MissionEvent] = []
        bus.subscribe(events.append)

        graph = MissionGraph()
        m = Mission(id=MissionID.generate(), title="Math", event_bus=bus, status=MissionStatus.READY)
        graph.add_mission(m)
        executor = MissionExecutor()
        with patch.object(executor._executor, "run", side_effect=_mock_run_success):
            executor.execute(graph)

        assert m.status == MissionStatus.COMPLETED
        # Should have multiple events: VERIFYING, COMPLETED, etc.
        status_changes = [e for e in events if e.event_type == MissionEventType.MISSION_STATUS_CHANGED]
        assert len(status_changes) >= 1
        completed = [e for e in events if e.event_type == MissionEventType.MISSION_COMPLETED]
        assert len(completed) == 1


# ---------------------------------------------------------------------------
# Dependency ordering
# ---------------------------------------------------------------------------


class TestMissionDependencyOrdering:
    def test_dependency_order_enforced(self):
        graph = MissionGraph()
        a = _make_mission("A", MissionStatus.READY)
        b = _make_mission("B", MissionStatus.READY)
        c = _make_mission("C", MissionStatus.READY)
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, b)
        graph.add_dependency(b, c)

        execution_order: list[str] = []
        executor = MissionExecutor()

        original_execute_one = executor._execute_one

        def tracking_execute_one(mission):
            execution_order.append(mission.title)
            return original_execute_one(mission)

        executor._execute_one = tracking_execute_one  # type: ignore[method-assign]
        with patch.object(executor._executor, "run", side_effect=_mock_run_success):
            executor.execute(graph)

        assert execution_order.index("A") < execution_order.index("B")
        assert execution_order.index("B") < execution_order.index("C")

    def test_independent_missions_can_run_in_any_order(self):
        graph = MissionGraph()
        a = _make_mission("A", MissionStatus.READY)
        b = _make_mission("B", MissionStatus.READY)
        graph.add_mission(a)
        graph.add_mission(b)
        executor = MissionExecutor()
        with patch.object(executor._executor, "run", side_effect=_mock_run_success):
            result = executor.execute(graph)
        assert result["success"] is True
        assert a.status == MissionStatus.COMPLETED
        assert b.status == MissionStatus.COMPLETED


# ---------------------------------------------------------------------------
# Planner integration
# ---------------------------------------------------------------------------


class TestPlannerIntegration:
    def test_planner_filters_terminal_missions(self):
        from brain.planner.planner import Planner
        planner = Planner()
        graph = MissionGraph()
        a = _make_mission("A", MissionStatus.COMPLETED)
        b = _make_mission("B", MissionStatus.FAILED)
        c = _make_mission("C", MissionStatus.READY)
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        plan = planner.plan_missions(graph)
        assert a not in plan
        assert b not in plan
        assert c in plan


# ---------------------------------------------------------------------------
# MissionExecutor integration
# ---------------------------------------------------------------------------


class TestMissionExecutorIntegration:
    def test_mission_executor_uses_planner(self):
        graph = MissionGraph()
        a = _make_mission("A", MissionStatus.READY)
        b = _make_mission("B", MissionStatus.READY)
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_dependency(a, b)
        executor = MissionExecutor()
        with patch.object(executor._executor, "run", side_effect=_mock_run_success):
            result = executor.execute(graph)
        assert result["success"] is True

    def test_mission_executor_result_structure(self):
        graph = MissionGraph()
        m = _make_mission("M", MissionStatus.READY)
        graph.add_mission(m)
        executor = MissionExecutor()
        with patch.object(executor._executor, "run", side_effect=_mock_run_success):
            result = executor.execute(graph)
        assert "success" in result
        assert "results" in result
        assert "executed" in result
        assert "skipped" in result

    def test_error_field_set_on_failure(self):
        graph = MissionGraph()
        m = _make_mission("M", MissionStatus.READY)
        graph.add_mission(m)
        executor = MissionExecutor()

        with patch.object(
            executor._executor,
            "run",
            return_value=MagicMock(status="failed", error="specific error", id="g1"),
        ):
            result = executor.execute(graph)

        assert result["success"] is False
        assert m.error == "specific error"


# ---------------------------------------------------------------------------
# Existing Goal execution unaffected
# ---------------------------------------------------------------------------


class TestGoalExecutionUnchanged:
    def test_autonomous_executor_goal_lifecycle_unchanged(self):
        ae = AutonomousExecutor()
        with patch.object(ae._executor, "submit", return_value=MagicMock(result=lambda *_: "ok")):
            goal = ae.run("Calculate 2+2")
        # Goal should still go through its own lifecycle
        assert goal.status in {"completed", "failed"}

    def test_autonomous_executor_progress_unchanged(self):
        ae = AutonomousExecutor()
        with patch.object(ae._executor, "submit", return_value=MagicMock(result=lambda *_: "ok")):
            goal = ae.run("Calculate 2+2")
        progress = ae.progress(goal.id)
        assert "queue" in progress
        assert "latest_record" in progress
