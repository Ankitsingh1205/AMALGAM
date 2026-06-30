from services.memory import MemoryService
from tools.base_tool import BaseTool


class MemoryTool(BaseTool):

    name = "memory"

    def __init__(self):
        self.memory = MemoryService()

    def remember(self, key, value):

        saved = self.memory.remember(key, value)

        if not saved:
            return "Memory Error: could not save memory."

        return f"Stored: {key}"

    def recall(self, key):

        value = self.memory.recall(key)

        if value is None:
            return "Memory not found."

        return value
