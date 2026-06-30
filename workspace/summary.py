class WorkspaceSummary:

    def create(self, project, tree):
        return {
            "name": project.name,
            "root": str(project.root),
            "is_git_repository": project.is_git_repository,
            "git_branch": project.git_branch,
            "package_count": len(project.python_packages),
            "module_count": project.module_count,
            "test_count": project.test_count,
            "dependency_count": len(project.dependencies),
            "top_level_items": len(tree.get("children", [])),
        }

