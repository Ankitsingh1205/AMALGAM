"""Universal ToolResult abstraction for the tool ecosystem.

Provides a structured result type returned by tool executions.  This
abstraction normalises disparate tool outputs (strings, lists, booleans,
``None``) into a single predictable contract with explicit success/failure
status, output payload, error message, timing, and metadata.

Existing tool methods are NOT modified.  ``ToolResult`` is an additive
abstraction used by ``ToolWrapper`` and capability-aware dispatch paths.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True, slots=True)
class ToolResult:
    """Structured result from a tool execution.

    Attributes:
        success: ``True`` if the tool completed without error.
        output: Raw output value from the tool (string, list, bool, etc.).
        error: Error message if the tool failed, ``None`` otherwise.
        tool_name: Name of the tool that produced this result.
        execution_time: Wall-clock execution time in seconds.
        metadata: Optional metadata dict (retries used, capability validated,
            permission checks applied, etc.).
    """

    success: bool
    output: Any
    error: Optional[str]
    tool_name: str
    execution_time: float
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(
        cls,
        output: Any,
        tool_name: str,
        execution_time: float = 0.0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "ToolResult":
        """Build a successful ToolResult.

        Args:
            output: Raw output from the tool.
            tool_name: Name of the tool that succeeded.
            execution_time: Wall-clock time in seconds.
            metadata: Optional metadata dict.

        Returns:
            A ``ToolResult`` with ``success=True`` and ``error=None``.
        """
        return cls(
            success=True,
            output=output,
            error=None,
            tool_name=tool_name,
            execution_time=execution_time,
            metadata=metadata or {},
        )

    @classmethod
    def fail(
        cls,
        error: str,
        tool_name: str,
        output: Any = None,
        execution_time: float = 0.0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "ToolResult":
        """Build a failed ToolResult.

        Args:
            error: Error message explaining the failure.
            tool_name: Name of the tool that failed.
            output: Partial output if any (default ``None``).
            execution_time: Wall-clock time in seconds.
            metadata: Optional metadata dict.

        Returns:
            A ``ToolResult`` with ``success=False`` and the error populated.
        """
        return cls(
            success=False,
            output=output,
            error=error,
            tool_name=tool_name,
            execution_time=execution_time,
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the ToolResult to a plain dict.

        Returns:
            A dictionary with all fields.
        """
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "tool_name": self.tool_name,
            "execution_time": self.execution_time,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolResult":
        """Deserialize a ToolResult from a plain dict.

        Args:
            data: Dictionary with keys matching the dataclass fields.

        Returns:
            A ``ToolResult`` reconstructed from ``data``.
        """
        return cls(
            success=bool(data.get("success", False)),
            output=data.get("output"),
            error=data.get("error"),
            tool_name=data.get("tool_name", ""),
            execution_time=float(data.get("execution_time", 0.0)),
            metadata=dict(data.get("metadata", {})),
        )
