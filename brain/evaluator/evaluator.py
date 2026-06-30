from __future__ import annotations

from typing import Any, Optional

from config import constants
from services.logger import get_logger


class Evaluator:
    """Validates execution results and determines outcome state.

    The evaluator inspects raw output, errors, and context to produce a
    structured verdict. It is intentionally decoupled from dispatchers so
    that evaluation logic can evolve independently.

    Attributes:
        _logger: Structured logger instance.
    """

    def __init__(self) -> None:
        self._logger = get_logger("evaluator")

    def evaluate(
        self,
        output: Any = None,
        error: Optional[str] = None,
        expected: Any = None,
    ) -> dict:
        """Evaluate an execution result and return a structured verdict.

        The evaluation follows a deterministic priority:

        1. If ``error`` is present and non-empty, the result is a failure.
        2. If ``output`` is a string and starts with a known error prefix,
           the result is a failure.
        3. If ``expected`` is provided and ``output`` does not match,
           the result is partial.
        4. Otherwise, the result is a success.

        Args:
            output: The raw execution output.
            error: An error string, if any.
            expected: An optional expected value for comparison.

        Returns:
            A dictionary with keys:

            - ``status``: One of ``success``, ``failure``, ``partial``, ``unknown``.
            - ``verified``: ``True`` if the result meets expectations.
            - ``message``: Human-readable evaluation summary.
            - ``output``: The original output (for chaining).
        """
        if error:
            return self._verdict(
                constants.EVALUATION_FAILURE,
                False,
                f"Execution error: {error}",
                output,
            )

        if isinstance(output, str) and output.startswith((
            "Dispatcher Error:",
            "Python Error:",
            "LLM Error:",
            "Memory Error:",
            "Internet Error:",
            "Read Error:",
            "Write Error:",
            "Directory Error:",
        )):
            return self._verdict(
                constants.EVALUATION_FAILURE,
                False,
                f"Tool/service returned an error: {output}",
                output,
            )

        if output is None:
            return self._verdict(
                constants.EVALUATION_UNKNOWN,
                False,
                "No output was produced.",
                output,
            )

        if expected is not None and output != expected:
            return self._verdict(
                constants.EVALUATION_PARTIAL,
                False,
                f"Output did not match expected value. Expected: {expected!r}, got: {output!r}",
                output,
            )

        return self._verdict(
            constants.EVALUATION_SUCCESS,
            True,
            "Execution completed successfully.",
            output,
        )

    def is_success(self, verdict: dict) -> bool:
        """Return whether the given verdict represents success."""
        return verdict.get("status") == constants.EVALUATION_SUCCESS

    def is_failure(self, verdict: dict) -> bool:
        """Return whether the given verdict represents failure."""
        return verdict.get("status") == constants.EVALUATION_FAILURE

    def is_verified(self, verdict: dict) -> bool:
        """Return whether the given verdict is verified."""
        return bool(verdict.get("verified"))

    def _verdict(
        self,
        status: str,
        verified: bool,
        message: str,
        output: Any,
    ) -> dict:
        self._logger.info(
            "evaluated",
            status=status,
            verified=verified,
            detail=message,
        )
        return {
            "status": status,
            "verified": verified,
            "message": message,
            "output": output,
        }
