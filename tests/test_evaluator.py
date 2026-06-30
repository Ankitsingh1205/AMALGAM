from __future__ import annotations

from brain.evaluator.evaluator import Evaluator
from config import constants


def test_evaluate_success_with_output():
    e = Evaluator()
    verdict = e.evaluate(output="hello")
    assert verdict["status"] == constants.EVALUATION_SUCCESS
    assert verdict["verified"] is True


def test_evaluate_failure_with_error():
    e = Evaluator()
    verdict = e.evaluate(error="something broke")
    assert verdict["status"] == constants.EVALUATION_FAILURE
    assert verdict["verified"] is False


def test_evaluate_failure_with_dispatcher_error():
    e = Evaluator()
    verdict = e.evaluate(output="Dispatcher Error: missing target")
    assert verdict["status"] == constants.EVALUATION_FAILURE


def test_evaluate_unknown_for_none():
    e = Evaluator()
    verdict = e.evaluate(output=None)
    assert verdict["status"] == constants.EVALUATION_UNKNOWN


def test_evaluate_partial_for_mismatch():
    e = Evaluator()
    verdict = e.evaluate(output="hello", expected="world")
    assert verdict["status"] == constants.EVALUATION_PARTIAL


def test_evaluate_success_for_match():
    e = Evaluator()
    verdict = e.evaluate(output="hello", expected="hello")
    assert verdict["status"] == constants.EVALUATION_SUCCESS


def test_is_success():
    e = Evaluator()
    assert e.is_success({"status": constants.EVALUATION_SUCCESS}) is True
    assert e.is_success({"status": constants.EVALUATION_FAILURE}) is False


def test_is_failure():
    e = Evaluator()
    assert e.is_failure({"status": constants.EVALUATION_FAILURE}) is True
    assert e.is_failure({"status": constants.EVALUATION_SUCCESS}) is False


def test_is_verified():
    e = Evaluator()
    assert e.is_verified({"verified": True}) is True
    assert e.is_verified({"verified": False}) is False
