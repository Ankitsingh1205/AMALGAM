from __future__ import annotations

from unittest.mock import patch

import pytest

from brain.mission import Mission, MissionEventBus, MissionEventType, MissionGraph, MissionID, MissionStatus
from brain.mission.mission_executor import MissionExecutor


def _make_mission(title: str = "Calc", description: str = "list files", status: MissionStatus = MissionStatus.READY):
    return Mission(id=MissionID.generate(), title=title, description=description, status=status)


class DummyThreadPool:
    """Simple synchronous thread pool replacement for AutonomousExecutor."""
    def submit(self, fn, *args, **kwargs):
        class Future:
            def result(self, timeout=None):
                return fn(*args, **kwargs)
        return Future()
    def shutdown(self, wait=False):
        pass


def test_mission_file_tool_success_and_events():
    # Setup a mission that triggers the calculator tool
    bus = MissionEventBus()
    events = []
    bus.subscribe(events.append)

    graph = MissionGraph()
    mission = _make_mission(description="list files")
    mission.event_bus = bus  # attach event bus after creation
    graph.add_mission(mission)

    executor = MissionExecutor()
    # Replace the internal thread pool of AutonomousExecutor with a synchronous version
    with patch.object(executor._executor, "_executor", DummyThreadPool()):
        result = executor.execute(graph)

    assert result["success"] is True
    assert mission.status == MissionStatus.COMPLETED
    # Verify that at least one status change and a completed event were emitted
    status_events = [e for e in events if e.event_type == MissionEventType.MISSION_STATUS_CHANGED]
    completed_events = [e for e in events if e.event_type == MissionEventType.MISSION_COMPLETED]
    assert len(status_events) >= 1
    assert len(completed_events) == 1


def test_mission_calculator_tool_failure_and_events():
    # Setup a mission with an invalid expression causing calculator to return None
    bus = MissionEventBus()
    events = []
    bus.subscribe(events.append)

    graph = MissionGraph()
    mission = _make_mission(description="Calculate not_an_expr")
    mission.event_bus = bus
    graph.add_mission(mission)

    executor = MissionExecutor()
    with patch.object(executor._executor, "_executor", DummyThreadPool()):
        result = executor.execute(graph)

    # The mission should end in FAILED because the calculator returns None (unknown result)
    assert result["success"] is False
    assert mission.status == MissionStatus.FAILED
    # Verify that a failed event was emitted
    failed_events = [e for e in events if e.event_type == MissionEventType.MISSION_FAILED]
    assert len(failed_events) == 1
