import pytest
from brain.agent_context import AgentContext


def test_agent_context_initial_state():
    ctx = AgentContext("test_agent")
    assert ctx.agent_name == "test_agent"
    assert ctx.snapshot() == {}
    assert ctx.get_history() == []


def test_agent_context_get_set():
    ctx = AgentContext("a")
    ctx.set("key", "value")
    assert ctx.get("key") == "value"
    assert ctx.get("missing", "default") == "default"


def test_agent_context_update():
    ctx = AgentContext("a")
    ctx.update({"x": 1, "y": 2})
    assert ctx.get("x") == 1
    assert ctx.get("y") == 2


def test_agent_context_snapshot():
    ctx = AgentContext("a")
    ctx.set("k", "v")
    snap = ctx.snapshot()
    assert snap == {"k": "v"}
    # Snapshot should be a copy
    snap["k"] = "x"
    assert ctx.get("k") == "v"


def test_agent_context_record_and_history():
    ctx = AgentContext("a")
    ctx.record({"event": "start"})
    ctx.record({"event": "end"})
    hist = ctx.get_history()
    assert len(hist) == 2
    assert hist[0]["event"] == "start"


def test_agent_context_clear_history():
    ctx = AgentContext("a")
    ctx.record({"event": "x"})
    ctx.clear_history()
    assert ctx.get_history() == []


def test_agent_context_clear():
    ctx = AgentContext("a")
    ctx.set("k", "v")
    ctx.record({"event": "x"})
    ctx.clear()
    assert ctx.snapshot() == {}
    assert ctx.get_history() == []
