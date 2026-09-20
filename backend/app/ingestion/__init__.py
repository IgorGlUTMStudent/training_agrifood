"""Raw dataset ingestion and structural diagnostics package.

Provides pure raw CSV reading and physical structural integrity verification.
Does NOT perform predictive modeling, cleaning, imputation, or domain entity conversion.
"""

from __future__ import annotations

from app.ingestion.canonical_mapper import (
    BatchNotFoundError,
    CanonicalMappingError,
    CanonicalValidationError,
    CardinalityError,
    build_batch_assessment_input,
)
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
    "BatchNotFoundError",
    "CanonicalMappingError",
    "CanonicalValidationError",
    "CardinalityError",
    "DiagnosticIssue",
    "ForeignKeySpec",
    "RawSnapshot",
    "RawTable",
    "StructuralDiagnostics",
    "TABLE_MANIFEST",
    "TableDiagnostics",
    "TableSpec",
    "build_batch_assessment_input",
    "read_raw_snapshot",
    "read_raw_table",
]
