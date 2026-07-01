import pytest
from agents.orchestrator_agent import OrchestratorAgent
from brain.agent_registry import AgentRegistry
from brain.messaging import Messaging
from brain.scheduler import Scheduler
from brain.shared_context import SharedContext


@pytest.fixture
def orchestrator():
    return OrchestratorAgent()


def test_orchestrator_execute_calculate(orchestrator):
    result = orchestrator.execute("2+2")
    assert result["success"] is True
    assert result["task"] == "2+2"
    assert result["goal"] is not None


def test_orchestrator_execute_memory(orchestrator):
    result = orchestrator.execute("remember test=hello")
    assert result["success"] is True
    assert result["task"] == "remember test=hello"


def test_orchestrator_no_task():
    orch = OrchestratorAgent()
    ctx = SharedContext()
    result = orch.run(ctx)
    assert result["success"] is False
    assert "No task provided" in result["errors"][0]


def test_orchestrator_custom_pipeline():
    orch = OrchestratorAgent(pipeline=["planner"])
    result = orch.execute("2+2")
    # Only planner runs, so engineer won't execute
    # The scheduler will succeed because planner succeeds
    assert result["success"] is True
    # But no goal from engineer
    assert result["goal"] is None


def test_orchestrator_get_progress():
    orch = OrchestratorAgent()
    ctx = SharedContext()
    ctx.set("task", "test")
    ctx.set("plan", "1. Test.")
    orch._shared = ctx
    progress = orch.get_progress()
    assert progress["task"] == "test"
    assert progress["plan"] == "1. Test."
