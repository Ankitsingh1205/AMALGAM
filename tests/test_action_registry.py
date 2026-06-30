from kernel.action_registry import ActionRegistry


def test_action_registry_returns_expected_routes():
    registry = ActionRegistry()

    assert registry.get("calculate") == ("calculator", "calculate")
    assert registry.get("remember") == ("memory", "remember")
    assert registry.get("run_python") == ("python", "execute")


def test_action_registry_returns_none_for_unknown_action():
    registry = ActionRegistry()

    assert registry.get("missing") is None
