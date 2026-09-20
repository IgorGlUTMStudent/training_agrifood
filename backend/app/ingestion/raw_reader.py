"""Raw CSV file reader and structural snapshot loader.

Preserves exact raw string values without transformation, imputation, or filtering.
Performs physical structure, row count, candidate PK uniqueness, and FK integrity checks.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.ingestion.diagnostics import (
    DiagnosticIssue,
    StructuralDiagnostics,
    TableDiagnostics,
)
from app.ingestion.structural_manifest import (
    TABLE_MANIFEST,
    TableSpec,
)


@dataclass
class RawTable:
    """An in-memory representation of a raw CSV table with preserved string values."""

    name: str
    source_path: Path
    headers: list[str]
    rows: list[dict[str, str]] = field(default_factory=list)

    @property
    def row_count(self) -> int:
        return len(self.rows)

    def get_column_values(self, column_name: str) -> list[str]:
        """Extract a column's raw values across all rows."""
        return [row.get(column_name, "") for row in self.rows]


@dataclass
class RawSnapshot:
    """A collection of all raw tables loaded from a data directory along with diagnostics."""

    directory: Path
    tables: dict[str, RawTable] = field(default_factory=dict)
    diagnostics: StructuralDiagnostics = field(
        default_factory=lambda: StructuralDiagnostics(directory="")
    )

    @property
    def loaded_tables(self) -> list[str]:
        return list(self.tables.keys())

    def __getitem__(self, table_name: str) -> RawTable:
        return self.tables[table_name]

    def __contains__(self, table_name: str) -> bool:
        return table_name in self.tables

    def get(self, table_name: str, default: Any = None) -> Any:
        return self.tables.get(table_name, default)


def read_raw_table(
    file_path: Path | str,
    table_name: str,
    spec: TableSpec | None = None,
) -> tuple[RawTable | None, list[DiagnosticIssue]]:
    """Read a single raw CSV file, preserving exact string values and validating headers.

    Does NOT coerce types, clean values, or drop rows/columns.
    """
    path = Path(file_path)
    issues: list[DiagnosticIssue] = []

    if not path.is_file():
        issues.append(
            DiagnosticIssue(
                code="MISSING_FILE",
                message=f"File not found: {path.name}",
                table_name=table_name,
                source_path=str(path),
            )
        )
        return None, issues

    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                issues.append(
                    DiagnosticIssue(
                        code="EMPTY_FILE",
                        message=f"File is empty: {path.name}",
                        table_name=table_name,
                        source_path=str(path),
                    )
                )
                return RawTable(name=table_name, source_path=path, headers=[], rows=[]), issues

            # Check for duplicate headers
            seen_headers: set[str] = set()
            dup_headers: list[str] = []
            for h in headers:
                if h in seen_headers:
                    dup_headers.append(h)
                seen_headers.add(h)

            if dup_headers:
                issues.append(
                    DiagnosticIssue(
                        code="DUPLICATE_HEADER",
                        message=f"Duplicate headers detected in {path.name}: {dup_headers}",
                        table_name=table_name,
                        source_path=str(path),
                        details={"duplicate_headers": dup_headers},
                    )
                )

            # Check headers against spec if provided
            if spec is not None:
                expected = list(spec.expected_headers)
                if headers != expected:
                    missing = [h for h in expected if h not in headers]
                    unexpected = [h for h in headers if h not in expected]
                    order_diff = headers != expected and not missing and not unexpected
                    issues.append(
                        DiagnosticIssue(
                            code="HEADER_MISMATCH",
                            message=f"Header mismatch in {path.name}",
                            table_name=table_name,
                            source_path=str(path),
                            details={
                                "expected_headers": expected,
                                "actual_headers": headers,
                                "missing_headers": missing,
                                "unexpected_headers": unexpected,
                                "order_mismatch": order_diff,
                            },
                        )
                    )

            # Read all rows preserving exact strings
            rows: list[dict[str, str]] = []
            for line_idx, row in enumerate(reader, start=2):
                if len(row) != len(headers):
                    issues.append(
                        DiagnosticIssue(
                            code="ROW_WIDTH_MISMATCH",
                            message=(
                                f"Row width mismatch in {path.name} at line {line_idx}: "
                                f"expected {len(headers)} fields, got {len(row)}"
                            ),
                            table_name=table_name,
                            source_path=str(path),
                            details={
                                "line_number": line_idx,
                                "row_index": line_idx - 2,
                                "expected_field_count": len(headers),
                                "actual_field_count": len(row),
                                "raw_row": row,
                            },
                        )
                    )
                    continue

                row_dict = {headers[i]: row[i] for i in range(len(headers))}
                rows.append(row_dict)

        return RawTable(name=table_name, source_path=path, headers=headers, rows=rows), issues

    except Exception as e:
        issues.append(
            DiagnosticIssue(
                code="UNREADABLE_FILE",
                message=f"Error reading file {path.name}: {e}",
                table_name=table_name,
                source_path=str(path),
                details={"error": str(e)},
            )
        )
        return None, issues


def read_raw_snapshot(
    data_dir: Path | str,
    manifest: dict[str, TableSpec] | None = None,
    check_vdr01_counts: bool = True,
) -> RawSnapshot:
    """Load all raw CSV tables from data_dir and run comprehensive structural diagnostics.

    Verifies:
    - Physical file presence
    - Header consistency
    - Row counts (compared against VDR-01 accepted counts if check_vdr01_counts is True)
    - Primary key uniqueness
    - Direct foreign key integrity
    """
    directory = Path(data_dir)
    specs = manifest if manifest is not None else TABLE_MANIFEST

    diagnostics = StructuralDiagnostics(directory=str(directory))
    tables: dict[str, RawTable] = {}

    # 1. Load all tables
    for table_name, spec in specs.items():
        file_path = directory / spec.filename
        raw_table, file_issues = read_raw_table(file_path, table_name, spec=spec)
        diagnostics.issues.extend(file_issues)

        table_diag = TableDiagnostics(
            table_name=table_name,
            source_path=str(file_path),
            expected_row_count=spec.expected_row_count,
            pk_column=spec.pk_column,
            issues=list(file_issues),
        )

        if raw_table is not None:
            tables[table_name] = raw_table
            diagnostics.loaded_tables.append(table_name)
            table_diag.row_count = raw_table.row_count
            table_diag.headers = raw_table.headers

            # Check row count against VDR-01 baseline
            if check_vdr01_counts and raw_table.row_count != spec.expected_row_count:
                count_issue = DiagnosticIssue(
                    code="ROW_COUNT_MISMATCH",
                    message=(
                        f"Row count mismatch for {table_name}: "
                        f"actual {raw_table.row_count} != expected {spec.expected_row_count}"
                    ),
                    table_name=table_name,
                    source_path=str(file_path),
                    details={
                        "actual_row_count": raw_table.row_count,
                        "expected_row_count": spec.expected_row_count,
                    },
                )
                diagnostics.issues.append(count_issue)
                table_diag.issues.append(count_issue)

            # Check PK uniqueness
            if spec.pk_column in raw_table.headers:
                pk_vals = raw_table.get_column_values(spec.pk_column)
                seen_pks: set[str] = set()
                dups: list[str] = []
                for val in pk_vals:
                    if val in seen_pks:
                        dups.append(val)
                    seen_pks.add(val)

                table_diag.duplicate_pks = dups
                table_diag.duplicate_pk_count = len(dups)

                if dups:
                    pk_issue = DiagnosticIssue(
                        code="DUPLICATE_PK",
                        message=(
                            f"Duplicate candidate primary keys in {table_name}.{spec.pk_column}: "
                            f"{len(dups)} duplicates"
                        ),
                        table_name=table_name,
                        source_path=str(file_path),
                        details={"pk_column": spec.pk_column, "duplicate_keys": dups},
                    )
                    diagnostics.issues.append(pk_issue)
                    table_diag.issues.append(pk_issue)
        else:
            diagnostics.missing_tables.append(table_name)

        diagnostics.table_stats[table_name] = table_diag

    # 2. Check foreign key integrity across loaded tables
    for table_name, spec in specs.items():
        if table_name not in tables:
            continue
        child_table = tables[table_name]
        table_diag = diagnostics.table_stats[table_name]

        for fk_spec in spec.fk_relations:
            rel_key = f"{fk_spec.child_column} -> {fk_spec.parent_table}.{fk_spec.parent_column}"
            if fk_spec.parent_table not in tables:
                # Parent table is missing, skip FK verification (already reported as MISSING_FILE)
                continue

            parent_table = tables[fk_spec.parent_table]
            if fk_spec.parent_column not in parent_table.headers:
                continue

            parent_keys = set(parent_table.get_column_values(fk_spec.parent_column))
            child_keys = child_table.get_column_values(fk_spec.child_column)

            orphans = [ck for ck in child_keys if ck not in parent_keys]
            table_diag.orphan_fks[rel_key] = orphans

            if orphans:
                fk_issue = DiagnosticIssue(
                    code="ORPHAN_FK",
                    message=(
                        f"Foreign key violation in {table_name}.{fk_spec.child_column}: "
                        f"{len(orphans)} orphan records referencing missing "
                        f"{fk_spec.parent_table}.{fk_spec.parent_column}"
                    ),
                    table_name=table_name,
                    source_path=str(child_table.source_path),
                    details={
                        "relation": rel_key,
                        "orphan_count": len(orphans),
                        "sample_orphans": orphans[:10],
                    },
                )
                diagnostics.issues.append(fk_issue)
                table_diag.issues.append(fk_issue)

    return RawSnapshot(
        directory=directory,
        tables=tables,
        diagnostics=diagnostics,
    )
