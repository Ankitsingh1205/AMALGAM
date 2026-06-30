import re

from config import constants


class IntentAnalyzer:

    def detect(self, text: str):

        text = text.strip()
        lower = text.lower()

        # Math
        if re.fullmatch(r"[0-9+\-*/(). ]+", text):
            return constants.INTENT_MATH

        # Memory
        if lower.startswith("remember "):
            return constants.INTENT_MEMORY

        if lower.startswith("recall "):
            return constants.INTENT_MEMORY

        # Files
        if any(word in lower for word in [
            "list files",
            "show files",
            "directory",
            "folders",
            "ls",
        ]):
            return constants.INTENT_FILES

        # Internet
        if any(word in lower for word in [
            "search ",
            "search web",
            "google",
            "find online",
        ]):
            return constants.INTENT_INTERNET

        # Python execution
        if any(word in lower for word in [
            "run python",
            "execute python",
            "python:",
        ]):
            return constants.INTENT_PYTHON

        # Coding
        coding_phrases = [
            "write code",
            "generate code",
            "write python",
            "python code",
            "create function",
            "create a function",
            "debug",
            "fix code",
            "implement",
            "program",
            "script",
            "algorithm",
        ]

        if any(phrase in lower for phrase in coding_phrases):
            return constants.INTENT_CODING

        # Project
        project_phrases = [
            "explain my project",
            "summarize my project",
            "summarize this repository",
            "project overview",
            "project architecture",
            "show project architecture",
            "explain this repository",
        ]

        if any(phrase in lower for phrase in project_phrases):
            return constants.INTENT_PROJECT

        return constants.INTENT_GENERAL
