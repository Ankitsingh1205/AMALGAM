class CapabilityRouter:
    """
    Decides which capability should handle a task.
    This class performs routing only.
    """

    def route(self, task):

        action = (task.action or "").lower()
        data = str(task.data or "").lower()

        # Memory
        if action in ["remember", "recall"]:
            return "memory"

        # Diagnostics
        if any(word in data for word in [
            "doctor",
            "diagnostic",
            "diagnostics",
            "health",
            "status",
        ]):
            return "diagnostics"

        # Workspace
        if any(word in data for word in [
            "workspace",
            "project",
            "tree",
            "folder",
            "directory",
            "structure",
        ]):
            return "workspace"

        # Knowledge
        if any(word in data for word in [
            "architecture",
            "import",
            "imports",
            "class",
            "classes",
            "function",
            "functions",
            "service",
            "services",
            "relationship",
        ]):
            return "knowledge"

        # Calculator
        if action == "calculate":
            return "calculator"

        # Python
        if action == "run_python":
            return "python"

        # Files
        if action == "list_files":
            return "files"

        # Default
        return "llm"
