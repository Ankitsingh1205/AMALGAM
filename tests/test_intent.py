from brain.intent.intent import IntentAnalyzer

intent = IntentAnalyzer()

tests = [
    "Write Python code",
    "Solve 144 * 82",
    "Remember my name",
    "Write a poem",
    "Search latest AI news",
    "Who are you?"
]

for t in tests:
    print(f"{t}  --->  {intent.analyze(t)}")
