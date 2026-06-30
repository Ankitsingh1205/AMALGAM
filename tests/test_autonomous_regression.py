from __future__ import annotations

from brain.executor.autonomous_executor import AutonomousExecutor
from brain.goal.goal import Goal
from brain.queue.task_queue import TaskQueue
from config import constants


class FakePartialKernelExecutor:
    """Fake kernel that fails once then succeeds."""

    def __init__(self):
        self.call_count = 0

    def execute(self, task):
        self.call_count += 1
        if self.call_count == 1:
            raise RuntimeError("first failure")
        return "success"


def test_code_injection_calculator_returns_none():
    """Calculator no longer generates Python code with raw user input."""
    executor = AutonomousExecutor()
    alt = executor._create_alternative_task({
        "action": constants.ACTION_CALCULATE,
        "data": "__import__('os').system('rm -rf /')",
    })
    assert alt is None


def test_code_injection_file_list_returns_none():
    """File listing no longer generates Python code with raw user input."""
    executor = AutonomousExecutor()
    alt = executor._create_alternative_task({
        "action": constants.ACTION_LIST_FILES,
        "data": "'; __import__('os').system('evil') #",
    })
    assert alt is None


def test_replanning_preserves_history():
    """Replanning must not discard prior task history."""
    executor = AutonomousExecutor()
    goal = Goal(id="g1", description="test")
    for state in [constants.GOAL_STATUS_NEW, constants.GOAL_STATUS_ANALYZING,
                  constants.GOAL_STATUS_PLANNING, constants.GOAL_STATUS_READY,
                  constants.GOAL_STATUS_RUNNING, constants.GOAL_STATUS_REFLECTING,
                  constants.GOAL_STATUS_REPLANNING]:
        goal.transition(state)
    executor._queue.enqueue({"id": "t1", "plan_version": 0})
    executor._queue.dequeue()
    executor._queue.fail_current(error="fail")
    assert len(executor._queue.list_history()) == 1

    executor._replan(goal)
    assert len(executor._queue.list_history()) == 1


def test_replanning_increments_plan_version():
    executor = AutonomousExecutor()
    goal = Goal(id="g1", description="test")
    for state in [constants.GOAL_STATUS_NEW, constants.GOAL_STATUS_ANALYZING,
                  constants.GOAL_STATUS_PLANNING, constants.GOAL_STATUS_READY,
                  constants.GOAL_STATUS_RUNNING, constants.GOAL_STATUS_REFLECTING,
                  constants.GOAL_STATUS_REPLANNING]:
        goal.transition(state)
    assert goal.plan_version == 0
    executor._replan(goal)
    assert goal.plan_version == 1


def test_replanning_tasks_get_new_plan_version():
    executor = AutonomousExecutor()
    goal = Goal(id="g1", description="test")
    for state in [constants.GOAL_STATUS_NEW, constants.GOAL_STATUS_ANALYZING,
                  constants.GOAL_STATUS_PLANNING, constants.GOAL_STATUS_READY,
                  constants.GOAL_STATUS_RUNNING, constants.GOAL_STATUS_REFLECTING,
                  constants.GOAL_STATUS_REPLANNING]:
        goal.transition(state)
    executor._replan(goal)
    tasks = executor._create_tasks_from_plan(goal)
    assert all(t.get("plan_version") == 1 for t in tasks)


def test_verify_goal_only_checks_current_plan():
    """Old failed tasks from a prior plan must not fail verification of a new plan."""
    executor = AutonomousExecutor()
    goal = Goal(id="g1", description="test")

    # Old plan: task failed
    executor._queue.enqueue({"id": "t1", "plan_version": 0})
    executor._queue.dequeue()
    executor._queue.fail_current(error="old fail")

    # New plan: task succeeded
    goal.plan_version = 1
    executor._queue.enqueue({"id": "t2", "plan_version": 1})
    executor._queue.dequeue()
    executor._queue.complete_current(result="ok")

    assert executor._verify_goal(goal) is True


def test_verify_goal_fails_if_current_plan_has_failed_task():
    executor = AutonomousExecutor()
    goal = Goal(id="g1", description="test", plan_version=0)
    executor._queue.enqueue({"id": "t1", "plan_version": 0})
    executor._queue.dequeue()
    executor._queue.fail_current(error="fail")
    assert executor._verify_goal(goal) is False


def test_retry_preserves_history_correctly():
    """A failed task that is retried and eventually succeeds should verify."""
    executor = AutonomousExecutor(
        kernel_executor=FakePartialKernelExecutor(),
    )
    goal = executor.run("2 + 2")
    assert goal.status == constants.GOAL_STATUS_COMPLETED


def test_timeout_is_configurable():
    executor = AutonomousExecutor(execution_timeout=5.0)
    assert executor._execution_timeout == 5.0


def test_task_queue_history_is_capped():
    q = TaskQueue(max_history=3)
    for i in range(5):
        q.enqueue({"id": f"t{i}"})
        q.dequeue()
        q.complete_current()
    assert len(q.list_history()) == 3


def test_task_queue_clear_pending_preserves_history():
    q = TaskQueue()
    q.enqueue({"id": "t1"})
    q.dequeue()
    q.complete_current()
    q.clear_pending()
    assert len(q.list_history()) == 1
    assert len(q.list_pending()) == 0

