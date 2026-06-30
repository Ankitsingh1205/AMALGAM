from kernel.executor import Executor
from kernel.task import Task


def test_executor_handles_unknown_action():
    executor = Executor()

    result = executor.execute(Task(intent="unknown", action="missing", data=None))

    assert result == "Unknown action: missing"


def test_executor_handles_malformed_task():
    executor = Executor()

    result = executor.execute(object())

    assert result == "Dispatcher Error: malformed task."


def test_dispatcher_handles_bad_remember_payload():
    executor = Executor()

    result = executor.execute(Task(intent="memory", action="remember", data="name"))

    assert result == "Dispatcher Error: remember action requires key and value."
