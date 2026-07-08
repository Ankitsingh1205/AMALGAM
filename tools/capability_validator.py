"""Capability validation for the tool ecosystem.

Validates whether a registered tool supports a requested action before
dispatch actually occurs.  This avoids runtime ``AttributeError`` blow-ups
by failing gracefully when an action is not available on a tool.
"""

from __future__ import annotations

from typing import Any, Optional

from kernel.action_registry import ActionRegistry
from tools.tool_registry import ToolRegistry


class CapabilityValidationError(Exception):
    """Raised when a requested capability is not available."""


class CapabilityValidator:
    """Validates that a tool supports a requested action.

    Wraps ``ActionRegistry`` (action -> (tool_name, method_name)) and
    ``ToolRegistry`` (tool_name -> instance) to verify that the action
    resolves to a target that actually has the expected method.
    """

    def __init__(
        self,
        actions: Optional[ActionRegistry] = None,
        tools: Optional[ToolRegistry] = None,
    ) -> None:
        """Initialise the validator.

        Args:
            actions: An ``ActionRegistry`` instance.  If ``None``, a
                fresh registry is created.
            tools: A ``ToolRegistry`` instance.  If ``None``, a fresh
                registry is created.
        """
        self._actions = actions or ActionRegistry()
        self._tools = tools or ToolRegistry()

    @property
    def actions(self) -> ActionRegistry:
        """Underlying ``ActionRegistry`` accessor."""
        return self._actions

    @property
    def tools(self) -> ToolRegistry:
        """Underlying ``ToolRegistry`` accessor."""
        return self._tools

    def validate(self, action: str) -> bool:
        """Validate that an action can be dispatched.

        Args:
            action: Action name from ``config.constants``.

        Returns:
            ``True`` if the action resolves to a target tool with the
            expected method.

        Raises:
            CapabilityValidationError: If the action is unknown, the
                target tool is missing, or the method does not exist on
                the tool instance.
        """
        route = self._actions.get(action)
        if route is None:
            raise CapabilityValidationError(f"Unknown action: {action!r}")

        target_name, method_name = route
        target = self._tools.get(target_name)
        if target is None:
            raise CapabilityValidationError(
                f"Target tool not registered: {target_name!r}"
            )

        if not hasattr(target, method_name):
            raise CapabilityValidationError(
                f"Tool {target_name!r} does not support method {method_name!r}"
            )

        return True

    def validate_target(self, action: str) -> tuple[str, str, Any]:
        """Validate an action and return the resolved (tool_name, method_name, tool_instance) tuple.

        Args:
            action: Action name.

        Returns:
            ``(tool_name, method_name, tool_instance)`` triple.

        Raises:
            CapabilityValidationError: If validation fails.
        """
        self.validate(action)
        target_name, method_name = self._actions.get(action)
        return target_name, method_name, self._tools.get(target_name)

    def has_capability(self, action: str) -> bool:
        """Return ``True`` if the action can be dispatched.

        Unlike :meth:`validate`, this does NOT raise; it returns
        ``bool``.

        Args:
            action: Action name.

        Returns:
            ``True`` if dispatchable, ``False`` otherwise.
        """
        try:
            self.validate(action)
            return True
        except CapabilityValidationError:
            return False
