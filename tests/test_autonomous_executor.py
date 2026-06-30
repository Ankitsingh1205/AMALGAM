from __future__ import annotations

from brain.executor.autonomous_executor import AutonomousExecutor
from brain.goal.goal import Goal
from brain.queue.task_queue import TaskQueue
from brain.evaluator.evaluator import Evaluator
from brain.reflection.reflection_engine import ReflectionEngine
from brain.retry.retry_manager import RetryManager
from brain.memory.execution_memory import ExecutionMemory
from config import constants


class FakeKernelExecutor:
    """Fake kernel that always succeeds with the task data."""

    def execute(self, task):
        return getattr(task, "data", None)


class FakeFailingKernelExecutor:
    """Fake kernel that always fails."""

    def execute(self, task):
        raise RuntimeError("always fails")


class FakePartialKernelExecutor:
    """Fake kernel that fails once then succeeds."""

    def __init__(self):
        self.call_count = 0

    def execute(self, task):
        self.call_count += 1
        if self.call_count == 1:
            raise RuntimeError("first failure")
        return "success"


def test_run_completes_successfully():
    executor = AutonomousExecutor(kernel_executor=FakeKernelExecutor())
    goal = executor.run("2 + 2")
    assert goal.status == constants.GOAL_STATUS_COMPLETED
    assert goal.error is None


def test_run_math_task():
    executor = AutonomousExecutor(kernel_executor=FakeKernelExecutor())
    goal = executor.run("144 * 82")
    assert goal.status == constants.GOAL_STATUS_COMPLETED


def test_run_fails_and_reflects():
    executor = AutonomousExecutor(
        kernel_executor=FakeFailingKernelExecutor(),
        retry=RetryManager(max_retries=2),
    )
    goal = executor.run("2 + 2")
    # After 2 retries + alternative + replan + user escalation, it should fail
    assert goal.status == constants.GOAL_STATUS_FAILED
    assert goal.error is not None


def test_run_retries_then_succeeds():
    executor = AutonomousExecutor(
        kernel_executor=FakePartialKernelExecutor(),
        retry=RetryManager(max_retries=2),
    )
    goal = executor.run("2 + 2")
    assert goal.status == constants.GOAL_STATUS_COMPLETED


def test_generate_plan_for_math():
    executor = AutonomousExecutor()
    plan = executor._generate_plan("calculate 2 + 2")
    assert "calculator" in plan.lower() or "expression" in plan.lower()


def test_generate_plan_for_files():
    executor = AutonomousExecutor()
    plan = executor._generate_plan("list files in docs")
    assert "file" in plan.lower() or "list" in plan.lower()


def test_create_tasks_from_plan_for_math():
    executor = AutonomousExecutor()
    goal = Goal(id="g1", description="2 + 2")
    tasks = executor._create_tasks_from_plan(goal)
    assert len(tasks) == 1
    assert tasks[0]["action"] == constants.ACTION_CALCULATE


def test_create_tasks_from_plan_for_memory():
    executor = AutonomousExecutor()
    goal = Goal(id="g1", description="remember name=Ankit")
    tasks = executor._create_tasks_from_plan(goal)
    assert len(tasks) == 1
    assert tasks[0]["action"] == constants.ACTION_REMEMBER


def test_create_alternative_task_for_calculator():
    executor = AutonomousExecutor()
    # Calculator no longer has a code-injection-prone Python fallback.
    alt = executor._create_alternative_task({"action": constants.ACTION_CALCULATE, "data": "2+2"})
    assert alt is None


def test_create_alternative_task_for_internet():
    executor = AutonomousExecutor()
    alt = executor._create_alternative_task({"action": constants.ACTION_SEARCH_WEB, "data": "AI"})
    assert alt is not None
    assert alt["action"] == constants.ACTION_CHAT


def test_create_alternative_task_returns_none_for_unknown():
    executor = AutonomousExecutor()
    alt = executor._create_alternative_task({"action": constants.ACTION_CHAT, "data": "hello"})
    assert alt is None


def test_verify_goal_passes_with_no_failures():
    executor = AutonomousExecutor()
    goal = Goal(id="g1", description="test")
    # Enqueue and dequeue a task so complete_current has something to work with
    task = {"id": "t1", "plan_version": goal.plan_version, "action": constants.ACTION_CHAT}
    executor._queue.enqueue(task)
    executor._queue.dequeue()
    executor._queue.complete_current(result="ok")
    assert executor._verify_goal(goal) is True


def test_verify_goal_fails_for_missing_tasks():
    executor = AutonomousExecutor()
    goal = Goal(id="g1", description="test")
    assert executor._verify_goal(goal) is False


def test_progress_returns_structure():
    executor = AutonomousExecutor()
    goal = executor.run("2 + 2")
    prog = executor.progress(goal.id)
    assert "queue" in prog
    assert "latest_record" in prog


def test_goal_priority_is_preserved():
    executor = AutonomousExecutor()
    goal = executor.run("list files", priority=constants.GOAL_PRIORITY_HIGH)
    assert goal.priority == constants.GOAL_PRIORITY_HIGH


def test_execution_memory_records_steps(tmp_path):
    memory = ExecutionMemory()
    memory._memory.file = tmp_path / "exec_memory.json"
    memory._memory.memories = {}

    executor = AutonomousExecutor(
        kernel_executor=FakeKernelExecutor(),
        memory=memory,
    )
    goal = executor.run("2 + 2")
    records = memory.recall(goal.id)
    assert len(records) > 0
    assert any(r["step"] == "created" for r in records)
    assert any(r["step"] == "finished" for r in records)
