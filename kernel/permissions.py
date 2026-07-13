"""Permission checking for tool execution.

Validates that tool targets and arguments respect workspace boundaries
before the tool is invoked.  This is part of the kernel layer and owns
JUST the boundary validation — it does NOT dispatch tools.

Permission rules:
    * FileTool paths must be within the workspace root.
    * PythonExecutor is restricted to read-only evaluation.
    * Calculator and MemoryTool and InternetTool operate on
      workspace-safe inputs and require NO path validation.
"""

from __future__ import annotations

from pathlib import Path, PureWindowsPath
from typing import Optional

from config import constants


class PermissionError(Exception):
    """Raised when permission validation denies a tool action."""


class PermissionChecker:
    """Validates tool actions for workspace boundary compliance.

    The checker is stateless — it maps (tool_name, method_name) pairs
    to validation rules and raises ``PermissionError`` on violation.
    No tool execution happens here; callers must invoke the checker
    BEFORE dispatching to a tool.
    """

    WORKSPACE_ROOT_METHODS: frozenset[str] = frozenset([
        "read", "write", "append", "delete", "copy", "move",
        "replace_text", "exists", "backup",
    ])

    RESTRICTED_TOOLS: frozenset[str] = frozenset([
        constants.TOOL_PYTHON,
    ])

    SAFE_TOOLS: frozenset[str] = frozenset([
        constants.TOOL_CALCULATOR,
        constants.TOOL_MEMORY,
        constants.TOOL_INTERNET,
        constants.TOOL_FILES,
    ])

    PATH_TOOLS: frozenset[str] = frozenset([
        constants.TOOL_FILES,
    ])

    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        """Initialise the checker.

        Args:
            workspace_root: The workspace root for filesystem boundary
                enforcement.  When ``None``, the current working directory
                of the process is used as the default boundary.
        """
        if workspace_root is None:
            self._workspace_root = Path.cwd().resolve()
        else:
            self._workspace_root = Path(workspace_root).resolve()

    @property
    def workspace_root(self) -> Path:
        """Return the configured workspace root."""
        return self._workspace_root

    def check(
        self,
        tool_name: str,
        method_name: str,
        data: object = None,
    ) -> bool:
        """Validate a tool action.

        Args:
            tool_name: Identifier of the target tool.
            method_name: Name of the method that will be called.
            data: Optional first-argument to the tool method (e.g. a
                file path).  For non-path tools this may be ``None``.

        Returns:
            ``True`` if the action is permitted.

        Raises:
            PermissionError: If the action violates a boundary rule.
        """
        if tool_name in self.PATH_TOOLS:
            self._check_file_tool(self._workspace_root, method_name, data)
        if tool_name in self.RESTRICTED_TOOLS:
            self._check_restricted_tool(tool_name)

        return True

    @staticmethod
    def _check_file_tool(
        workspace_root: Path,
        method_name: str,
        data: object,
    ) -> None:
        """Validate FileTool boundary constraints.

        Args:
            workspace_root: The workspace root.
            method_name: The ``FileTool`` method being invoked.
            data: The first positional argument (often a path).

        Raises:
            PermissionError: If the path escapes the workspace root.
        """
        if method_name not in PermissionChecker.WORKSPACE_ROOT_METHODS:
            return

        if data is None:
            return

        if isinstance(data, dict):
            data = data.get("path")
        if data is None:
            return
        if not isinstance(data, (str, Path)):
            raise PermissionError("Filesystem action requires a path")

        text = str(data)
        # Reject Windows absolute/drive paths even when running on POSIX.
        if PureWindowsPath(text).drive:
            raise PermissionError(f"Path escapes workspace root: {text}")
        raw = Path(text)
        candidate = (workspace_root / raw).resolve() if not raw.is_absolute() else raw.resolve()
        try:
            candidate.relative_to(workspace_root)
        except ValueError:
            raise PermissionError(
                f"Path escapes workspace root: {candidate} "
                f"not within {workspace_root}"
            )

    @staticmethod
    def _check_restricted_tool(tool_name: str) -> None:
        """Validate restricted-tool constraints.

        Restricted tools must not be granted persistent filesystem writes
        outside their sandboxed semantic.  This method is the future
        extension point for sandboxing rules — at the moment it permits
        restricted tools because actual enforcement happens in their
        implementations.

        Args:
            tool_name: The restricted tool name.

        Raises:
            PermissionError: If the tool is explicitly forbidden.
        """
        return None
