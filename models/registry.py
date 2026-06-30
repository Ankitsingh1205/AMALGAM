from config import settings


class ModelRegistry:

    def __init__(self):
        self.models = settings.MODELS

    def get(self, role: str):

        return self.models.get(
            role,
            self.models["general"]
        )

    def list_models(self):

        return self.models
