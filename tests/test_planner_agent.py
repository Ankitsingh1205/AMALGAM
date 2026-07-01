import pytest
from agents.planner_agent import PlannerAgent
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
