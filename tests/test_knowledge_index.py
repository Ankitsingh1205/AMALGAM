from knowledge.index import KnowledgeIndex


def test_knowledge_index_builds_lookup_maps():
    documents = [{"path": "README.md", "content": "docs"}]
    symbols = [{"qualified_name": "pkg.module", "kind": "module"}]
    relationships = [{"source": "pkg.module", "target": "os", "type": "import"}]

    index = KnowledgeIndex().build(documents, symbols, relationships)

    assert index["documents"]["README.md"] == documents[0]
    assert index["symbols"]["pkg.module"] == symbols[0]
    assert index["relationships"] == relationships

