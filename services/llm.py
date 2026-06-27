import ollama


class LLMService:

    def __init__(self):
        self.client = ollama.Client(host="http://127.0.0.1:11434")
        self.model = "qwen3:8b"

    def ask(self, prompt: str):

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]