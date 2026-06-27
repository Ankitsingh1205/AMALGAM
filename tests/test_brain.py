from brain.intent.intent import IntentAnalyzer
from brain.planner.planner import Planner

intent = IntentAnalyzer()

planner = Planner()

queries = [
    "144*82",
    "Write Python code",
    "What is AI?"
]

for query in queries:

    detected = intent.detect(query)

    task = planner.create_task(detected, query)

    print()

    print("Input :", query)

    print("Intent:", detected)

    print("Task  :", task)