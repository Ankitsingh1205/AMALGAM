from workspace.git import GitInfo


def test_git_info_detects_repository_and_branch(tmp_path):
    root = tmp_path / "project"
    git_dir = root / ".git"
    git_dir.mkdir(parents=True)
    (git_dir / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")

    git = GitInfo()

    assert git.is_repository(root) is True
    assert git.current_branch(root) == "main"


def test_git_info_handles_non_repository(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    git = GitInfo()

    assert git.is_repository(root) is False
    assert git.current_branch(root) == ""

