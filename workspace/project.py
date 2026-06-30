from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProjectInfo:
    root: Path
    name: str
    readme: str = ""
    requirements: str = ""
    pyproject: str = ""
    is_git_repository: bool = False
    git_branch: str = ""
    python_packages: list[str] = field(default_factory=list)
    module_count: int = 0
    test_count: int = 0
    dependencies: list[str] = field(default_factory=list)


@dataclass
class WorkspaceReport:
    project: ProjectInfo
    tree: dict
    summary: dict

    def as_dict(self):
        return {
            "project": {
                "root": str(self.project.root),
                "name": self.project.name,
                "readme": self.project.readme,
                "requirements": self.project.requirements,
                "pyproject": self.project.pyproject,
                "is_git_repository": self.project.is_git_repository,
                "git_branch": self.project.git_branch,
                "python_packages": self.project.python_packages,
                "module_count": self.project.module_count,
                "test_count": self.project.test_count,
                "dependencies": self.project.dependencies,
            },
            "tree": self.tree,
            "summary": self.summary,
        }

