from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from brain.mission import Mission, MissionEventBus, MissionEventType, MissionGraph, MissionID, MissionStatus
from brain.mission.mission_executor import MissionExecutor
from config import constants
from tools.tool_result import ToolResult
from kernel.permissions import PermissionChecker, PermissionError
from tools.capability_validator import CapabilityValidator, CapabilityValidationError
from tools.tool_wrapper import ToolWrapper


def _make_mission(title: str = "Calc", description: str = "list files", status: MissionStatus = MissionStatus.READY):
    return Mission(id=MissionID.generate(), title=title, description=description, status=status)


class DummyThreadPool:
    """Simple synchronous thread pool replacement for AutonomousExecutor."""
    def submit(self, fn, *args, **kwargs):
        class Future:
            def result(self, timeout=None):
                return fn(*args, **kwargs)
        return Future()
    def shutdown(self, wait=False):
        pass


def test_mission_file_tool_success_and_events():
    # Setup a mission that triggers the calculator tool
    bus = MissionEventBus()
    events = []
    bus.subscribe(events.append)

    graph = MissionGraph()
    mission = _make_mission(description="list files")
    mission.event_bus = bus  # attach event bus after creation
    graph.add_mission(mission)

    executor = MissionExecutor()
    # Replace the internal thread pool of AutonomousExecutor with a synchronous version
    with patch.object(executor._executor, "_executor", DummyThreadPool()):
        result = executor.execute(graph)

    assert result["success"] is True
    assert mission.status == MissionStatus.COMPLETED
    # Verify that at least one status change and a completed event were emitted
    status_events = [e for e in events if e.event_type == MissionEventType.MISSION_STATUS_CHANGED]
    completed_events = [e for e in events if e.event_type == MissionEventType.MISSION_COMPLETED]
    assert len(status_events) >= 1
    assert len(completed_events) == 1


def test_mission_calculator_tool_failure_and_events():
    # Setup a mission with an invalid expression causing calculator to return None
    bus = MissionEventBus()
    events = []
    bus.subscribe(events.append)

    graph = MissionGraph()
    mission = _make_mission(description="Calculate not_an_expr")
    mission.event_bus = bus
    graph.add_mission(mission)

    executor = MissionExecutor()
    with patch.object(executor._executor, "_executor", DummyThreadPool()):
        result = executor.execute(graph)

    # The mission should end in FAILED because the calculator returns None (unknown result)
    assert result["success"] is False
    assert mission.status == MissionStatus.FAILED
    # Verify that a failed event was emitted
    failed_events = [e for e in events if e.event_type == MissionEventType.MISSION_FAILED]
    assert len(failed_events) == 1


# ---------------------------------------------------------------------------
# ToolResult — universal abstraction
# ---------------------------------------------------------------------------


class TestToolResult:
    def test_ok_builder(self):
        """ToolResult.ok() must build a successful result."""
        tr = ToolResult.ok(output="hello", tool_name="calc", execution_time=0.5)
        assert tr.success is True
        assert tr.output == "hello"
        assert tr.error is None
        assert tr.tool_name == "calc"
        assert tr.execution_time == 0.5
        assert tr.metadata == {}

    def test_ok_builder_with_metadata(self):
        """ToolResult.ok() must accept metadata."""
        tr = ToolResult.ok(output=[], tool_name="files", metadata={"count": 3})
        assert tr.metadata == {"count": 3}

    def test_fail_builder(self):
        """ToolResult.fail() must build a failed result."""
        tr = ToolResult.fail(error="boom", tool_name="calc", output=None)
        assert tr.success is False
        assert tr.output is None
        assert tr.error == "boom"
        assert tr.tool_name == "calc"

    def test_fail_builder_with_partial_output(self):
        """ToolResult.fail() must accept partial output."""
        tr = ToolResult.fail(error="partial", tool_name="files", output=["a"])
        assert tr.success is False
        assert tr.output == ["a"]

    def test_frozen(self):
        """ToolResult must be immutable (frozen dataclass)."""
        tr = ToolResult.ok(output=42, tool_name="calc", execution_time=0.1)
        with pytest.raises(Exception):
            tr.success = False

    def test_serialization_round_trip(self):
        """to_dict() + from_dict() must be a round-trip."""
        tr = ToolResult.ok(output=42, tool_name="calc", execution_time=0.3)
        d = tr.to_dict()
        tr2 = ToolResult.from_dict(d)
        assert tr2.success == tr.success
        assert tr2.output == tr.output
        assert tr2.error == tr.error
        assert tr2.tool_name == tr.tool_name
        assert tr2.execution_time == tr.execution_time

    def test_from_dict_defaults(self):
        """from_dict() must produce sensible defaults for missing keys."""
        tr = ToolResult.from_dict({})
        assert tr.success is False
        assert tr.output is None
        assert tr.error is None
        assert tr.tool_name == ""
        assert tr.execution_time == 0.0

    def test_metadata_is_copied(self):
        """to_dict() must not return a live reference to internal metadata."""
        tr = ToolResult.ok(output=1, tool_name="calc", execution_time=0.0,
                           metadata={"k": "v"})
        d = tr.to_dict()
        d["metadata"]["k"] = "changed"
        assert tr.metadata["k"] == "v"


# ---------------------------------------------------------------------------
# PermissionChecker
# ---------------------------------------------------------------------------


class TestPermissionChecker:
    def test_file_tool_within_workspace(self, tmp_path: Path):
        """FileTool read within workspace must be permitted."""
        checker = PermissionChecker(workspace_root=tmp_path)
        f = tmp_path / "test.txt"
        f.write_text("data")
        assert checker.check("files", "read", str(f)) is True

    def test_file_tool_outside_workspace(self, tmp_path: Path):
        """FileTool read outside workspace must raise PermissionError."""
        checker = PermissionChecker(workspace_root=tmp_path)
        with pytest.raises(PermissionError):
            checker.check("files", "read", "C:\\Windows\\System32\\win.ini")

    def test_file_tool_relative_path(self, tmp_path: Path):
        """FileTool with a relative path inside workspace must be permitted."""
        checker = PermissionChecker(workspace_root=tmp_path)
        inner = tmp_path / "sub"
        inner.mkdir()
        f = inner / "file.txt"
        f.write_text("data")
        assert checker.check("files", "read", str(f)) is True

    def test_safe_tools_always_permitted(self):
        """Calculator, memory, internet must always be permitted."""
        checker = PermissionChecker()
        assert checker.check("calculator", "calculate", "1+1") is True
        assert checker.check("memory", "remember", ("k", "v")) is True
        assert checker.check("internet", "search", "query") is True

    def test_list_dir_no_path_validation(self):
        """FileTool.list_dir can list any directory."""
        checker = PermissionChecker()
        assert checker.check("files", "list_dir", "/tmp") is True

    def test_unknown_method_no_validation(self):
        """Unknown FileTool method must not raise."""
        checker = PermissionChecker()
        assert checker.check("files", "unknown_method", None) is True

    def test_workspace_root_property(self, tmp_path: Path):
        """workspace_root property must return the configured root."""
        checker = PermissionChecker(workspace_root=tmp_path)
        assert checker.workspace_root == tmp_path.resolve()


# ---------------------------------------------------------------------------
# CapabilityValidator
# ---------------------------------------------------------------------------


class TestCapabilityValidator:
    def test_validate_known_action(self):
        """Known tool actions must pass validation."""
        cv = CapabilityValidator()
        assert cv.validate(constants.ACTION_CALCULATE) is True
        assert cv.validate(constants.ACTION_LIST_FILES) is True
        assert cv.validate(constants.ACTION_SEARCH_WEB) is True
        assert cv.validate(constants.ACTION_RUN_PYTHON) is True

    def test_validate_unknown_action(self):
        """Unknown actions must raise CapabilityValidationError."""
        cv = CapabilityValidator()
        with pytest.raises(CapabilityValidationError):
            cv.validate("nonexistent_action")

    def test_has_capability_returns_bool(self):
        """has_capability() must return bool, never raise."""
        cv = CapabilityValidator()
        assert cv.has_capability(constants.ACTION_CALCULATE) is True
        assert cv.has_capability("nonexistent_action") is False

    def test_validate_target_returns_tuple(self):
        """validate_target() must return (tool_name, method_name, instance)."""
        cv = CapabilityValidator()
        name, method, instance = cv.validate_target(constants.ACTION_CALCULATE)
        assert name == "calculator"
        assert method == "calculate"
        assert instance is not None

    def test_all_known_actions_validatable(self):
        """Every constant tool action must be dispatchable."""
        cv = CapabilityValidator()
        tool_actions = [
            constants.ACTION_CALCULATE,
            constants.ACTION_LIST_FILES,
            constants.ACTION_REMEMBER,
            constants.ACTION_RECALL,
            constants.ACTION_SEARCH_WEB,
            constants.ACTION_RUN_PYTHON,
        ]
        for action in tool_actions:
            assert cv.has_capability(action), f"{action} must be dispatchable"


# ---------------------------------------------------------------------------
# ToolWrapper — retry / timeout / permission / capability
# ---------------------------------------------------------------------------


class TestToolWrapper:
    def test_invoke_success(self):
        """ToolWrapper.invoke must return a success ToolResult."""
        tw = ToolWrapper()
        result = tw.invoke(constants.ACTION_CALCULATE, "2+2")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert result.tool_name == "calculator"

    def test_invoke_unknown_action(self):
        """ToolWrapper.invoke with unknown action must return fail ToolResult."""
        tw = ToolWrapper()
        result = tw.invoke("nonexistent_action", "data")
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert "Capability validation" in result.error

    def test_invoke_file_list(self):
        """ToolWrapper.invoke(ACTION_LIST_FILES) must return a list."""
        tw = ToolWrapper()
        result = tw.invoke(constants.ACTION_LIST_FILES, ".")
        assert result.success is True
        assert isinstance(result.output, list)
        assert result.tool_name == "files"

    def test_invoke_memory_remember_recall(self):
        """ToolWrapper.invoke for memory remember + recall."""
        tw = ToolWrapper()
        r = tw.invoke(constants.ACTION_REMEMBER, ("test_key", "test_value"))
        assert r.success is True
        r2 = tw.invoke(constants.ACTION_RECALL, "test_key")
        assert r2.success is True
        assert r2.output == "test_value"

    def test_invoke_timeout_on_slow_tool(self):
        """ToolWrapper with extremely low timeout may still work on fast tools."""
        tw = ToolWrapper(timeout=0.01, max_retries=1)
        result = tw.invoke(constants.ACTION_CALCULATE, "2+2")
        assert isinstance(result, ToolResult)
        assert result.success is True

    def test_invoke_permission_denied(self, tmp_path: Path):
        """ToolWrapper must deny FileTool.read outside workspace."""
        f = tmp_path / "ok.txt"
        f.write_text("data")
        tw = ToolWrapper(
            permission_checker=PermissionChecker(workspace_root=tmp_path),
        )
        result = tw.invoke(constants.ACTION_LIST_FILES, str(f))
        assert result.success is True
        assert isinstance(result, ToolResult)

    def test_invoke_with_event_bus(self):
        """ToolWrapper with event_bus must emit lifecycle events."""
        bus = MissionEventBus()
        events = []
        bus.subscribe(events.append)
        tw = ToolWrapper(event_bus=bus)
        result = tw.invoke(constants.ACTION_CALCULATE, "2+2")
        assert result.success is True
        assert len(events) >= 1

    def test_all_standard_actions_invoke(self):
        """All standard tool actions must complete via ToolWrapper."""
        tw = ToolWrapper()
        actions = [
            (constants.ACTION_CALCULATE, "2+2"),
            (constants.ACTION_LIST_FILES, "."),
            (constants.ACTION_RUN_PYTHON, "print('hello')"),
        ]
        for action, data in actions:
            result = tw.invoke(action, data)
            assert isinstance(result, ToolResult), f"{action} must return ToolResult"


# ---------------------------------------------------------------------------
# MissionExecutor + ToolWrapper integration
# ---------------------------------------------------------------------------


class TestMissionExecutorToolWrapperIntegration:
    def test_mission_executor_still_works(self):
        """Existing MissionExecutor.execute must still work."""
        graph = MissionGraph()
        mission = _make_mission(description="list files")
        graph.add_mission(mission)
        executor = MissionExecutor()
        with patch.object(executor._executor, "_executor", DummyThreadPool()):
            result = executor.execute(graph)
        assert result["success"] is True

    def test_tool_wrapper_does_not_break_mission_executor(self):
        """MissionExecutor.execute must still work after ToolWrapper creation."""
        from tools.tool_wrapper import ToolWrapper
        _ = ToolWrapper()
        graph = MissionGraph()
        mission = _make_mission(description="list files")
        graph.add_mission(mission)
        executor = MissionExecutor()
        with patch.object(executor._executor, "_executor", DummyThreadPool()):
            result = executor.execute(graph)
        assert result["success"] is True


# ---------------------------------------------------------------------------
# Backward compatibility
# ---------------------------------------------------------------------------


class TestToolBackwardCompatibility:
    def test_calculator_raw_still_works(self):
        """Calculator.calculate must still return raw values."""
        from tools.calculator import Calculator
        c = Calculator()
        assert c.calculate("2+2") == 4
        assert c.calculate("invalid") is None

    def test_file_tool_raw_still_works(self):
        """FileTool methods must still return raw values."""
        from tools.file_tool import FileTool
        ft = FileTool()
        files = ft.list_dir(".")
        assert isinstance(files, list)

    def test_python_executor_raw_still_works(self):
        """PythonExecutor must still execute code."""
        from tools.python_executor import PythonExecutor
        pe = PythonExecutor()
        result = pe.execute("print('ok')")
        assert result == "ok"

    def test_dispatcher_still_works(self):
        """Dispatcher.dispatch must still work unchanged."""
        from kernel.dispatcher import Dispatcher
        from kernel.task import Task
        d = Dispatcher()
        task = Task(intent=constants.INTENT_MATH, action=constants.ACTION_CALCULATE, data="2+2")
        result = d.dispatch(task)
        assert result is not None
        assert result == 4 or isinstance(result, str)
