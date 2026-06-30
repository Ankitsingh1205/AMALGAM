from kernel.executor import Executor
from kernel.task import Task
from services.memory import MemoryService
from tools.memory_tool import MemoryTool


def test_memory_service_remembers_and_recalls(tmp_path):
    service = MemoryService()
    service.file = tmp_path / "memory.json"
    service.memories = {}

    assert service.remember("name", "Ankit") is True
    assert service.recall("name") == "Ankit"


def test_memory_service_handles_invalid_json(tmp_path):
    memory_file = tmp_path / "memory.json"
    memory_file.write_text("{invalid", encoding="utf-8")

    service = MemoryService()
    service.file = memory_file
    service.load()

    assert service.show_all() == {}


def test_memory_tool_remember_and_recall(tmp_path):
    tool = MemoryTool()
    tool.memory.file = tmp_path / "memory.json"
    tool.memory.memories = {}

    assert tool.remember("name", "Ankit") == "Stored: name"
    assert tool.recall("name") == "Ankit"


def test_executor_dispatches_memory_tasks(tmp_path):
    kernel = Executor()
    memory_tool = kernel.dispatcher.tools.get("memory")
    memory_tool.memory.file = tmp_path / "memory.json"
    memory_tool.memory.memories = {}

    stored = kernel.execute(
        Task(
            intent="memory",
            action="remember",
            data=("name", "Ankit"),
        )
    )
    recalled = kernel.execute(
        Task(
            intent="memory",
            action="recall",
            data="name",
        )
    )

    assert stored == "Stored: name"
    assert recalled == "Ankit"
