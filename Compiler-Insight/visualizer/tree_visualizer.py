"""Render the actual compiler AST as a dependency-free inline SVG tree."""

from __future__ import annotations

from html import escape

from compiler.ast_nodes import Assignment, Binary, Expression, Identifier, Number, Program, Unary


class _TreeNode:
    def __init__(self, label: str, children: list["_TreeNode"] | None = None):
        self.label = label
        self.children = children or []
        self.x = 0.0
        self.y = 0.0


def _expression_tree(node: Expression) -> _TreeNode:
    if isinstance(node, Number):
        return _TreeNode(f"Number: {node.value}")
    if isinstance(node, Identifier):
        return _TreeNode(f"Identifier: {node.name}")
    if isinstance(node, Unary):
        return _TreeNode(f"Unary: {node.operator}", [_expression_tree(node.operand)])
    return _TreeNode(
        f"Binary: {node.operator}",
        [_expression_tree(node.left), _expression_tree(node.right)],
    )


def _program_tree(program: Program) -> _TreeNode:
    return _TreeNode(
        "Program",
        [
            _TreeNode(
                f"Assignment: {statement.name}",
                [_expression_tree(statement.expression)],
            )
            for statement in program
            if isinstance(statement, Assignment)
        ],
    )


def _measure(node: _TreeNode) -> int:
    if not node.children:
        return 1
    return sum(_measure(child) for child in node.children)


def _place(node: _TreeNode, left: float, depth: int, gap: float, level_gap: float) -> float:
    node.y = 50 + depth * level_gap
    if not node.children:
        node.x = left + gap / 2
        return left + gap
    cursor = left
    child_centers: list[float] = []
    for child in node.children:
        cursor = _place(child, cursor, depth + 1, gap, level_gap)
        child_centers.append(child.x)
    node.x = (child_centers[0] + child_centers[-1]) / 2
    return cursor


def build_ast_svg(program: Program) -> str:
    """Build an SVG whose nodes and edges mirror the supplied AST."""
    root = _program_tree(program)
    leaves = max(1, _measure(root))
    gap = 150.0
    level_gap = 112.0
    width = max(420, int(leaves * gap + 100))
    max_depth = 1

    def find_depth(node: _TreeNode, depth: int = 1) -> None:
        nonlocal max_depth
        max_depth = max(max_depth, depth)
        for child in node.children:
            find_depth(child, depth + 1)

    find_depth(root)
    height = max_depth * level_gap + 80
    _place(root, 50, 0, gap, level_gap)
    nodes: list[_TreeNode] = []
    edges: list[tuple[_TreeNode, _TreeNode]] = []

    def collect(node: _TreeNode) -> None:
        nodes.append(node)
        for child in node.children:
            edges.append((node, child))
            collect(child)

    collect(root)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="Abstract syntax tree" viewBox="0 0 {width} {int(height)}" '
        f'width="100%" height="{int(height)}" style="font-family: sans-serif; '
        f'background: #f8fafc; border-radius: 12px">'
    ]
    for parent, child in edges:
        parts.append(
            f'<line x1="{parent.x:g}" y1="{parent.y + 25:g}" '
            f'x2="{child.x:g}" y2="{child.y - 25:g}" '
            f'stroke="#94a3b8" stroke-width="2"/>'
        )
    for node in nodes:
        parts.append(
            f'<rect x="{node.x - 58:g}" y="{node.y - 25:g}" width="116" height="50" '
            f'rx="10" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.5"/>'
        )
        parts.append(
            f'<text x="{node.x:g}" y="{node.y + 5:g}" text-anchor="middle" '
            f'font-size="12" font-weight="700" fill="#0f172a">'
            f'{escape(node.label)}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)
