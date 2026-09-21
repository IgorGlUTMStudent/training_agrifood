"""Raw dataset ingestion, structural diagnostics, and canonical mapping package.

Provides pure raw CSV reading, physical structural integrity verification, and
canonical BatchAssessmentInput mapping.
Does NOT perform predictive modeling, feature engineering, imputation,
analytics scoring, or recommendation generation.
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
