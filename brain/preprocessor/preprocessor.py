class Preprocessor:

    def process(self, text: str) -> str:

        text = text.strip()

        text = text.replace("\n", " ")

        text = text.lower()

        return text
