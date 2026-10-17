"""Streamlit interface for Compiler Insight."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from compiler import CompilationResult, compile_source
from visualizer import build_ast_svg


ROOT = Path(__file__).resolve().parent
EXAMPLE_PATH = ROOT / "examples" / "basic_program.txt"
EXAMPLE_SOURCE = EXAMPLE_PATH.read_text(encoding="utf-8").rstrip()

st.set_page_config(
    page_title="Compiler Insight",
    page_icon="CI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "source_editor" not in st.session_state:
    st.session_state["source_editor"] = EXAMPLE_SOURCE


def show_compilation_summary(result: CompilationResult) -> None:
    st.subheader("Compilation summary")
    status = "Success" if result.success else result.stage
    st.write(f"**Status:** {status}")
    columns = st.columns(5)
    columns[0].metric("Tokens", result.token_count)
    columns[1].metric("Statements", result.statement_count)
    columns[2].metric("AST nodes", result.ast_node_count)
    columns[3].metric("Semantic errors", result.semantic_error_count)
    columns[4].metric("TAC instructions", len(result.tac))
    st.caption(
        f"Optimized instructions: {len(result.optimized_tac)} · "
        f"Last completed stage: {result.stage}"
    )
    if result.errors:
        for error in result.errors:
            st.error(error)
    elif result.success:
        st.success("All compiler stages completed.")


def show_lexical_tab(result: CompilationResult) -> None:
    st.markdown(
        "The lexer reads characters from left to right and groups them into "
        "tokens—the smallest meaningful units in this language."
    )
    st.caption("Identifiers use letters, digits, or underscores; integers contain digits.")
    if result.tokens:
        rows = [
            {
                "Token type": token.kind,
                "Value": token.value if token.value else "—",
                "Line": token.line,
                "Column": token.column,
            }
            for token in result.tokens
            if token.kind not in {"NEWLINE", "EOF"}
        ]
        st.dataframe(rows, hide_index=True, use_container_width=True)
        st.info(
            f"The lexer recognized {result.token_count} program tokens. "
            "Newlines separate assignments and are not counted as program tokens."
        )
    else:
        st.info("Tokens appear here after the source passes lexical analysis.")
    if result.lexical_error:
        st.error(str(result.lexical_error))


def show_syntax_tab(result: CompilationResult) -> None:
    st.markdown(
        "The parser checks that tokens follow the language grammar. Multiplication "
        "and division bind more tightly than addition and subtraction; parentheses "
        "can change that order."
    )
    with st.expander("Grammar used by this parser"):
        st.code(
            "program      ::= NEWLINE* (assignment NEWLINE+)* assignment? NEWLINE* EOF\n"
            "assignment   ::= IDENTIFIER '=' expression\n"
            "expression   ::= additive\n"
            "additive     ::= multiplicative (('+' | '-') multiplicative)*\n"
            "multiplicative ::= unary (('*' | '/') unary)*\n"
            "unary        ::= ('+' | '-') unary | primary\n"
            "primary      ::= INTEGER | IDENTIFIER | '(' expression ')'",
            language="text",
        )
    if result.program is not None:
        st.success(
            f"Syntax is valid. The parser produced {result.statement_count} "
            "assignment statement(s)."
        )
        st.write(
            "The grammar groups operators by precedence. For example, "
            "`2 + 3 * 4` is parsed as `2 + (3 * 4)`."
        )
    elif result.syntax_error:
        st.error(str(result.syntax_error))
    else:
        st.info("Syntax analysis runs after the lexer has produced valid tokens.")


def show_ast_tab(result: CompilationResult) -> None:
    st.markdown(
        "An Abstract Syntax Tree keeps the program's structure, not its original "
        "spacing. Each assignment and arithmetic operation is a node; its children "
        "are the values or subexpressions it uses."
    )
    if result.program is not None:
        st.caption(
            "This tree is drawn from the parser's AST. Editing the program refreshes it."
        )
        components.html(build_ast_svg(result.program), height=490, scrolling=True)
    elif result.syntax_error:
        st.info("The AST is not available because parsing stopped on a syntax error.")
    else:
        st.info("The AST appears after syntax analysis succeeds.")


def show_semantic_tab(result: CompilationResult) -> None:
    st.markdown(
        "Semantic analysis checks meaning after syntax is valid. A variable must "
        "have been assigned before it is read. The symbol table tracks assignments, "
        "uses, source lines, and values that can be determined statically."
    )
    if result.semantic is None:
        st.info("Semantic analysis runs only after successful parsing.")
        return
    if result.semantic.symbol_table.symbols:
        st.dataframe(
            result.semantic.symbol_table.as_rows(),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No variables were declared in this program.")
    if result.semantic.errors:
        st.subheader("Semantic errors")
        for error in result.semantic.errors:
            st.error(str(error))
    else:
        st.success("No undefined variables or detectable division-by-zero errors.")
    st.caption(
        "A value is marked as known only when its expression can be evaluated "
        "from earlier assignments and integer literals."
    )


def show_code_tab(result: CompilationResult) -> None:
    st.markdown(
        "Three-address code (TAC) breaks larger expressions into simple operations. "
        "A temporary such as `t1` holds one intermediate result."
    )
    if result.program is None or result.semantic is None:
        st.info("TAC generation is skipped until lexical, syntax, and semantic checks pass.")
    elif not result.semantic.success:
        st.warning("TAC was not generated because semantic analysis found errors.")
    elif result.tac:
        st.code("\n".join(result.tac), language="text")
        st.caption(
            "Instructions follow expression evaluation order, respecting the "
            "parser's operator precedence."
        )
    else:
        st.info("This valid program has no assignment instructions.")


def show_optimization_tab(result: CompilationResult) -> None:
    st.markdown(
        "Constant folding evaluates an expression during compilation when all of "
        "its operands are known numeric constants. Non-constant expressions are "
        "kept, and a divisor of zero is never evaluated by the optimizer."
    )
    if result.program is None or result.semantic is None:
        st.info("Optimization is skipped when an earlier compiler stage fails.")
        return
    if not result.semantic.success:
        st.warning("Optimization was skipped because semantic analysis found errors.")
        return
    before, after = st.columns(2)
    with before:
        st.subheader("Before optimization")
        st.code("\n".join(result.tac) or "(no instructions)", language="text")
    with after:
        st.subheader("After constant folding")
        st.code(
            "\n".join(result.optimized_tac) or "(no instructions)",
            language="text",
        )
    st.caption(
        "For example, `x = 2 + 3 * 4` becomes `x = 14`. The optimizer transforms "
        "the AST; both code listings are generated from their respective ASTs."
    )


st.title("Compiler Insight")
st.subheader("Visualizing the Compilation Process")
st.write(
    "Explore how a small arithmetic program moves through a compiler—from source "
    "characters to tokens, a syntax tree, semantic checks, intermediate code, and "
    "constant-folded output."
)
st.caption("An offline-friendly academic mini-project. Your source stays in this app.")

st.subheader("Source program")
st.write(
    "Edit the sample and the result panels update automatically. "
    "Only assignments and arithmetic expressions are supported."
)
source_column, action_column = st.columns([5, 1])
with source_column:
    source = st.text_area(
        "Write one assignment per line",
        key="source_editor",
        height=210,
        label_visibility="collapsed",
    )
with action_column:
    st.write("")
    st.write("")
    compile_clicked = st.button("Compile program", type="primary", use_container_width=True)
    reset_clicked = st.button("Reset example", use_container_width=True)

if reset_clicked:
    st.session_state["source_editor"] = EXAMPLE_SOURCE
    st.session_state["last_compiled_source"] = None
    st.rerun()

if (
    compile_clicked
    or "last_compiled_source" not in st.session_state
    or st.session_state["last_compiled_source"] != source
):
    st.session_state["compilation_result"] = compile_source(source)
    st.session_state["last_compiled_source"] = source

result: CompilationResult = st.session_state["compilation_result"]
show_compilation_summary(result)

tabs = st.tabs(
    [
        "Lexical analysis",
        "Syntax analysis",
        "AST visualization",
        "Semantic analysis",
        "Intermediate code",
        "Optimization",
    ]
)
tab_views = [
    show_lexical_tab,
    show_syntax_tab,
    show_ast_tab,
    show_semantic_tab,
    show_code_tab,
    show_optimization_tab,
]
for tab, render in zip(tabs, tab_views):
    with tab:
        render(result)

st.divider()
with st.expander("Learn compiler concepts", expanded=False):
    st.markdown(
        """
### What does a compiler do?
A compiler transforms a source program into a different representation through
several stages. This teaching compiler makes those stages visible and stops when
an earlier stage reports an error.

### Lexical analysis: characters become tokens
The lexer groups characters into identifiers (`count`), integer literals (`12`),
operators (`+`, `*`, `=`), and parentheses. An unsupported character is a lexical
error because it cannot be classified by this language.

### Syntax analysis: tokens become a structure
The recursive-descent parser follows the grammar shown in the Syntax tab. Its
separate grammar rules encode precedence: multiplication and division are parsed
before addition and subtraction. Parenthesized expressions are parsed as a unit.

### Abstract Syntax Tree
The AST captures nested meaning. In `2 + 3 * 4`, the multiplication node is a
child of addition's right side. Whitespace and redundant parentheses are not
needed in the tree.

### Semantic analysis and the symbol table
Parsing checks form; semantic analysis checks context. It processes statements
from top to bottom, tracks assigned variables, reports reads before assignment,
and detects divisors that evaluate to zero. The symbol table reports where each
variable is assigned and used.

### Three-address code
TAC gives each operation a simple instruction, often storing a result in a
temporary (`t1`, `t2`). This makes evaluation order explicit and creates a useful
intermediate representation between a source language and machine code.

### Optimization: constant folding
The optimizer replaces arithmetic subtrees made entirely of constants with their
computed value. It does not evaluate division by zero. Non-constant expressions
remain unchanged. This project demonstrates one local optimization, not a full
production compiler.

### Error stages
Lexical errors mean a character is unsupported. Syntax errors mean tokens do not
fit the grammar. Semantic errors mean a syntactically valid program uses a
variable before assignment or has a detectable division by zero. TAC and
optimization are skipped after an earlier failure.
"""
    )
st.caption("Compiler Insight · B.Tech CSE academic mini-project")
