from knowledge.documents import DocumentReader


def test_document_reader_reads_readme_docs_and_spec(tmp_path):
    root = tmp_path / "project"
    docs = root / "docs"
    spec = root / "spec"
    docs.mkdir(parents=True)
    spec.mkdir()
    (root / "README.md").write_text("# Demo\nRoot docs", encoding="utf-8")
    (docs / "Architecture.md").write_text("# Architecture", encoding="utf-8")
    (spec / "Feature.txt").write_text("Feature spec", encoding="utf-8")

    documents = DocumentReader().read(root)
    paths = [document["path"] for document in documents]

    assert paths == ["README.md", "docs/Architecture.md", "spec/Feature.txt"]
    assert documents[0]["title"] == "Demo"

