from models.registry import ModelRegistry


class ModelSelector:

    def __init__(self):

        self.registry = ModelRegistry()

    def select(self, plan: str):

        mapping = {

            "use_coder": "coding",

            "use_creative_model": "creative",

            "use_general_model": "general",

            "use_reasoning": "reasoning",

            "use_fast": "fast"

        }

        role = mapping.get(plan, "general")

        return self.registry.get(role)