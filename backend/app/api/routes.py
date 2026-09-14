"""Versioned foundation endpoints."""

from fastapi import APIRouter

from app.domain.assessment import HealthResponse, RiskAssessment
from app.services.demo_assessment import build_demo_assessment

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="smart-harvest",
        analytics="not_configured",
    )


@router.get("/demo/assessment", response_model=RiskAssessment)
def demo_assessment() -> RiskAssessment:
    """Return a synthetic contract fixture; this is not challenge data."""

    return build_demo_assessment()
