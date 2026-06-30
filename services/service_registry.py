from services.llm import LLMService
from services.memory import MemoryService
from services.ollama_service import OllamaService
from services.project_service import ProjectService
from config import constants


class ServiceRegistry:

    def __init__(self):

        self.services = {
            constants.SERVICE_LLM: LLMService(),
            constants.SERVICE_MEMORY: MemoryService(),
            constants.SERVICE_OLLAMA: OllamaService(),
            constants.SERVICE_PROJECT: ProjectService()
        }

    def get(self, name):

        return self.services.get(name)

    def list_services(self):

        return list(self.services.keys())

