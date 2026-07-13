from kernel.action_registry import ActionRegistry
from kernel.permissions import PermissionChecker
from tools.tool_registry import ToolRegistry
from tools.tool_wrapper import ToolWrapper
from tools.capability_validator import CapabilityValidator
from services.service_registry import ServiceRegistry
from config import constants
from services.logger import get_logger

# Frozenset for O(1) membership test -- avoids rebuilding a list on every dispatch.
_LLM_ACTIONS = frozenset([constants.ACTION_CHAT, constants.ACTION_GENERATE_CODE])


class Dispatcher:
    """Routes tasks to the appropriate tool or service.

    Mission 7.5 integration:
    - Tool-targeted actions are now dispatched through :class:`ToolWrapper`,
      gaining capability validation, workspace permission checks, bounded
      timeout, and bounded retry on the production path (previously the
      wrapper existed but was only exercised by tests).
    - The dispatcher no longer prints results (ARCH-005). It returns the
      raw result; presentation is owned by the caller (CLI layer).

    Optimizations retained from Mission 6.5.2:
    - LLM action membership test uses a module-level ``frozenset``.
    - Tool/service lookup is short-circuited: tools are checked first and
      the service lookup is only attempted when the tool lookup misses.
    """

    def __init__(self, workspace_root=None):
        self.actions = ActionRegistry()
        self.tools = ToolRegistry(workspace_root=workspace_root)
        self.services = ServiceRegistry()
        self.logger = get_logger("dispatcher")

        # Safety layer (Mission 7.1.8 components, wired in Mission 7.5).
        # Registries are shared so wrapper validation sees the same
        # routing table the dispatcher uses.
        self.tool_wrapper = ToolWrapper(
            validator=CapabilityValidator(actions=self.actions, tools=self.tools),
            permission_checker=PermissionChecker(workspace_root=workspace_root),
        )

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
            if self.tools.get(target_name) is not None:
                return self._dispatch_tool(action, target_name, task)

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

            return result

        message = f"Unknown action: {action}"
        self.logger.warning(message, action=action)

        return message

    def _dispatch_tool(self, action, target_name, task):
        """Dispatch a tool-targeted action through the ToolWrapper.

        The wrapper provides capability validation, permission checks,
        timeout, and retry. The raw tool output is returned on success
        to preserve the historical dispatch contract; failures return a
        ``Dispatcher Error`` string as before.
        """
        tool_result = self.tool_wrapper.invoke(action, getattr(task, "data", None))

        self.logger.debug(
            "dispatch complete",
            action=action,
            target=target_name,
            success=tool_result.success,
            execution_time=tool_result.execution_time,
        )

        if tool_result.success:
            return tool_result.output

        message = f"Dispatcher Error: {tool_result.error}"
        self.logger.error(message)
        return message
