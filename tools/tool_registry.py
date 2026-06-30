from tools.calculator import Calculator
from tools.python_executor import PythonExecutor
from tools.file_tool import FileTool
from tools.memory_tool import MemoryTool
from tools.internet_tool import InternetTool
from config import constants


class ToolRegistry:

    def __init__(self):

        self.tools = {
            constants.TOOL_CALCULATOR: Calculator(),
            constants.TOOL_PYTHON: PythonExecutor(),
            constants.TOOL_FILES: FileTool(),
            constants.TOOL_MEMORY: MemoryTool(),
            constants.TOOL_INTERNET: InternetTool()
        }

    def get(self, name):

        return self.tools.get(name)

    def list_tools(self):

        return list(self.tools.keys())
