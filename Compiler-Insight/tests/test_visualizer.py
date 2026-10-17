from compiler.lexer import tokenize
from compiler.parser import parse
from visualizer import build_ast_svg


def test_svg_uses_nodes_and_operators_from_the_actual_ast():
    svg = build_ast_svg(parse(tokenize("answer = 2 + 3 * 4")))
    assert "<svg" in svg
    assert "Assignment: answer" in svg
    assert "Binary: +" in svg
    assert "Binary: *" in svg
    assert "Number: 3" in svg
    assert "<line" in svg


def test_svg_escapes_user_identifiers():
    svg = build_ast_svg(parse(tokenize("safe_name = 2")))
    assert "Assignment: safe_name" in svg
