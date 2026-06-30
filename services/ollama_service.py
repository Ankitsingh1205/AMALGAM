try:
    import ollama
except ImportError:
    ollama = None

from config import settings


class OllamaService:

    def __init__(self):
        if ollama is None:
            self.client = None
            return

        self.client = ollama.Client(host=settings.OLLAMA_HOST)

    def is_running(self):

        if self.client is None:
            return False

        try:
            self.client.list()
            return True
        except Exception:
            return False

    def list_models(self):

        if self.client is None:
            return []

        try:
            response = self.client.list()

            return [model.model for model in response.models]

        except Exception:
            return []

    def count_models(self):

        return len(self.list_models())
