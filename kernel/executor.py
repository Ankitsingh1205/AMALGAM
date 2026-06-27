from kernel.state import KernelState
from kernel.task import Task
from kernel.dispatcher import Dispatcher


class Executor:

    def __init__(self):

        self.state = KernelState()
        self.dispatcher = Dispatcher()

    def boot(self):

        print("=" * 60)
        print("AMALGAM OS")
        print("Artificial Intelligence Operating System")
        print("=" * 60)

        self.state.memory_loaded = True
        self.state.models_loaded = 5
        self.state.tools_loaded = 2
        self.state.services_loaded = 4

        self.state.ready()

        print(f"Kernel Version : {self.state.version}")
        print(f"Kernel Status  : {self.state.status}")
        print(f"Models Loaded  : {self.state.models_loaded}")
        print(f"Services       : {self.state.services_loaded}")
        print(f"Memory         : {'Connected' if self.state.memory_loaded else 'Offline'}")
        print("=" * 60)

    def execute(self, task: Task):

        print()
        print("[Kernel]")
        print(task)

        return self.dispatcher.dispatch(task)