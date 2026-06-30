from workspace.workspace import Workspace


def test_workspace_report_returns_structured_project_report(tmp_path):
    root = tmp_path / "project"
    package = root / "pkg"
    tests = root / "tests"
    package.mkdir(parents=True)
    tests.mkdir()
    (root / "pyproject.toml").write_text('dependencies = [\n"requests",\n]', encoding="utf-8")
    (root / "requirements.txt").write_text("ollama\n", encoding="utf-8")
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "module.py").write_text("", encoding="utf-8")
    (tests / "test_module.py").write_text("", encoding="utf-8")

    report = Workspace(root).report()
    data = report.as_dict()

    assert report.project.name == "project"
    assert report.summary["module_count"] == 2
    assert report.summary["test_count"] == 1
    assert report.summary["dependency_count"] == 2
    assert data["project"]["dependencies"] == ["ollama", "requests"]
    assert data["tree"]["type"] == "directory"


def test_workspace_exposes_simple_api(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    (root / "pyproject.toml").write_text("", encoding="utf-8")

    workspace = Workspace(root)

    assert workspace.root() == root
    assert isinstance(workspace.scan(), list)
    assert workspace.as_dict()["project"]["name"] == "project"

