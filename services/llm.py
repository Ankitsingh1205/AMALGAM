import ollama


class LLMService:

    def __init__(self):
        self.client = ollama.Client(host="http://127.0.0.1:11434")

    def ask(self, prompt: str, model: str):

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
