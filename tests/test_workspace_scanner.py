from workspace.scanner import WorkspaceScanner


def test_scanner_detects_project_root_from_nested_path(tmp_path):
    root = tmp_path / "project"
    nested = root / "pkg" / "module"
    nested.mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")

    scanner = WorkspaceScanner()

    assert scanner.detect_root(nested) == root


def test_scanner_skips_cache_and_git_directories(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    (root / "pyproject.toml").write_text("", encoding="utf-8")
    (root / ".git").mkdir()
    (root / ".git" / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
    (root / "__pycache__").mkdir()
    (root / "__pycache__" / "module.pyc").write_text("", encoding="utf-8")
    (root / "app.py").write_text("", encoding="utf-8")

    paths = WorkspaceScanner().scan(root)
    names = {path.name for path in paths}

    assert "app.py" in names
    assert ".git" not in names
    assert "__pycache__" not in names

