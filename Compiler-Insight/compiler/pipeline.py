"""Orchestrate compiler stages and stop after the first failed stage."""

from __future__ import annotations

from dataclasses import dataclass, field

from .ast_nodes import Program, count_program_nodes
from .lexer import LexError, Token, tokenize
from .optimizer import optimize
from .parser import ParseError, parse
from .semantic_analyzer import SemanticResult, analyze
from .tac_generator import generate_tac


@dataclass
class CompilationResult:
    source: str
    tokens: list[Token] = field(default_factory=list)
    program: Program | None = None
    semantic: SemanticResult | None = None
    tac: list[str] = field(default_factory=list)
    optimized_program: Program | None = None
    optimized_tac: list[str] = field(default_factory=list)
    stage: str = "Not started"
    errors: list[str] = field(default_factory=list)
    lexical_error: LexError | None = None
    syntax_error: ParseError | None = None

    @property
    def success(self) -> bool:
        return self.stage == "Complete" and not self.errors

    @property
    def token_count(self) -> int:
        return sum(token.kind not in {"NEWLINE", "EOF"} for token in self.tokens)

    @property
    def statement_count(self) -> int:
        return len(self.program or [])

    @property
    def ast_node_count(self) -> int:
        return count_program_nodes(self.program) if self.program is not None else 0

    @property
    def semantic_error_count(self) -> int:
        return len(self.semantic.errors) if self.semantic is not None else 0


def compile_source(source: str) -> CompilationResult:
    """Compile source through lexing, parsing, semantics, TAC, and optimization."""
    result = CompilationResult(source=source)
    try:
        result.tokens = tokenize(source)
    except LexError as error:
        result.tokens = error.tokens
        result.lexical_error = error
        result.errors.append(str(error))
        result.stage = "Lexical analysis failed"
        return result
    result.stage = "Lexical analysis complete"

    try:
        result.program = parse(result.tokens)
    except ParseError as error:
        result.syntax_error = error
        result.errors.append(str(error))
        result.stage = "Syntax analysis failed"
        return result
    result.stage = "Syntax analysis complete"

    result.semantic = analyze(result.program)
    if not result.semantic.success:
        result.errors.extend(str(issue) for issue in result.semantic.errors)
        result.stage = "Semantic analysis failed"
        return result
    result.stage = "Semantic analysis complete"

    result.tac = generate_tac(result.program)
    result.optimized_program = optimize(result.program)
    result.optimized_tac = generate_tac(result.optimized_program)
    result.stage = "Complete"
    return result
