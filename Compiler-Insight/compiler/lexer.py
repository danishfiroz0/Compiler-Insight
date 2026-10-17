"""Lexer for identifiers, integers, assignment, arithmetic, and parentheses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    column: int


class LexError(ValueError):
    def __init__(
        self,
        message: str,
        line: int,
        column: int,
        tokens: list[Token] | None = None,
    ):
        self.message = message
        self.line = line
        self.column = column
        self.tokens = tokens or []
        super().__init__(f"{message} at line {line}, column {column}")


def tokenize(source: str) -> list[Token]:
    """Return source tokens, preserving newlines as statement separators.

    Spaces and tabs are ignored. Newlines become NEWLINE tokens; carriage
    returns are accepted for Windows-style line endings.
    """
    tokens: list[Token] = []
    index = 0
    line = 1
    column = 1
    length = len(source)

    while index < length:
        char = source[index]
        if char in " \t":
            index += 1
            column += 1
            continue
        if char == "\r":
            index += 1
            if index < length and source[index] == "\n":
                index += 1
            tokens.append(Token("NEWLINE", "\\n", line, column))
            line += 1
            column = 1
            continue
        if char == "\n":
            tokens.append(Token("NEWLINE", "\\n", line, column))
            index += 1
            line += 1
            column = 1
            continue
        if char.isalpha() or char == "_":
            start = index
            start_column = column
            while index < length and (
                source[index].isalnum() or source[index] == "_"
            ):
                index += 1
                column += 1
            tokens.append(Token("IDENTIFIER", source[start:index], line, start_column))
            continue
        if char.isdigit():
            start = index
            start_column = column
            while index < length and source[index].isdigit():
                index += 1
                column += 1
            tokens.append(Token("INTEGER", source[start:index], line, start_column))
            continue

        kinds = {
            "=": "ASSIGN",
            "+": "PLUS",
            "-": "MINUS",
            "*": "MULTIPLY",
            "/": "DIVIDE",
            "(": "LEFT_PAREN",
            ")": "RIGHT_PAREN",
        }
        if char in kinds:
            tokens.append(Token(kinds[char], char, line, column))
            index += 1
            column += 1
            continue

        raise LexError(
            f"Invalid character {char!r}", line, column, tokens=tokens.copy()
        )

    tokens.append(Token("EOF", "", line, column))
    return tokens
