from kernel.task import Task
from models.registry import ModelRegistry


class Planner:

    def __init__(self):

        self.registry = ModelRegistry()

    def create_task(self, intent: str, user_input: str):

        if intent == "math":

            return Task(
                intent="math",
                action="calculate",
                data=user_input
            )

        if intent == "coding":

            return Task(
                intent="coding",
                action="generate_code",
                model=self.registry.get("coding"),
                data=user_input
            )

        return Task(
            intent="general",
            action="chat",
            model=self.registry.get("general"),
            data=user_input
        )