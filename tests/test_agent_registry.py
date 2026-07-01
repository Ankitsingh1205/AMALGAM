import pytest
from brain.agent_registry import AgentRegistry


class FakeAgent:
    pass


def test_register_and_get():
    reg = AgentRegistry()
    agent = FakeAgent()
    reg.register("alpha", agent)
    assert reg.get("alpha") is agent


def test_list_all():
    reg = AgentRegistry()
    reg.register("a", FakeAgent())
    reg.register("b", FakeAgent())
    assert sorted(reg.list_all()) == ["a", "b"]


def test_get_missing():
    reg = AgentRegistry()
    assert reg.get("missing") is None


def test_unregister():
    reg = AgentRegistry()
    reg.register("a", FakeAgent())
    reg.unregister("a")
    assert reg.get("a") is None
    assert "a" not in reg


def test_contains():
    reg = AgentRegistry()
    reg.register("a", FakeAgent())
    assert "a" in reg
    assert "b" not in reg


def test_reset():
    reg = AgentRegistry()
    reg.register("a", FakeAgent())
    reg.reset()
    assert reg.list_all() == []
