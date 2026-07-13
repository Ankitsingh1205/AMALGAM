"""Security regression tests for Mission 7.6 (SEC-001..004).

Verifies the fixes for the Critical findings from the Mission 6.4.3
security audit stay fixed:
    SEC-001  Calculator eval() code execution
    SEC-002  PythonExecutor in-process exec()
    SEC-003  FileTool path traversal
    SEC-004  FileTool absolute-path escape
"""

import sys

from tools.calculator import Calculator
from tools.file_tool import FileTool
from tools.python_executor import PythonExecutor


# ---------------------------------------------------------------- SEC-001

def test_calculator_still_does_math():
    calc = Calculator()
    assert calc.calculate("144*82") == 11808
    assert calc.calculate("2**10") == 1024
    assert calc.calculate("-(3+4)/2") == -3.5


def test_calculator_rejects_code_execution():
    calc = Calculator()
    assert calc.calculate("__import__('os').getcwd()") is None
    assert calc.calculate("().__class__.__mro__") is None
    assert calc.calculate("open('/etc/passwd').read()") is None
    assert calc.calculate("[1]*3") is None  # non-numeric operands


def test_calculator_rejects_huge_exponents():
    calc = Calculator()
    assert calc.calculate("9**9**9") is None


# ---------------------------------------------------------------- SEC-002

def test_python_executor_runs_in_subprocess():
    executor = PythonExecutor()
    result = executor.execute("import os; print(os.getpid())")
    assert result.isdigit()
    assert int(result) != __import__("os").getpid()


def test_python_executor_cannot_mutate_host_state():
    executor = PythonExecutor()
    sentinel = "amalgam_sec002_sentinel"
    executor.execute(f"import sys; sys.modules['{sentinel}'] = object()")
    assert sentinel not in sys.modules


def test_python_executor_times_out():
    executor = PythonExecutor(timeout=1)
    result = executor.execute("while True: pass")
    assert result.startswith("Python Error:")
    assert "timeout" in result


# ------------------------------------------------------------ SEC-003/004

def test_file_tool_blocks_traversal_when_confined(tmp_path):
    root = tmp_path / "workspace"
    root.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("top secret", encoding="utf-8")

    tool = FileTool(workspace_root=root)
    result = tool.read("../secret.txt")
    assert isinstance(result, str) and result.startswith("Read Error:")


def test_file_tool_blocks_absolute_escape_when_confined(tmp_path):
    root = tmp_path / "workspace"
    root.mkdir()
    outside = tmp_path / "outside.txt"

    tool = FileTool(workspace_root=root)
    result = tool.write(str(outside), "escape")
    assert result.startswith("Write Error:")
    assert not outside.exists()


def test_file_tool_allows_workspace_paths_when_confined(tmp_path):
    tool = FileTool(workspace_root=tmp_path)
    assert tool.write("note.txt", "hello") == "File saved."
    assert tool.read("note.txt") == "hello"
    assert tool.list_dir(".") == ["note.txt"]


def test_file_tool_unconfined_preserves_legacy_behavior(tmp_path):
    tool = FileTool()
    path = tmp_path / "note.txt"
    assert tool.write(path, "hello") == "File saved."
    assert tool.read(path) == "hello"
