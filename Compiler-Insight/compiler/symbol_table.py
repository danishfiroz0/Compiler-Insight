"""Symbol-table data structures shared with semantic analysis."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Symbol:
    name: str
    first_assigned_line: int
    last_assigned_line: int
    assignment_count: int = 1
    usage_count: int = 0
    known_value: int | float | None = None


@dataclass
class SymbolTable:
    symbols: dict[str, Symbol] = field(default_factory=dict)

    def record_assignment(
        self, name: str, line: int, known_value: int | float | None
    ) -> None:
        if name in self.symbols:
            symbol = self.symbols[name]
            symbol.last_assigned_line = line
            symbol.assignment_count += 1
            symbol.known_value = known_value
        else:
            self.symbols[name] = Symbol(
                name=name,
                first_assigned_line=line,
                last_assigned_line=line,
                known_value=known_value,
            )

    def record_usage(self, name: str) -> None:
        if name in self.symbols:
            self.symbols[name].usage_count += 1

    def as_rows(self) -> list[dict[str, str | int]]:
        """Return stable, presentation-ready rows without exposing internals."""
        rows: list[dict[str, str | int]] = []
        for symbol in self.symbols.values():
            value = "Unknown" if symbol.known_value is None else str(symbol.known_value)
            rows.append(
                {
                    "Variable": symbol.name,
                    "First assigned": symbol.first_assigned_line,
                    "Last assigned": symbol.last_assigned_line,
                    "Assignments": symbol.assignment_count,
                    "Uses": symbol.usage_count,
                    "Known value": value,
                }
            )
        return rows
