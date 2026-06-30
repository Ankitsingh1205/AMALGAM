from __future__ import annotations

from brain.goal.goal import Goal
from config import constants


def test_goal_starts_in_idle():
    goal = Goal(id="g1", description="Test goal")
    assert goal.status == constants.GOAL_STATUS_IDLE


def test_goal_transition_updates_status():
    goal = Goal(id="g1", description="Test goal")
    goal.transition(constants.GOAL_STATUS_NEW)
    assert goal.status == constants.GOAL_STATUS_NEW
    assert goal.updated_at >= goal.created_at


def test_goal_is_terminal_for_completed():
    goal = Goal(id="g1", description="Test goal", status=constants.GOAL_STATUS_COMPLETED)
    assert goal.is_terminal() is True


def test_goal_is_terminal_for_failed():
    goal = Goal(id="g1", description="Test goal", status=constants.GOAL_STATUS_FAILED)
    assert goal.is_terminal() is True


def test_goal_is_not_terminal_for_running():
    goal = Goal(id="g1", description="Test goal", status=constants.GOAL_STATUS_RUNNING)
    assert goal.is_terminal() is False


def test_goal_is_active_for_running():
    goal = Goal(id="g1", description="Test goal", status=constants.GOAL_STATUS_RUNNING)
    assert goal.is_active() is True


def test_goal_is_not_active_for_idle():
    goal = Goal(id="g1", description="Test goal", status=constants.GOAL_STATUS_IDLE)
    assert goal.is_active() is False


def test_goal_as_dict_roundtrip():
    goal = Goal(id="g1", description="Test goal", priority=constants.GOAL_PRIORITY_HIGH)
    data = goal.as_dict()
    restored = Goal.from_dict(data)
    assert restored.id == "g1"
    assert restored.description == "Test goal"
    assert restored.priority == constants.GOAL_PRIORITY_HIGH


def test_goal_priority_constants():
    assert constants.GOAL_PRIORITY_LOW < constants.GOAL_PRIORITY_NORMAL
    assert constants.GOAL_PRIORITY_NORMAL < constants.GOAL_PRIORITY_HIGH
    assert constants.GOAL_PRIORITY_HIGH < constants.GOAL_PRIORITY_CRITICAL
