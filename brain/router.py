from config.models import MODELS


class Router:

    def choose_model(self, prompt: str):

        text = prompt.lower()

        coding_keywords = [
            "code",
            "python",
            "java",
            "c++",
            "javascript",
            "html",
            "css",
            "bug",
            "debug",
            "flask",
            "django",
            "react",
            "sql"
        ]

        reasoning_keywords = [
            "why",
            "prove",
            "calculate",
            "math",
            "equation",
            "reason",
            "logic"
        ]

        creative_keywords = [
            "story",
            "poem",
            "lyrics",
            "novel",
            "write creatively"
        ]

        if any(word in text for word in coding_keywords):
            return MODELS["coding"]

        if any(word in text for word in reasoning_keywords):
            return MODELS["reasoning"]

        if any(word in text for word in creative_keywords):
            return MODELS["creative"]

        return MODELS["general"]
