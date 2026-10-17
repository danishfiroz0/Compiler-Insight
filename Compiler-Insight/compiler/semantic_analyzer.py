"""Sequential semantic checks and symbol-table construction."""

from __future__ import annotations

from dataclasses import dataclass, field

from .ast_nodes import Assignment, Binary, Expression, Identifier, Number, Program, Unary
from .symbol_table import SymbolTable


@dataclass(frozen=True)
class SemanticIssue:
    message: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"{self.message} (line {self.line}, column {self.column})"


@dataclass
class SemanticResult:
    symbol_table: SymbolTable = field(default_factory=SymbolTable)
    errors: list[SemanticIssue] = field(default_factory=list)
    final_values: dict[str, int | float | None] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return not self.errors


def _evaluate(
    expression: Expression,
    values: dict[str, int | float | None],
    table: SymbolTable,
    errors: list[SemanticIssue],
) -> int | float | None:
    if isinstance(expression, Number):
        return expression.value
    if isinstance(expression, Identifier):
        if expression.name not in values:
            errors.append(
                SemanticIssue(
                    f"Undefined variable {expression.name!r}",
                    expression.line,
                    expression.column,
                )
            )
            return None
        table.record_usage(expression.name)
        return values[expression.name]
    if isinstance(expression, Unary):
        value = _evaluate(expression.operand, values, table, errors)
        if value is None:
            return None
        return value if expression.operator == "+" else -value

    left = _evaluate(expression.left, values, table, errors)
    right = _evaluate(expression.right, values, table, errors)
    if expression.operator == "/" and right == 0:
        errors.append(
            SemanticIssue(
                "Division by zero: the divisor evaluates to zero",
                expression.line,
                expression.column,
            )
        )
        return None
    if left is None or right is None:
        return None
    try:
        if expression.operator == "+":
            return left + right
        if expression.operator == "-":
            return left - right
        if expression.operator == "*":
            return left * right
        return left / right
    except (ArithmeticError, OverflowError):
        return None


def analyze(program: Program) -> SemanticResult:
    """Analyze assignments in source order, reporting undefined reads and zero division."""
    result = SemanticResult()
    values: dict[str, int | float | None] = {}
    for statement in program:
        assert isinstance(statement, Assignment)
        value = _evaluate(
            statement.expression, values, result.symbol_table, result.errors
        )
        values[statement.name] = value
        result.symbol_table.record_assignment(statement.name, statement.line, value)
    result.final_values = values
    return result
