from workspace.tree import ProjectTree


def test_project_tree_builds_nested_structure(tmp_path):
    root = tmp_path / "project"
    package = root / "pkg"
    package.mkdir(parents=True)
    module = package / "module.py"
    module.write_text("", encoding="utf-8")

    tree = ProjectTree().build(root, [package, module])

    assert tree["name"] == "project"
    assert tree["type"] == "directory"
    assert tree["children"][0]["name"] == "pkg"
    assert tree["children"][0]["children"][0]["name"] == "module.py"

