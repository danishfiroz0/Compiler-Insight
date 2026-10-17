"""Safe constant-folding optimizer for the compiler's arithmetic AST."""

from __future__ import annotations

from .ast_nodes import Assignment, Binary, Expression, Identifier, Number, Program, Unary
from .tac_generator import format_number


def _constant_value(node: Expression) -> int | float | None:
    if isinstance(node, Number):
        return node.value
    if isinstance(node, Identifier):
        return None
    if isinstance(node, Unary):
        value = _constant_value(node.operand)
        if value is None:
            return None
        return value if node.operator == "+" else -value
    left = _constant_value(node.left)
    right = _constant_value(node.right)
    if left is None or right is None:
        return None
    if node.operator == "/" and right == 0:
        return None
    if node.operator == "+":
        return left + right
    if node.operator == "-":
        return left - right
    if node.operator == "*":
        return left * right
    try:
        return left / right
    except (ArithmeticError, OverflowError):
        return None


def fold_expression(node: Expression) -> Expression:
    """Fold fully constant subtrees, never evaluating division by zero."""
    if isinstance(node, (Number, Identifier)):
        return node
    if isinstance(node, Unary):
        operand = fold_expression(node.operand)
        folded = Unary(node.operator, operand, node.line, node.column)
        value = _constant_value(folded)
        if value is not None:
            return Number(
                int(value) if isinstance(value, float) and value.is_integer() else value,
                node.line,
                node.column,
            )
        return folded

    left = fold_expression(node.left)
    right = fold_expression(node.right)
    folded = Binary(left, node.operator, right, node.line, node.column)
    value = _constant_value(folded)
    if value is None:
        return folded
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return Number(value, node.line, node.column)


def optimize(program: Program) -> Program:
    """Return a new AST with constant arithmetic subtrees folded."""
    return [
        Assignment(
            statement.name,
            fold_expression(statement.expression),
            statement.line,
            statement.column,
        )
        for statement in program
    ]


def describe_folded_program(program: Program) -> list[str]:
    """Provide readable assignment forms for a folded AST."""
    from .ast_nodes import Binary, Identifier, Number, Unary

    def render(node: Expression) -> str:
        if isinstance(node, Number):
            return format_number(node.value)
        if isinstance(node, Identifier):
            return node.name
        if isinstance(node, Unary):
            return f"{node.operator}{render(node.operand)}"
        return f"({render(node.left)} {node.operator} {render(node.right)})"

    return [f"{item.name} = {render(item.expression)}" for item in program]
