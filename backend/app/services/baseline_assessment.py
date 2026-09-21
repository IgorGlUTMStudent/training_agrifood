"""Runtime deterministic baseline assessment service (IGR-04B).

Orchestrates a fitted CropMedianBaseline and validated BatchAssessmentInput into
a valid, schema-compliant RiskAssessment per ADR 0003 and ADR 0004.
"""

from __future__ import annotations

from datetime import datetime

from app.analytics.crop_median_baseline import (
    CropMedianBaseline,
    predict_risk_score,
)
from app.domain.assessment import (
    AssessmentStatus,
    Provenance,
    Reliability,
    ReliabilityLevel,
    RiskAssessment,
    RiskEstimate,
)
from app.domain.batch import BatchAssessmentInput


def build_baseline_assessment(
    baseline: CropMedianBaseline,
    batch_input: BatchAssessmentInput,
    *,
    engine_version: str,
    generated_at: datetime,
    source_dataset_id: str | None,
    simulation: bool,
    notice: str,
) -> RiskAssessment:
    """Build a deterministic baseline RiskAssessment for a single batch.

    Delegates scoring to predict_risk_score and constructs a compliant
    RiskAssessment with uncalibrated baseline semantics:
    - status = AssessmentStatus.ASSESSED
    - risk = RiskEstimate(score=score, band=None)
    - deterioration_horizon = None
    - factors = []
    - recommendation = None
    - reliability = UNAVAILABLE (empty reason codes, no fabrication)
    - provenance = engine_tier "deterministic_baseline", contract_version "1.0.0"
    """
    score = predict_risk_score(baseline, batch_input)
    return RiskAssessment(
        batch_id=batch_input.identity.batch_id,
        status=AssessmentStatus.ASSESSED,
        risk=RiskEstimate(score=score, band=None),
        deterioration_horizon=None,
        factors=[],
        recommendation=None,
        reliability=Reliability(
            level=ReliabilityLevel.UNAVAILABLE,
            confidence_score=None,
            reason_codes=[],
            missing_requirements=[],
        ),
        provenance=Provenance(
            contract_version="1.0.0",
            engine_tier="deterministic_baseline",
            engine_version=engine_version,
            generated_at=generated_at,
            source_dataset_id=source_dataset_id,
            simulation=simulation,
            notice=notice,
        ),
    )
