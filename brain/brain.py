from brain.intent.intent import IntentAnalyzer
from brain.planner.planner import Planner


class Brain:

    def __init__(self):

        self.intent = IntentAnalyzer()
        self.planner = Planner()

    def think(self, user_input: str):

        detected_intent = self.intent.detect(user_input)

        task = self.planner.create_task(
            detected_intent,
            user_input
        )

        return task