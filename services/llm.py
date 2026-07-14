"""Local Ollama service with plain-text and schema-validated JSON APIs."""
from __future__ import annotations

import json
import os
from typing import Any, Callable, Optional

try:
    import ollama
except ImportError:
    ollama = None

from config import settings


class StructuredLLMError(RuntimeError):
    pass


def _resolve_ollama_host() -> str:
    """Resolve the Ollama host from environment, settings, or a default."""
    host = (
        os.environ.get("OLLAMA_HOST")
        or os.environ.get("AMALGAM_OLLAMA_HOST")
        or getattr(settings, "OLLAMA_HOST", None)
        or "http://127.0.0.1:11434"
    )
    return host


class LLMService:
    def __init__(self, client=None):
        self._client_error: Optional[str] = None
        self._host = _resolve_ollama_host()
        if client is not None:
            self.client = client
        elif ollama is None:
            self.client = None
            self._client_error = (
                "Python 'ollama' package is not installed. "
                "Install it with: pip install ollama"
            )
        else:
            try:
                self.client = ollama.Client(host=self._host)
            except Exception as error:
                self.client = None
                self._client_error = (
                    f"Ollama client construction failed for host "
                    f"{self._host}: {error}"
                )

    def _unavailable_detail(self) -> str:
        """Return a diagnostic message for an unavailable Ollama client."""
        if self._client_error:
            base = self._client_error
        else:
            base = "Ollama client is unavailable"
        return (
            f"{base}\n"
            f"  host           : {self._host}\n"
            f"  fix steps      :\n"
            f"    pip install ollama\n"
            f"    ollama serve\n"
            f"    ollama pull qwen2.5-coder:7b\n"
            f"    set OLLAMA_HOST if your server is not on "
            f"http://127.0.0.1:11434"
        )

    def ask(self, prompt: str, model: str, system: str | None = None):
        if self.client is None:
            return f"LLM Error: {self._unavailable_detail()}"
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
            raise StructuredLLMError(self._unavailable_detail())
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
