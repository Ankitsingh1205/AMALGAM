from tools.tool_registry import ToolRegistry
from services.service_registry import ServiceRegistry


class Dispatcher:

    def __init__(self):

        self.tools = ToolRegistry()
        self.services = ServiceRegistry()

    def dispatch(self, task):

        print()
        print(f"[Dispatcher] Action: {task.action}")

        calculator = self.tools.get("calculator")
        python = self.tools.get("python")
        files = self.tools.get("files")

        llm = self.services.get("llm")

        if task.action == "calculate":

            result = calculator.calculate(task.data)

            print(f"[Calculator] {task.data} = {result}")

            return result

        if task.action == "run_python":

            result = python.execute(task.data)

            print(result)

            return result

        if task.action == "list_files":

            result = files.list_dir(task.data or ".")

            print(result)

            return result

        if task.action in ["chat", "generate_code"]:

            result = llm.ask(task.data, task.model)

            print()

            print("AMALGAM:\n")

            print(result)

            return result

        print("Unknown action.")

        return None