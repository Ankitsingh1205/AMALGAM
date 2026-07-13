"""Safe arithmetic calculator (Mission 7.6, SEC-001).

Replaces the previous ``eval()``-based implementation with an AST
whitelist evaluator.  Only numeric literals and arithmetic operators
are permitted -- names, calls, attribute access, subscripts, and any
other syntax are rejected, which eliminates the arbitrary-code-execution
vector flagged in the Mission 6.4.3 security audit.
"""

import ast
import operator

from tools.base_tool import BaseTool

_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

# Guard against memory-exhaustion via huge exponents (e.g. 9**9**9).
_MAX_POW_EXPONENT = 10_000


class Calculator(BaseTool):

    name = "calculator"

    def calculate(self, expression: str):
        """Evaluate an arithmetic expression safely.

        Returns the numeric result, or ``None`` when the expression is
        not pure arithmetic (preserving the historical error contract).
        """
        try:
            tree = ast.parse(str(expression), mode="eval")
            return self._eval_node(tree.body)
        except Exception:
            return None

    def _eval_node(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                return node.value
            raise ValueError("non-numeric literal")

        if isinstance(node, ast.BinOp):
            op = _BINARY_OPS.get(type(node.op))
            if op is None:
                raise ValueError("operator not allowed")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > _MAX_POW_EXPONENT:
                raise ValueError("exponent too large")
            return op(left, right)

        if isinstance(node, ast.UnaryOp):
            op = _UNARY_OPS.get(type(node.op))
            if op is None:
                raise ValueError("operator not allowed")
            return op(self._eval_node(node.operand))

        raise ValueError("expression not allowed")
