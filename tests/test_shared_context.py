import pytest
from brain.shared_context import SharedContext


def test_shared_context_get_set():
    ctx = SharedContext()
    ctx.set("key", "value")
    assert ctx.get("key") == "value"
    assert ctx.get("missing", "default") == "default"


def test_shared_context_update():
    ctx = SharedContext()
    ctx.update({"a": 1, "b": 2})
    assert ctx.get("a") == 1
    assert ctx.get("b") == 2


def test_shared_context_snapshot():
    ctx = SharedContext()
    ctx.set("k", "v")
    snap = ctx.snapshot()
    assert snap == {"k": "v"}
    snap["k"] = "x"
    assert ctx.get("k") == "v"


def test_shared_context_record_and_history():
    ctx = SharedContext()
    ctx.record({"event": "test"})
    hist = ctx.get_history()
    assert len(hist) == 1
    assert hist[0]["event"] == "test"


def test_shared_context_clear():
    ctx = SharedContext()
    ctx.set("k", "v")
    ctx.record({"event": "x"})
    ctx.clear()
    assert ctx.snapshot() == {}
    assert ctx.get_history() == []


def test_shared_context_thread_safety():
    import threading
    ctx = SharedContext()
    errors = []

    def writer():
        try:
            for i in range(100):
                ctx.set("counter", i)
                ctx.update({"a": i})
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=writer) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
