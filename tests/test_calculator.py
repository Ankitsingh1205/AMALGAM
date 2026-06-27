from kernel.executor import Executor
from kernel.task import Task

kernel = Executor()

task = Task(
    intent="math",
    action="calculate",
    data="144*82"
)

kernel.execute(task)