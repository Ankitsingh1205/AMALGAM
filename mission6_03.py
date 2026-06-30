
"""
Mission 6.1 - Create EngineerAgent
Run from AMALGAM project root:
    python mission6_03.py
"""
from pathlib import Path
import sys

root = Path.cwd()
agents = root / "agents"
agents.mkdir(exist_ok=True)

(agents / "__init__.py").touch(exist_ok=True)

engineer = agents / "engineer.py"

code = """from tools.file_tool import FileTool
from tools.python_executor import PythonExecutor

try:
    from services.project_service import ProjectService
except Exception:
    ProjectService = None


class EngineerAgent:
    def __init__(self):
        self.files = FileTool()
        self.executor = PythonExecutor()
        self.project = ProjectService() if ProjectService else None

    def execute(self, task: str):
        result = {
            "success": True,
            "task": task,
            "project": None,
            "errors": [],
        }

        if self.project:
            try:
                if hasattr(self.project, "summarize"):
                    result["project"] = self.project.summarize()
            except Exception as e:
                result["errors"].append(str(e))

        return result
"""

engineer.write_text(code, encoding="utf-8")

print("[OK] Created", engineer)

try:
    import py_compile
    py_compile.compile(str(engineer), doraise=True)
    print("[OK] Syntax verified")
except Exception as e:
    print("[ERROR]", e)
    sys.exit(1)

print("Mission 6.1 complete")
