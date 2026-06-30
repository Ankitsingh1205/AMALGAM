from knowledge import KnowledgeEngine


def create_project(root):
    package = root / "pkg"
    docs = root / "docs"
    package.mkdir(parents=True)
    docs.mkdir()
    (root / "README.md").write_text("# Demo\nService overview", encoding="utf-8")
    (root / "pyproject.toml").write_text("", encoding="utf-8")
    (docs / "Architecture.md").write_text("# Architecture\nModule graph", encoding="utf-8")
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "service.py").write_text(
        """
import os

class Service:
    def run(self):
        pass
""",
        encoding="utf-8",
    )


def test_knowledge_engine_builds_structured_report(tmp_path):
    root = tmp_path / "project"
    create_project(root)

    report = KnowledgeEngine(root).build()
    data = report.as_dict()

    assert report.summary["document_count"] == 2
    assert report.summary["class_count"] == 1
    assert report.summary["relationship_count"] >= 1
    assert "documents" in data
    assert "symbols" in data
    assert "graph" in data


def test_knowledge_engine_exposes_search_apis(tmp_path):
    root = tmp_path / "project"
    create_project(root)
    engine = KnowledgeEngine(root)

    assert engine.search_symbols("Service")[0]["qualified_name"] == "pkg.service.Service"
    assert engine.search_documents("overview")[0]["path"] == "README.md"
    assert engine.search_relationships("os")[0]["target"] == "os"

