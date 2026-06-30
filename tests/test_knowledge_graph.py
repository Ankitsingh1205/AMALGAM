from knowledge.graph import KnowledgeGraph


def test_knowledge_graph_builds_nodes_and_edges():
    symbols = [
        {
            "name": "module",
            "qualified_name": "pkg.module",
            "kind": "module",
            "module": "pkg.module",
            "line": 1,
        }
    ]
    relationships = [
        {
            "source": "pkg.module",
            "target": "os",
            "type": "import",
            "line": 1,
        }
    ]

    graph = KnowledgeGraph().build(symbols, relationships)

    assert {node["id"] for node in graph["nodes"]} == {"pkg.module", "os"}
    assert graph["edges"] == [
        {
            "source": "pkg.module",
            "target": "os",
            "type": "import",
        }
    ]

