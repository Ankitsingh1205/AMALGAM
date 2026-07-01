import pytest
from agents.reviewer_agent import ReviewerAgent
from brain.shared_context import SharedContext


@pytest.fixture
def reviewer():
    return ReviewerAgent()


def test_reviewer_approves_valid_task(reviewer):
    ctx = SharedContext()
    ctx.set("task", "Calculate 2+2")
    ctx.set("plan", "1. Extract expression. 2. Execute calculator.")
    ctx.set("research", {})
    result = reviewer.run(ctx)

    assert result["success"] is True
    assert result["approved"] is True
    assert result["issues"] == []
    assert ctx.get("review")["approved"] is True


def test_reviewer_rejects_empty_task(reviewer):
    ctx = SharedContext()
    ctx.set("task", "")
    ctx.set("plan", "")
    ctx.set("research", {})
    result = reviewer.run(ctx)

    assert result["success"] is False
    assert result["approved"] is False
    assert any("empty" in i.lower() for i in result["issues"])


def test_reviewer_rejects_missing_plan(reviewer):
    ctx = SharedContext()
    ctx.set("task", "Calculate 2+2")
    ctx.set("plan", "")
    ctx.set("research", {})
    result = reviewer.run(ctx)

    assert result["success"] is False
    assert result["approved"] is False
    assert any("missing" in i.lower() for i in result["issues"])


def test_reviewer_rejects_dangerous_task(reviewer):
    ctx = SharedContext()
    ctx.set("task", "eval('__import__(\\'os\\').system(\\'rm -rf /\\')')")
    ctx.set("plan", "1. Extract code. 2. Execute.")
    ctx.set("research", {})
    result = reviewer.run(ctx)

    assert result["success"] is False
    assert result["approved"] is False
    assert any("dangerous" in i.lower() for i in result["issues"])


def test_reviewer_rejects_unsupported_type(reviewer):
    ctx = SharedContext()
    ctx.set("task", "do something completely unsupported xyz")
    ctx.set("plan", "1. Do it.")
    ctx.set("research", {})
    result = reviewer.run(ctx)

    assert result["success"] is False
    assert result["approved"] is False
    assert any("supported" in i.lower() for i in result["issues"])
