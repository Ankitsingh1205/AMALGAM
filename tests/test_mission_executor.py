from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from brain.mission import (
    Mission,
    MissionGraph,
    MissionID,
    MissionPriority,
    MissionStatus,
    MissionExecutor,
)

# ---------------------------------------------------------------------------
# Mocks & Helpers
# ---------------------------------------------------------------------------

class MockGoal:
    def __init__(self, id: str, status: str, error: str = None):
        self.id = id
        self.status = status
        self.error = error

# ---------------------------------------------------------------------------
# TestMissionExecutor
# ---------------------------------------------------------------------------

class TestMissionExecutor:
    @pytest.fixture
    def executor(self) -> MissionExecutor:
        return MissionExecutor()

    @pytest.fixture
    def simple_graph(self) -> MissionGraph:
        m1 = Mission(id=MissionID.generate(), title="M1", description="Desc 1")
        m2 = Mission(id=MissionID.generate(), title="M2", description="Desc 2")
        m2.add_dependency(m1)
        graph = MissionGraph()
        graph.add_mission(m1)
        graph.add_mission(m2)
        return graph

    def test_init(self, executor):
        assert executor._planner is not None
        assert executor._executor is not None
        assert executor._logger is not None

    def test_execute_success_flow(self, executor, simple_graph):
        """Verify that a simple linear graph executes all missions in order."""
        with patch.object(executor._executor, "run") as mock_run:
            # Mock AutonomousExecutor.run to return a successful goal
            mock_run.side_effect = lambda description, priority: MockGoal(
                id="g1", status="completed"
            )

            result = executor.execute(simple_graph)

            assert result["success"] is True
            assert result["executed"] == 2
            assert result["skipped"] == 0
            
            # Verify topological order: M1 then M2
            calls = mock_run.call_args_list
            assert "M1" in calls[0].kwargs["description"]
            assert "M2" in calls[1].kwargs["description"]

            # Verify status transitions
            for node in simple_graph._nodes.values():
                assert node.mission.status == MissionStatus.COMPLETED

    def test_execute_halt_on_failure(self, executor, simple_graph):
        """Verify that execution stops when a mission fails and halt_on_failure=True."""
        with patch.object(executor._executor, "run") as mock_run:
            # First mission fails
            mock_run.side_effect = lambda description, priority: MockGoal(
                id="g1", status="failed", error="Critical Error"
            )

            result = executor.execute(simple_graph, halt_on_failure=True)

            assert result["success"] is False
            assert result["executed"] == 1
            assert result["failed_at"] is not None
            assert result["error"] == "Critical Error"
            
            # Only one mission should have been attempted
            assert mock_run.call_count == 1

    def test_execute_continue_on_failure(self, executor, simple_graph):
        """Verify that execution continues for independent missions if halt_on_failure=False."""
        # Create a graph with two independent missions
        m1 = Mission(id=MissionID.generate(), title="M1")
        m2 = Mission(id=MissionID.generate(), title="M2")
        graph = MissionGraph()
        graph.add_mission(m1)
        graph.add_mission(m2)

        with patch.object(executor._executor, "run") as mock_run:
            # M1 fails, M2 succeeds
            def side_effect(description, priority):
                if "M1" in description:
                    return MockGoal("g1", "failed", "Error 1")
                return MockGoal("g2", "completed")
            
            mock_run.side_effect = side_effect

            result = executor.execute(graph, halt_on_failure=False)

            assert result["success"] is False
            assert result["executed"] == 2
            assert mock_run.call_count == 2
            
            assert m1.status == MissionStatus.FAILED
            assert m2.status == MissionStatus.COMPLETED

    def test_execute_skips_terminal_missions(self, executor):
        """Verify that missions already in terminal states are skipped."""
        m1 = Mission(id=MissionID.generate(), title="M1", status=MissionStatus.COMPLETED)
        graph = MissionGraph()
        graph.add_mission(m1)

        with patch.object(executor._executor, "run") as mock_run:
            result = executor.execute(graph)
            assert result["executed"] == 0
            assert result["skipped"] == 1
            assert mock_run.call_count == 0

    def test_is_currently_executable(self, executor):
        m_created = Mission(id=MissionID.generate(), title="C", status=MissionStatus.CREATED)
        m_running = Mission(id=MissionID.generate(), title="R", status=MissionStatus.RUNNING)
        m_done = Mission(id=MissionID.generate(), title="D", status=MissionStatus.COMPLETED)
        
        assert executor._is_currently_executable(m_created) is True
        assert executor._is_currently_executable(m_running) is True
        assert executor._is_currently_executable(m_done) is False
