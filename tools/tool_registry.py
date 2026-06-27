from tools.calculator import Calculator
from tools.python_executor import PythonExecutor
from tools.file_tool import FileTool


class ToolRegistry:

    def __init__(self):

        self.tools = {
            "calculator": Calculator(),
            "python": PythonExecutor(),
            "files": FileTool()
        }

    def get(self, name):

        return self.tools.get(name)

    def list_tools(self):

        return list(self.tools.keys())