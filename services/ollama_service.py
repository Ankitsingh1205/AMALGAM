import ollama


class OllamaService:

    def __init__(self):
        self.client = ollama.Client(host="http://127.0.0.1:11434")

    def is_running(self):

        try:
            self.client.list()
            return True
        except Exception:
            return False

    def list_models(self):

        response = self.client.list()

        return [model.model for model in response.models]

    def count_models(self):

        return len(self.list_models())