from knowledge.search import KnowledgeSearch


def test_knowledge_search_finds_symbols_documents_and_relationships():
    search = KnowledgeSearch()
    symbols = [
        {
            "name": "Service",
            "qualified_name": "pkg.module.Service",
            "kind": "class",
        }
    ]
    documents = [
        {
            "path": "README.md",
            "title": "Demo",
            "content": "Service docs",
        }
    ]
    relationships = [
        {
            "source": "pkg.module",
            "target": "os",
            "type": "import",
        }
    ]

    assert search.search_symbols("service", symbols) == symbols
    assert search.search_documents("service", documents)[0]["path"] == "README.md"
    assert search.search_relationships("os", relationships) == relationships

