"""Stable application/domain output contracts."""

from app.domain.assessment import RiskAssessment
from app.domain.batch import BatchAssessmentInput

__all__ = [
    "BatchAssessmentInput",
    "RiskAssessment",
]
