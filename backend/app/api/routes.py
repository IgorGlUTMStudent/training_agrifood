"""Versioned foundation endpoints."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.domain.assessment import HealthResponse, RiskAssessment
from app.services.demo_assessment import build_demo_assessment
from app.ingestion.canonical_mapper import build_batch_assessment_input
from app.runtime.artifact import DATASET_ID, ENGINE_VERSION, NOTICE
from app.runtime.context import AnalyticsRuntimeContext, get_runtime
from app.services.baseline_assessment import build_baseline_assessment

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="smart-harvest",
        analytics=request.app.state.analytics_runtime.analytics,
    )


@router.get("/demo/assessment", response_model=RiskAssessment)
def demo_assessment() -> RiskAssessment:
    """Return a synthetic contract fixture; this is not challenge data."""

    return build_demo_assessment()


@router.get("/assessments/{batch_id}", response_model=RiskAssessment)
def assessment(
    batch_id: str,
    response: Response,
    runtime: AnalyticsRuntimeContext = Depends(get_runtime),
) -> RiskAssessment:
    headers = {"Cache-Control": "no-store"}
    response.headers.update(headers)
    if batch_id in runtime.training_ids:
        raise HTTPException(409, "Batch is not eligible for this assessment release", headers=headers)
    if batch_id not in runtime.held_out_ids:
        raise HTTPException(404, "Batch not found", headers=headers)
    try:
        batch_input = build_batch_assessment_input(runtime.snapshot, batch_id)
        return build_baseline_assessment(
            runtime.baseline, batch_input,
            engine_version=ENGINE_VERSION,
            generated_at=datetime.now(timezone.utc),
            source_dataset_id=DATASET_ID,
            simulation=True,
            notice=NOTICE,
        )
    except Exception:
        logger.exception("Dataset-backed assessment failed")
        raise HTTPException(500, "Assessment could not be completed", headers=headers) from None
