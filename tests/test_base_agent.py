import pytest
from agents.base_agent import BaseAgent
from brain.messaging import Message, Messaging
from brain.shared_context import SharedContext


class DummyAgent(BaseAgent):
    def run(self, shared_context):
        self.send_message("other", "test", payload="hello")
        return {"success": True, "data": shared_context.get("data")}


def test_base_agent_lifecycle():
    agent = DummyAgent("dummy")
    assert agent.status == "idle"
    agent.setup()
    assert agent.status == "ready"
    agent.teardown()
    assert agent.status == "idle"


def test_base_agent_run():
    ctx = SharedContext()
    ctx.set("data", 42)
    agent = DummyAgent("dummy")
    result = agent.run(ctx)
    assert result["success"] is True
    assert result["data"] == 42


def test_base_agent_messaging():
    bus = Messaging()
    agent = DummyAgent("dummy", messaging=bus)
    ctx = SharedContext()
    agent.run(ctx)

    msgs = bus.receive("other")
    assert len(msgs) == 1
    assert msgs[0].payload == "hello"
    assert msgs[0].sender == "dummy"


def test_base_agent_receive_messages():
    bus = Messaging()
    agent = DummyAgent("dummy", messaging=bus)
    bus.send(Message(sender="x", recipient="dummy", msg_type="note", payload="ping"))
    received = agent.receive_messages()
    assert len(received) == 1
    assert received[0].payload == "ping"


def test_base_agent_has_messages():
    bus = Messaging()
    agent = DummyAgent("dummy", messaging=bus)
    assert not agent.has_messages()
    bus.send(Message(sender="x", recipient="dummy", msg_type="note", payload="ping"))
    assert agent.has_messages()
