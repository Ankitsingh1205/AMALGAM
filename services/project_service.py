from workspace import Workspace
from knowledge import KnowledgeEngine


class ProjectService:

    def __init__(self, root="."):
        self.root = root

    def summarize(self):

        workspace = Workspace(self.root).report()
        knowledge = KnowledgeEngine(self.root).build()

        return {
            "workspace": workspace.as_dict(),
            "knowledge": knowledge.as_dict(),
            "summary": {
                "project_root": workspace.project.root,
                "python_packages": workspace.project.python_packages,
                "documents": len(knowledge.documents),
                "symbols": len(knowledge.symbols),
                "relationships": len(knowledge.relationships),
            },
        }