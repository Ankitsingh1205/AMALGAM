from kernel.executor import Executor
from kernel.task import Task

kernel = Executor()

task = Task(
    intent="coding",
    action="generate_code",
    model="qwen2.5-coder:7b"
)

kernel.execute(task)