# Compiler Insight: Visualizing the Compilation Process

An educational, local Streamlit application that demonstrates how a small
arithmetic language passes through lexical analysis, parsing, AST construction,
semantic analysis, three-address code generation, and constant folding.

## Abstract

Compiler Insight is a beginner-friendly mini-project for exploring the stages of
a compiler without relying on a remote service. It includes a real lexer, a
recursive-descent parser, a typed Abstract Syntax Tree (AST), a symbol table,
semantic checks, three-address code (TAC) generation, and a constant-folding
optimizer. A Streamlit interface displays the actual results produced by the
compiler implementation and updates them when the source changes.

## Problem statement

Compiler stages can be difficult to understand when each transformation is
hidden inside a command-line tool. Students need a small, inspectable example
that connects source text to tokens, syntax, variable meaning, intermediate
instructions, and a simple optimization while showing where errors occur.

## Objectives

- Implement lexical analysis for the project's arithmetic language.
- Parse assignments and expressions with a documented precedence-aware grammar.
- Construct and visualize an AST from parsed input.
- Check variable use and detectable division by zero using a symbol table.
- Generate TAC from the AST rather than from hardcoded examples.
- Demonstrate safe constant folding and compare code before and after it.
- Provide local, beginner-friendly explanations and meaningful automated tests.

## Features

- Source editor with a working multi-line sample and reset button.
- Tokens with type and source location, plus invalid-character reporting.
- Recursive-descent parsing with operator precedence, unary signs, and parentheses.
- AST rendered as an SVG tree directly from the current parsed AST.
- Sequential symbol-table updates, undefined-variable checks, and division-by-zero
  checks for divisors that can be evaluated statically.
- TAC with generated temporary variables.
- Constant-folded AST and regenerated optimized TAC.
- Compilation summary with status, token/statement/AST counts, semantic error
  count, and instruction counts.
- Six stage tabs, deterministic learning material, examples, and pytest coverage.
- No API keys, paid services, database, Graphviz binary, or other system
  dependencies are required.

## Technologies

- Python 3.11 or newer
- Streamlit for the browser-based interface
- pytest for automated tests
- Inline SVG for dependency-free AST visualization

The SVG renderer is a small local alternative to Graphviz, so no external
`dot` executable or network service is needed.

## Language and grammar

The language accepts integer literals, identifiers, assignments, `+`, `-`, `*`,
`/`, parentheses, unary `+` and `-`, and newline-separated assignments. Identifiers
start with a letter or underscore and may then contain letters, digits, or
underscores. There are no comments, decimal literals, comparisons, or control
flow statements.

```text
program        ::= NEWLINE* (assignment NEWLINE+)* assignment? NEWLINE* EOF
assignment     ::= IDENTIFIER '=' expression
expression     ::= additive
additive       ::= multiplicative (('+' | '-') multiplicative)*
multiplicative ::= unary (('*' | '/') unary)*
unary          ::= ('+' | '-') unary | primary
primary        ::= INTEGER | IDENTIFIER | '(' expression ')'
```

Multiplication and division therefore have higher precedence than addition and
subtraction; operators at the same precedence level associate from left to
right.

## Architecture

1. **Lexer** (`compiler/lexer.py`) scans characters and emits tokens with
   line/column positions.
2. **Parser** (`compiler/parser.py`) consumes the token stream and constructs
   dataclass AST nodes defined in `compiler/ast_nodes.py`.
3. **Semantic analyzer** (`compiler/semantic_analyzer.py`) reads statements in
   order and builds the symbol table defined in `compiler/symbol_table.py`.
4. **TAC generator** (`compiler/tac_generator.py`) recursively turns AST
   expressions into three-address instructions.
5. **Optimizer** (`compiler/optimizer.py`) creates a new AST by folding constant
   arithmetic subtrees without evaluating division by zero.
6. **Pipeline** (`compiler/pipeline.py`) runs these stages in order and stops
   later work after a lexical, syntax, or semantic error.
7. **Visualizer and UI** (`visualizer/tree_visualizer.py`, `app.py`) show the
   actual tree and compiler results in Streamlit.

## Directory structure

```text
Compiler-Insight/
├── app.py
├── compiler/
│   ├── __init__.py
│   ├── ast_nodes.py
│   ├── lexer.py
│   ├── optimizer.py
│   ├── parser.py
│   ├── pipeline.py
│   ├── semantic_analyzer.py
│   ├── symbol_table.py
│   └── tac_generator.py
├── docs/
│   └── project_report.md
├── examples/
│   ├── basic_program.txt
│   └── error_examples.txt
├── screenshots/
│   └── README.md
├── tests/
│   ├── test_lexer.py
│   ├── test_optimizer.py
│   ├── test_parser.py
│   ├── test_semantic_analyzer.py
│   ├── test_tac_generator.py
│   └── test_visualizer.py
├── visualizer/
│   ├── __init__.py
│   └── tree_visualizer.py
├── .gitignore
├── .streamlit/
│   └── config.toml
├── LICENSE
├── pytest.ini
├── README.md
└── requirements.txt
```

## Installation

Install Python 3.11 or newer. No system-level Graphviz installation is needed.
From the extracted project directory, create and activate a virtual environment
(recommended):

### Windows (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

If `python3` points to a version older than 3.11, use the command for your
Python 3.11+ installation when creating the environment.

## Run the application

From the `Compiler-Insight` directory, with the environment active:

```bash
streamlit run app.py
```

Streamlit prints the local URL in the terminal. Open it in a browser. The
included standard Streamlit configuration runs headlessly, suppresses its
first-run email prompt, and disables usage-stat collection. The app uses local
compiler code and does not send source code to an external API.

## Run tests

```bash
pytest
```

Tests cover tokenization and invalid characters, source positions, precedence,
parentheses, assignments, syntax failures, undefined variables, symbol-table
updates, TAC, constant folding, division-by-zero safety, and pipeline stopping
behavior.

## Sample input and output

Input (also available in `examples/basic_program.txt`):

```text
x = 10
y = 20
z = x + y * 2
result = (z - 5) / 3
```

The lexer recognizes the identifiers, integer literals, assignment symbols,
arithmetic operators, and parentheses. The parser nests `y * 2` below `x + ...`
because multiplication has higher precedence. The semantic stage can determine
`x = 10`, `y = 20`, and `z = 50`; `result` is computed using `/` as true
division.

The generated TAC is:

```text
x = 10
y = 20
t1 = y * 2
t2 = x + t1
z = t2
t3 = z - 5
t4 = t3 / 3
result = t4
```

Temporary numbering increases across the program. For a constant-only input:

```text
x = 2 + 3 * 4
```

The unoptimized TAC is:

```text
t1 = 3 * 4
t2 = 2 + t1
x = t2
```

After constant folding, the optimized TAC is:

```text
x = 14
```

The app generates these results from the parsed AST; it does not special-case
these examples.

## Limitations

- The project implements a small teaching language, not a general-purpose
  programming language.
- Only integer literals are accepted; division can produce a floating-point
  static value.
- Variables must be assigned before use; there are no declarations, scopes, or
  functions.
- The optimizer implements constant folding only. It does not perform
  propagation, dead-code elimination, or machine-code generation.
- An error stops later pipeline stages. The error examples file contains
  separate snippets, not one valid program.

## Future enhancements

- Add decimal literals, comparisons, and boolean expressions.
- Add control-flow constructs and control-flow graph visualizations.
- Add constant propagation and further semantics-preserving optimizations.
- Add source highlighting and more precise parser recovery.
- Add export to a standalone TAC or AST file.
- Extend the grammar and tests before introducing new language features.

## Uploading to GitHub

1. Extract the ZIP archive and open the extracted `Compiler-Insight` folder.
2. Create a new empty GitHub repository.
3. In the extracted folder, run `git init`, `git add .`, and
   `git commit -m "Add Compiler Insight mini-project"`.
4. Add the repository URL provided by GitHub as `origin` and push the commit.

The included `.gitignore` excludes virtual environments, caches, and local
environment files.
