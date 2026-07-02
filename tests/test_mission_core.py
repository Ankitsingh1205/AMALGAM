from __future__ import annotations

import pytest

from brain.mission import Mission, MissionID, MissionPriority, MissionStatus


# ---------------------------------------------------------------------------
# MissionID
# ---------------------------------------------------------------------------


class TestMissionID:
    def test_generate_returns_mission_id(self):
        mid = MissionID.generate()
        assert isinstance(mid, MissionID)

    def test_generate_returns_valid_uuid4(self):
        mid = MissionID.generate()
        assert MissionID.validate(str(mid)) is True

    def test_validate_accepts_valid_uuid4(self):
        assert MissionID.validate("550e8400-e29b-41d4-a716-446655440000") is True

    def test_validate_rejects_version_1_uuid(self):
        assert MissionID.validate("a0eebc99-9c0b-1ef8-bb6d-6bb9bd380a11") is False  # version 1

    def test_validate_rejects_invalid_string(self):
        assert MissionID.validate("not-a-uuid") is False

    def test_validate_rejects_empty_string(self):
        assert MissionID.validate("") is False

    def test_validate_rejects_non_string(self):
        assert MissionID.validate(None) is False  # type: ignore[arg-type]
        assert MissionID.validate(123) is False  # type: ignore[arg-type]

    def test_equality(self):
        mid1 = MissionID("550e8400-e29b-41d4-a716-446655440000")
        mid2 = MissionID("550e8400-e29b-41d4-a716-446655440000")
        mid3 = MissionID("550e8400-e29b-41d4-a716-446655440001")
        assert mid1 == mid2
        assert mid1 != mid3
        assert mid1 != "550e8400-e29b-41d4-a716-446655440000"

    def test_hash(self):
        mid = MissionID("550e8400-e29b-41d4-a716-446655440000")
        assert hash(mid) == hash("550e8400-e29b-41d4-a716-446655440000")

    def test_str(self):
        mid = MissionID("550e8400-e29b-41d4-a716-446655440000")
        assert str(mid) == "550e8400-e29b-41d4-a716-446655440000"

    def test_repr(self):
        mid = MissionID("550e8400-e29b-41d4-a716-446655440000")
        assert repr(mid) == "MissionID('550e8400-e29b-41d4-a716-446655440000')"


# ---------------------------------------------------------------------------
# MissionPriority
# ---------------------------------------------------------------------------


class TestMissionPriority:
    def test_values(self):
        assert MissionPriority.LOW == 1
        assert MissionPriority.NORMAL == 5
        assert MissionPriority.HIGH == 10
        assert MissionPriority.CRITICAL == 20

    def test_ordering(self):
        assert MissionPriority.LOW < MissionPriority.NORMAL
        assert MissionPriority.NORMAL < MissionPriority.HIGH
        assert MissionPriority.HIGH < MissionPriority.CRITICAL

    def test_is_int_enum(self):
        assert isinstance(MissionPriority.NORMAL, int)


# ---------------------------------------------------------------------------
# MissionStatus
# ---------------------------------------------------------------------------


class TestMissionStatus:
    def test_values(self):
        assert MissionStatus.CREATED.value == "created"
        assert MissionStatus.ANALYZING.value == "analyzing"
        assert MissionStatus.PLANNING.value == "planning"
        assert MissionStatus.READY.value == "ready"
        assert MissionStatus.RUNNING.value == "running"
        assert MissionStatus.VERIFYING.value == "verifying"
        assert MissionStatus.COMPLETED.value == "completed"
        assert MissionStatus.FAILED.value == "failed"
        assert MissionStatus.RECOVERING.value == "recovering"
        assert MissionStatus.CANCELLED.value == "cancelled"

    def test_terminal_states(self):
        assert MissionStatus.COMPLETED.is_terminal() is True
        assert MissionStatus.FAILED.is_terminal() is True
        assert MissionStatus.CANCELLED.is_terminal() is True

    def test_non_terminal_states(self):
        assert MissionStatus.CREATED.is_terminal() is False
        assert MissionStatus.ANALYZING.is_terminal() is False
        assert MissionStatus.PLANNING.is_terminal() is False
        assert MissionStatus.READY.is_terminal() is False
        assert MissionStatus.RUNNING.is_terminal() is False
        assert MissionStatus.VERIFYING.is_terminal() is False
        assert MissionStatus.RECOVERING.is_terminal() is False


# ---------------------------------------------------------------------------
# Mission construction
# ---------------------------------------------------------------------------


class TestMissionConstruction:
    def test_defaults(self):
        mid = MissionID.generate()
        mission = Mission(id=mid, title="Test")
        assert mission.id == mid
        assert mission.title == "Test"
        assert mission.description == ""
        assert mission.priority == MissionPriority.NORMAL
        assert mission.status == MissionStatus.CREATED
        assert mission.owner is None
        assert mission.children == []
        assert mission.dependencies == []
        assert mission.metadata == {}
        assert mission.created_at is not None
        assert mission.updated_at is not None

    def test_explicit_fields(self):
        mid = MissionID.generate()
        mission = Mission(
            id=mid,
            title="Explicit",
            description="Desc",
            priority=MissionPriority.HIGH,
            status=MissionStatus.RUNNING,
            owner="agent-1",
            metadata={"key": "value"},
        )
        assert mission.description == "Desc"
        assert mission.priority == MissionPriority.HIGH
        assert mission.status == MissionStatus.RUNNING
        assert mission.owner == "agent-1"
        assert mission.metadata == {"key": "value"}


# ---------------------------------------------------------------------------
# Status transitions
# ---------------------------------------------------------------------------


class TestMissionTransitions:
    def _make(self, status: MissionStatus = MissionStatus.CREATED) -> Mission:
        return Mission(id=MissionID.generate(), title="T", status=status)

    def test_created_to_analyzing(self):
        m = self._make(MissionStatus.CREATED)
        m.transition(MissionStatus.ANALYZING)
        assert m.status == MissionStatus.ANALYZING

    def test_analyzing_to_planning(self):
        m = self._make(MissionStatus.ANALYZING)
        m.transition(MissionStatus.PLANNING)
        assert m.status == MissionStatus.PLANNING

    def test_planning_to_ready(self):
        m = self._make(MissionStatus.PLANNING)
        m.transition(MissionStatus.READY)
        assert m.status == MissionStatus.READY

    def test_ready_to_running(self):
        m = self._make(MissionStatus.READY)
        m.transition(MissionStatus.RUNNING)
        assert m.status == MissionStatus.RUNNING

    def test_running_to_verifying(self):
        m = self._make(MissionStatus.RUNNING)
        m.transition(MissionStatus.VERIFYING)
        assert m.status == MissionStatus.VERIFYING

    def test_verifying_to_completed(self):
        m = self._make(MissionStatus.VERIFYING)
        m.transition(MissionStatus.COMPLETED)
        assert m.status == MissionStatus.COMPLETED

    def test_running_to_recovering(self):
        m = self._make(MissionStatus.RUNNING)
        m.transition(MissionStatus.RECOVERING)
        assert m.status == MissionStatus.RECOVERING

    def test_recovering_to_analyzing(self):
        m = self._make(MissionStatus.RECOVERING)
        m.transition(MissionStatus.ANALYZING)
        assert m.status == MissionStatus.ANALYZING

    def test_recovering_to_planning(self):
        m = self._make(MissionStatus.RECOVERING)
        m.transition(MissionStatus.PLANNING)
        assert m.status == MissionStatus.PLANNING

    def test_recovering_to_ready(self):
        m = self._make(MissionStatus.RECOVERING)
        m.transition(MissionStatus.READY)
        assert m.status == MissionStatus.READY

    def test_recovering_to_running(self):
        m = self._make(MissionStatus.RECOVERING)
        m.transition(MissionStatus.RUNNING)
        assert m.status == MissionStatus.RUNNING

    def test_idempotent_transition(self):
        m = self._make(MissionStatus.RUNNING)
        old_updated = m.updated_at
        m.transition(MissionStatus.RUNNING)
        assert m.status == MissionStatus.RUNNING
        assert m.updated_at == old_updated

    def test_invalid_transition_created_to_completed(self):
        m = self._make(MissionStatus.CREATED)
        with pytest.raises(ValueError, match="Invalid transition"):
            m.transition(MissionStatus.COMPLETED)

    def test_invalid_transition_analyzing_to_running(self):
        m = self._make(MissionStatus.ANALYZING)
        with pytest.raises(ValueError, match="Invalid transition"):
            m.transition(MissionStatus.RUNNING)

    def test_invalid_transition_ready_to_analyzing(self):
        m = self._make(MissionStatus.READY)
        with pytest.raises(ValueError, match="Invalid transition"):
            m.transition(MissionStatus.ANALYZING)

    def test_invalid_transition_from_terminal_completed(self):
        m = self._make(MissionStatus.COMPLETED)
        with pytest.raises(ValueError, match="Cannot transition from terminal state"):
            m.transition(MissionStatus.FAILED)

    def test_invalid_transition_from_terminal_failed(self):
        m = self._make(MissionStatus.FAILED)
        with pytest.raises(ValueError, match="Cannot transition from terminal state"):
            m.transition(MissionStatus.CREATED)

    def test_invalid_transition_from_terminal_cancelled(self):
        m = self._make(MissionStatus.CANCELLED)
        with pytest.raises(ValueError, match="Cannot transition from terminal state"):
            m.transition(MissionStatus.RUNNING)

    def test_universal_sink_failed(self):
        for status in MissionStatus:
            if status.is_terminal():
                continue
            m = self._make(status)
            m.transition(MissionStatus.FAILED)
            assert m.status == MissionStatus.FAILED

    def test_universal_sink_cancelled(self):
        for status in MissionStatus:
            if status.is_terminal():
                continue
            m = self._make(status)
            m.transition(MissionStatus.CANCELLED)
            assert m.status == MissionStatus.CANCELLED

    def test_updated_at_changes_on_valid_transition(self):
        m = self._make(MissionStatus.CREATED)
        old = m.updated_at
        import time
        time.sleep(0.01)
        m.transition(MissionStatus.ANALYZING)
        assert m.updated_at > old


# ---------------------------------------------------------------------------
# Children
# ---------------------------------------------------------------------------


class TestMissionChildren:
    def test_add_child(self):
        parent = Mission(id=MissionID.generate(), title="Parent")
        child = Mission(id=MissionID.generate(), title="Child")
        parent.add_child(child)
        assert child in parent.children
        assert len(parent.children) == 1

    def test_add_child_is_idempotent(self):
        parent = Mission(id=MissionID.generate(), title="Parent")
        child = Mission(id=MissionID.generate(), title="Child")
        parent.add_child(child)
        parent.add_child(child)
        assert len(parent.children) == 1

    def test_remove_child(self):
        parent = Mission(id=MissionID.generate(), title="Parent")
        child = Mission(id=MissionID.generate(), title="Child")
        parent.add_child(child)
        parent.remove_child(child)
        assert child not in parent.children
        assert len(parent.children) == 0

    def test_remove_child_noop_when_missing(self):
        parent = Mission(id=MissionID.generate(), title="Parent")
        child = Mission(id=MissionID.generate(), title="Child")
        parent.remove_child(child)  # should not raise
        assert len(parent.children) == 0


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------


class TestMissionDependencies:
    def test_add_dependency(self):
        m1 = Mission(id=MissionID.generate(), title="M1")
        dep = Mission(id=MissionID.generate(), title="Dep")
        m1.add_dependency(dep)
        assert dep in m1.dependencies
        assert len(m1.dependencies) == 1

    def test_add_dependency_is_idempotent(self):
        m1 = Mission(id=MissionID.generate(), title="M1")
        dep = Mission(id=MissionID.generate(), title="Dep")
        m1.add_dependency(dep)
        m1.add_dependency(dep)
        assert len(m1.dependencies) == 1

    def test_remove_dependency(self):
        m1 = Mission(id=MissionID.generate(), title="M1")
        dep = Mission(id=MissionID.generate(), title="Dep")
        m1.add_dependency(dep)
        m1.remove_dependency(dep)
        assert dep not in m1.dependencies
        assert len(m1.dependencies) == 0

    def test_remove_dependency_noop_when_missing(self):
        m1 = Mission(id=MissionID.generate(), title="M1")
        dep = Mission(id=MissionID.generate(), title="Dep")
        m1.remove_dependency(dep)  # should not raise
        assert len(m1.dependencies) == 0


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


class TestMissionSerialization:
    def test_to_dict_structure(self):
        mid = MissionID.generate()
        mission = Mission(id=mid, title="T", description="D", owner="O")
        d = mission.to_dict()
        assert d["id"] == str(mid)
        assert d["title"] == "T"
        assert d["description"] == "D"
        assert d["priority"] == MissionPriority.NORMAL.value
        assert d["status"] == MissionStatus.CREATED.value
        assert d["owner"] == "O"
        assert d["children"] == []
        assert d["dependencies"] == []
        assert d["metadata"] == {}
        assert "created_at" in d
        assert "updated_at" in d

    def test_to_dict_with_nested_children(self):
        parent = Mission(id=MissionID.generate(), title="Parent")
        child = Mission(id=MissionID.generate(), title="Child")
        parent.add_child(child)
        d = parent.to_dict()
        assert len(d["children"]) == 1
        assert d["children"][0]["title"] == "Child"

    def test_to_dict_with_nested_dependencies(self):
        m1 = Mission(id=MissionID.generate(), title="M1")
        dep = Mission(id=MissionID.generate(), title="Dep")
        m1.add_dependency(dep)
        d = m1.to_dict()
        assert len(d["dependencies"]) == 1
        assert d["dependencies"][0]["title"] == "Dep"

    def test_from_dict_basic(self):
        mid = MissionID.generate()
        data = {
            "id": str(mid),
            "title": "Restored",
            "description": "Desc",
            "priority": MissionPriority.HIGH.value,
            "status": MissionStatus.RUNNING.value,
            "owner": "agent-1",
            "metadata": {"k": "v"},
        }
        restored = Mission.from_dict(data)
        assert restored.id == mid
        assert restored.title == "Restored"
        assert restored.description == "Desc"
        assert restored.priority == MissionPriority.HIGH
        assert restored.status == MissionStatus.RUNNING
        assert restored.owner == "agent-1"
        assert restored.metadata == {"k": "v"}

    def test_from_dict_with_children(self):
        mid = MissionID.generate()
        data = {
            "id": str(mid),
            "title": "Parent",
            "children": [
                {"id": str(MissionID.generate()), "title": "Child"},
            ],
        }
        restored = Mission.from_dict(data)
        assert len(restored.children) == 1
        assert restored.children[0].title == "Child"

    def test_from_dict_with_dependencies(self):
        mid = MissionID.generate()
        data = {
            "id": str(mid),
            "title": "M1",
            "dependencies": [
                {"id": str(MissionID.generate()), "title": "Dep"},
            ],
        }
        restored = Mission.from_dict(data)
        assert len(restored.dependencies) == 1
        assert restored.dependencies[0].title == "Dep"

    def test_from_dict_ignores_unknown_keys(self):
        mid = MissionID.generate()
        data = {
            "id": str(mid),
            "title": "T",
            "unknown_key": "should_be_ignored",
        }
        restored = Mission.from_dict(data)
        assert restored.title == "T"

    def test_roundtrip(self):
        mid = MissionID.generate()
        original = Mission(
            id=mid,
            title="Roundtrip",
            description="Desc",
            priority=MissionPriority.CRITICAL,
            status=MissionStatus.VERIFYING,
            owner="owner-1",
            metadata={"key": "value"},
        )
        data = original.to_dict()
        restored = Mission.from_dict(data)
        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.description == original.description
        assert restored.priority == original.priority
        assert restored.status == original.status
        assert restored.owner == original.owner
        assert restored.metadata == original.metadata
        assert restored.created_at == original.created_at
        assert restored.updated_at == original.updated_at
