from workspace.analyzer import WorkspaceAnalyzer
from workspace.project import WorkspaceReport
from workspace.scanner import WorkspaceScanner
from workspace.summary import WorkspaceSummary
from workspace.tree import ProjectTree


class Workspace:

    def __init__(self, start_path="."):
        self.start_path = start_path
        self.scanner = WorkspaceScanner()
        self.analyzer = WorkspaceAnalyzer()
        self.tree_builder = ProjectTree()
        self.summary_builder = WorkspaceSummary()

    def root(self):
        return self.scanner.detect_root(self.start_path)

    def scan(self):
        root = self.root()
        return self.scanner.scan(root)

    def report(self):
        root = self.root()
        paths = self.scanner.scan(root)
        tree = self.tree_builder.build(root, paths)
        project = self.analyzer.analyze(root, paths)
        summary = self.summary_builder.create(project, tree)

        return WorkspaceReport(
            project=project,
            tree=tree,
            summary=summary,
        )

    def as_dict(self):
        return self.report().as_dict()

