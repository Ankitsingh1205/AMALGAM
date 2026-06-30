from workspace.analyzer import WorkspaceAnalyzer
from workspace.scanner import WorkspaceScanner


def test_workspace_analyzer_reads_project_metadata(tmp_path):
    root = tmp_path / "project"
    package = root / "pkg"
    tests = root / "tests"
    git_dir = root / ".git"
    package.mkdir(parents=True)
    tests.mkdir()
    git_dir.mkdir()
    (root / "README.md").write_text("# Demo", encoding="utf-8")
    (root / "requirements.txt").write_text("requests\n", encoding="utf-8")
    (root / "pyproject.toml").write_text('dependencies = [\n"ollama",\n]', encoding="utf-8")
    (git_dir / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "module.py").write_text("", encoding="utf-8")
    (tests / "test_module.py").write_text("", encoding="utf-8")

    paths = WorkspaceScanner().scan(root)
    project = WorkspaceAnalyzer().analyze(root, paths)

    assert project.name == "project"
    assert project.readme == "# Demo"
    assert project.is_git_repository is True
    assert project.git_branch == "main"
    assert project.python_packages == ["pkg"]
    assert project.module_count == 2
    assert project.test_count == 1
    assert project.dependencies == ["ollama", "requests"]

