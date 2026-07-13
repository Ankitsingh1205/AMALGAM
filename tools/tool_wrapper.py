"""ToolWrapper — retry, timeout, permission and capability wrapping for tools.

Apps a :class:`ToolWrapper` around any registered tool invocation.  The
wrapper validates capability and permission, dispatches with a timeout,
retries on transient failures, records lifecycle events on an optional
``MissionEventBus``, and returns a structured :class:`ToolResult`.

This wrapper is *additive*.  It does NOT modify existing tools or the
:class:`Dispatcher`.  Callers that want the structured result use the
wrapper; raw callers continue to use ``Dispatcher.dispatch`` directly.
"""

from __future__ import annotations

import concurrent.futures
import time
from pathlib import Path
from typing import Any, Optional

from kernel.permissions import PermissionChecker, PermissionError
from tools.capability_validator import CapabilityValidator, CapabilityValidationError
from tools.tool_result import ToolResult


class ToolWrapper:
    """Wraps a registered tool invocation with safety guarantees.

    Guarantees provided:

    * Capability validation (action -> tool.method exists).
    * Permission validation (workspace boundaries for filesystem tools).
    * Bounded timeout (default: 15 seconds).
    * Bounded retry (default: 1 retry on ``Exception``).
    * Structured :class:`ToolResult` output.
    * Optional lifecycle event emission on a ``MissionEventBus``.

    The wrapper does NOT duplicate ``RetryManager`` policy; semantics are
    limited to transient tool failures.  Persistent failures propagate.
    """

    DEFAULT_TIMEOUT: float = 15.0
    DEFAULT_MAX_RETRIES: int = 1

    def __init__(
        self,
        validator: Optional[CapabilityValidator] = None,
        permission_checker: Optional[PermissionChecker] = None,
        timeout: float = 15.0,
        max_retries: int = 1,
        event_bus: Optional[Any] = None,
    ) -> None:
        """Initialise the wrapper.

        Args:
            validator: ``CapabilityValidator`` instance.  If ``None``
                a fresh one is created.
            permission_checker: ``PermissionChecker`` instance.  If
                ``None`` a fresh one using the current cwd is created.
            timeout: Per-invocation timeout in seconds.
            max_retries: Maximum retry attempts on transient failure.
            event_bus: Optional ``MissionEventBus`` for lifecycle
                notifications.
        """
        self._validator = validator or CapabilityValidator()
        self._permissions = permission_checker or PermissionChecker()
        self._timeout = timeout
        self._max_retries = max_retries
        self._event_bus = event_bus

    @property
    def timeout(self) -> float:
        """Configured per-invocation timeout."""
        return self._timeout

    @property
    def max_retries(self) -> int:
        """Configured maximum retry attempts."""
        return self._max_retries

    def invoke(
        self,
        action: str,
        data: Any = None,
    ) -> ToolResult:
        """Validate, dispatch, and wrap the result as a ``ToolResult``.

        Args:
            action: Action name from ``config.constants``.
            data: Positional argument forwarded to the tool method.

        Returns:
            A ``ToolResult`` describing the outcome.
        """
        # ----- Capability validation ----------------------------------
        try:
            tool_name, method_name, tool_instance = self._validator.validate_target(action)
        except CapabilityValidationError as e:
            return ToolResult.fail(
                error=f"Capability validation failed: {e}",
                tool_name="",
                execution_time=0.0,
                metadata={"reason": "capability_validation", "action": action},
            )

        # ----- Permission validation ---------------------------------
        try:
            self._permissions.check(tool_name, method_name, data)
        except PermissionError as e:
            return ToolResult.fail(
                error=f"Permission denied: {e}",
                tool_name=tool_name,
                execution_time=0.0,
                metadata={"reason": "permission_denied", "action": action, "method": method_name},
            )

        # ----- Spawn pre-execution event ------------------------------
        self._publish_event("tool_invoking", tool_name, method_name, None)

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            method = getattr(tool_instance, method_name)
            attempt = 0
            last_error: Optional[Exception] = None
            start = time.monotonic()

            while attempt <= self._max_retries:
                attempt += 1
                try:
                    future = executor.submit(self._invoke_method, method,
                                             action, data)
                    raw_output = future.result(timeout=self._timeout)
                    elapsed = time.monotonic() - start
                    self._publish_event("tool_succeeded", tool_name, method_name, raw_output)
                    return ToolResult.ok(
                        output=raw_output,
                        tool_name=tool_name,
                        execution_time=round(elapsed, 6),
                        metadata={"action": action, "method": method_name, "attempts": attempt},
                    )
                except TimeoutError:
                    last_error = TimeoutError(
                        f"Tool {tool_name!r} exceeded timeout of {self._timeout}s"
                    )
                    continue
                except Exception as e:
                    last_error = e
                    continue
        finally:
            executor.shutdown(wait=False)

        # ----- Exhausted retries --------------------------------------
        elapsed = time.monotonic() - start
        self._publish_event("tool_failed", tool_name, method_name, None)
        error_msg = str(last_error) if last_error is not None else "Unknown failure"
        return ToolResult.fail(
            error=error_msg,
            tool_name=tool_name,
            execution_time=round(elapsed, 6),
            metadata={"reason": "exhausted_retries",
                      "action": action,
                      "method": method_name,
                      "attempts": attempt},
        )

    @staticmethod
    def _invoke_method(method: Any, action: str, data: Any) -> Any:
        """Dispatch to the bound tool method.

        ``ACTION_REMEMBER`` requires a tuple of ``(key, value)``.  All
        other actions receive ``data`` as-is.

        Args:
            method: Bound method on the tool instance.
            action: Action name.
            data: First argument.

        Returns:
            Raw tool output.

        Raises:
            ValueError: If ``ACTION_REMEMBER`` is dispatched without a
                length-2 tuple/list.
        """
        from config import constants

        if action == constants.ACTION_REMEMBER:
            if not isinstance(data, (tuple, list)) or len(data) != 2:
                raise ValueError("remember action requires key and value.")
            return method(data[0], data[1])
        return method(data)

    def _publish_event(
        self,
        event_name: str,
        tool_name: str,
        method_name: str,
        output: Any,
    ) -> None:
        """Emit a lifecycle event on the optional ``MissionEventBus``.

        Args:
            event_name: One of ``tool_invoking``, ``tool_succeeded``,
                ``tool_failed``.
            tool_name: Name of the tool.
            method_name: Method being invoked.
            output: Output for successful events, ``None`` otherwise.
        """
        if self._event_bus is None:
            return
        try:
            from brain.mission.event import MissionEvent
            from brain.mission.event_types import MissionEventType
            self._event_bus.publish(MissionEvent(
                mission_id="tool-execution",
                event_type=MissionEventType.MISSION_STATUS_CHANGED,
                payload={
                    "event": event_name,
                    "tool": tool_name,
                    "method": method_name,
                    "output": output,
                },
            ))
        except Exception:
            return
