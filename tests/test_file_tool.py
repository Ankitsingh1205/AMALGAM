from kernel.executor import Executor
from kernel.task import Task

kernel = Executor()

task = Task(
    intent="files",
    action="list_files",
    data="."
)

kernel.execute(task)