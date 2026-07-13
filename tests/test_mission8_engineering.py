"""Mission 8 repository-awareness, authority, reasoning and commit tests."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from brain.engineering_contracts import EngineeringPlan, PlanTask, RepairStrategy
from brain.engineering_controller import AuthorityError, EngineeringController
from brain.mission_checkpoint import MissionCheckpointStore
from brain.repository_context import RepositoryContextEngine
from brain.structured_reasoning import StructuredReasoner
from services.git_service import GitSafetyError, GitService
from services.llm import LLMService, StructuredLLMError


class FakeClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = 0
    def chat(self, **kwargs):
        self.calls += 1
        item = next(self.responses)
        if isinstance(item, Exception):
            raise item
        return {"message": {"content": item}}


class FixedReasoner:
    def __init__(self, plan):
        self.fixed = plan
        self.calls = 0
    def plan(self, goal, context):
        self.calls += 1
        return self.fixed


class SequenceReasoner:
    def __init__(self, plans):
        self.plans = iter(plans)
        self.calls = 0
    def plan(self, goal, context):
        self.calls += 1
        return next(self.plans)


def git(root: Path, *args: str):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()


def init_repository(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "Test")
    (tmp_path / ".gitignore").write_text(".amalgam-core/MISSION_8_STATE.json\n", encoding="utf-8")
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "check.py").write_text(
        "from pathlib import Path\nassert Path('hello.txt').read_text() == 'hello\\n'\n",
        encoding="utf-8",
    )
    docs = tmp_path / "docs" / "00_START_HERE"
    docs.mkdir(parents=True)
    (docs / "ROADMAP_CANON.md").write_text("Mission 8 IN PROGRESS", encoding="utf-8")
    (docs / "MISSION_8_MASTER_ARCHITECTURE.md").write_text("FROZEN", encoding="utf-8")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "fixture")
    return tmp_path


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    return init_repository(tmp_path)


def write_plan() -> EngineeringPlan:
    return EngineeringPlan(
        plan_id="plan-1", goal="create greeting",
        tasks=[PlanTask(
            id="write", description="write greeting", action="write_file", capability="files",
            affected_paths=["hello.txt"], acceptance_criteria=["file contains hello"],
            data={"path": "hello.txt", "content": "hello\n"},
        )],
        verification_commands=["python scripts/check.py"],
    )


def test_plan_hash_is_canonical_and_scope_sensitive():
    first = write_plan()
    second = write_plan()
    assert first.plan_hash == second.plan_hash
    second.tasks[0].affected_paths = ["other.txt"]
    assert first.plan_hash != second.plan_hash


def test_plan_rejects_cycles():
    plan = write_plan()
    plan.tasks.append(PlanTask("two", "second", "list_files", "files", ["write"], acceptance_criteria=["listed"]))
    plan.tasks[0].dependencies = ["two"]
    with pytest.raises(ValueError, match="cycle"):
        plan.validate()


def test_repository_context_recovers_without_chat(repository):
    context = RepositoryContextEngine(repository).build()
    assert context.mission == "Mission 8"
    assert context.branch
    assert "Mission 8" in context.summaries["roadmap"]
    assert context.next_action == "run"


def test_checkpoint_is_atomic_and_rejects_unknown_state(tmp_path):
    store = MissionCheckpointStore(tmp_path)
    state = store.transition("awaiting_approval", plan_id="p")
    assert state["plan_id"] == "p"
    assert not store.path.with_suffix(".tmp").exists()
    with pytest.raises(ValueError, match="invalid lifecycle"):
        store.transition("invented")


def test_structured_llm_repairs_invalid_json():
    client = FakeClient(["not-json", '{"ok": true}'])
    service = LLMService(client=client)
    result = service.ask_structured("x", "qwen2.5-coder:7b", "system",
                                    lambda value: None, retries=1)
    assert result["ok"] is True
    assert result["_meta"]["attempt"] == 2


def test_structured_llm_fails_closed():
    service = LLMService(client=FakeClient(["bad", "still bad"]))
    with pytest.raises(StructuredLLMError):
        service.ask_structured("x", "model", "system", lambda value: None, retries=1)


def test_deterministic_control_intent_needs_no_model(repository):
    reasoner = StructuredReasoner(llm=LLMService(client=FakeClient([])))
    context = RepositoryContextEngine(repository).build()
    result = reasoner.classify("status", context)
    assert result["action"] == "status"
    assert result["requires_plan"] is False


def test_no_modification_before_exact_approval(tmp_path):
    root = init_repository(tmp_path)
    controller = EngineeringController(root, reasoner=FixedReasoner(write_plan()))
    result = controller.run("create greeting")
    assert result["status"] == "awaiting_approval"
    assert not (root / "hello.txt").exists()
    with pytest.raises(AuthorityError):
        controller.approve("wrong-plan")
    assert not (root / "hello.txt").exists()


def test_approval_executes_tests_reviews_and_local_commit(tmp_path):
    root = init_repository(tmp_path)
    controller = EngineeringController(root, reasoner=FixedReasoner(write_plan()))
    pending = controller.run("create greeting")
    result = controller.approve(pending["plan"]["plan_id"])
    assert result["status"] == "completed"
    assert (root / "hello.txt").read_text() == "hello\n"
    assert result["review"]["approved"] is True
    assert git(root, "show", "HEAD:hello.txt") == "hello"


def test_changed_plan_invalidates_approval(tmp_path):
    root = init_repository(tmp_path)
    controller = EngineeringController(root, reasoner=FixedReasoner(write_plan()))
    controller.run("create greeting")
    state = controller.store.load()
    state["plan"]["goal"] = "expanded scope"
    controller.store.save(state)
    with pytest.raises(AuthorityError, match="changed"):
        controller.approve("plan-1")


def test_unplanned_change_blocks_execution(tmp_path):
    root = init_repository(tmp_path)
    controller = EngineeringController(root, reasoner=FixedReasoner(write_plan()))
    controller.run("create greeting")
    (root / "intruder.txt").write_text("unexpected")
    result = controller.approve("plan-1")
    assert result["status"] == "blocked"
    assert result["requires_human_help"] is True


def test_abort_clears_approval(tmp_path):
    root = init_repository(tmp_path)
    controller = EngineeringController(root, reasoner=FixedReasoner(write_plan()))
    controller.run("create greeting")
    assert controller.abort()["status"] == "aborted"
    with pytest.raises(AuthorityError):
        controller.approve("plan-1")


def test_git_service_rejects_unplanned_path(tmp_path):
    root = init_repository(tmp_path)
    (root / "other.txt").write_text("x")
    with pytest.raises(GitSafetyError, match="unplanned"):
        GitService(root).local_commit("bad", {"hello.txt"})


def test_git_service_rejects_secret_in_untracked_file(tmp_path):
    root = init_repository(tmp_path)
    (root / "config.txt").write_text("api_key=super-secret")
    service = GitService(root)
    # Secret scanning is enforced over staged diff/content before commit.
    with pytest.raises(GitSafetyError, match="secret"):
        service.local_commit("bad", {"config.txt"})


def test_failed_review_creates_fresh_approval_boundary(tmp_path):
    root = init_repository(tmp_path)
    broken = write_plan()
    broken.verification_commands = ["python scripts/missing.py"]
    repaired = write_plan()
    repaired.plan_id = "repair-2"
    controller = EngineeringController(root, reasoner=SequenceReasoner([broken, repaired]))
    pending = controller.run("create greeting")
    result = controller.approve(pending["plan"]["plan_id"])
    assert result["status"] == "awaiting_approval"
    assert result["reason"] == "mandatory review failed"
    assert result["repair_plan"]["plan_id"] == "repair-2"
    assert controller.store.load()["approved_plan_hash"] is None


def test_repair_limit_stops_and_requests_human_help(tmp_path):
    root = init_repository(tmp_path)
    controller = EngineeringController(root, reasoner=FixedReasoner(write_plan()))
    controller.store.transition(
        "repair", goal="x", repair_count=controller.MAX_REPAIRS,
    )
    result = controller._repair_or_block(write_plan(), "persistent failure", ["same evidence"])
    assert result["status"] == "blocked"
    assert result["requires_human_help"] is True


def test_repair_strategy_hash_changes_with_strategy():
    first = RepairStrategy("test", "cause", ["e"], "change A", ["a"])
    second = RepairStrategy("test", "cause", ["e"], "change B", ["b"])
    assert first.strategy_hash != second.strategy_hash
