from pathlib import Path

from workspace.dependency import DependencySummary
from workspace.git import GitInfo
from workspace.project import ProjectInfo


README_FILES = (
    "README.md",
    "README.rst",
    "README.txt",
)


class WorkspaceAnalyzer:

    def __init__(self):
        self.dependencies = DependencySummary()
        self.git = GitInfo()

    def analyze(self, root, paths):
        root = Path(root).resolve()
        files = [path for path in paths if path.is_file()]
        requirements = self.dependencies.read_file(root / "requirements.txt")
        pyproject = self.dependencies.read_file(root / "pyproject.toml")

        return ProjectInfo(
            root=root,
            name=root.name,
            readme=self.read_readme(root),
            requirements=requirements,
            pyproject=pyproject,
            is_git_repository=self.git.is_repository(root),
            git_branch=self.git.current_branch(root),
            python_packages=self.detect_python_packages(root, paths),
            module_count=self.count_modules(files),
            test_count=self.count_tests(files),
            dependencies=self.dependencies.summarize(requirements, pyproject),
        )

    def read_readme(self, root):
        for name in README_FILES:
            path = Path(root) / name

            if path.exists():
                try:
                    return path.read_text(encoding="utf-8")

                except OSError:
                    return ""

        return ""

    def detect_python_packages(self, root, paths):
        packages = []

        for path in paths:
            if path.name != "__init__.py":
                continue

            package_path = path.parent.relative_to(root)

            if package_path == Path("."):
                continue

            packages.append(".".join(package_path.parts))

        return sorted(packages)

    def count_modules(self, files):
        return sum(
            1
            for path in files
            if path.suffix == ".py" and not path.name.startswith("test_")
        )

    def count_tests(self, files):
        return sum(
            1
            for path in files
            if path.suffix == ".py" and path.name.startswith("test_")
        )

