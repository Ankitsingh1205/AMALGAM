"""Local Ollama service with plain-text and schema-validated JSON APIs."""
from __future__ import annotations

import json
from typing import Any, Callable

try:
    import ollama
except ImportError:
    ollama = None

from config import settings


class StructuredLLMError(RuntimeError):
    pass


class LLMService:
    def __init__(self, client=None):
        if client is not None:
            self.client = client
        elif ollama is None:
            self.client = None
        else:
            self.client = ollama.Client(host=settings.OLLAMA_HOST)

    def ask(self, prompt: str, model: str, system: str | None = None):
        if self.client is None:
            return "LLM Error: ollama package is not installed."
        if not prompt:
            return "LLM Error: prompt is empty."
        if not model:
            return "LLM Error: model is not configured."
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            response = self.client.chat(model=model, messages=messages)
            return response["message"]["content"]
        except Exception as error:
            return f"LLM Error: {error}"

    def ask_structured(
        self,
        prompt: str,
        model: str,
        system: str,
        validator: Callable[[dict[str, Any]], Any],
        retries: int = 2,
    ) -> dict[str, Any]:
        """Generate, parse and validate JSON; fail closed after bounded retries."""
        if self.client is None:
            raise StructuredLLMError("Ollama client is unavailable")
        repair = ""
        last_error = "unknown structured-output error"
        for attempt in range(retries + 1):
            messages = [
                {"role": "system", "content": system + "\nReturn one JSON object only. No markdown."},
                {"role": "user", "content": prompt + repair},
            ]
            try:
                response = self.client.chat(model=model, messages=messages, format="json")
                raw = response["message"]["content"]
                value = json.loads(raw)
                if not isinstance(value, dict):
                    raise ValueError("root must be an object")
                validator(value)
                value["_meta"] = {"model": model, "attempt": attempt + 1}
                return value
            except Exception as error:
                last_error = str(error)
                repair = f"\nPrevious response was invalid: {last_error}. Correct it without changing scope."
        raise StructuredLLMError(f"structured generation failed after {retries + 1} attempts: {last_error}")
