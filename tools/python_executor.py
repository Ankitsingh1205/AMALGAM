import io
import contextlib

from tools.base_tool import BaseTool


class PythonExecutor(BaseTool):

    name = "python"

    def execute(self, code: str):

        output = io.StringIO()

        try:

            with contextlib.redirect_stdout(output):
                exec(code, {})

            return output.getvalue().strip()

        except Exception as e:

            return f"Python Error: {e}"