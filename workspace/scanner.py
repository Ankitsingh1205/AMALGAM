from pathlib import Path


PROJECT_MARKERS = (
    ".git",
    "pyproject.toml",
    "requirements.txt",
    "README.md",
    "README.rst",
    "README.txt",
)

SKIP_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    ".venv",
    "venv",
}


class WorkspaceScanner:

    def detect_root(self, start_path="."):
        path = Path(start_path).resolve()

        if path.is_file():
            path = path.parent

        for candidate in [path, *path.parents]:
            if any((candidate / marker).exists() for marker in PROJECT_MARKERS):
                return candidate

        return path

    def scan(self, root):
        root = Path(root).resolve()
        paths = []

        for path in root.rglob("*"):
            if self.should_skip(path, root):
                continue

            paths.append(path)

        return paths

    def should_skip(self, path, root):
        try:
            relative = path.relative_to(root)
        except ValueError:
            return True

        return any(part in SKIP_DIRECTORIES for part in relative.parts)

