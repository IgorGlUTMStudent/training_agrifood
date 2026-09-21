"""Tests for deterministic crop-median baseline analytics engine (IGR-04A).

Validates:
Positive:
  A. Crop-specific median
  B. Global fallback for unseen crop
  C. Risk transformation
  D. Determinism under permutation
  E. Canonical-input inference
  F. Non-crop invariance

Negative:
  N1. Empty training set -> explicit raise
  N2. Non-finite targets (NaN, +inf, -inf) -> explicit raise
  N3. Empty/invalid crop identifier in a training record -> explicit raise
  N4. Outcome leakage: input carries no outcome fields; prediction does not use them
  N5. No silent full-snapshot fitting
  N6. No unsupported output semantics (risk.band, confidence, horizon, factors, recommendation absent)
"""

from __future__ import annotations

from datetime import datetime
import pytest
from pydantic import ValidationError

from app.analytics.crop_median_baseline import (
    CropMedianTrainingRecord,
    fit_crop_median_baseline,
    predict_loss_fraction_pct,
    predict_risk_score,
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


def _make_batch_input(
    crop_type: str = "apple",
    batch_id: str = "BAT-TEST-0001",
    storage_session_id: str = "SESS-0001",
    facility_id: str = "FAC-001",
    zone_id: str = "ZONE-001",
    air_temp: float = 2.5,
    firmness_pd: float = 6.8,
    with_logistics: bool = True,
    storage_duration_days: int = 14,
) -> BatchAssessmentInput:
    """Construct a minimal valid BatchAssessmentInput for analytics testing."""
    harvest_dt = datetime(2025, 8, 1, 8, 0)
    harvest_qc_dt = datetime(2025, 8, 1, 10, 0)
    entry_dt = datetime(2025, 8, 1, 14, 0)
    pd_qc_dt = datetime(2025, 8, 15, 9, 0)
    dispatch_dt = datetime(2025, 8, 15, 11, 0)

    logistics = None
    if with_logistics:
        logistics = PlannedLogisticsContext(
            shipment_id="SHP-0001",
            destination_market="Central Market Berlin",
            destination_region="EU-Central",
            vehicle_type="Refrigerated Truck 20t",
            planned_departure_datetime=datetime(2025, 8, 15, 12, 0),
            planned_arrival_datetime=datetime(2025, 8, 17, 18, 0),
            planned_duration_hours=54.0,
        )

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
            variety="Test Variety",
            origin_region="North",
            harvest_datetime=harvest_dt,
            harvest_weight_kg=5200.0,
            initial_quality_score=92.5,
            harvest_temperature_c=18.5,
            harvest_conditions="Optimal Dry",
            field_precooled=True,
        ),
        storage=StorageContext(
            entry_datetime=entry_dt,
            planned_dispatch_datetime=dispatch_dt,
            bin_stack_tier=2,
            storage_duration_days=storage_duration_days,
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
                defect_pct=1.2,
            ),
            pre_dispatch=StageQualityCheck(
                check_datetime=pd_qc_dt,
                firmness_kg_cm2=firmness_pd,
                sugar_brix=14.0,
                defect_pct=2.1,
            ),
        ),
        telemetry=TelemetryContext(
            zone_id=zone_id,
            window_start=entry_dt,
            window_end=dispatch_dt,
            readings=[
                TelemetryReading(
                    timestamp=datetime(2025, 8, 8, 12, 0),
                    air_temperature_c=air_temp,
                    produce_surface_temperature_c=air_temp + 0.3,
                    relative_humidity_pct=89.5,
                    dew_point_c=0.9,
                    condensation_flag=False,
                    co2_ppm=None,
                    o2_pct=None,
                    cooling_on=True,
                    defrost_on=False,
                )
            ],
        ),
        planned_logistics=logistics,
    )


# ==============================================================================
# POSITIVE TEST CASES
# ==============================================================================


def test_positive_case_a_crop_specific_median() -> None:
    """Case A: Crop-specific median.

    Training: Apple=[10, 20, 30] (median=20), Pear=[40] (median=40).
    Predict(Apple) == 20.0; Predict(Pear) == 40.0.
    """
    records = [
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=10.0),
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=20.0),
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=30.0),
        CropMedianTrainingRecord(crop_type="pear", loss_fraction_pct=40.0),
    ]
    baseline = fit_crop_median_baseline(records)

    apple_input = _make_batch_input(crop_type="apple")
    pear_input = _make_batch_input(crop_type="pear")

    pred_apple = predict_loss_fraction_pct(baseline, apple_input)
    pred_pear = predict_loss_fraction_pct(baseline, pear_input)

    assert pred_apple == 20.0
    assert pred_pear == 40.0


def test_positive_case_b_global_fallback_for_unseen_crop() -> None:
    """Case B: Global fallback for unseen crop.

    Train on {Apple, Pear}.
    Global records = [10, 20, 30, 40] -> global median = (20 + 30) / 2 = 25.0.
    Predict("plum") == 25.0.
    Must NOT return 0, raise, or borrow another crop.
    """
    records = [
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=10.0),
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=20.0),
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=30.0),
        CropMedianTrainingRecord(crop_type="pear", loss_fraction_pct=40.0),
    ]
    baseline = fit_crop_median_baseline(records)

    plum_input = _make_batch_input(crop_type="plum")
    pred_plum = predict_loss_fraction_pct(baseline, plum_input)

    assert pred_plum == 25.0
    assert pred_plum != 0.0
    assert pred_plum != baseline.crop_medians["apple"]
    assert pred_plum != baseline.crop_medians["pear"]


def test_positive_case_c_risk_transformation() -> None:
    """Case C: Risk transformation.

    predicted=20 -> risk_score=0.20
    predicted<0  -> risk_score=0.0
    predicted>100 -> risk_score=1.0
    Do NOT reinterpret as probability.
    """
    records = [
        CropMedianTrainingRecord(crop_type="normal_crop", loss_fraction_pct=20.0),
        CropMedianTrainingRecord(crop_type="negative_loss_crop", loss_fraction_pct=-15.0),
        CropMedianTrainingRecord(crop_type="extreme_loss_crop", loss_fraction_pct=135.0),
        CropMedianTrainingRecord(crop_type="zero_loss_crop", loss_fraction_pct=0.0),
        CropMedianTrainingRecord(crop_type="hundred_loss_crop", loss_fraction_pct=100.0),
    ]
    baseline = fit_crop_median_baseline(records)

    input_normal = _make_batch_input(crop_type="normal_crop")
    input_neg = _make_batch_input(crop_type="negative_loss_crop")
    input_extreme = _make_batch_input(crop_type="extreme_loss_crop")
    input_zero = _make_batch_input(crop_type="zero_loss_crop")
    input_hundred = _make_batch_input(crop_type="hundred_loss_crop")

    assert predict_risk_score(baseline, input_normal) == 0.20
    assert predict_risk_score(baseline, input_neg) == 0.0
    assert predict_risk_score(baseline, input_extreme) == 1.0
    assert predict_risk_score(baseline, input_zero) == 0.0
    assert predict_risk_score(baseline, input_hundred) == 1.0


def test_positive_case_d_determinism() -> None:
    """Case D: Determinism.

    Same records in different order -> identical fitted medians and predictions.
    """
    records_1 = [
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=10.0),
        CropMedianTrainingRecord(crop_type="pear", loss_fraction_pct=40.0),
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=30.0),
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=20.0),
        CropMedianTrainingRecord(crop_type="grape", loss_fraction_pct=5.0),
    ]
    records_2 = [
        CropMedianTrainingRecord(crop_type="grape", loss_fraction_pct=5.0),
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=20.0),
        CropMedianTrainingRecord(crop_type="pear", loss_fraction_pct=40.0),
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=10.0),
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=30.0),
    ]

    baseline_1 = fit_crop_median_baseline(records_1)
    baseline_2 = fit_crop_median_baseline(records_2)

    assert baseline_1.crop_medians == baseline_2.crop_medians
    assert baseline_1.global_median == baseline_2.global_median

    for crop in ["apple", "pear", "grape", "unseen_cherry"]:
        inp = _make_batch_input(crop_type=crop)
        assert predict_loss_fraction_pct(baseline_1, inp) == predict_loss_fraction_pct(
            baseline_2, inp
        )
        assert predict_risk_score(baseline_1, inp) == predict_risk_score(
            baseline_2, inp
        )


def test_positive_case_e_canonical_input_inference() -> None:
    """Case E: Canonical-input inference.

    Prediction accepts a real BatchAssessmentInput and reads batch_input.batch.crop_type.
    """
    records = [
        CropMedianTrainingRecord(crop_type="golden_delicious", loss_fraction_pct=14.5),
    ]
    baseline = fit_crop_median_baseline(records)

    batch_input = _make_batch_input(crop_type="golden_delicious")
    assert isinstance(batch_input, BatchAssessmentInput)

    loss_pct = predict_loss_fraction_pct(baseline, batch_input)
    risk_score = predict_risk_score(baseline, batch_input)

    assert loss_pct == 14.5
    assert risk_score == 0.145


def test_positive_case_f_non_crop_invariance() -> None:
    """Case F: Non-crop invariance.

    Two BatchAssessmentInput instances with the same crop_type but different
    telemetry / facility / zone / planned logistics / quality / identity
    MUST yield identical baseline predictions.
    """
    records = [
        CropMedianTrainingRecord(crop_type="plums", loss_fraction_pct=18.0),
    ]
    baseline = fit_crop_median_baseline(records)

    # Instance 1: standard cold facility, chamber 1, has logistics, cool air
    input_1 = _make_batch_input(
        crop_type="plums",
        batch_id="BAT-000001",
        storage_session_id="SESS-0001",
        facility_id="FAC-001",
        zone_id="ZONE-001",
        air_temp=1.5,
        firmness_pd=7.0,
        with_logistics=True,
        storage_duration_days=10,
    )

    # Instance 2: completely different identity, different facility, different zone,
    # higher air temp, different firmness, NO planned logistics, longer stay
    input_2 = _make_batch_input(
        crop_type="plums",
        batch_id="BAT-999999",
        storage_session_id="SESS-9999",
        facility_id="FAC-999",
        zone_id="ZONE-999",
        air_temp=12.0,
        firmness_pd=3.0,
        with_logistics=False,
        storage_duration_days=45,
    )

    assert predict_loss_fraction_pct(baseline, input_1) == predict_loss_fraction_pct(
        baseline, input_2
    )
    assert predict_risk_score(baseline, input_1) == predict_risk_score(
        baseline, input_2
    )


# ==============================================================================
# NEGATIVE TEST CASES
# ==============================================================================


def test_negative_case_n1_empty_training_set() -> None:
    """N1: Empty training set -> explicit raise (not silent zero/default)."""
    with pytest.raises(ValueError, match="empty"):
        fit_crop_median_baseline([])


def test_negative_case_n2_non_finite_targets() -> None:
    """N2: Non-finite targets (NaN, +inf, -inf) -> explicit raise."""
    # NaN
    with pytest.raises(ValueError, match="finite"):
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=float("nan"))

    # +inf
    with pytest.raises(ValueError, match="finite"):
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=float("inf"))

    # -inf
    with pytest.raises(ValueError, match="finite"):
        CropMedianTrainingRecord(crop_type="apple", loss_fraction_pct=float("-inf"))


def test_negative_case_n3_invalid_crop_identifier() -> None:
    """N3: Empty/invalid crop identifier in a training record -> explicit raise."""
    # Empty string
    with pytest.raises(ValueError, match="non-empty"):
        CropMedianTrainingRecord(crop_type="", loss_fraction_pct=10.0)

    # Whitespace-only string
    with pytest.raises(ValueError, match="non-empty"):
        CropMedianTrainingRecord(crop_type="   ", loss_fraction_pct=10.0)

    # Non-string
    with pytest.raises(ValueError, match="non-empty"):
        CropMedianTrainingRecord(crop_type=None, loss_fraction_pct=10.0)  # type: ignore[arg-type]


def test_negative_case_n4_outcome_leakage() -> None:
    """N4: Outcome leakage.

    The prediction function must not reference loss_fraction_pct, quality_status,
    quality_score, economic_loss_eur on the input.
    Proven by:
    1. BatchAssessmentInput demonstrably forbids extra/outcome fields (extra="forbid").
    2. Prediction succeeds on valid BatchAssessmentInput with zero outcome attributes.
    """
    batch_input = _make_batch_input(crop_type="apples")

    # Assert outcome fields are not attributes of the canonical domain input
    for forbidden_field in [
        "loss_fraction_pct",
        "quality_status",
        "quality_score",
        "economic_loss_eur",
    ]:
        assert not hasattr(batch_input, forbidden_field)
        assert not hasattr(batch_input.batch, forbidden_field)

    # Assert attempting to pass outcome fields to BatchAssessmentInput raises ValidationError
    with pytest.raises(ValidationError):
        BatchAssessmentInput(
            **batch_input.model_dump(),
            loss_fraction_pct=15.0,  # forbidden
        )

    # Predict works without any outcome data
    baseline = fit_crop_median_baseline(
        [CropMedianTrainingRecord(crop_type="apples", loss_fraction_pct=12.0)]
    )
    score = predict_risk_score(baseline, batch_input)
    assert score == 0.12


def test_negative_case_n5_no_silent_full_snapshot_fitting() -> None:
    """N5: No silent full-snapshot fitting.

    Assert that the baseline module does not accept a RawSnapshot or provide
    any convenience function that silently fits on historical outcomes without
    explicit caller-supplied records.
    """
    import app.analytics.crop_median_baseline as baseline_module

    # Assert RawSnapshot is not imported or used as type hint in crop_median_baseline
    assert "RawSnapshot" not in baseline_module.__dict__

    # Assert fit_crop_median_baseline rejects non-Sequence arguments
    with pytest.raises(TypeError):
        fit_crop_median_baseline("not_a_sequence")  # type: ignore[arg-type]

    class FakeSnapshot:
        tables = {}

    with pytest.raises(TypeError):
        fit_crop_median_baseline(FakeSnapshot())  # type: ignore[arg-type]


def test_negative_case_n6_no_unsupported_output_semantics() -> None:
    """N6: No unsupported output semantics.

    The baseline must not return risk.band, confidence_score, deterioration_horizon,
    recommendation, or factor directions. Assert absence on the returned types.
    """
    records = [
        CropMedianTrainingRecord(crop_type="peaches", loss_fraction_pct=22.0),
    ]
    baseline = fit_crop_median_baseline(records)
    batch_input = _make_batch_input(crop_type="peaches")

    loss_pred = predict_loss_fraction_pct(baseline, batch_input)
    risk_score = predict_risk_score(baseline, batch_input)

    # Assert exact primitive float returns
    assert type(loss_pred) is float
    assert type(risk_score) is float

    # Assert returned values have no unsupported attributes
    for unsupported_attr in [
        "band",
        "confidence_score",
        "deterioration_horizon",
        "recommendation",
        "factors",
        "reliability",
    ]:
        assert not hasattr(loss_pred, unsupported_attr)
        assert not hasattr(risk_score, unsupported_attr)
