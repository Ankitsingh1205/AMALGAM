from kernel.executor import Executor
from kernel.task import Task
from tools.calculator import Calculator


def test_calculator_returns_math_result():
    calculator = Calculator()

    assert calculator.calculate("144*82") == 11808


def test_calculator_returns_none_for_invalid_expression():
    calculator = Calculator()

    assert calculator.calculate("not math") is None


def test_executor_dispatches_calculator_task():
    kernel = Executor()

    result = kernel.execute(
        Task(
            intent="math",
            action="calculate",
            data="2+2",
        )
    )

    assert result == 4
