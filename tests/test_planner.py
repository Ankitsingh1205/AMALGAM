from brain.planner.planner import Planner

planner = Planner()

tests = [
    "coding",
    "math",
    "memory",
    "creative",
    "web",
    "general"
]

for t in tests:
    print(f"{t} ---> {planner.plan(t)}")
