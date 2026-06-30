try:
    import ollama
except ImportError:
    ollama = None

from config import settings


class LLMService:

    def __init__(self):
        if ollama is None:
            self.client = None
            return

        self.client = ollama.Client(host=settings.OLLAMA_HOST)

    def ask(self, prompt: str, model: str):

        if self.client is None:
            return "LLM Error: ollama package is not installed."

        if not prompt:
            return "LLM Error: prompt is empty."

        if not model:
            return "LLM Error: model is not configured."

        try:
            response = self.client.chat(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response["message"]["content"]

        except Exception as e:
            return f"LLM Error: {e}"
