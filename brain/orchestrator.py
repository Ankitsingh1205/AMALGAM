from services.memory import MemoryService
from services.llm import LLMService
from brain.router import Router
from config import constants, settings


class Orchestrator:

    def __init__(self):
        self.version = settings.APP_VERSION
        self.memory = MemoryService()
        self.llm = LLMService()
        self.router = Router()

    def start(self):
        print(constants.BUILD_SEPARATOR * 50)
        print(settings.APP_NAME)
        print(f"Version : {self.version}")
        print(constants.BUILD_SEPARATOR * 50)

    def process(self, user_input: str):

        # Memory Commands
        if user_input.lower().startswith("remember "):

            data = user_input[9:]

            if "=" not in data:
                print("Format: remember key=value")
                return

            key, value = data.split("=", 1)

            self.memory.remember(key.strip(), value.strip())

            print(f"Stored: {key.strip()}")

            return

        if user_input.lower().startswith("recall "):

            key = user_input[7:].strip()

            value = self.memory.recall(key)

            if value:
                print(value)
            else:
                print("Memory not found.")

            return

        # AI Model Selection
        model = self.router.choose_model(user_input)

        print(f"\n[Model Selected: {model}]")

        answer = self.llm.ask(user_input, model)

        print("\nAMALGAM:\n")
        print(answer)
