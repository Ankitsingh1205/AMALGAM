import re

from config import constants

# ---------------------------------------------------------------------------
# Module-level frozensets for O(1) keyword membership testing.
# These are compiled once at import time and shared across all
# IntentAnalyzer instances.
# ---------------------------------------------------------------------------
_INTENT_FILES_KW = frozenset([
    "list files", "show files", "directory", "folders", "ls",
])
_INTENT_INTERNET_KW = frozenset([
    "search ", "search web", "google", "find online",
])
_INTENT_PYTHON_KW = frozenset([
    "run python", "execute python", "python:",
])
_INTENT_CODING_KW = frozenset([
    "write code", "generate code", "write python", "python code",
    "create function", "create a function", "debug", "fix code",
    "implement", "program", "script", "algorithm",
])
_INTENT_PROJECT_KW = frozenset([
    "explain my project", "summarize my project", "summarize this repository",
    "project overview", "project architecture", "show project architecture",
    "explain this repository",
])

# Precompiled regex for math detection — avoids recompiling on every call.
_MATH_RE = re.compile(r"[0-9+\-*/(). ]+")


class IntentAnalyzer:
    """Classifies user input into a canonical intent.

    Optimizations (Mission 6.5.2):
    - All keyword lists promoted to module-level frozensets (O(1) ``in``).
    - Math regex precompiled at module level (no per-call ``re.compile``).
    """

    def detect(self, text: str):
        text = text.strip()
        lower = text.lower()

        # Math
        if _MATH_RE.fullmatch(text):
            return constants.INTENT_MATH

        # Memory
        if lower.startswith("remember "):
            return constants.INTENT_MEMORY

        if lower.startswith("recall "):
            return constants.INTENT_MEMORY

        # Files
        if any(word in lower for word in _INTENT_FILES_KW):
            return constants.INTENT_FILES

        # Internet
        if any(word in lower for word in _INTENT_INTERNET_KW):
            return constants.INTENT_INTERNET

        # Python execution
        if any(word in lower for word in _INTENT_PYTHON_KW):
            return constants.INTENT_PYTHON

        # Coding
        if any(phrase in lower for phrase in _INTENT_CODING_KW):
            return constants.INTENT_CODING

        # Project
        if any(phrase in lower for phrase in _INTENT_PROJECT_KW):
            return constants.INTENT_PROJECT

        return constants.INTENT_GENERAL
