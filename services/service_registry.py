from services.llm import LLMService
from services.memory import MemoryService
from services.ollama_service import OllamaService


class ServiceRegistry:

    def __init__(self):

        self.services = {
            "llm": LLMService(),
            "memory": MemoryService(),
            "ollama": OllamaService()
        }

    def get(self, name):

        return self.services.get(name)

    def list_services(self):

        return list(self.services.keys())