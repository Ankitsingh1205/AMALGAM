from kernel.executor import Executor
from kernel.task import Task
from tools.file_tool import FileTool


def test_file_tool_reads_and_writes_file(tmp_path):
    tool = FileTool()
    path = tmp_path / "note.txt"

    assert tool.write(path, "hello") == "File saved."
    assert tool.read(path) == "hello"


def test_file_tool_lists_directory(tmp_path):
    tool = FileTool()
    path = tmp_path / "note.txt"
    path.write_text("hello", encoding="utf-8")

    assert tool.list_dir(tmp_path) == ["note.txt"]


def test_executor_dispatches_file_list_task(tmp_path):
    path = tmp_path / "note.txt"
    path.write_text("hello", encoding="utf-8")
    kernel = Executor()

    result = kernel.execute(
        Task(
            intent="files",
            action="list_files",
            data=tmp_path,
        )
    )

    assert result == ["note.txt"]
