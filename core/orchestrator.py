from services.memory import MemoryService


class Orchestrator:
    def __init__(self):
        self.version = "Genesis"
        self.status = "Initializing"
        self.memory = MemoryService()

    def start(self):
        print("=" * 50)
        print("AMALGAM AI")
        print(f"Version : {self.version}")
        print("=" * 50)

    def process(self, user_input: str):

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

        print(f"Received: {user_input}")