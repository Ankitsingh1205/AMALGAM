from brain.planner.planner import Planner
from brain.mission import Mission, MissionGraph, MissionID, MissionStatus

import pytest


def test_creates_math_task():
    planner = Planner()

    task = planner.create_task("math", "144*82")

    assert task.intent == "math"
    assert task.action == "calculate"
    assert task.data == "144*82"
    assert task.model is None


def test_creates_coding_task_with_model():
    planner = Planner()

    task = planner.create_task("coding", "Write Python code")

    assert task.intent == "coding"
    assert task.action == "generate_code"
    assert task.model == "qwen2.5-coder:7b"
    assert task.data == "Write Python code"


def test_creates_general_task_by_default():
    planner = Planner()

    task = planner.create_task("unknown", "What is AI?")

    assert task.intent == "general"
    assert task.action == "chat"
    assert task.model == "qwen3:8b"
    assert task.data == "What is AI?"


# ---------------------------------------------------------------------------
# Mission planning
# ---------------------------------------------------------------------------


class TestPlannerMissionPlanning:
    def _make_graph(self, *missions: Mission) -> MissionGraph:
        graph = MissionGraph()
        for m in missions:
            graph.add_mission(m)
        return graph

    def test_plan_missions_empty_graph(self):
        planner = Planner()
        graph = MissionGraph()
        plan = planner.plan_missions(graph)
        assert plan == []

    def test_plan_missions_single_mission(self):
        planner = Planner()
        m = Mission(id=MissionID.generate(), title="M")
        graph = self._make_graph(m)
        plan = planner.plan_missions(graph)
        assert plan == [m]

    def test_plan_missions_chain(self):
        planner = Planner()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph = self._make_graph(a, b, c)
        graph.add_dependency(a, b)
        graph.add_dependency(b, c)
        plan = planner.plan_missions(graph)
        assert plan.index(a) < plan.index(b) < plan.index(c)

    def test_plan_missions_dependency_ordering(self):
        planner = Planner()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        d = Mission(id=MissionID.generate(), title="D")
        graph = self._make_graph(a, b, c, d)
        graph.add_dependency(a, b)
        graph.add_dependency(a, c)
        graph.add_dependency(b, d)
        graph.add_dependency(c, d)
        plan = planner.plan_missions(graph)
        assert plan.index(a) < plan.index(b)
        assert plan.index(a) < plan.index(c)
        assert plan.index(b) < plan.index(d)
        assert plan.index(c) < plan.index(d)

    def test_plan_missions_skips_completed(self):
        planner = Planner()
        a = Mission(id=MissionID.generate(), title="A", status=MissionStatus.COMPLETED)
        b = Mission(id=MissionID.generate(), title="B")
        graph = self._make_graph(a, b)
        graph.add_dependency(a, b)
        plan = planner.plan_missions(graph)
        assert a not in plan
        assert b in plan

    def test_plan_missions_skips_failed(self):
        planner = Planner()
        a = Mission(id=MissionID.generate(), title="A", status=MissionStatus.FAILED)
        b = Mission(id=MissionID.generate(), title="B")
        graph = self._make_graph(a, b)
        graph.add_dependency(a, b)
        plan = planner.plan_missions(graph)
        assert a not in plan
        assert b in plan

    def test_plan_missions_skips_cancelled(self):
        planner = Planner()
        a = Mission(id=MissionID.generate(), title="A", status=MissionStatus.CANCELLED)
        b = Mission(id=MissionID.generate(), title="B")
        graph = self._make_graph(a, b)
        graph.add_dependency(a, b)
        plan = planner.plan_missions(graph)
        assert a not in plan
        assert b in plan

    def test_plan_missions_keeps_executable_states(self):
        planner = Planner()
        states = [
            MissionStatus.CREATED,
            MissionStatus.ANALYZING,
            MissionStatus.PLANNING,
            MissionStatus.READY,
            MissionStatus.RUNNING,
            MissionStatus.VERIFYING,
            MissionStatus.RECOVERING,
        ]
        for state in states:
            m = Mission(id=MissionID.generate(), title=f"M-{state.value}", status=state)
            graph = MissionGraph()
            graph.add_mission(m)
            plan = planner.plan_missions(graph)
            assert m in plan, f"Mission with status {state.value} should be executable"

    def test_plan_missions_rejects_cycle(self):
        planner = Planner()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph = self._make_graph(a, b)
        graph.add_dependency(a, b)
        with pytest.raises(ValueError, match="cycle"):
            graph.add_dependency(b, a)

    def test_plan_missions_rejects_invalid_graph(self):
        planner = Planner()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph = self._make_graph(a, b)
        graph.add_dependency(a, b)
        # Remove edge from _edges but keep parent-child relationships
        from brain.mission.graph import MissionDependency
        graph._edges.discard(MissionDependency(str(a.id), str(b.id)))
        with pytest.raises(ValueError, match="Invalid"):
            planner.plan_missions(graph)

    def test_plan_missions_deterministic(self):
        planner = Planner()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph = self._make_graph(a, b, c)
        graph.add_dependency(a, b)
        graph.add_dependency(a, c)
        plan1 = planner.plan_missions(graph)
        plan2 = planner.plan_missions(graph)
        assert [m.title for m in plan1] == [m.title for m in plan2]

    def test_plan_mission_executable(self):
        planner = Planner()
        m = Mission(id=MissionID.generate(), title="M", status=MissionStatus.READY)
        result = planner.plan_mission(m)
        assert result is m

    def test_plan_mission_completed_returns_none(self):
        planner = Planner()
        m = Mission(id=MissionID.generate(), title="M", status=MissionStatus.COMPLETED)
        result = planner.plan_mission(m)
        assert result is None

    def test_plan_mission_failed_returns_none(self):
        planner = Planner()
        m = Mission(id=MissionID.generate(), title="M", status=MissionStatus.FAILED)
        result = planner.plan_mission(m)
        assert result is None

    def test_plan_mission_cancelled_returns_none(self):
        planner = Planner()
        m = Mission(id=MissionID.generate(), title="M", status=MissionStatus.CANCELLED)
        result = planner.plan_mission(m)
        assert result is None

    def test_disconnected_graph(self):
        planner = Planner()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        d = Mission(id=MissionID.generate(), title="D")
        graph = self._make_graph(a, b, c, d)
        graph.add_dependency(a, b)
        graph.add_dependency(c, d)
        plan = planner.plan_missions(graph)
        assert len(plan) == 4
        assert plan.index(a) < plan.index(b)
        assert plan.index(c) < plan.index(d)

    def test_all_terminal_skipped(self):
        planner = Planner()
        a = Mission(id=MissionID.generate(), title="A", status=MissionStatus.COMPLETED)
        b = Mission(id=MissionID.generate(), title="B", status=MissionStatus.FAILED)
        c = Mission(id=MissionID.generate(), title="C", status=MissionStatus.CANCELLED)
        graph = self._make_graph(a, b, c)
        plan = planner.plan_missions(graph)
        assert plan == []
