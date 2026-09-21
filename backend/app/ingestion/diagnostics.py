"""Diagnostic models and structures for physical data integrity and schema validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DiagnosticIssue:
    """Represents a structural defect, deviation, or invariant failure in raw data."""

    code: str
    message: str
    table_name: str
    source_path: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class TableDiagnostics:
    """Detailed structural diagnostic summary for an individual raw table."""

    table_name: str
    source_path: str
    row_count: int = 0
    expected_row_count: int = 0
    headers: list[str] = field(default_factory=list)
    pk_column: str = ""
    duplicate_pks: list[str] = field(default_factory=list)
    duplicate_pk_count: int = 0
    orphan_fks: dict[str, list[str]] = field(default_factory=dict)
    issues: list[DiagnosticIssue] = field(default_factory=list)


@dataclass
class StructuralDiagnostics:
    """Aggregate structural diagnostics across an entire raw dataset snapshot."""

    directory: str
    loaded_tables: list[str] = field(default_factory=list)
    missing_tables: list[str] = field(default_factory=list)
    table_stats: dict[str, TableDiagnostics] = field(default_factory=dict)
    issues: list[DiagnosticIssue] = field(default_factory=list)

    def has_errors(self) -> bool:
        """Return True if any diagnostic issues were identified."""
        return len(self.issues) > 0

    def is_valid(self) -> bool:
        """Return True if the snapshot is structurally clean with 0 issues."""
        return not self.has_errors()

    def get_issues_by_code(self, code: str) -> list[DiagnosticIssue]:
        """Filter issues by diagnostic code."""
        return [i for i in self.issues if i.code == code]
