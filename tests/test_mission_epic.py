from __future__ import annotations

import pytest

from brain.mission import Epic, Mission, MissionID, MissionPriority, MissionStatus


# ---------------------------------------------------------------------------
# Epic construction
# ---------------------------------------------------------------------------


class TestEpicConstruction:
    def test_defaults(self):
        eid = MissionID.generate()
        epic = Epic(id=eid, title="Test Epic")
        assert epic.id == eid
        assert epic.title == "Test Epic"
        assert epic.description == ""
        assert epic.missions == []
        assert epic.metadata == {}
        assert epic.created_at is not None
        assert epic.updated_at is not None

    def test_explicit_fields(self):
        eid = MissionID.generate()
        epic = Epic(
            id=eid,
            title="Explicit",
            description="Desc",
            metadata={"key": "value"},
        )
        assert epic.description == "Desc"
        assert epic.metadata == {"key": "value"}


# ---------------------------------------------------------------------------
# Add mission
# ---------------------------------------------------------------------------


class TestEpicAddMission:
    def test_add_mission(self):
        epic = Epic(id=MissionID.generate(), title="E")
        mission = Mission(id=MissionID.generate(), title="M")
        epic.add_mission(mission)
        assert mission in epic.missions
        assert len(epic.missions) == 1

    def test_add_multiple_missions(self):
        epic = Epic(id=MissionID.generate(), title="E")
        m1 = Mission(id=MissionID.generate(), title="M1")
        m2 = Mission(id=MissionID.generate(), title="M2")
        epic.add_mission(m1)
        epic.add_mission(m2)
        assert epic.missions == [m1, m2]
        assert len(epic.missions) == 2

    def test_add_preserves_insertion_order(self):
        epic = Epic(id=MissionID.generate(), title="E")
        m1 = Mission(id=MissionID.generate(), title="M1")
        m2 = Mission(id=MissionID.generate(), title="M2")
        m3 = Mission(id=MissionID.generate(), title="M3")
        epic.add_mission(m1)
        epic.add_mission(m2)
        epic.add_mission(m3)
        assert epic.missions[0].title == "M1"
        assert epic.missions[1].title == "M2"
        assert epic.missions[2].title == "M3"

    def test_add_mission_updates_updated_at(self):
        epic = Epic(id=MissionID.generate(), title="E")
        old = epic.updated_at
        import time

        time.sleep(0.01)
        mission = Mission(id=MissionID.generate(), title="M")
        epic.add_mission(mission)
        assert epic.updated_at > old


# ---------------------------------------------------------------------------
# Duplicate prevention
# ---------------------------------------------------------------------------


class TestEpicDuplicatePrevention:
    def test_add_duplicate_mission_raises(self):
        epic = Epic(id=MissionID.generate(), title="E")
        mid = MissionID.generate()
        mission = Mission(id=mid, title="M")
        epic.add_mission(mission)
        with pytest.raises(ValueError, match="already exists"):
            epic.add_mission(Mission(id=mid, title="Duplicate"))

    def test_add_different_missions_with_different_ids(self):
        epic = Epic(id=MissionID.generate(), title="E")
        m1 = Mission(id=MissionID.generate(), title="M1")
        m2 = Mission(id=MissionID.generate(), title="M2")
        epic.add_mission(m1)
        epic.add_mission(m2)  # should not raise
        assert len(epic.missions) == 2


# ---------------------------------------------------------------------------
# Remove mission
# ---------------------------------------------------------------------------


class TestEpicRemoveMission:
    def test_remove_mission(self):
        epic = Epic(id=MissionID.generate(), title="E")
        mission = Mission(id=MissionID.generate(), title="M")
        epic.add_mission(mission)
        epic.remove_mission(mission)
        assert mission not in epic.missions
        assert len(epic.missions) == 0

    def test_remove_mission_noop_when_missing(self):
        epic = Epic(id=MissionID.generate(), title="E")
        mission = Mission(id=MissionID.generate(), title="M")
        epic.remove_mission(mission)  # should not raise
        assert len(epic.missions) == 0

    def test_remove_mission_updates_updated_at(self):
        epic = Epic(id=MissionID.generate(), title="E")
        mission = Mission(id=MissionID.generate(), title="M")
        epic.add_mission(mission)
        old = epic.updated_at
        import time

        time.sleep(0.01)
        epic.remove_mission(mission)
        assert epic.updated_at > old


# ---------------------------------------------------------------------------
# Find mission
# ---------------------------------------------------------------------------


class TestEpicFindMission:
    def test_find_mission_by_mission_id(self):
        epic = Epic(id=MissionID.generate(), title="E")
        mid = MissionID.generate()
        mission = Mission(id=mid, title="M")
        epic.add_mission(mission)
        found = epic.find_mission(mid)
        assert found is mission

    def test_find_mission_by_string(self):
        epic = Epic(id=MissionID.generate(), title="E")
        mid = MissionID.generate()
        mission = Mission(id=mid, title="M")
        epic.add_mission(mission)
        found = epic.find_mission(str(mid))
        assert found is mission

    def test_find_mission_not_found(self):
        epic = Epic(id=MissionID.generate(), title="E")
        assert epic.find_mission(MissionID.generate()) is None

    def test_find_mission_in_empty_epic(self):
        epic = Epic(id=MissionID.generate(), title="E")
        assert epic.find_mission(MissionID.generate()) is None


# ---------------------------------------------------------------------------
# Empty epic
# ---------------------------------------------------------------------------


class TestEpicEmpty:
    def test_empty_epic_has_no_missions(self):
        epic = Epic(id=MissionID.generate(), title="Empty")
        assert epic.missions == []

    def test_empty_epic_to_dict(self):
        epic = Epic(id=MissionID.generate(), title="Empty")
        d = epic.to_dict()
        assert d["missions"] == []
        assert d["title"] == "Empty"


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


class TestEpicSerialization:
    def test_to_dict_structure(self):
        eid = MissionID.generate()
        epic = Epic(id=eid, title="E", description="Desc", metadata={"k": "v"})
        d = epic.to_dict()
        assert d["id"] == str(eid)
        assert d["title"] == "E"
        assert d["description"] == "Desc"
        assert d["missions"] == []
        assert d["metadata"] == {"k": "v"}
        assert "created_at" in d
        assert "updated_at" in d

    def test_to_dict_with_missions(self):
        epic = Epic(id=MissionID.generate(), title="E")
        m1 = Mission(id=MissionID.generate(), title="M1")
        m2 = Mission(id=MissionID.generate(), title="M2")
        epic.add_mission(m1)
        epic.add_mission(m2)
        d = epic.to_dict()
        assert len(d["missions"]) == 2
        assert d["missions"][0]["title"] == "M1"
        assert d["missions"][1]["title"] == "M2"

    def test_to_dict_deterministic_order(self):
        epic = Epic(id=MissionID.generate(), title="E")
        m1 = Mission(id=MissionID.generate(), title="M1")
        m2 = Mission(id=MissionID.generate(), title="M2")
        epic.add_mission(m1)
        epic.add_mission(m2)
        d1 = epic.to_dict()
        d2 = epic.to_dict()
        assert d1["missions"] == d2["missions"]

    def test_from_dict_basic(self):
        eid = MissionID.generate()
        data = {
            "id": str(eid),
            "title": "Restored",
            "description": "Desc",
            "metadata": {"k": "v"},
        }
        restored = Epic.from_dict(data)
        assert restored.id == eid
        assert restored.title == "Restored"
        assert restored.description == "Desc"
        assert restored.metadata == {"k": "v"}
        assert restored.missions == []

    def test_from_dict_with_missions(self):
        eid = MissionID.generate()
        mid = MissionID.generate()
        data = {
            "id": str(eid),
            "title": "E",
            "missions": [
                {
                    "id": str(mid),
                    "title": "M",
                    "description": "MDesc",
                    "priority": MissionPriority.HIGH.value,
                    "status": MissionStatus.RUNNING.value,
                }
            ],
        }
        restored = Epic.from_dict(data)
        assert len(restored.missions) == 1
        assert restored.missions[0].title == "M"
        assert restored.missions[0].description == "MDesc"
        assert restored.missions[0].priority == MissionPriority.HIGH
        assert restored.missions[0].status == MissionStatus.RUNNING

    def test_from_dict_ignores_unknown_keys(self):
        eid = MissionID.generate()
        data = {
            "id": str(eid),
            "title": "T",
            "unknown_key": "should_be_ignored",
        }
        restored = Epic.from_dict(data)
        assert restored.title == "T"

    def test_roundtrip(self):
        eid = MissionID.generate()
        original = Epic(
            id=eid,
            title="Roundtrip",
            description="Desc",
            metadata={"key": "value"},
        )
        m1 = Mission(id=MissionID.generate(), title="M1")
        original.add_mission(m1)
        data = original.to_dict()
        restored = Epic.from_dict(data)
        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.description == original.description
        assert restored.metadata == original.metadata
        assert restored.created_at == original.created_at
        assert restored.updated_at == original.updated_at
        assert len(restored.missions) == 1
        assert restored.missions[0].title == "M1"
