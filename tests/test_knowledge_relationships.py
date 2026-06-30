from knowledge.relationships import RelationshipBuilder


def test_relationship_builder_extracts_import_and_package_relationships(tmp_path):
    root = tmp_path / "project"
    package = root / "pkg"
    subpackage = package / "sub"
    subpackage.mkdir(parents=True)
    module = subpackage / "module.py"
    module.write_text("from pkg import service\n", encoding="utf-8")

    relationships = RelationshipBuilder().build(
        root,
        [module],
        ["pkg", "pkg.sub"],
    )

    assert {
        (item["source"], item["target"], item["type"])
        for item in relationships
    } == {
        ("pkg.sub.module", "pkg", "import"),
        ("pkg", "pkg.sub", "package"),
    }

