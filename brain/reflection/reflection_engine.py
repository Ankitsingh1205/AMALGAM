from __future__ import annotations

from typing import Optional

from config import constants
from services.logger import get_logger


class ReflectionEngine:
    """Analyzes execution failures and proposes recovery strategies.

    The engine inspects the error message, output, and action to classify
    the root cause and select the best next step. It is deterministic and
    does not rely on external LLM calls.

    Attributes:
        _logger: Structured logger instance.
    """

    # Pre-built frozenset keywords for fast O(1) membership testing.
    _MISSING_DEP_KEYWORDS = frozenset([
        "no module named", "importerror", "modulenotfounderror",
        "cannot import", "missing dependency",
    ])
    _INVALID_PATH_KEYWORDS = frozenset([
        "no such file", "file not found", "filenotfounderror",
        "oserror", "directory error", "path not found",
    ])
    _RUNTIME_EXC_KEYWORDS = frozenset([
        "runtimeerror", "valueerror", "typeerror", "attributeerror",
        "keyerror", "indexerror", "assertionerror", "exception",
    ])
    _WRONG_TOOL_KEYWORDS = frozenset([
        "dispatcher error: missing target", "dispatcher error: missing method",
        "unknown action", "missing target", "missing method",
    ])
    _WRONG_PLAN_KEYWORDS = frozenset([
        "dispatcher error: malformed", "dispatcher error: remember action",
        "malformed task",
    ])
    _SERVICE_ERR_KEYWORDS = frozenset([
        "llm error", "ollama", "connection refused", "timeout", "not available",
    ])

    def __init__(self) -> None:
        self._logger = get_logger("reflection_engine")

    def reflect(
        self,
        action: Optional[str] = None,
        output: Optional[str] = None,
        error: Optional[str] = None,
    ) -> dict:
        """Analyze a failure and return a structured reflection.

        The reflection contains:

        - ``root_cause``: One of the known cause categories.
        - ``strategy``: Recommended recovery strategy.
        - ``reasoning``: Human-readable explanation.

        Args:
            action: The action that was attempted.
            output: The raw output, if any.
            error: The error message, if any.

        Returns:
            A reflection dictionary.
        """
        text = " ".join(filter(None, [str(error), str(output)])).lower()

        root_cause, strategy, reasoning = self._classify(text, action)

        self._logger.info(
            "reflection generated",
            root_cause=root_cause,
            strategy=strategy,
            action=action,
        )

        return {
            "root_cause": root_cause,
            "strategy": strategy,
            "reasoning": reasoning,
            "action": action,
            "error": error,
            "output": output,
        }

    def _classify(
        self,
        text: str,
        action: Optional[str],
    ) -> tuple[str, str, str]:
        """Classify the failure and select a strategy.

        Returns a tuple of (root_cause, strategy, reasoning).
        """
        # Missing dependency / import
        if any(k in text for k in self._MISSING_DEP_KEYWORDS):
            return (
                "missing_dependency",
                constants.REFLECTION_STRATEGY_REPLAN,
                "A required module or dependency is missing. Replan with an alternative approach.",
            )

        # Invalid path / file not found
        if any(k in text for k in self._INVALID_PATH_KEYWORDS):
            return (
                "invalid_path",
                constants.REFLECTION_STRATEGY_ALTERNATIVE,
                "The requested file or path does not exist. Try an alternative path or tool.",
            )

        # Runtime exception
        if any(k in text for k in self._RUNTIME_EXC_KEYWORDS):
            return (
                "runtime_exception",
                constants.REFLECTION_STRATEGY_RETRY,
                "A runtime exception occurred. This may be transient; retrying is recommended.",
            )

        # Wrong tool / missing target
        if any(k in text for k in self._WRONG_TOOL_KEYWORDS):
            return (
                "wrong_tool",
                constants.REFLECTION_STRATEGY_ALTERNATIVE,
                "The selected tool or action is not available. Choose an alternative tool.",
            )

        # Wrong planning / malformed
        if any(k in text for k in self._WRONG_PLAN_KEYWORDS):
            return (
                "wrong_planning",
                constants.REFLECTION_STRATEGY_REPLAN,
                "The task was malformed or incorrectly planned. Replan the task.",
            )

        # LLM / service errors
        if any(k in text for k in self._SERVICE_ERR_KEYWORDS):
            return (
                "service_unavailable",
                constants.REFLECTION_STRATEGY_RETRY,
                "An external service is unavailable. Retrying may resolve the issue.",
            )

        # Default fallback
        return (
            "unknown",
            constants.REFLECTION_STRATEGY_RETRY,
            "The failure cause is unclear. Retry as a first step.",
        )

    def should_escalate_to_user(self, reflection: dict) -> bool:
        """Return whether the reflection recommends user escalation.

        User escalation is the final fallback when automated strategies
        are exhausted.
        """
        return reflection.get("strategy") == constants.REFLECTION_STRATEGY_USER
