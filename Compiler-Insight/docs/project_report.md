# Compiler Insight: Visualizing the Compilation Process

## Title page

**Project title:** Compiler Insight: Visualizing the Compilation Process  
**Student name:** [Your name]  
**Roll number:** [Your roll number]  
**University:** [Your university]  
**Department:** [Your department]  
**Instructor:** [Instructor name]  
**Submission date:** [Submission date]

## Abstract

Compiler Insight is a small educational compiler and a Streamlit application
designed to make a basic compilation pipeline visible. It accepts a line-based
language of variable assignments and arithmetic expressions. The implementation
tokenizes source text, parses it with recursive descent, creates an Abstract
Syntax Tree (AST), performs sequential semantic checks, generates three-address
code (TAC), and folds constant arithmetic subtrees. The application presents
the stage outputs, an SVG tree drawing, a symbol table, errors, and a summary.
The project is intended for introductory study and does not attempt to compile
to machine code or support a general-purpose language.

## 1. Introduction

A compiler transforms a source program through multiple representations. The
transitions between characters, tokens, syntax, meaning, intermediate
instructions, and optimized code can be difficult to observe in ordinary
compiler tools. This project provides a small implementation where each
transformation is explicit and can be inspected in a browser.

The source language is deliberately restricted to keep the implementation
approachable. It supports integer literals, identifiers, assignments,
parentheses, arithmetic, and unary signs. The restriction keeps attention on
core compiler concepts rather than a large grammar or machine architecture.

## 2. Problem statement

Beginning students may understand individual compiler terms but have difficulty
connecting the stages into a working process. A compact tool is needed to show
how actual source input is tokenized, parsed into a tree, checked for semantic
errors, lowered into intermediate code, and optimized.

## 3. Objectives

1. Implement a real lexer that reports unsupported characters and source
   locations.
2. Implement a recursive-descent parser using an explicit precedence grammar.
3. Construct an AST and visualize its actual nodes and edges.
4. Maintain a symbol table while checking variable uses and detectable
   division-by-zero expressions.
5. Generate TAC from parsed AST nodes.
6. Apply constant folding without evaluating a zero divisor.
7. Stop compilation after a failed earlier stage and provide local explanatory
   material.
8. Test compiler behavior using pytest.

## 4. Background

### 4.1 Lexical analysis

Lexical analysis groups input characters into tokens. This project recognizes
identifiers, integer literals, assignment, four arithmetic operators, and
parentheses. Newlines are retained as statement boundaries and whitespace is
otherwise ignored.

### 4.2 Syntax analysis

Syntax analysis checks whether the token sequence matches a grammar. A
recursive-descent parser implements grammar rules as functions. The grammar
separates additive from multiplicative expressions so that multiplication and
division bind more strongly than addition and subtraction.

### 4.3 Abstract Syntax Tree

An AST contains the structural meaning of a program. Nodes in this project
represent assignments, numeric literals, identifiers, unary operations, and
binary operations. Parentheses affect the structure during parsing but do not
need separate nodes in the resulting tree.

### 4.4 Semantic analysis and symbol tables

Semantic checks validate context that grammar alone cannot express. The analyzer
walks assignments in source order, records variable definitions and uses, and
reports a read before assignment. It also reports a divisor that evaluates to
zero from integer literals and earlier known assignments.

### 4.5 Intermediate code and optimization

TAC breaks compound expressions into simple instructions with temporary
variables. Constant folding evaluates a subtree when all its operands are
numeric constants. The optimizer leaves expressions unchanged when they depend
on variables or when evaluating them would divide by zero.

## 5. Requirements

### 5.1 Functional requirements

- Accept and edit a multi-line source program in a web interface.
- Recognize the supported token categories and report invalid characters.
- Parse assignments and arithmetic with precedence, parentheses, and unary
  signs.
- Build and display the AST.
- Track variables and report undefined reads and detectable division by zero.
- Generate TAC, then optimize and regenerate TAC.
- Display stage status, counts, errors, and explanations.
- Do not run a later compiler stage after an earlier stage fails.

### 5.2 Non-functional requirements

- Run locally with Python 3.11 or newer.
- Use standard Python packaging through `requirements.txt`.
- Require no paid APIs, secrets, remote services, or Graphviz installation.
- Keep modules small and testable.
- Run tests with `pytest`.

## 6. System design

### 6.1 Architecture

```text
Source editor
     |
     v
Lexer -- lexical error --> stop
     |
     v
Recursive-descent parser -- syntax error --> stop
     |
     v
Semantic analyzer + symbol table -- semantic error --> stop
     |
     v
TAC generation
     |
     v
Constant-folded AST --> optimized TAC
     |
     v
Streamlit stage tabs, AST SVG, and compilation summary
```

### 6.2 Grammar

```text
program        ::= NEWLINE* (assignment NEWLINE+)* assignment? NEWLINE* EOF
assignment     ::= IDENTIFIER '=' expression
expression     ::= additive
additive       ::= multiplicative (('+' | '-') multiplicative)*
multiplicative ::= unary (('*' | '/') unary)*
unary          ::= ('+' | '-') unary | primary
primary        ::= INTEGER | IDENTIFIER | '(' expression ')'
```

Assignments are separated by newlines. Operators at one precedence level
associate from left to right.

### 6.3 Data flow

The pipeline produces a `CompilationResult`. Each stage populates only the
outputs it has successfully produced. Lexical or parser exceptions are reported
and return immediately. Semantic errors preserve the symbol table and AST for
inspection but prevent TAC and optimization from running.

## 7. Implementation

- `compiler/lexer.py` scans the input and attaches line and column coordinates
  to tokens.
- `compiler/parser.py` implements one recursive-descent method per expression
  precedence rule and returns AST nodes.
- `compiler/ast_nodes.py` defines immutable dataclass nodes and AST counting
  helpers.
- `compiler/symbol_table.py` stores assignment locations, assignment counts,
  usage counts, and values known from static evaluation.
- `compiler/semantic_analyzer.py` evaluates known expressions as it checks
  assignments in source order.
- `compiler/tac_generator.py` recursively emits instructions with generated
  temporaries.
- `compiler/optimizer.py` creates a new folded AST and safely leaves zero
  division unevaluated.
- `compiler/pipeline.py` coordinates stages and enforces stop-on-error behavior.
- `visualizer/tree_visualizer.py` converts AST nodes to a dependency-free SVG
  tree.
- `app.py` presents the compiler and deterministic educational explanations in
  Streamlit.

## 8. Testing

Automated tests are located in `tests/` and are run with:

```bash
pytest
```

The test suite covers token categories and positions, invalid characters,
precedence, parentheses, assignments, syntax failures, undefined reads, symbol
table updates, TAC instruction order, constant folding, division-by-zero safety,
and pipeline stopping behavior. Test outcomes should be reported from the
actual `pytest` run performed in the target environment; this report does not
claim an unrun result.

## 9. Limitations

- The language has no comments, decimal literals, declarations, scopes,
  functions, control flow, or types beyond numeric expressions.
- Division uses true division, so static values may be floating point.
- Static analysis is limited to the implemented arithmetic expressions.
- The optimizer demonstrates constant folding only.
- No machine code or executable program is produced.
- The parser reports the first syntax error instead of recovering and continuing.

## 10. Future scope

Potential extensions include decimal and boolean types, comparison operators,
control flow, control-flow graph visualization, constant propagation, dead-code
elimination, source highlighting, parser error recovery, and output export.
Each extension should add corresponding grammar rules, semantic behavior, and
tests.

## 11. Conclusion

Compiler Insight provides an end-to-end, inspectable example of a small
compiler pipeline. It connects lexical, syntactic, semantic, intermediate-code,
and optimization concepts through code generated from user input. Its modular
design and local tests make it suitable as a starting point for academic
exploration and future improvements.

## References

1. A. V. Aho, M. S. Lam, R. Sethi, and J. D. Ullman, *Compilers: Principles,
   Techniques, and Tools*, 2nd ed. Pearson, 2006.
2. A. K. Nystrom, *Crafting Interpreters*. Genever Benning, 2021.
   Available at: https://craftinginterpreters.com/
3. Python Software Foundation, “Python 3 Documentation.”
   Available at: https://docs.python.org/3/
4. Streamlit, “Streamlit Documentation.”
   Available at: https://docs.streamlit.io/
