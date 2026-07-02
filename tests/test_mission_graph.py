from __future__ import annotations

import pytest

from brain.mission import Mission, MissionGraph, MissionID
from brain.mission.graph import MissionDependency


# ---------------------------------------------------------------------------
# Construction and empty graph
# ---------------------------------------------------------------------------


class TestEmptyGraph:
    def test_empty_graph_has_no_nodes(self):
        graph = MissionGraph()
        assert len(graph) == 0
        assert graph.roots() == []
        assert graph.leaves() == []
        assert graph.topological_sort() == []
        assert graph.has_cycle() is False
        assert graph.validate() is True


# ---------------------------------------------------------------------------
# Single node
# ---------------------------------------------------------------------------


class TestSingleNode:
    def test_add_single_mission(self):
        graph = MissionGraph()
        m = Mission(id=MissionID.generate(), title="M")
        graph.add_mission(m)
        assert len(graph) == 1
        assert m in graph

    def test_single_node_is_root_and_leaf(self):
        graph = MissionGraph()
        m = Mission(id=MissionID.generate(), title="M")
        graph.add_mission(m)
        assert graph.roots() == [m]
        assert graph.leaves() == [m]

    def test_single_node_topological_sort(self):
        graph = MissionGraph()
        m = Mission(id=MissionID.generate(), title="M")
        graph.add_mission(m)
        assert graph.topological_sort() == [m]

    def test_single_node_has_no_dependencies(self):
        graph = MissionGraph()
        m = Mission(id=MissionID.generate(), title="M")
        graph.add_mission(m)
        assert graph.get_dependencies(m) == []
        assert graph.get_dependents(m) == []

    def test_remove_single_mission(self):
        graph = MissionGraph()
        m = Mission(id=MissionID.generate(), title="M")
        graph.add_mission(m)
        graph.remove_mission(m)
        assert len(graph) == 0
        assert m not in graph

    def test_remove_nonexistent_mission_noop(self):
        graph = MissionGraph()
        m = Mission(id=MissionID.generate(), title="M")
        graph.remove_mission(m)  # should not raise
        assert len(graph) == 0


# ---------------------------------------------------------------------------
# Multiple nodes without dependencies
# ---------------------------------------------------------------------------


class TestMultipleNodes:
    def test_add_multiple_missions(self):
        graph = MissionGraph()
        m1 = Mission(id=MissionID.generate(), title="M1")
        m2 = Mission(id=MissionID.generate(), title="M2")
        m3 = Mission(id=MissionID.generate(), title="M3")
        graph.add_mission(m1)
        graph.add_mission(m2)
        graph.add_mission(m3)
        assert len(graph) == 3

    def test_all_are_roots_and_leaves_without_edges(self):
        graph = MissionGraph()
        m1 = Mission(id=MissionID.generate(), title="M1")
        m2 = Mission(id=MissionID.generate(), title="M2")
        graph.add_mission(m1)
        graph.add_mission(m2)
        roots = graph.roots()
        leaves = graph.leaves()
        assert m1 in roots and m2 in roots
        assert m1 in leaves and m2 in leaves
        assert len(roots) == 2
        assert len(leaves) == 2

    def test_duplicate_mission_rejected(self):
        graph = MissionGraph()
        mid = MissionID.generate()
        m1 = Mission(id=mid, title="M1")
        m2 = Mission(id=mid, title="M2")
        graph.add_mission(m1)
        with pytest.raises(ValueError, match="already exists"):
            graph.add_mission(m2)


# ---------------------------------------------------------------------------
# Dependency creation
# ---------------------------------------------------------------------------


class TestDependencyCreation:
    def test_add_single_dependency(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_dependency(a, b)  # B depends on A
        assert graph.get_dependencies(b) == [a]
        assert graph.get_dependents(a) == [b]

    def test_add_chain(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, b)
        graph.add_dependency(b, c)
        assert graph.get_dependencies(b) == [a]
        assert graph.get_dependencies(c) == [b]
        assert graph.get_dependents(a) == [b]
        assert graph.get_dependents(b) == [c]

    def test_add_diamond(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        d = Mission(id=MissionID.generate(), title="D")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_mission(d)
        graph.add_dependency(a, b)
        graph.add_dependency(a, c)
        graph.add_dependency(b, d)
        graph.add_dependency(c, d)
        deps = graph.get_dependencies(d)
        assert len(deps) == 2
        assert set(m.title for m in deps) == {"B", "C"}
        assert set(m.title for m in graph.get_dependents(a)) == {"B", "C"}

    def test_add_dependency_not_in_graph_source(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph.add_mission(b)
        with pytest.raises(ValueError, match="Source mission"):
            graph.add_dependency(a, b)

    def test_add_dependency_not_in_graph_target(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph.add_mission(a)
        with pytest.raises(ValueError, match="Target mission"):
            graph.add_dependency(a, b)


# ---------------------------------------------------------------------------
# Duplicate dependency rejection
# ---------------------------------------------------------------------------


class TestDuplicateDependency:
    def test_duplicate_dependency_rejected(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_dependency(a, b)
        with pytest.raises(ValueError, match="already exists"):
            graph.add_dependency(a, b)

    def test_same_source_different_target(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, b)
        graph.add_dependency(a, c)  # should not raise
        assert len(graph.get_dependents(a)) == 2


# ---------------------------------------------------------------------------
# Dependency removal
# ---------------------------------------------------------------------------


class TestDependencyRemoval:
    def test_remove_existing_dependency(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_dependency(a, b)
        graph.remove_dependency(a, b)
        assert graph.get_dependencies(b) == []
        assert graph.get_dependents(a) == []

    def test_remove_nonexistent_dependency_noop(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.remove_dependency(a, b)  # should not raise
        assert graph.get_dependencies(b) == []
        assert graph.get_dependents(a) == []

    def test_remove_dependency_then_node(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_dependency(a, b)
        graph.remove_dependency(a, b)
        graph.remove_mission(a)
        graph.remove_mission(b)
        assert len(graph) == 0


# ---------------------------------------------------------------------------
# Node removal with dependencies
# ---------------------------------------------------------------------------


class TestNodeRemovalWithEdges:
    def test_remove_node_cleans_incoming_edges(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_dependency(a, b)
        graph.remove_mission(b)
        assert graph.get_dependents(a) == []
        assert len(graph) == 1

    def test_remove_node_cleans_outgoing_edges(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_dependency(a, b)
        graph.remove_mission(a)
        assert graph.get_dependencies(b) == []
        assert len(graph) == 1

    def test_remove_middle_node_in_chain(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, b)
        graph.add_dependency(b, c)
        graph.remove_mission(b)
        assert graph.get_dependents(a) == []
        assert graph.get_dependencies(c) == []
        assert len(graph) == 2


# ---------------------------------------------------------------------------
# Root and leaf detection
# ---------------------------------------------------------------------------


class TestRootLeafDetection:
    def test_roots_in_chain(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, b)
        graph.add_dependency(b, c)
        assert graph.roots() == [a]
        assert graph.leaves() == [c]

    def test_roots_in_diamond(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        d = Mission(id=MissionID.generate(), title="D")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_mission(d)
        graph.add_dependency(a, b)
        graph.add_dependency(a, c)
        graph.add_dependency(b, d)
        graph.add_dependency(c, d)
        assert graph.roots() == [a]
        assert graph.leaves() == [d]

    def test_multiple_roots(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, c)
        assert set(m.title for m in graph.roots()) == {"A", "B"}

    def test_multiple_leaves(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, b)
        graph.add_dependency(a, c)
        assert set(m.title for m in graph.leaves()) == {"B", "C"}


# ---------------------------------------------------------------------------
# Topological sort
# ---------------------------------------------------------------------------


class TestTopologicalSort:
    def test_chain(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, b)
        graph.add_dependency(b, c)
        order = graph.topological_sort()
        assert order.index(a) < order.index(b) < order.index(c)

    def test_diamond(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        d = Mission(id=MissionID.generate(), title="D")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_mission(d)
        graph.add_dependency(a, b)
        graph.add_dependency(a, c)
        graph.add_dependency(b, d)
        graph.add_dependency(c, d)
        order = graph.topological_sort()
        assert order.index(a) < order.index(b)
        assert order.index(a) < order.index(c)
        assert order.index(b) < order.index(d)
        assert order.index(c) < order.index(d)

    def test_disconnected_graph(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        d = Mission(id=MissionID.generate(), title="D")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_mission(d)
        graph.add_dependency(a, b)
        graph.add_dependency(c, d)
        order = graph.topological_sort()
        assert order.index(a) < order.index(b)
        assert order.index(c) < order.index(d)
        assert len(order) == 4

    def test_deterministic(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, b)
        graph.add_dependency(a, c)
        order1 = graph.topological_sort()
        order2 = graph.topological_sort()
        assert [m.title for m in order1] == [m.title for m in order2]


# ---------------------------------------------------------------------------
# Cycle detection
# ---------------------------------------------------------------------------


class TestCycleDetection:
    def test_self_loop(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        graph.add_mission(a)
        with pytest.raises(ValueError, match="cycle"):
            graph.add_dependency(a, a)

    def test_two_node_cycle(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_dependency(a, b)
        with pytest.raises(ValueError, match="cycle"):
            graph.add_dependency(b, a)

    def test_three_node_cycle(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, b)
        graph.add_dependency(b, c)
        with pytest.raises(ValueError, match="cycle"):
            graph.add_dependency(c, a)

    def test_no_cycle_in_valid_graph(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, b)
        graph.add_dependency(b, c)
        assert graph.has_cycle() is False
        assert graph.validate() is True

    def test_has_cycle_on_manually_corrupted_graph(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, b)
        graph.add_dependency(b, c)
        # Manually add a back edge to corrupt the graph
        graph._edges.add(MissionDependency(str(c.id), str(a.id)))
        graph._nodes[str(c.id)].children.add(str(a.id))
        graph._nodes[str(a.id)].parents.add(str(c.id))
        assert graph.has_cycle() is True
        assert graph.validate() is False
        with pytest.raises(ValueError, match="cycle"):
            graph.topological_sort()

    def test_validate_detects_missing_edge_reference(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_dependency(a, b)
        # Corrupt by removing node but leaving edge
        graph._nodes.pop(str(a.id))
        assert graph.validate() is False

    def test_validate_detects_inconsistent_bidirectional(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_dependency(a, b)
        # Break consistency: b no longer knows about a as parent
        graph._nodes[str(b.id)].parents.discard(str(a.id))
        assert graph.validate() is False


# ---------------------------------------------------------------------------
# Graph validation
# ---------------------------------------------------------------------------


class TestGraphValidation:
    def test_valid_graph(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_dependency(a, b)
        assert graph.validate() is True

    def test_empty_graph_valid(self):
        graph = MissionGraph()
        assert graph.validate() is True

    def test_single_node_graph_valid(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        graph.add_mission(a)
        assert graph.validate() is True


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


class TestSerialization:
    def test_to_dict_empty(self):
        graph = MissionGraph()
        d = graph.to_dict()
        assert d["missions"] == []
        assert d["dependencies"] == []

    def test_to_dict_with_nodes_and_edges(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_dependency(a, b)
        d = graph.to_dict()
        assert len(d["missions"]) == 2
        assert len(d["dependencies"]) == 1
        assert d["dependencies"][0] == {
            "source": str(a.id),
            "target": str(b.id),
        }

    def test_from_dict_empty(self):
        graph = MissionGraph.from_dict({"missions": [], "dependencies": []})
        assert len(graph) == 0

    def test_from_dict_with_nodes_and_edges(self):
        a_id = MissionID.generate()
        b_id = MissionID.generate()
        data = {
            "missions": [
                {"id": str(a_id), "title": "A"},
                {"id": str(b_id), "title": "B"},
            ],
            "dependencies": [
                {"source": str(a_id), "target": str(b_id)},
            ],
        }
        graph = MissionGraph.from_dict(data)
        assert len(graph) == 2
        a = graph._nodes[str(a_id)].mission
        b = graph._nodes[str(b_id)].mission
        assert graph.get_dependencies(b) == [a]
        assert graph.get_dependents(a) == [b]

    def test_roundtrip(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, b)
        graph.add_dependency(b, c)
        data = graph.to_dict()
        restored = MissionGraph.from_dict(data)
        assert len(restored) == 3
        ra = restored._nodes[str(a.id)].mission
        rb = restored._nodes[str(b.id)].mission
        rc = restored._nodes[str(c.id)].mission
        assert restored.get_dependencies(rb) == [ra]
        assert restored.get_dependencies(rc) == [rb]
        assert restored.get_dependents(ra) == [rb]
        assert restored.get_dependents(rb) == [rc]
        assert restored.topological_sort() == [ra, rb, rc]

    def test_deterministic_serialization(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_dependency(a, b)
        graph.add_dependency(a, c)
        d1 = graph.to_dict()
        d2 = graph.to_dict()
        assert d1 == d2

    def test_from_dict_ignores_unknown_keys(self):
        data = {
            "missions": [],
            "dependencies": [],
            "extra": "ignored",
        }
        graph = MissionGraph.from_dict(data)
        assert len(graph) == 0


# ---------------------------------------------------------------------------
# Disconnected graphs
# ---------------------------------------------------------------------------


class TestDisconnectedGraphs:
    def test_two_disconnected_chains(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        d = Mission(id=MissionID.generate(), title="D")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_mission(d)
        graph.add_dependency(a, b)
        graph.add_dependency(c, d)
        order = graph.topological_sort()
        assert len(order) == 4
        assert order.index(a) < order.index(b)
        assert order.index(c) < order.index(d)
        assert graph.validate() is True

    def test_roots_and_leaves_in_disconnected(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        c = Mission(id=MissionID.generate(), title="C")
        d = Mission(id=MissionID.generate(), title="D")
        graph.add_mission(a)
        graph.add_mission(b)
        graph.add_mission(c)
        graph.add_mission(d)
        graph.add_dependency(a, b)
        graph.add_dependency(c, d)
        assert set(m.title for m in graph.roots()) == {"A", "C"}
        assert set(m.title for m in graph.leaves()) == {"B", "D"}

    def test_isolated_nodes(self):
        graph = MissionGraph()
        a = Mission(id=MissionID.generate(), title="A")
        b = Mission(id=MissionID.generate(), title="B")
        graph.add_mission(a)
        graph.add_mission(b)
        assert graph.roots() == [a, b]
        assert graph.leaves() == [a, b]
        assert graph.topological_sort() == [a, b]


# ---------------------------------------------------------------------------
# get_dependencies / get_dependents for missing missions
# ---------------------------------------------------------------------------


class TestQueriesForMissing:
    def test_get_dependencies_for_missing_mission(self):
        graph = MissionGraph()
        m = Mission(id=MissionID.generate(), title="M")
        assert graph.get_dependencies(m) == []

    def test_get_dependents_for_missing_mission(self):
        graph = MissionGraph()
        m = Mission(id=MissionID.generate(), title="M")
        assert graph.get_dependents(m) == []
