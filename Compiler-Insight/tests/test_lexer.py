import pytest

from compiler.lexer import LexError, tokenize


def test_tokenizes_identifiers_integers_and_operators():
    tokens = tokenize("total_2 = 12 + value * (3 - 1)")
    assert [token.kind for token in tokens] == [
        "IDENTIFIER",
        "ASSIGN",
        "INTEGER",
        "PLUS",
        "IDENTIFIER",
        "MULTIPLY",
        "LEFT_PAREN",
        "INTEGER",
        "MINUS",
        "INTEGER",
        "RIGHT_PAREN",
        "EOF",
    ]


def test_tracks_newlines_and_locations():
    tokens = tokenize("a = 1\nb = 2")
    assert tokens[3].kind == "NEWLINE"
    assert (tokens[4].line, tokens[4].column) == (2, 1)


def test_rejects_invalid_characters_with_location():
    with pytest.raises(LexError, match="Invalid character '@'.*line 1, column 5"):
        tokenize("x = @")


def test_keeps_tokens_recognized_before_an_invalid_character():
    from compiler import compile_source

    result = compile_source("x = 2 + @")
    assert result.token_count == 4
    assert [token.value for token in result.tokens] == ["x", "=", "2", "+"]
    assert result.stage == "Lexical analysis failed"


def test_accepts_windows_line_endings():
    tokens = tokenize("x = 1\r\ny = 2")
    assert sum(token.kind == "NEWLINE" for token in tokens) == 1
