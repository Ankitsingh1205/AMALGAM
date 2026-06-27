from kernel.executor import Executor
from kernel.task import Task

kernel = Executor()

task = Task(
    intent="python",
    action="run_python",
    data="""
for i in range(5):
    print(i)
"""
)

kernel.execute(task)