from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.tac_generator import generate_tac


def test_generates_three_address_code_in_precedence_order():
    program = parse(tokenize("z = x + y * 2"))
    assert generate_tac(program) == [
        "t1 = y * 2",
        "t2 = x + t1",
        "z = t2",
    ]


def test_generates_direct_assignment_without_extra_temporary():
    program = parse(tokenize("x = 10"))
    assert generate_tac(program) == ["x = 10"]


def test_generates_multiple_statements_in_order():
    program = parse(tokenize("x = 10\ny = x + 2"))
    assert generate_tac(program) == ["x = 10", "t1 = x + 2", "y = t1"]


def test_generates_unary_minus():
    program = parse(tokenize("x = -4"))
    assert generate_tac(program) == ["t1 = - 4", "x = t1"]
