from __future__ import annotations

from brain.retry.retry_manager import RetryManager
from config import constants


def test_can_retry_initially():
    r = RetryManager()
    assert r.can_retry("g1") is True


def test_record_attempt_increments():
    r = RetryManager()
    assert r.record_attempt("g1") == 1
    assert r.record_attempt("g1") == 2
    assert r.record_attempt("g1") == 3


def test_can_retry_after_max():
    r = RetryManager(max_retries=2)
    r.record_attempt("g1")
    r.record_attempt("g1")
    assert r.can_retry("g1") is False


def test_attempts_left():
    r = RetryManager(max_retries=3)
    r.record_attempt("g1")
    assert r.attempts_left("g1") == 2


def test_decide_next_step_retries():
    r = RetryManager(max_retries=3)
    decision = r.decide_next_step("g1", constants.REFLECTION_STRATEGY_RETRY)
    assert decision["next_step"] == constants.REFLECTION_STRATEGY_RETRY
    assert "3 attempt(s) left" in decision["message"]


def test_decide_next_step_escalates_to_alternative():
    r = RetryManager(max_retries=2)
    r.record_attempt("g1")
    r.record_attempt("g1")
    decision = r.decide_next_step("g1", constants.REFLECTION_STRATEGY_RETRY)
    assert decision["next_step"] == constants.REFLECTION_STRATEGY_ALTERNATIVE


def test_decide_next_step_escalates_to_replan():
    r = RetryManager(max_retries=2)
    r.record_attempt("g1")
    r.record_attempt("g1")
    decision = r.decide_next_step("g1", constants.REFLECTION_STRATEGY_ALTERNATIVE)
    assert decision["next_step"] == constants.REFLECTION_STRATEGY_REPLAN


def test_decide_next_step_escalates_to_user():
    r = RetryManager(max_retries=2)
    r.record_attempt("g1")
    r.record_attempt("g1")
    decision = r.decide_next_step("g1", constants.REFLECTION_STRATEGY_REPLAN)
    assert decision["next_step"] == constants.REFLECTION_STRATEGY_USER


def test_decide_next_step_gives_up():
    r = RetryManager(max_retries=2)
    r.record_attempt("g1")
    r.record_attempt("g1")
    decision = r.decide_next_step("g1", constants.REFLECTION_STRATEGY_USER)
    assert decision["next_step"] == constants.REFLECTION_STRATEGY_GIVE_UP


def test_reset_clears_attempts():
    r = RetryManager(max_retries=2)
    r.record_attempt("g1")
    r.record_attempt("g1")
    r.reset("g1")
    assert r.can_retry("g1") is True


def test_reset_all_clears_all():
    r = RetryManager()
    r.record_attempt("g1")
    r.record_attempt("g2")
    r.reset_all()
    assert r.can_retry("g1") is True
    assert r.can_retry("g2") is True
