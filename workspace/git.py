from pathlib import Path


class GitInfo:

    def is_repository(self, root):
        return (Path(root) / ".git").exists()

    def current_branch(self, root):
        git_dir = Path(root) / ".git"
        head = git_dir / "HEAD"

        if not head.exists() or not head.is_file():
            return ""

        try:
            content = head.read_text(encoding="utf-8").strip()

        except OSError:
            return ""

        prefix = "ref: refs/heads/"

        if content.startswith(prefix):
            return content[len(prefix):]

        return content[:12]

