from kernel.executor import Executor
from kernel.task import Task
from tools.python_executor import PythonExecutor


def test_python_executor_captures_stdout():
    executor = PythonExecutor()

    result = executor.execute("print('hello')")

    assert result == "hello"


def test_python_executor_returns_error_message():
    executor = PythonExecutor()

    result = executor.execute("raise ValueError('bad')")

    assert result.startswith("Python Error:")


def test_executor_dispatches_python_task():
    kernel = Executor()

    result = kernel.execute(
        Task(
            intent="python",
            action="run_python",
            data="print(2 + 3)",
        )
    )

    assert result == "5"
