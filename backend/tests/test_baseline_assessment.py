"""Tests for runtime deterministic baseline assessment service (IGR-04B).

Validates:
- Positive:
  - Known crop scoring matches IGR-04A predict_risk_score
  - Unseen crop fallback scoring matches IGR-04A global median
  - Provenance caller pass-through (engine_version, generated_at, source_dataset_id, simulation, notice)
  - Contract conformance: contract_version="1.0.0", engine_tier="deterministic_baseline"
  - Round-trip serialization through RiskAssessment schema
- Non-fabrication (mandatory in every positive test):
  - risk.band is None
  - deterioration_horizon is None
  - factors == []
  - recommendation is None
  - reliability.confidence_score is None
  - reliability.reason_codes == []
  - reliability.missing_requirements == []
  - reliability.level == ReliabilityLevel.UNAVAILABLE
- Immutability:
  - Neither baseline nor batch_input is mutated by build_baseline_assessment
- Negative:
  - Invalid provenance fields (empty engine_version, empty notice) raise ValidationError
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.analytics.crop_median_baseline import (
    CropMedianBaseline,
    CropMedianTrainingRecord,
    fit_crop_median_baseline,
)
from app.domain.assessment import (
    AssessmentStatus,
    ReliabilityLevel,
    RiskAssessment,
)
from app.domain.batch import (
    AssessmentContext,
    BatchAssessmentInput,
    BatchContext,
    BatchIdentity,
    FacilityContext,
    PlannedLogisticsContext,
    QualityContext,
    StageQualityCheck,
    StorageContext,
    StorageZoneContext,
    TelemetryContext,
    TelemetryReading,
)
from app.services.baseline_assessment import build_baseline_assessment


def _make_batch_input(
    crop_type: str = "apple",
    batch_id: str = "BAT-TEST-0001",
    storage_session_id: str = "SESS-0001",
    facility_id: str = "FAC-001",
    zone_id: str = "ZONE-001",
) -> BatchAssessmentInput:
    """Construct a minimal valid BatchAssessmentInput for service testing."""
    harvest_dt = datetime(2025, 8, 1, 8, 0, tzinfo=timezone.utc)
    harvest_qc_dt = datetime(2025, 8, 1, 10, 0, tzinfo=timezone.utc)
    entry_dt = datetime(2025, 8, 1, 14, 0, tzinfo=timezone.utc)
    pd_qc_dt = datetime(2025, 8, 15, 9, 0, tzinfo=timezone.utc)
    dispatch_dt = datetime(2025, 8, 15, 11, 0, tzinfo=timezone.utc)

    return BatchAssessmentInput(
        identity=BatchIdentity(
            batch_id=batch_id,
            storage_session_id=storage_session_id,
            facility_id=facility_id,
            zone_id=zone_id,
        ),
        assessment_context=AssessmentContext(
            assessment_timestamp=dispatch_dt,
        ),
        batch=BatchContext(
            crop_type=crop_type,
            variety="Gala",
            origin_region="North",
            harvest_datetime=harvest_dt,
            harvest_weight_kg=5000.0,
            initial_quality_score=92.0,
            harvest_temperature_c=18.0,
            harvest_conditions="Dry",
            field_precooled=True,
        ),
        storage=StorageContext(
            entry_datetime=entry_dt,
            planned_dispatch_datetime=dispatch_dt,
            bin_stack_tier=2,
            storage_duration_days=14,
        ),
        facility=FacilityContext(
            facility_name="Test Facility Alpha",
            region="North",
            district="Bălți",
            facility_type="Commercial Cold Store",
            capacity_tonnes=5000,
            commissioned_year=2019,
            has_controlled_atmosphere=True,
        ),
        zone=StorageZoneContext(
            zone_name="Chamber 1",
            zone_type="Standard Cold Room",
            nominal_capacity_tonnes=200,
            target_temperature_c=1.0,
            target_relative_humidity_pct=90.0,
            cooling_system_type="DX Ammonia",
            insulation_quality="High",
            defrost_cycle_frequency_per_day=2,
        ),
        quality=QualityContext(
            harvest=StageQualityCheck(
                check_datetime=harvest_qc_dt,
                firmness_kg_cm2=8.2,
                sugar_brix=13.5,
                defect_pct=1.0,
            ),
            pre_dispatch=StageQualityCheck(
                check_datetime=pd_qc_dt,
                firmness_kg_cm2=7.0,
                sugar_brix=14.0,
                defect_pct=2.0,
            ),
        ),
        telemetry=TelemetryContext(
            zone_id=zone_id,
            window_start=entry_dt,
            window_end=dispatch_dt,
            readings=[
                TelemetryReading(
                    timestamp=datetime(2025, 8, 8, 12, 0, tzinfo=timezone.utc),
                    air_temperature_c=2.0,
                    produce_surface_temperature_c=2.3,
                    relative_humidity_pct=90.0,
                    dew_point_c=0.8,
                    condensation_flag=False,
                    co2_ppm=None,
                    o2_pct=None,
                    cooling_on=True,
                    defrost_on=False,
                )
            ],
        ),
        planned_logistics=PlannedLogisticsContext(
            shipment_id="SHP-0001",
            destination_market="Central Market Berlin",
            destination_region="EU-Central",
            vehicle_type="Refrigerated Truck 20t",
            planned_departure_datetime=datetime(2025, 8, 15, 12, 0, tzinfo=timezone.utc),
            planned_arrival_datetime=datetime(2025, 8, 17, 18, 0, tzinfo=timezone.utc),
            planned_duration_hours=54.0,
        ),
    )


def _assert_non_fabrication(assessment: RiskAssessment) -> None:
    """Explicitly verify that all uncalculated/unsupported semantics remain null/empty."""
    assert assessment.risk is not None
    assert assessment.risk.band is None
    assert assessment.deterioration_horizon is None
    assert assessment.factors == []
    assert assessment.recommendation is None
    assert assessment.reliability.level == ReliabilityLevel.UNAVAILABLE
    assert assessment.reliability.confidence_score is None
    assert assessment.reliability.reason_codes == []
    assert assessment.reliability.missing_requirements == []


def test_positive_known_crop() -> None:
    """Verify service assessment for a known crop against fitted crop median."""
    training = [
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=12.5),
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=15.5),
        CropMedianTrainingRecord(crop_type="plum", loss_fraction_pct=30.0),
    ]
    baseline = fit_crop_median_baseline(training)
    batch_input = _make_batch_input(crop_type="apple", batch_id="BAT-APP-001")

    fixed_dt = datetime(2025, 8, 15, 12, 0, 0, tzinfo=timezone.utc)
    engine_ver = "test-baseline-engine-v1.0.0"
    dataset_id = "test-dataset-season-2024"
    notice_text = "Operational baseline test notice"

    assessment = build_baseline_assessment(
        baseline=baseline,
        batch_input=batch_input,
        engine_version=engine_ver,
        generated_at=fixed_dt,
        source_dataset_id=dataset_id,
        simulation=False,
        notice=notice_text,
    )

    # Core identity & status
    assert assessment.batch_id == "BAT-APP-001"
    assert assessment.status == AssessmentStatus.ASSESSED

    # Scoring: median(12.5, 15.5) = 14.0 -> score = 0.14
    assert assessment.risk is not None
    assert assessment.risk.score == pytest.approx(0.14)

    # Non-fabrication assertions
    _assert_non_fabrication(assessment)

    # Provenance
    assert assessment.provenance.contract_version == "1.0.0"
    assert assessment.provenance.engine_tier == "deterministic_baseline"
    assert assessment.provenance.engine_version == engine_ver
    assert assessment.provenance.generated_at == fixed_dt
    assert assessment.provenance.source_dataset_id == dataset_id
    assert assessment.provenance.simulation is False
    assert assessment.provenance.notice == notice_text


def test_positive_unseen_crop_fallback() -> None:
    """Verify service assessment for an unseen crop falls back to global training median."""
    training = [
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=10.0),
        CropMedianTrainingRecord(crop_type="pear", loss_fraction_pct=20.0),
    ]
    baseline = fit_crop_median_baseline(training)
    # Global median of [10.0, 20.0] is 15.0 -> score = 0.15
    batch_input = _make_batch_input(crop_type="plum", batch_id="BAT-PLUM-001")

    fixed_dt = datetime(2025, 8, 15, 12, 0, 0, tzinfo=timezone.utc)

    assessment = build_baseline_assessment(
        baseline=baseline,
        batch_input=batch_input,
        engine_version="test-engine-v1",
        generated_at=fixed_dt,
        source_dataset_id=None,
        simulation=True,
        notice="Unseen crop fallback assessment",
    )

    assert assessment.batch_id == "BAT-PLUM-001"
    assert assessment.status == AssessmentStatus.ASSESSED
    assert assessment.risk is not None
    assert assessment.risk.score == pytest.approx(0.15)
    _assert_non_fabrication(assessment)
    assert assessment.provenance.source_dataset_id is None
    assert assessment.provenance.simulation is True


def test_positive_provenance_passthrough() -> None:
    """Verify caller-provided provenance values are passed through without alteration."""
    training = [CropMedianTrainingRecord(crop_type="grape", loss_fraction_pct=5.0)]
    baseline = fit_crop_median_baseline(training)
    batch_input = _make_batch_input(crop_type="grape", batch_id="BAT-GRP-123")

    fixed_dt = datetime(2026, 1, 10, 8, 30, 0, tzinfo=timezone.utc)

    # Test simulation=True
    ass_sim = build_baseline_assessment(
        baseline=baseline,
        batch_input=batch_input,
        engine_version="test-baseline-engine-v123",
        generated_at=fixed_dt,
        source_dataset_id="test-dataset-xyz",
        simulation=True,
        notice="test provenance notice",
    )
    assert ass_sim.provenance.engine_version == "test-baseline-engine-v123"
    assert ass_sim.provenance.source_dataset_id == "test-dataset-xyz"
    assert ass_sim.provenance.simulation is True
    assert ass_sim.provenance.notice == "test provenance notice"
    assert ass_sim.provenance.contract_version == "1.0.0"
    assert ass_sim.provenance.engine_tier == "deterministic_baseline"
    _assert_non_fabrication(ass_sim)

    # Test simulation=False with no dataset_id
    ass_prod = build_baseline_assessment(
        baseline=baseline,
        batch_input=batch_input,
        engine_version="production-baseline-v2",
        generated_at=fixed_dt,
        source_dataset_id=None,
        simulation=False,
        notice="live production assessment notice",
    )
    assert ass_prod.provenance.engine_version == "production-baseline-v2"
    assert ass_prod.provenance.source_dataset_id is None
    assert ass_prod.provenance.simulation is False
    assert ass_prod.provenance.notice == "live production assessment notice"
    assert ass_prod.provenance.contract_version == "1.0.0"
    assert ass_prod.provenance.engine_tier == "deterministic_baseline"
    _assert_non_fabrication(ass_prod)


def test_input_and_baseline_immutability() -> None:
    """Verify build_baseline_assessment mutates neither the baseline nor the batch input."""
    training = [CropMedianTrainingRecord(crop_type="cherry", loss_fraction_pct=8.0)]
    baseline = fit_crop_median_baseline(training)
    batch_input = _make_batch_input(crop_type="cherry", batch_id="BAT-CH-001")

    # Deep snapshot inputs before service call
    baseline_before = copy.deepcopy(baseline)
    batch_input_before = copy.deepcopy(batch_input)

    _ = build_baseline_assessment(
        baseline=baseline,
        batch_input=batch_input,
        engine_version="engine-v1",
        generated_at=datetime(2025, 9, 1, 12, 0, 0, tzinfo=timezone.utc),
        source_dataset_id="ds-01",
        simulation=True,
        notice="immutability check",
    )

    # Assert equality after call
    assert baseline == baseline_before
    assert batch_input == batch_input_before


def test_negative_provenance_invalid() -> None:
    """Verify empty engine_version or notice raises ValidationError without fabricated fallback."""
    training = [CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=10.0)]
    baseline = fit_crop_median_baseline(training)
    batch_input = _make_batch_input(crop_type="apple")
    now_dt = datetime(2025, 8, 1, 12, 0, 0, tzinfo=timezone.utc)

    # Empty engine_version must raise ValidationError
    with pytest.raises(ValidationError):
        build_baseline_assessment(
            baseline=baseline,
            batch_input=batch_input,
            engine_version="",
            generated_at=now_dt,
            source_dataset_id=None,
            simulation=True,
            notice="Valid notice",
        )

    # Empty notice must raise ValidationError
    with pytest.raises(ValidationError):
        build_baseline_assessment(
            baseline=baseline,
            batch_input=batch_input,
            engine_version="valid-version",
            generated_at=now_dt,
            source_dataset_id=None,
            simulation=True,
            notice="",
        )


def test_baseline_assessment_round_trips_through_contract() -> None:
    """Verify RiskAssessment produced by service round-trips losslessly through JSON schema."""
    training = [CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=15.0)]
    baseline = fit_crop_median_baseline(training)
    batch_input = _make_batch_input(crop_type="apple", batch_id="BAT-ROUNDTRIP-01")

    assessment = build_baseline_assessment(
        baseline=baseline,
        batch_input=batch_input,
        engine_version="engine-v1",
        generated_at=datetime(2025, 8, 15, 12, 0, 0, tzinfo=timezone.utc),
        source_dataset_id="ds-rt-01",
        simulation=True,
        notice="round-trip test notice",
    )

    serialized = assessment.model_dump(mode="json")
    restored = RiskAssessment.model_validate(serialized)

    assert restored == assessment
