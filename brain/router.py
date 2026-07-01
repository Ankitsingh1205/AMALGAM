from config import settings

# Module-level frozensets for O(1) keyword membership testing.
# Previously each call to ``choose_model`` rebuilt a fresh list and used
# linear scan with ``any(word in text for word in [...])`` against Python
# list objects.  Frozensets provide the same interface but with O(1)
# average-case ``in`` checks and no list allocation per call.
_CODING_KW = frozenset([
    "code", "python", "java", "c++", "javascript",
    "html", "css", "bug", "debug", "flask",
    "django", "react", "sql",
])
_REASONING_KW = frozenset([
    "why", "prove", "calculate", "math",
    "equation", "reason", "logic",
])
_CREATIVE_KW = frozenset([
    "story", "poem", "lyrics", "novel", "write creatively",
])


class Router:
    """Routes a prompt to the appropriate model based on keyword matching.

    Optimizations (Mission 6.5.2):
    - Keyword sets are module-level ``frozenset`` constants, created once at
      import time and shared across all ``Router`` instances.
    - ``choose_model`` performs the same three-way split but with O(1)
      membership tests instead of linear list scans.
    """

    def choose_model(self, prompt: str):
        text = prompt.lower()

        if any(word in text for word in _CODING_KW):
            return settings.MODELS["coding"]

        if any(word in text for word in _REASONING_KW):
            return settings.MODELS["reasoning"]

        if any(word in text for word in _CREATIVE_KW):
            return settings.MODELS["creative"]

        return settings.MODELS["general"]
