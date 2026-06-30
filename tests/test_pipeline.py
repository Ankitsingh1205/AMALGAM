from brain.brain import Brain
from kernel.executor import Executor


def test_canonical_math_pipeline_returns_result():
    brain = Brain()
    kernel = Executor()

    task = brain.think("144*82")
    result = kernel.execute(task)

    assert result == 11808


def test_canonical_general_pipeline_returns_llm_error_without_crashing():
    brain = Brain()
    kernel = Executor()

    task = brain.think("What is Artificial Intelligence?")
    result = kernel.execute(task)

    assert isinstance(result, str)
    assert result
