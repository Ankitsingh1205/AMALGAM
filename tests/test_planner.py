from brain.planner.planner import Planner


def test_creates_math_task():
    planner = Planner()

    task = planner.create_task("math", "144*82")

    assert task.intent == "math"
    assert task.action == "calculate"
    assert task.data == "144*82"
    assert task.model is None


def test_creates_coding_task_with_model():
    planner = Planner()

    task = planner.create_task("coding", "Write Python code")

    assert task.intent == "coding"
    assert task.action == "generate_code"
    assert task.model == "qwen2.5-coder:7b"
    assert task.data == "Write Python code"


def test_creates_general_task_by_default():
    planner = Planner()

    task = planner.create_task("unknown", "What is AI?")

    assert task.intent == "general"
    assert task.action == "chat"
    assert task.model == "qwen3:8b"
    assert task.data == "What is AI?"
