from tools.tool_registry import ToolRegistry


def test_tool_registry_lists_expected_tools():
    registry = ToolRegistry()

    assert set(registry.list_tools()) == {
        "calculator",
        "python",
        "files",
        "memory",
        "internet",
    }


def test_tool_registry_returns_tool_by_name():
    registry = ToolRegistry()

    assert registry.get("calculator").name == "calculator"
    assert registry.get("missing") is None
