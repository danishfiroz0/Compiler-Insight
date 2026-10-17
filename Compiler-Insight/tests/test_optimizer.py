from compiler import compile_source
from compiler.ast_nodes import Number
from compiler.lexer import tokenize
from compiler.optimizer import optimize
from compiler.parser import parse
from compiler.tac_generator import generate_tac


def test_folds_constant_expression_with_correct_precedence():
    result = compile_source("x = 2 + 3 * 4")
    assert result.success
    assert result.tac == ["t1 = 3 * 4", "t2 = 2 + t1", "x = t2"]
    assert result.optimized_tac == ["x = 14"]


def test_folds_parenthesized_constants():
    result = compile_source("x = (2 + 3) * 4")
    assert result.optimized_tac == ["x = 20"]


def test_leaves_division_by_zero_unfolded_without_crashing():
    program = parse(tokenize("x = 4 / 0"))
    optimized = optimize(program)
    assert isinstance(optimized[0].expression, type(program[0].expression))
    assert generate_tac(optimized) == ["t1 = 4 / 0", "x = t1"]


def test_preserves_nonconstant_expression():
    result = compile_source("x = 4\ny = x + 2")
    assert result.success
    assert result.optimized_tac == result.tac


def test_folds_constant_unary_expression():
    program = optimize(parse(tokenize("x = -(3 + 2)")))
    assert isinstance(program[0].expression, Number)
    assert program[0].expression.value == -5


def test_invalid_program_never_generates_tac():
    result = compile_source("x = missing + 1")
    assert not result.success
    assert result.optimized_tac == []
