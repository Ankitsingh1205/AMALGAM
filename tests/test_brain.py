from brain.brain import Brain


def test_brain_creates_math_task():
    brain = Brain()

    task = brain.think("144*82")

    assert task.intent == "math"
    assert task.action == "calculate"


def test_brain_creates_coding_task():
    brain = Brain()

    task = brain.think("Write Python code")

    assert task.intent == "coding"
    assert task.action == "generate_code"


def test_brain_creates_general_task():
    brain = Brain()

    task = brain.think("What is AI?")

    assert task.intent == "general"
    assert task.action == "chat"
