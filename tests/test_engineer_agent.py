from __future__ import annotations

from agents.engineer import EngineerAgent
from brain.executor.autonomous_executor import AutonomousExecutor
from brain.goal.goal import Goal
from config import constants


class FakeKernelExecutor:
    def execute(self, task):
        return getattr(task, "data", None)


class FakeFailingKernelExecutor:
    def execute(self, task):
        raise RuntimeError("always fails")


def test_engineer_agent_initializes_with_defaults():
    agent = EngineerAgent()
    assert agent.files is not None
    assert agent.executor is not None
    assert agent.autonomous is not None


def test_engineer_agent_executes_successfully():
    agent = EngineerAgent(
        autonomous_executor=AutonomousExecutor(kernel_executor=FakeKernelExecutor())
    )
    result = agent.execute("2 + 2")
    assert result["success"] is True
    assert result["goal"] is not None
    assert result["goal"]["status"] == constants.GOAL_STATUS_COMPLETED


def test_engineer_agent_handles_failure():
    agent = EngineerAgent(
        autonomous_executor=AutonomousExecutor(
            kernel_executor=FakeFailingKernelExecutor(),
            retry=RetryManager(max_retries=2),
        )
    )
    result = agent.execute("2 + 2")
    assert result["success"] is False
    assert result["errors"]


def test_engineer_agent_run_goal_returns_goal():
    agent = EngineerAgent(
        autonomous_executor=AutonomousExecutor(kernel_executor=FakeKernelExecutor())
    )
    goal = agent.run_goal("list files")
    assert isinstance(goal, Goal)
    assert goal.status == constants.GOAL_STATUS_COMPLETED


def test_engineer_agent_goal_progress():
    agent = EngineerAgent(
        autonomous_executor=AutonomousExecutor(kernel_executor=FakeKernelExecutor())
    )
    goal = agent.run_goal("2 + 2")
    prog = agent.goal_progress(goal.id)
    assert "queue" in prog
    assert "latest_record" in prog


def test_engineer_agent_backward_compatible_execute():
    """execute() must still return a dict with success, task, goal, errors."""
    agent = EngineerAgent(
        autonomous_executor=AutonomousExecutor(kernel_executor=FakeKernelExecutor())
    )
    result = agent.execute("hello")
    assert "success" in result
    assert "task" in result
    assert "goal" in result
    assert "errors" in result


from brain.retry.retry_manager import RetryManager
