import pytest
from pydantic import ValidationError

from app.domain.assessment import RiskAssessment
from app.services.demo_assessment import build_demo_assessment


def test_synthetic_assessment_round_trips_through_contract() -> None:
    assessment = build_demo_assessment()
    serialized = assessment.model_dump(mode="json")

    restored = RiskAssessment.model_validate(serialized)

    assert restored == assessment


def test_insufficient_data_rejects_false_precision() -> None:
    payload = build_demo_assessment().model_dump(mode="json")
    payload["risk"] = {"score": 0.5, "band": None}

    with pytest.raises(ValidationError, match="cannot claim risk"):
        RiskAssessment.model_validate(payload)
