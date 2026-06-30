from __future__ import annotations

from brain.memory.execution_memory import ExecutionMemory


def test_execution_memory_prunes_old_records(tmp_path):
    memory = ExecutionMemory(max_records_per_goal=3)
    memory._memory.file = tmp_path / "exec_memory.json"
    memory._memory.memories = {}

    for i in range(5):
        memory.record("g1", f"step{i}")

    records = memory.recall("g1")
    assert len(records) == 3
    assert records[0]["step"] == "step2"


def test_execution_memory_flush_writes_to_memory_service(tmp_path):
    memory = ExecutionMemory(batch_size=5)
    memory._memory.file = tmp_path / "exec_memory.json"
    memory._memory.memories = {}

    for i in range(3):
        memory.record("g1", f"step{i}")

    # Not yet flushed (batch_size=5)
    assert len(memory._memory.show_all()) == 0

    memory.flush()
    assert len(memory._memory.show_all()) == 3


def test_execution_memory_local_index_avoids_scan(tmp_path):
    memory = ExecutionMemory()
    memory._memory.file = tmp_path / "exec_memory.json"
    memory._memory.memories = {}

    memory.record("g1", "step1")
    memory.record("g2", "stepA")

    # recall should use local index, not scan all memory
    g1_records = memory.recall("g1")
    assert len(g1_records) == 1
    assert g1_records[0]["step"] == "step1"


def test_memory_service_forget_removes_key(tmp_path):
    from services.memory import MemoryService
    service = MemoryService()
    service.file = tmp_path / "mem.json"
    service.memories = {}

    service.remember("key1", "value1")
    service.remember("key2", "value2")
    assert "key1" in service.show_all()

    service.forget("key1")
    assert "key1" not in service.show_all()
    assert "key2" in service.show_all()


def test_memory_service_forget_missing_key_returns_true():
    from services.memory import MemoryService
    service = MemoryService()
    service.memories = {}
    assert service.forget("missing") is True
