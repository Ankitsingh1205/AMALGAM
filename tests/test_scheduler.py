import pytest
from brain.agent_registry import AgentRegistry
from brain.messaging import Messaging
from brain.scheduler import Scheduler
from brain.shared_context import SharedContext


class SuccessAgent:
    def run(self, ctx):
        return {"success": True, "value": 42}


class FailureAgent:
    def run(self, ctx):
        return {"success": False, "error": "bad thing"}


class ExceptionAgent:
    def run(self, ctx):
        raise RuntimeError("boom")


def test_scheduler_pipeline_success():
    reg = AgentRegistry()
    reg.register("a", SuccessAgent())
    reg.register("b", SuccessAgent())
    sched = Scheduler(reg)
    ctx = SharedContext()

    result = sched.run_pipeline(["a", "b"], ctx)
    assert result["success"] is True
    assert "a" in result["results"]
    assert "b" in result["results"]
    assert ctx.get("result_a") == {"success": True, "value": 42}


def test_scheduler_pipeline_missing_agent():
    reg = AgentRegistry()
    sched = Scheduler(reg)
    ctx = SharedContext()

    result = sched.run_pipeline(["missing"], ctx)
    assert result["success"] is False
    assert result["failed_agent"] == "missing"
    assert ctx.get("error") is not None


def test_scheduler_pipeline_failure_agent():
    reg = AgentRegistry()
    reg.register("a", FailureAgent())
    sched = Scheduler(reg)
    ctx = SharedContext()

    result = sched.run_pipeline(["a"], ctx)
    assert result["success"] is False
    assert result["failed_agent"] == "a"


def test_scheduler_pipeline_exception():
    reg = AgentRegistry()
    reg.register("a", ExceptionAgent())
    sched = Scheduler(reg)
    ctx = SharedContext()

    result = sched.run_pipeline(["a"], ctx)
    assert result["success"] is False
    assert result["failed_agent"] == "a"
    assert "boom" in result["error"]


def test_scheduler_parallel():
    reg = AgentRegistry()
    reg.register("a", SuccessAgent())
    reg.register("b", SuccessAgent())
    sched = Scheduler(reg)
    ctx = SharedContext()

    result = sched.run_parallel(["a", "b"], ctx)
    assert result["success"] is True
    assert "a" in result["results"]
    assert "b" in result["results"]


def test_scheduler_parallel_missing():
    reg = AgentRegistry()
    sched = Scheduler(reg)
    ctx = SharedContext()

    result = sched.run_parallel(["missing"], ctx)
    assert result["success"] is False
    assert "missing" in result["errors"]
