"""Sandboxed Python execution (Mission 7.6, SEC-002).

Replaces the previous in-process ``exec()`` with subprocess isolation:
code runs in a separate interpreter with ``-I`` (isolated mode: no
site-packages, no user site, no PYTHONPATH inheritance), a bounded
timeout, and an empty environment.  A crash or hang in executed code
can no longer take down or block the AMALGAM process, and executed
code cannot mutate AMALGAM's in-memory state.
"""

import subprocess
import sys

from tools.base_tool import BaseTool

_DEFAULT_TIMEOUT_SECONDS = 10


class PythonExecutor(BaseTool):

    name = "python"

    def __init__(self, timeout: float = _DEFAULT_TIMEOUT_SECONDS):
        self._timeout = timeout

    def execute(self, code: str):
        """Run code in an isolated subprocess and return its stdout.

        Preserves the historical contract: stripped stdout on success,
        a string starting with ``"Python Error:"`` on failure.
        """
        try:
            completed = subprocess.run(
                [sys.executable, "-I", "-c", str(code)],
                capture_output=True,
                text=True,
                timeout=self._timeout,
                env={},
            )
        except subprocess.TimeoutExpired:
            return f"Python Error: execution exceeded {self._timeout}s timeout"
        except Exception as e:
            return f"Python Error: {e}"

        if completed.returncode != 0:
            stderr = completed.stderr.strip().splitlines()
            detail = stderr[-1] if stderr else f"exit code {completed.returncode}"
            return f"Python Error: {detail}"

        return completed.stdout.strip()
