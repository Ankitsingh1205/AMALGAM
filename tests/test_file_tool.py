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


def test_executor_dispatches_file_list_task():
    kernel = Executor()

    result = kernel.execute(
        Task(
            intent="files",
            action="list_files",
            data=".",
        )
    )

    assert isinstance(result, list)
    assert "main.py" in result


def test_executor_blocks_file_list_outside_workspace(tmp_path):
    """Mission 7.6 (SEC-003/004): kernel-dispatched FileTool is confined
    to the workspace root; paths outside it are rejected."""
    kernel = Executor()

    result = kernel.execute(
        Task(
            intent="files",
            action="list_files",
            data=tmp_path,
        )
    )

    assert isinstance(result, str)
    assert "Error" in result
