import pytest
from agents.research_agent import ResearchAgent
from brain.shared_context import SharedContext


@pytest.fixture
def researcher():
    return ResearchAgent()


def test_research_memory_task(researcher):
    ctx = SharedContext()
    ctx.set("task", "recall my password")
    ctx.set("plan", "1. Extract key. 2. Recall from memory.")
    result = researcher.run(ctx)

    assert result["success"] is True
    assert "memory" in result["findings"] or result["findings"] == {}
    assert ctx.get("research") is not None


def test_research_file_task(researcher):
    ctx = SharedContext()
    ctx.set("task", "list files in current directory")
    ctx.set("plan", "1. Identify target directory. 2. List files.")
    result = researcher.run(ctx)

    assert result["success"] is True
    assert "files" in result["findings"] or result["findings"] == {}
    assert ctx.get("research") is not None


def test_research_project_task(researcher):
    ctx = SharedContext()
    ctx.set("task", "summarize my project")
    ctx.set("plan", "1. Analyze workspace. 2. Summarize.")
    result = researcher.run(ctx)

    assert result["success"] is True
    assert "project" in result["findings"] or result["findings"] == {}
    assert ctx.get("research") is not None


def test_research_no_relevant_keywords(researcher):
    ctx = SharedContext()
    ctx.set("task", "hello world")
    ctx.set("plan", "1. Greet. 2. Return.")
    result = researcher.run(ctx)

    assert result["success"] is True
    assert result["findings"] == {}
