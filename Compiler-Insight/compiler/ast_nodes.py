"""Typed abstract syntax tree nodes for the language."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias


@dataclass(frozen=True)
class Number:
    value: int
    line: int
    column: int


@dataclass(frozen=True)
class Identifier:
    name: str
    line: int
    column: int


@dataclass(frozen=True)
class Unary:
    operator: str
    operand: "Expression"
    line: int
    column: int


@dataclass(frozen=True)
class Binary:
    left: "Expression"
    operator: str
    right: "Expression"
    line: int
    column: int


Expression: TypeAlias = Number | Identifier | Unary | Binary


@dataclass(frozen=True)
class Assignment:
    name: str
    expression: Expression
    line: int
    column: int


Statement: TypeAlias = Assignment
Program: TypeAlias = list[Statement]


def count_expression_nodes(expression: Expression) -> int:
    """Count every expression node in a tree."""
    if isinstance(expression, (Number, Identifier)):
        return 1
    if isinstance(expression, Unary):
        return 1 + count_expression_nodes(expression.operand)
    return (
        1
        + count_expression_nodes(expression.left)
        + count_expression_nodes(expression.right)
    )


def count_program_nodes(program: Program) -> int:
    """Count assignment nodes as well as their expression descendants."""
    return sum(1 + count_expression_nodes(item.expression) for item in program)
