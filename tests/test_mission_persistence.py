from __future__ import annotations

import json
from pathlib import Path

import pytest

from brain.mission import (
    Epic,
    Mission,
    MissionGraph,
    MissionID,
    MissionPersistence,
    MissionPersistenceError,
    MissionStatus,
)


# ---------------------------------------------------------------------------
# Mission save/load
# ---------------------------------------------------------------------------


class TestMissionPersistence:
    def test_save_and_load_mission(self, tmp_path: Path):
        path = tmp_path / "mission.json"
        original = Mission(id=MissionID.generate(), title="M", description="Desc")
        MissionPersistence.save_mission(original, path)
        restored = MissionPersistence.load_mission(path)
        assert restored.title == original.title
        assert restored.description == original.description
        assert restored.id == original.id

    def test_mission_roundtrip_with_status(self, tmp_path: Path):
        path = tmp_path / "mission.json"
        original = Mission(
            id=MissionID.generate(),
            title="M",
            status=MissionStatus.RUNNING,
        )
        MissionPersistence.save_mission(original, path)
        restored = MissionPersistence.load_mission(path)
        assert restored.status == MissionStatus.RUNNING

    def test_mission_with_children_and_dependencies(self, tmp_path: Path):
        path = tmp_path / "mission.json"
        parent = Mission(id=MissionID.generate(), title="Parent")
        child = Mission(id=MissionID.generate(), title="Child")
        dep = Mission(id=MissionID.generate(), title="Dep")
        parent.add_child(child)
        parent.add_dependency(dep)
        MissionPersistence.save_mission(parent, path)
        restored = MissionPersistence.load_mission(path)
        assert len(restored.children) == 1
        assert restored.children[0].title == "Child"
        assert len(restored.dependencies) == 1
        assert restored.dependencies[0].title == "Dep"

    def test_load_mission_missing_file(self, tmp_path: Path):
        path = tmp_path / "missing.json"
        with pytest.raises(MissionPersistenceError):
            MissionPersistence.load_mission(path)

    def test_load_mission_empty_file(self, tmp_path: Path):
        path = tmp_path / "empty.json"
        path.write_text("", encoding="utf-8")
        with pytest.raises(MissionPersistenceError):
            MissionPersistence.load_mission(path)

    def test_load_mission_malformed_json(self, tmp_path: Path):
        path = tmp_path / "bad.json"
        path.write_text("{not json", encoding="utf-8")
        with pytest.raises(MissionPersistenceError, match="Malformed JSON"):
            MissionPersistence.load_mission(path)

    def test_load_mission_corrupted_schema(self, tmp_path: Path):
        path = tmp_path / "corrupted.json"
        path.write_text('"just a string"', encoding="utf-8")
        with pytest.raises(MissionPersistenceError, match="Expected dict"):
            MissionPersistence.load_mission(path)


# ---------------------------------------------------------------------------
# Epic save/load
# ---------------------------------------------------------------------------


class TestEpicPersistence:
    def test_save_and_load_epic(self, tmp_path: Path):
        path = tmp_path / "epic.json"
        original = Epic(id=MissionID.generate(), title="E", description="Desc")
        MissionPersistence.save_epic(original, path)
        restored = MissionPersistence.load_epic(path)
        assert restored.title == original.title
        assert restored.description == original.description
        assert restored.id == original.id

    def test_epic_with_missions(self, tmp_path: Path):
        path = tmp_path / "epic.json"
        epic = Epic(id=MissionID.generate(), title="E")
        m1 = Mission(id=MissionID.generate(), title="M1")
        m2 = Mission(id=MissionID.generate(), title="M2")
        epic.add_mission(m1)
        epic.add_mission(m2)
        MissionPersistence.save_epic(epic, path)
        restored = MissionPersistence.load_epic(path)
        assert len(restored.missions) == 2
        assert restored.missions[0].title == "M1"
        assert restored.missions[1].title == "M2"

    def test_load_epic_missing_file(self, tmp_path: Path):
        path = tmp_path / "missing.json"
        with pytest.raises(MissionPersistenceError):
            MissionPersistence.load_epic(path)

    def test_load_epic_empty_file(self, tmp_path: Path):
        path = tmp_path / "empty.json"
        path.write_text("", encoding="utf-8")
        with pytest.raises(MissionPersistenceError):
            MissionPersistence.load_epic(path)

    def test_load_epic_malformed_json(self, tmp_path: Path):
        path = tmp_path / "bad.json"
        path.write_text("[1, 2, 3", encoding="utf-8")
        with pytest.raises(MissionPersistenceError, match="Malformed JSON"):
            MissionPersistence.load_epic(path)

    def test_load_epic_corrupted_schema(self, tmp_path: Path):
        path = tmp_path / "corrupted.json"
        path.write_text("42", encoding="utf-8")
        with pytest.raises(MissionPersistenceError, match="Expected dict"):
            MissionPersistence.load_epic(path)


# ---------------------------------------------------------------------------
# Graph save/load
# ---------------------------------------------------------------------------


class TestGraphPersistence:
    def test_save_and_load_graph(self, tmp_path: Path):
        path = tmp_path / "graph.json"
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph = MissionGraph()
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_dependency(a, b)
        MissionPersistence.save_graph(graph, path)
        restored = MissionPersistence.load_graph(path)
        assert len(restored) == 2
        assert restored.get_dependencies(b) == [a]
        assert restored.get_dependents(a) == [b]

    def test_load_graph_missing_file(self, tmp_path: Path):
        path = tmp_path / "missing.json"
        restored = MissionPersistence.load_graph(path)
        assert len(restored) == 0

    def test_load_graph_empty_file(self, tmp_path: Path):
        path = tmp_path / "empty.json"
        path.write_text("", encoding="utf-8")
        restored = MissionPersistence.load_graph(path)
        assert len(restored) == 0

    def test_load_graph_malformed_json(self, tmp_path: Path):
        path = tmp_path / "bad.json"
        path.write_text("not json at all", encoding="utf-8")
        with pytest.raises(MissionPersistenceError, match="Malformed JSON"):
            MissionPersistence.load_graph(path)

    def test_load_graph_corrupted_schema(self, tmp_path: Path):
        path = tmp_path / "corrupted.json"
        path.write_text('{"missions": "not a list"}', encoding="utf-8")
        with pytest.raises(MissionPersistenceError):
            MissionPersistence.load_graph(path)

    def test_large_graph_persistence(self, tmp_path: Path):
        path = tmp_path / "large_graph.json"
        graph = MissionGraph()
        missions = [Mission(id=MissionID.generate(), title=f"M{i}") for i in range(20)]
        for m in missions:
            graph.add_mission(m)
        for i in range(19):
            graph.add_dependency(missions[i], missions[i + 1])
        MissionPersistence.save_graph(graph, path)
        restored = MissionPersistence.load_graph(path)
        assert len(restored) == 20
        order = restored.topological_sort()
        assert len(order) == 20
        for i in range(19):
            assert order.index(missions[i]) < order.index(missions[i + 1])


# ---------------------------------------------------------------------------
# save_all / load_all
# ---------------------------------------------------------------------------


class TestSaveAllLoadAll:
    def test_save_all_and_load_all(self, tmp_path: Path):
        path = tmp_path / "all.json"
        m1 = Mission(id=MissionID.generate(), title="M1")
        epic = Epic(id=MissionID.generate(), title="E")
        MissionPersistence.save_all({
            "missions": [m1],
            "epics": [epic],
            "version": "1.0",
        }, path)
        loaded = MissionPersistence.load_all(path)
        assert loaded["version"] == "1.0"
        assert len(loaded["missions"]) == 1
        assert loaded["missions"][0]["title"] == "M1"
        assert len(loaded["epics"]) == 1
        assert loaded["epics"][0]["title"] == "E"

    def test_load_all_missing_file(self, tmp_path: Path):
        path = tmp_path / "missing.json"
        loaded = MissionPersistence.load_all(path)
        assert loaded == {}

    def test_load_all_empty_file(self, tmp_path: Path):
        path = tmp_path / "empty.json"
        path.write_text("", encoding="utf-8")
        loaded = MissionPersistence.load_all(path)
        assert loaded == {}

    def test_load_all_malformed_json(self, tmp_path: Path):
        path = tmp_path / "bad.json"
        path.write_text("{bad json", encoding="utf-8")
        with pytest.raises(MissionPersistenceError, match="Malformed JSON"):
            MissionPersistence.load_all(path)


# ---------------------------------------------------------------------------
# Round-trip persistence
# ---------------------------------------------------------------------------


class TestRoundTrip:
    def test_multiple_missions_roundtrip(self, tmp_path: Path):
        paths = [tmp_path / f"m{i}.json" for i in range(5)]
        originals = [Mission(id=MissionID.generate(), title=f"M{i}") for i in range(5)]
        for m, p in zip(originals, paths):
            MissionPersistence.save_mission(m, p)
        restored = [MissionPersistence.load_mission(p) for p in paths]
        for orig, rest in zip(originals, restored):
            assert orig.id == rest.id
            assert orig.title == rest.title

    def test_repeated_save_load(self, tmp_path: Path):
        path = tmp_path / "mission.json"
        m = Mission(id=MissionID.generate(), title="M")
        for _ in range(5):
            MissionPersistence.save_mission(m, path)
            restored = MissionPersistence.load_mission(path)
            assert restored.id == m.id


# ---------------------------------------------------------------------------
# Stable / deterministic serialization
# ---------------------------------------------------------------------------


class TestDeterministicSerialization:
    def test_mission_output_is_deterministic(self, tmp_path: Path):
        path = tmp_path / "mission.json"
        m = Mission(id=MissionID.generate(), title="M")
        MissionPersistence.save_mission(m, path)
        first = path.read_text(encoding="utf-8")
        MissionPersistence.save_mission(m, path)
        second = path.read_text(encoding="utf-8")
        assert first == second

    def test_epic_output_is_deterministic(self, tmp_path: Path):
        path = tmp_path / "epic.json"
        epic = Epic(id=MissionID.generate(), title="E")
        m1 = Mission(id=MissionID.generate(), title="M1")
        m2 = Mission(id=MissionID.generate(), title="M2")
        epic.add_mission(m1)
        epic.add_mission(m2)
        MissionPersistence.save_epic(epic, path)
        first = path.read_text(encoding="utf-8")
        MissionPersistence.save_epic(epic, path)
        second = path.read_text(encoding="utf-8")
        assert first == second

    def test_graph_output_is_deterministic(self, tmp_path: Path):
        path = tmp_path / "graph.json"
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph = MissionGraph()
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, b)
        graph.add_dependency(a, c)
        MissionPersistence.save_graph(graph, path)
        first = path.read_text(encoding="utf-8")
        MissionPersistence.save_graph(graph, path)
        second = path.read_text(encoding="utf-8")
        assert first == second

    def test_human_readable_json(self, tmp_path: Path):
        path = tmp_path / "mission.json"
        m = Mission(id=MissionID.generate(), title="M")
        MissionPersistence.save_mission(m, path)
        text = path.read_text(encoding="utf-8")
        assert "    " in text  # pretty-printed with indent
        assert "\n" in text
        assert json.loads(text)  # valid JSON

    def test_utf8_encoding(self, tmp_path: Path):
        path = tmp_path / "mission.json"
        m = Mission(id=MissionID.generate(), title="日本語", description="テスト")
        MissionPersistence.save_mission(m, path)
        restored = MissionPersistence.load_mission(path)
        assert restored.title == "日本語"
        assert restored.description == "テスト"


# ---------------------------------------------------------------------------
# Parent directory creation
# ---------------------------------------------------------------------------


class TestDirectoryCreation:
    def test_creates_nested_directories(self, tmp_path: Path):
        path = tmp_path / "a" / "b" / "c" / "mission.json"
        m = Mission(id=MissionID.generate(), title="M")
        MissionPersistence.save_mission(m, path)
        assert path.exists()
