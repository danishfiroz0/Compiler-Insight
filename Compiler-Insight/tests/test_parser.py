import pytest

from compiler.ast_nodes import Assignment, Binary, Identifier, Number
from compiler.lexer import tokenize
from compiler.parser import ParseError, parse


def test_multiplication_has_precedence_over_addition():
    program = parse(tokenize("answer = 2 + 3 * 4"))
    expression = program[0].expression
    assert isinstance(expression, Binary)
    assert expression.operator == "+"
    assert isinstance(expression.right, Binary)
    assert expression.right.operator == "*"


def test_parentheses_override_precedence():
    program = parse(tokenize("answer = (2 + 3) * 4"))
    expression = program[0].expression
    assert isinstance(expression, Binary)
    assert expression.operator == "*"
    assert isinstance(expression.left, Binary)
    assert expression.left.operator == "+"


def test_parses_assignments_and_repeated_lines():
    program = parse(tokenize("x = 1\nx = x + 2\n"))
    assert len(program) == 2
    assert all(isinstance(item, Assignment) for item in program)
    assert isinstance(program[1].expression, Binary)
    assert isinstance(program[1].expression.left, Identifier)


@pytest.mark.parametrize("source", ["x =", "= 4", "x = (2 + 3", "x = 1 2", "x = 1 +"])
def test_reports_syntax_errors(source):
    with pytest.raises(ParseError):
        parse(tokenize(source))


def test_empty_program_is_valid():
    assert parse(tokenize("\n  \n")) == []


def test_integer_leaf_is_number():
    assert isinstance(parse(tokenize("x = 9"))[0].expression, Number)
