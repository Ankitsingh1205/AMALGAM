import pytest
from agents.planner_agent import PlannerAgent
from brain.mission import Mission, MissionGraph, MissionID, MissionStatus
from brain.shared_context import SharedContext


@pytest.fixture
def planner():
    return PlannerAgent()


def test_planner_creates_goal_and_plan(planner):
    ctx = SharedContext()
    ctx.set("task", "Calculate 2+2")
    result = planner.run(ctx)

    assert result["success"] is True
    assert "goal_id" in result
    assert "plan" in result
    assert "calculator" in result["plan"].lower()

    goal = ctx.get("goal")
    assert goal is not None
    assert goal["description"] == "Calculate 2+2"
    assert goal["plan"] == result["plan"]


def test_planner_missing_task(planner):
    ctx = SharedContext()
    result = planner.run(ctx)
    assert result["success"] is False
    assert "No task provided" in result["error"]


def test_planner_file_task(planner):
    ctx = SharedContext()
    ctx.set("task", "Read my file.txt")
    result = planner.run(ctx)
    assert result["success"] is True
    assert "file" in result["plan"].lower()


def test_planner_memory_task(planner):
    ctx = SharedContext()
    ctx.set("task", "remember name=Alice")
    result = planner.run(ctx)
    assert result["success"] is True
    assert "memory" in result["plan"].lower()


def test_planner_sets_priority(planner):
    ctx = SharedContext()
    ctx.set("task", "Calculate 2+2")
    ctx.set("priority", 10)
    result = planner.run(ctx)
    goal = ctx.get("goal")
    assert goal["priority"] == 10


# ---------------------------------------------------------------------------
# Mission planning via PlannerAgent
# ---------------------------------------------------------------------------


class TestPlannerAgentMissionPlanning:
    def _make_graph(self, *missions: Mission) -> MissionGraph:
        graph = MissionGraph()
        for m in missions:
            graph.add_mission(m)
        return graph

    def test_run_missions_valid_graph(self):
        planner = PlannerAgent()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph = self._make_graph(a, b)
        graph.add_dependency(a, b)
        ctx = SharedContext()
        result = planner.run_missions(graph, ctx)
        assert result["success"] is True
        assert result["mission_count"] == 2
        assert result["plan"] == ["A", "B"]
        assert ctx.get("mission_plan") == [a, b]
        assert ctx.get("mission_count") == 2

    def test_run_missions_skips_completed(self):
        planner = PlannerAgent()
        a = Mission(id=MissionID.generate(), title="A", status=MissionStatus.COMPLETED)
        b = Mission(id=MissionID.generate(), title="B")
        graph = self._make_graph(a, b)
        graph.add_dependency(a, b)
        ctx = SharedContext()
        result = planner.run_missions(graph, ctx)
        assert result["success"] is True
        assert result["mission_count"] == 1
        assert result["plan"] == ["B"]

    def test_run_missions_skips_failed(self):
        planner = PlannerAgent()
        a = Mission(id=MissionID.generate(), title="A", status=MissionStatus.FAILED)
        b = Mission(id=MissionID.generate(), title="B")
        graph = self._make_graph(a, b)
        graph.add_dependency(a, b)
        ctx = SharedContext()
        result = planner.run_missions(graph, ctx)
        assert result["success"] is True
        assert result["mission_count"] == 1
        assert result["plan"] == ["B"]

    def test_run_missions_rejects_cycle(self):
        planner = PlannerAgent()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph = self._make_graph(a, b)
        graph.add_dependency(a, b)
        # Manually corrupt graph to create cycle
        from brain.mission.graph import MissionDependency
        graph._edges.add(MissionDependency(str(b.id), str(a.id)))
        graph._nodes[str(b.id)].children.add(str(a.id))
        graph._nodes[str(a.id)].parents.add(str(b.id))
        ctx = SharedContext()
        result = planner.run_missions(graph, ctx)
        assert result["success"] is False
        assert "cycle" in result["error"].lower()
        assert ctx.get("error") is not None

    def test_run_missions_empty_graph(self):
        planner = PlannerAgent()
        graph = MissionGraph()
        ctx = SharedContext()
        result = planner.run_missions(graph, ctx)
        assert result["success"] is True
        assert result["mission_count"] == 0
        assert result["plan"] == []

    def test_run_missions_deterministic(self):
        planner = PlannerAgent()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph = self._make_graph(a, b, c)
        graph.add_dependency(a, b)
        graph.add_dependency(a, c)
        ctx1 = SharedContext()
        ctx2 = SharedContext()
        result1 = planner.run_missions(graph, ctx1)
        result2 = planner.run_missions(graph, ctx2)
        assert result1["plan"] == result2["plan"]

    def test_run_missions_dependency_ordering(self):
        planner = PlannerAgent()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        d = Mission(id=MissionID.generate(), title="D")
        graph = self._make_graph(a, b, c, d)
        graph.add_dependency(a, b)
        graph.add_dependency(a, c)
        graph.add_dependency(b, d)
        graph.add_dependency(c, d)
        ctx = SharedContext()
        result = planner.run_missions(graph, ctx)
        plan = result["plan"]
        assert plan.index("A") < plan.index("B")
        assert plan.index("A") < plan.index("C")
        assert plan.index("B") < plan.index("D")
        assert plan.index("C") < plan.index("D")

    def test_run_missions_disconnected_graph(self):
        planner = PlannerAgent()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        d = Mission(id=MissionID.generate(), title="D")
        graph = self._make_graph(a, b, c, d)
        graph.add_dependency(a, b)
        graph.add_dependency(c, d)
        ctx = SharedContext()
        result = planner.run_missions(graph, ctx)
        assert result["mission_count"] == 4
        plan = result["plan"]
        assert plan.index("A") < plan.index("B")
        assert plan.index("C") < plan.index("D")

    def test_run_missions_all_terminal_returns_empty(self):
        planner = PlannerAgent()
        a = Mission(id=MissionID.generate(), title="A", status=MissionStatus.COMPLETED)
        b = Mission(id=MissionID.generate(), title="B", status=MissionStatus.FAILED)
        c = Mission(id=MissionID.generate(), title="C", status=MissionStatus.CANCELLED)
        graph = self._make_graph(a, b, c)
        ctx = SharedContext()
        result = planner.run_missions(graph, ctx)
        assert result["success"] is True
        assert result["mission_count"] == 0
        assert result["plan"] == []
