from __future__ import annotations

from brain.reflection.reflection_engine import ReflectionEngine
from config import constants


def test_reflect_missing_dependency():
    r = ReflectionEngine()
    result = r.reflect(error="No module named 'missing'")
    assert result["root_cause"] == "missing_dependency"
    assert result["strategy"] == constants.REFLECTION_STRATEGY_REPLAN


def test_reflect_invalid_path():
    r = ReflectionEngine()
    result = r.reflect(error="No such file or directory")
    assert result["root_cause"] == "invalid_path"
    assert result["strategy"] == constants.REFLECTION_STRATEGY_ALTERNATIVE


def test_reflect_runtime_exception():
    r = ReflectionEngine()
    result = r.reflect(error="ValueError: bad input")
    assert result["root_cause"] == "runtime_exception"
    assert result["strategy"] == constants.REFLECTION_STRATEGY_RETRY


def test_reflect_wrong_tool():
    r = ReflectionEngine()
    result = r.reflect(output="Dispatcher Error: missing target 'x'")
    assert result["root_cause"] == "wrong_tool"
    assert result["strategy"] == constants.REFLECTION_STRATEGY_ALTERNATIVE


def test_reflect_wrong_planning():
    r = ReflectionEngine()
    result = r.reflect(output="Dispatcher Error: malformed task")
    assert result["root_cause"] == "wrong_planning"
    assert result["strategy"] == constants.REFLECTION_STRATEGY_REPLAN


def test_reflect_service_unavailable():
    r = ReflectionEngine()
    result = r.reflect(error="LLM Error: connection refused")
    assert result["root_cause"] == "service_unavailable"
    assert result["strategy"] == constants.REFLECTION_STRATEGY_RETRY


def test_reflect_unknown():
    r = ReflectionEngine()
    result = r.reflect(error="something unexpected")
    assert result["root_cause"] == "unknown"
    assert result["strategy"] == constants.REFLECTION_STRATEGY_RETRY


def test_should_escalate_to_user():
    r = ReflectionEngine()
    assert r.should_escalate_to_user({"strategy": constants.REFLECTION_STRATEGY_USER}) is True
    assert r.should_escalate_to_user({"strategy": constants.REFLECTION_STRATEGY_RETRY}) is False
