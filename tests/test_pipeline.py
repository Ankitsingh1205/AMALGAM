from brain.brain import Brain
from kernel.executor import Executor

brain = Brain()
kernel = Executor()

queries = [
    "144*82",
    "Write Python code to print Hello World",
    "What is Artificial Intelligence?"
]

for query in queries:

    print()
    print("=" * 50)
    print("User:", query)

    task = brain.think(query)

    kernel.execute(task)