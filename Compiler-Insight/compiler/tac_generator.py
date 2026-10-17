"""Three-address-code generation from the syntax tree."""

from __future__ import annotations

from .ast_nodes import Assignment, Binary, Expression, Identifier, Number, Program, Unary


def format_number(value: int | float) -> str:
    """Render integral floats as integers and other values with stable precision."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return format(value, ".12g") if isinstance(value, float) else str(value)


class TACGenerator:
    def __init__(self) -> None:
        self.instructions: list[str] = []
        self.temporary_count = 0

    def new_temporary(self) -> str:
        self.temporary_count += 1
        return f"t{self.temporary_count}"

    def expression(self, node: Expression) -> str:
        if isinstance(node, Number):
            return str(node.value)
        if isinstance(node, Identifier):
            return node.name
        if isinstance(node, Unary):
            operand = self.expression(node.operand)
            if node.operator == "+":
                return operand
            temporary = self.new_temporary()
            self.instructions.append(f"{temporary} = - {operand}")
            return temporary

        left = self.expression(node.left)
        right = self.expression(node.right)
        temporary = self.new_temporary()
        self.instructions.append(f"{temporary} = {left} {node.operator} {right}")
        return temporary

    def generate(self, program: Program) -> list[str]:
        for statement in program:
            assert isinstance(statement, Assignment)
            value = self.expression(statement.expression)
            self.instructions.append(f"{statement.name} = {value}")
        return self.instructions


def generate_tac(program: Program) -> list[str]:
    """Generate temporaries in evaluation order and one write per assignment."""
    return TACGenerator().generate(program)
