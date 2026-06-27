from tools.base_tool import BaseTool


class Calculator(BaseTool):

    name = "calculator"

    def calculate(self, expression: str):

        try:
            return eval(expression)

        except Exception:
            return None