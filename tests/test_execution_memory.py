from __future__ import annotations

from brain.memory.execution_memory import ExecutionMemory


def test_record_and_recall(tmp_path):
    memory = ExecutionMemory()
    memory._memory.file = tmp_path / "exec_memory.json"
    memory._memory.memories = {}

    assert memory.record("g1", "step1", output="hello") is True
    records = memory.recall("g1")
    assert len(records) == 1
    assert records[0]["goal_id"] == "g1"
    assert records[0]["step"] == "step1"


def test_recall_latest(tmp_path):
    memory = ExecutionMemory()
    memory._memory.file = tmp_path / "exec_memory.json"
    memory._memory.memories = {}

    memory.record("g1", "step1", output="a")
    memory.record("g1", "step2", output="b")

    latest = memory.recall_latest("g1")
    assert latest["step"] == "step2"
    assert latest["output"] == "b"


def test_recall_latest_empty():
    memory = ExecutionMemory()
    memory._memory.memories = {}
    assert memory.recall_latest("g1") is None


def test_record_serialization(tmp_path):
    memory = ExecutionMemory()
    memory._memory.file = tmp_path / "exec_memory.json"
    memory._memory.memories = {}

    class Unserializable:
        pass

    assert memory.record("g1", "step1", output=Unserializable()) is True
    records = memory.recall("g1")
    assert isinstance(records[0]["output"], str)


def test_record_with_all_fields(tmp_path):
    memory = ExecutionMemory()
    memory._memory.file = tmp_path / "exec_memory.json"
    memory._memory.memories = {}

    assert memory.record(
        goal_id="g1",
        step="execute",
        goal={"id": "g1"},
        plan="do it",
        task={"id": "t1"},
        action="calculate",
        output="4",
        error=None,
        reflection="none",
    ) is True

    records = memory.recall("g1")
    assert records[0]["action"] == "calculate"
    assert records[0]["plan"] == "do it"
