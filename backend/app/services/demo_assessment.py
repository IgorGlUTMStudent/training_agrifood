"""Synthetic assessment used only to prove the vertical contract."""

from datetime import datetime, timezone

from app.domain.assessment import (
    AssessmentFactor,
    AssessmentStatus,
    FactorCategory,
    FactorEffect,
    Provenance,
    Reliability,
    ReliabilityLevel,
    RiskAssessment,
)

SIMULATION_NOTICE = "SIMULATION / synthetic fixture / not challenge data"


def build_demo_assessment() -> RiskAssessment:
    return RiskAssessment(
        batch_id="synthetic-batch-001",
        status=AssessmentStatus.INSUFFICIENT_DATA,
        risk=None,
        deterioration_horizon=None,
        factors=[
            AssessmentFactor(
                code="validated_inputs_unavailable",
                category=FactorCategory.DATA_QUALITY,
                effect=FactorEffect.UNKNOWN,
                summary="Validated assessment inputs are not configured for this fixture.",
            )
        ],
        recommendation=None,
        reliability=Reliability(
            level=ReliabilityLevel.UNAVAILABLE,
            confidence_score=None,
            reason_codes=["INSUFFICIENT_VALIDATED_INPUTS"],
            missing_requirements=["Validated challenge dataset schema"],
        ),
        provenance=Provenance(
            contract_version="1.0.0",
            engine_tier="fixture",
            engine_version="foundation-fixture-v1",
            generated_at=datetime.now(timezone.utc),
            source_dataset_id=None,
            simulation=True,
            notice=SIMULATION_NOTICE,
        ),
    )
