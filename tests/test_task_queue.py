from __future__ import annotations

from brain.queue.task_queue import TaskQueue
from config import constants


def test_enqueue_adds_task():
    q = TaskQueue()
    q.enqueue({"id": "t1"})
    assert len(q.list_pending()) == 1


def test_dequeue_returns_task():
    q = TaskQueue()
    q.enqueue({"id": "t1"})
    task = q.dequeue()
    assert task is not None
    assert task["id"] == "t1"
    assert task["status"] == constants.TASK_STATUS_RUNNING


def test_dequeue_returns_none_when_empty():
    q = TaskQueue()
    assert q.dequeue() is None


def test_dequeue_returns_none_when_paused():
    q = TaskQueue()
    q.enqueue({"id": "t1"})
    q.pause()
    assert q.dequeue() is None


def test_resume_allows_dequeue():
    q = TaskQueue()
    q.enqueue({"id": "t1"})
    q.pause()
    q.resume()
    assert q.dequeue() is not None


def test_cancel_pending_task():
    q = TaskQueue()
    q.enqueue({"id": "t1"})
    assert q.cancel("t1") is True
    assert q.is_empty() is True


def test_cancel_running_task():
    q = TaskQueue()
    q.enqueue({"id": "t1"})
    q.dequeue()
    assert q.cancel() is True
    assert q.is_empty() is True


def test_cancel_unknown_task_returns_false():
    q = TaskQueue()
    assert q.cancel("missing") is False


def test_progress_counts():
    q = TaskQueue()
    q.enqueue({"id": "t1"})
    q.enqueue({"id": "t2"})
    q.dequeue()
    q.complete_current()
    prog = q.progress()
    assert prog["completed"] == 1
    assert prog["pending"] == 1
    assert prog["total"] == 2


def test_complete_current_clears_running():
    q = TaskQueue()
    q.enqueue({"id": "t1"})
    q.dequeue()
    q.complete_current(result="done")
    assert q.is_empty() is True
    history = q.list_history()
    assert history[0]["status"] == constants.TASK_STATUS_COMPLETED
    assert history[0]["result"] == "done"


def test_fail_current_records_error():
    q = TaskQueue()
    q.enqueue({"id": "t1"})
    q.dequeue()
    q.fail_current(error="boom")
    assert q.is_empty() is True
    history = q.list_history()
    assert history[0]["status"] == constants.TASK_STATUS_FAILED
    assert history[0]["error"] == "boom"


def test_is_empty_true():
    q = TaskQueue()
    assert q.is_empty() is True


def test_is_empty_false_with_pending():
    q = TaskQueue()
    q.enqueue({"id": "t1"})
    assert q.is_empty() is False


def test_is_paused_false_by_default():
    q = TaskQueue()
    assert q.is_paused() is False
