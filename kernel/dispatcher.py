from kernel.action_registry import ActionRegistry
from tools.tool_registry import ToolRegistry
from services.service_registry import ServiceRegistry
from config import constants
from services.logger import get_logger

# Frozenset for O(1) membership test — avoids rebuilding a list on every dispatch.
_LLM_ACTIONS = frozenset([constants.ACTION_CHAT, constants.ACTION_GENERATE_CODE])


class Dispatcher:
    """Routes tasks to the appropriate tool or service.

    Optimizations (Mission 6.5.2):
    - LLM action membership test now uses a module-level ``frozenset``
      (O(1)) instead of a list literal rebuilt on every ``dispatch()`` call.
    - Tool/service lookup is short-circuited: tools are checked first and
      the service lookup is only attempted when the tool lookup misses.
    - Repeated ``getattr(task, ...)`` calls are replaced with local variable
      bindings to avoid repeated attribute lookup overhead.
    - Trailing CRLF line endings cleaned up.
    """

    def __init__(self):
        self.actions = ActionRegistry()
        self.tools = ToolRegistry()
        self.services = ServiceRegistry()
        self.logger = get_logger("dispatcher")

    def dispatch(self, task):
        action = getattr(task, "action", None)

        if not action:
            message = "Dispatcher Error: malformed task."
            self.logger.error(message)
            return message

        self.logger.info("dispatching task", action=action)

        route = self.actions.get(action)

        if route:
            target_name, method_name = route

            # Prefer tool; fall back to service.
            target = self.tools.get(target_name)
            if target is None:
                target = self.services.get(target_name)

            if target is None:
                message = f"Dispatcher Error: missing target '{target_name}'."
                self.logger.error(message)
                return message

            method = getattr(target, method_name, None)

            if method is None:
                message = f"Dispatcher Error: missing method '{method_name}'."
                self.logger.error(message)
                return message

            try:
                if action == constants.ACTION_REMEMBER:
                    task_data = getattr(task, "data", None)
                    if (
                        not isinstance(task_data, (tuple, list))
                        or len(task_data) != 2
                    ):
                        return "Dispatcher Error: remember action requires key and value."
                    result = method(task_data[0], task_data[1])
                else:
                    result = method(getattr(task, "data", None))

            except Exception as e:
                result = f"Dispatcher Error: {e}"
                self.logger.error(result)

            self.logger.debug(
                "dispatch complete",
                action=action,
                target=target_name,
            )

            print()

            if action == constants.ACTION_PROJECT_SUMMARY:
                summary = result["summary"]
                print("AMALGAM")
                print()
                print(f"Project Root : {summary['project_root']}")
                print(f"Packages     : {len(summary['python_packages'])}")
                print(f"Documents    : {summary['documents']}")
                print(f"Symbols      : {summary['symbols']}")
                print(f"Relations    : {summary['relationships']}")
            else:
                print("AMALGAM:")
                print()
                print(result)

            return result

        if action in _LLM_ACTIONS:
            llm = self.services.get(constants.SERVICE_LLM)

            if llm is None:
                result = "Dispatcher Error: missing service 'llm'."
                self.logger.error(result)
                return result

            try:
                result = llm.ask(
                    getattr(task, "data", None),
                    getattr(task, "model", None),
                )
            except Exception as e:
                result = f"Dispatcher Error: {e}"
                self.logger.error(result)

            print()
            print("AMALGAM:\n")
            print(result)

            return result

        message = f"Unknown action: {action}"
        self.logger.warning(message, action=action)

        return message
