from config.models import MODELS


class ModelRegistry:

    def __init__(self):
        self.models = MODELS

    def get(self, role: str):

        return self.models.get(
            role,
            self.models["general"]
        )

    def list_models(self):

        return self.models