"""Raw dataset ingestion and structural diagnostics package.

Provides pure raw CSV reading and physical structural integrity verification.
Does NOT perform predictive modeling, cleaning, imputation, or domain entity conversion.
"""

from __future__ import annotations

from app.ingestion.diagnostics import (
    DiagnosticIssue,
    StructuralDiagnostics,
    TableDiagnostics,
)
from app.ingestion.raw_reader import (
    RawSnapshot,
    RawTable,
    read_raw_snapshot,
    read_raw_table,
)
from app.ingestion.structural_manifest import (
    TABLE_MANIFEST,
    ForeignKeySpec,
    TableSpec,
)

__all__ = [
    "DiagnosticIssue",
    "ForeignKeySpec",
    "RawSnapshot",
    "RawTable",
    "StructuralDiagnostics",
    "TABLE_MANIFEST",
    "TableDiagnostics",
    "TableSpec",
    "read_raw_snapshot",
    "read_raw_table",
]
