from kernel.task import Task


def test_task_stores_fields():
    task = Task(
        intent="coding",
        action="generate_code",
        model="qwen2.5-coder:7b",
        tool="python",
        data="print('hello')",
    )

    assert task.intent == "coding"
    assert task.action == "generate_code"
    assert task.model == "qwen2.5-coder:7b"
    assert task.tool == "python"
    assert task.data == "print('hello')"


def test_task_repr_contains_core_fields():
    task = Task(intent="math", action="calculate", data="1+1")

    rendered = repr(task)

    assert "intent=math" in rendered
    assert "action=calculate" in rendered
