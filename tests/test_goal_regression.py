from __future__ import annotations

from brain.goal.goal import Goal
from config import constants
import pytest


def test_goal_valid_transition_idle_to_new():
    goal = Goal(id="g1", description="test")
    goal.transition(constants.GOAL_STATUS_NEW)
    assert goal.status == constants.GOAL_STATUS_NEW


def test_goal_valid_transition_new_to_analyzing():
    goal = Goal(id="g1", description="test", status=constants.GOAL_STATUS_NEW)
    goal.transition(constants.GOAL_STATUS_ANALYZING)
    assert goal.status == constants.GOAL_STATUS_ANALYZING


def test_goal_invalid_transition_idle_to_running():
    goal = Goal(id="g1", description="test")
    with pytest.raises(ValueError, match="Invalid transition"):
        goal.transition(constants.GOAL_STATUS_RUNNING)


def test_goal_invalid_transition_from_terminal():
    goal = Goal(id="g1", description="test", status=constants.GOAL_STATUS_COMPLETED)
    with pytest.raises(ValueError, match="Cannot transition from terminal state"):
        goal.transition(constants.GOAL_STATUS_FAILED)


def test_goal_failed_is_universal_sink():
    goal = Goal(id="g1", description="test", status=constants.GOAL_STATUS_RUNNING)
    goal.transition(constants.GOAL_STATUS_FAILED)
    assert goal.status == constants.GOAL_STATUS_FAILED


def test_goal_idempotent_transition():
    goal = Goal(id="g1", description="test", status=constants.GOAL_STATUS_RUNNING)
    goal.transition(constants.GOAL_STATUS_RUNNING)
    assert goal.status == constants.GOAL_STATUS_RUNNING


def test_goal_plan_version_defaults_to_zero():
    goal = Goal(id="g1", description="test")
    assert goal.plan_version == 0


def test_goal_from_dict_ignores_unknown_keys():
    goal = Goal.from_dict({
        "id": "g1",
        "description": "test",
        "unknown_key": "ignored",
    })
    assert goal.id == "g1"
