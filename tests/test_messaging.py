import pytest
from brain.messaging import Message, Messaging


def test_message_creation():
    msg = Message(sender="a", recipient="b", msg_type="test", payload=42)
    assert msg.sender == "a"
    assert msg.recipient == "b"
    assert msg.msg_type == "test"
    assert msg.payload == 42
    assert msg.id is not None
    assert msg.timestamp is not None


def test_messaging_send_and_receive():
    bus = Messaging()
    msg = Message(sender="alice", recipient="bob", msg_type="task", payload="do work")
    bus.send(msg)

    received = bus.receive("bob")
    assert len(received) == 1
    assert received[0].payload == "do work"

    # Inbox should be empty after receive
    assert bus.receive("bob") == []


def test_messaging_broadcast():
    bus = Messaging()
    bus.send(Message(sender="a", recipient="bob", msg_type="ping"))
    bus.send(Message(sender="a", recipient="carol", msg_type="ping"))
    bus.send(Message(sender="a", recipient="*", msg_type="alert", payload="all hands"))

    bob = bus.receive("bob")
    carol = bus.receive("carol")
    assert len(bob) == 2
    assert len(carol) == 2
    assert any(m.msg_type == "alert" for m in bob)
    assert any(m.msg_type == "alert" for m in carol)


def test_messaging_peek():
    bus = Messaging()
    bus.send(Message(sender="a", recipient="x", msg_type="t"))
    assert bus.peek("x")
    assert bus.has_messages("x")
    # Peek does not clear
    assert bus.peek("x")
    assert bus.has_messages("x")


def test_messaging_clear_inbox():
    bus = Messaging()
    bus.send(Message(sender="a", recipient="x", msg_type="t"))
    bus.clear_inbox("x")
    assert not bus.has_messages("x")


def test_messaging_subscribe_handler():
    bus = Messaging()
    received = []

    def handler(msg):
        received.append(msg)

    bus.subscribe("agent1", handler)
    bus.send(Message(sender="a", recipient="agent1", msg_type="note"))
    assert len(received) == 1
    assert received[0].msg_type == "note"


def test_messaging_handler_exception_ignored():
    bus = Messaging()

    def bad_handler(msg):
        raise RuntimeError("boom")

    bus.subscribe("agent1", bad_handler)
    # Should not raise
    bus.send(Message(sender="a", recipient="agent1", msg_type="note"))
