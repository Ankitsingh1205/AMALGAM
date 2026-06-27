from brain.preprocessor.preprocessor import Preprocessor


class Pipeline:

    def __init__(self):
        self.preprocessor = Preprocessor()

    def run(self, text: str):
        return self.preprocessor.process(text)
