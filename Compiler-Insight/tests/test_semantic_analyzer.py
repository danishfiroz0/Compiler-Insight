from compiler import compile_source
from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.semantic_analyzer import analyze


def test_detects_undefined_variables_in_source_order():
    result = analyze(parse(tokenize("x = missing + 1\ny = 4")))
    assert any("Undefined variable 'missing'" in str(error) for error in result.errors)
    assert "y" in result.symbol_table.symbols


def test_symbol_table_tracks_assignments_uses_and_known_values():
    result = analyze(parse(tokenize("x = 2\nx = x + 3\ny = x * 2")))
    x = result.symbol_table.symbols["x"]
    y = result.symbol_table.symbols["y"]
    assert x.assignment_count == 2
    assert x.usage_count == 2
    assert x.known_value == 5
    assert y.known_value == 10


def test_detects_direct_and_computed_division_by_zero():
    for source in ("x = 1 / 0", "x = 1 / (3 - 3)"):
        result = compile_source(source)
        assert result.stage == "Semantic analysis failed"
        assert any("Division by zero" in error for error in result.errors)
        assert result.tac == []


def test_undefined_reads_are_not_added_to_symbol_table():
    result = analyze(parse(tokenize("x = missing + 1")))
    assert "missing" not in result.symbol_table.symbols
    assert "x" in result.symbol_table.symbols


def test_compiler_stops_after_lexical_and_syntax_failures():
    lexical = compile_source("x = 1 @ 2")
    syntax = compile_source("x = (1 + 2")
    assert lexical.program is None
    assert lexical.tac == []
    assert syntax.semantic is None
    assert syntax.tac == []
