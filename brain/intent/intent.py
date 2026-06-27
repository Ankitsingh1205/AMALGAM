import re


class IntentAnalyzer:

    def detect(self, text: str):

        text = text.strip()
        lower = text.lower()

        # Math expressions
        if re.fullmatch(r"[0-9+\-*/(). ]+", text):
            return "math"

        # Coding requests
        coding_phrases = [
            "write code",
            "generate code",
            "write python",
            "python code",
            "create function",
            "create a function",
            "debug",
            "fix code",
            "fix this code",
            "implement",
            "program",
            "script",
            "algorithm"
        ]

        if any(phrase in lower for phrase in coding_phrases):
            return "coding"

        # Everything else is general
        return "general"