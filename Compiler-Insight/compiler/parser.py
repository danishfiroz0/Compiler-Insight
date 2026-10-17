"""Recursive-descent parser for the documented assignment-expression grammar."""

from __future__ import annotations

from .ast_nodes import Assignment, Binary, Expression, Identifier, Number, Program, Unary
from .lexer import Token


class ParseError(ValueError):
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(
            f"{message} at line {token.line}, column {token.column}"
        )


class Parser:
    """Parse a token sequence using one method per grammar precedence level."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.position]

    def advance(self) -> Token:
        token = self.current
        if token.kind != "EOF":
            self.position += 1
        return token

    def expect(self, kind: str, description: str) -> Token:
        if self.current.kind != kind:
            raise ParseError(
                f"Expected {description}, found {self.describe(self.current)}",
                self.current,
            )
        return self.advance()

    @staticmethod
    def describe(token: Token) -> str:
        return repr(token.value) if token.value else "end of input"

    def parse(self) -> Program:
        statements: Program = []
        self.skip_newlines()
        while self.current.kind != "EOF":
            statements.append(self.parse_assignment())
            if self.current.kind not in {"NEWLINE", "EOF"}:
                raise ParseError(
                    f"Expected a new line, found {self.describe(self.current)}",
                    self.current,
                )
            self.skip_newlines()
        return statements

    def skip_newlines(self) -> None:
        while self.current.kind == "NEWLINE":
            self.advance()

    def parse_assignment(self) -> Assignment:
        name = self.expect("IDENTIFIER", "an assignment target")
        self.expect("ASSIGN", "'='")
        expression = self.parse_expression()
        return Assignment(name.value, expression, name.line, name.column)

    def parse_expression(self) -> Expression:
        return self.parse_additive()

    def parse_additive(self) -> Expression:
        expression = self.parse_multiplicative()
        while self.current.kind in {"PLUS", "MINUS"}:
            operator = self.advance()
            right = self.parse_multiplicative()
            expression = Binary(
                expression, operator.value, right, operator.line, operator.column
            )
        return expression

    def parse_multiplicative(self) -> Expression:
        expression = self.parse_unary()
        while self.current.kind in {"MULTIPLY", "DIVIDE"}:
            operator = self.advance()
            right = self.parse_unary()
            expression = Binary(
                expression, operator.value, right, operator.line, operator.column
            )
        return expression

    def parse_unary(self) -> Expression:
        if self.current.kind in {"PLUS", "MINUS"}:
            operator = self.advance()
            return Unary(
                operator.value,
                self.parse_unary(),
                operator.line,
                operator.column,
            )
        return self.parse_primary()

    def parse_primary(self) -> Expression:
        token = self.current
        if token.kind == "INTEGER":
            self.advance()
            return Number(int(token.value), token.line, token.column)
        if token.kind == "IDENTIFIER":
            self.advance()
            return Identifier(token.value, token.line, token.column)
        if token.kind == "LEFT_PAREN":
            self.advance()
            expression = self.parse_expression()
            self.expect("RIGHT_PAREN", "')'")
            return expression
        raise ParseError(
            f"Expected a number, variable, or parenthesized expression, found "
            f"{self.describe(token)}",
            token,
        )


def parse(tokens: list[Token]) -> Program:
    """Parse tokens into assignment statements."""
    return Parser(tokens).parse()
