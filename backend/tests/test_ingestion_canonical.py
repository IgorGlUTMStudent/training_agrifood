"""Tests for canonical BatchAssessmentInput mapping (IGR-03).

Validates:
1. Positive acceptance against supplied sponsor snapshot:
   - Maps known batch successfully.
   - Anchor clock: assessment_timestamp == storage_sessions.dispatch_datetime.
   - Identity joins: batch -> storage_session -> storage_zone -> facility.
   - Typed parsing: int, float, bool, datetime, nullable fields.
   - Quality checks: harvest and pre_dispatch mapped; arrival strictly absent.
   - Telemetry bounds: entry_datetime <= timestamp <= dispatch_datetime.
   - Structural missingness: empty sensor channels preserved as None.
   - Planned logistics: planned fields only.
   - Strict negative contract: forbidden fields (arrival QC, actual transit,
     historical outcomes, post-dispatch telemetry) are absent from the model.
   - Model strictness: extra unexpected fields rejected (extra="forbid").
   - Leakage invariance: canonical output invariant under forbidden-data mutation.

2. Negative / Failure acceptance (fail-closed behavior):
   - Unknown batch_id raises BatchNotFoundError.
   - Malformed float, int, bool, datetime raises CanonicalValidationError.
   - Duplicate batch, storage_session, storage_zone, facility, shipment raises CardinalityError.
   - Missing storage_session, storage_zone, facility raises CardinalityError.
   - Duplicate harvest or pre_dispatch QC raises CardinalityError.
   - Arrival-only QC cannot substitute for pre_dispatch QC (raises CardinalityError).
   - Unexpected QC stage raises CanonicalValidationError.
   - Post-dispatch and pre-entry telemetry excluded.
   - Strong leakage invariance across synthetic fixtures differing ONLY in forbidden data.
"""

from __future__ import annotations

import copy
from datetime import datetime
from pathlib import Path
import pytest
from pydantic import ValidationError

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
from app.ingestion.canonical_mapper import (
    BatchNotFoundError,
    CanonicalValidationError,
    CardinalityError,
    build_batch_assessment_input,
)
from app.ingestion.raw_reader import RawSnapshot, RawTable, read_raw_snapshot

DATA_DIR = Path(__file__).parent.parent.parent / "sponsor_pack" / "data"


@pytest.fixture(scope="module")
def supplied_snapshot() -> RawSnapshot:
    """Load the authoritative supplied sponsor snapshot once for module tests."""
    return read_raw_snapshot(DATA_DIR)


def _make_synthetic_snapshot() -> RawSnapshot:
    """Build a minimal, valid synthetic RawSnapshot for isolated unit and negative testing."""
    return RawSnapshot(
        directory=Path("/synthetic"),
        tables={
            "facilities": RawTable(
                name="facilities",
                source_path=Path("/synthetic/facilities.csv"),
                headers=[
                    "facility_id",
                    "facility_name",
                    "region",
                    "district",
                    "facility_type",
                    "capacity_tonnes",
                    "commissioned_year",
                    "has_controlled_atmosphere",
                ],
                rows=[
                    {
                        "facility_id": "FAC-TEST-01",
                        "facility_name": "Test Facility Alpha",
                        "region": "North",
                        "district": "Bălți",
                        "facility_type": "Commercial Cold Store",
                        "capacity_tonnes": "5000",
                        "commissioned_year": "2019",
                        "has_controlled_atmosphere": "True",
                    }
                ],
            ),
            "storage_zones": RawTable(
                name="storage_zones",
                source_path=Path("/synthetic/storage_zones.csv"),
                headers=[
                    "zone_id",
                    "facility_id",
                    "zone_name",
                    "zone_type",
                    "nominal_capacity_tonnes",
                    "target_temperature_c",
                    "target_relative_humidity_pct",
                    "cooling_system_type",
                    "insulation_quality",
                    "defrost_cycle_frequency_per_day",
                ],
                rows=[
                    {
                        "zone_id": "ZONE-TEST-01",
                        "facility_id": "FAC-TEST-01",
                        "zone_name": "Test Chamber 1",
                        "zone_type": "Controlled Atmosphere (CA)",
                        "nominal_capacity_tonnes": "100",
                        "target_temperature_c": "1.5",
                        "target_relative_humidity_pct": "92.0",
                        "cooling_system_type": "Propane Chiller",
                        "insulation_quality": "Premium",
                        "defrost_cycle_frequency_per_day": "2",
                    }
                ],
            ),
            "batches": RawTable(
                name="batches",
                source_path=Path("/synthetic/batches.csv"),
                headers=[
                    "batch_id",
                    "crop_type",
                    "variety",
                    "origin_region",
                    "harvest_datetime",
                    "harvest_weight_kg",
                    "initial_quality_score",
                    "harvest_temperature_c",
                    "harvest_conditions",
                    "field_precooled",
                ],
                rows=[
                    {
                        "batch_id": "BAT-SYN-001",
                        "crop_type": "apples",
                        "variety": "Gala",
                        "origin_region": "North",
                        "harvest_datetime": "2024-09-01 08:00:00",
                        "harvest_weight_kg": "12500.50",
                        "initial_quality_score": "95.0",
                        "harvest_temperature_c": "18.5",
                        "harvest_conditions": "Optimal Dry",
                        "field_precooled": "True",
                    }
                ],
            ),
            "storage_sessions": RawTable(
                name="storage_sessions",
                source_path=Path("/synthetic/storage_sessions.csv"),
                headers=[
                    "storage_session_id",
                    "batch_id",
                    "zone_id",
                    "entry_datetime",
                    "dispatch_datetime",
                    "planned_dispatch_datetime",
                    "bin_stack_tier",
                    "storage_duration_days",
                ],
                rows=[
                    {
                        "storage_session_id": "SES-SYN-001",
                        "batch_id": "BAT-SYN-001",
                        "zone_id": "ZONE-TEST-01",
                        "entry_datetime": "2024-09-01 12:00:00",
                        "dispatch_datetime": "2024-10-01 12:00:00",
                        "planned_dispatch_datetime": "2024-10-01 12:00:00",
                        "bin_stack_tier": "4",
                        "storage_duration_days": "30",
                    }
                ],
            ),
            "sensor_readings": RawTable(
                name="sensor_readings",
                source_path=Path("/synthetic/sensor_readings.csv"),
                headers=[
                    "reading_id",
                    "zone_id",
                    "timestamp",
                    "air_temperature_c",
                    "produce_surface_temperature_c",
                    "relative_humidity_pct",
                    "dew_point_c",
                    "condensation_flag",
                    "co2_ppm",
                    "o2_pct",
                    "cooling_on",
                    "defrost_on",
                ],
                rows=[
                    {
                        "reading_id": "SR-PRE-01",
                        "zone_id": "ZONE-TEST-01",
                        "timestamp": "2024-09-01 11:30:00",  # Prior to entry -> must be excluded
                        "air_temperature_c": "1.8",
                        "produce_surface_temperature_c": "2.1",
                        "relative_humidity_pct": "91.0",
                        "dew_point_c": "0.4",
                        "condensation_flag": "False",
                        "co2_ppm": "12000.0",
                        "o2_pct": "2.0",
                        "cooling_on": "False",
                        "defrost_on": "False",
                    },
                    {
                        "reading_id": "SR-VALID-01",
                        "zone_id": "ZONE-TEST-01",
                        "timestamp": "2024-09-01 12:00:00",  # Exactly at entry -> valid
                        "air_temperature_c": "1.5",
                        "produce_surface_temperature_c": "",  # Nullable -> None
                        "relative_humidity_pct": "92.0",
                        "dew_point_c": "0.3",
                        "condensation_flag": "False",
                        "co2_ppm": "12500.0",
                        "o2_pct": "2.1",
                        "cooling_on": "True",
                        "defrost_on": "False",
                    },
                    {
                        "reading_id": "SR-VALID-02",
                        "zone_id": "ZONE-TEST-01",
                        "timestamp": "2024-10-01 12:00:00",  # Exactly at dispatch -> valid
                        "air_temperature_c": "1.6",
                        "produce_surface_temperature_c": "",
                        "relative_humidity_pct": "91.8",
                        "dew_point_c": "0.35",
                        "condensation_flag": "False",
                        "co2_ppm": "",  # Nullable -> None
                        "o2_pct": "",  # Nullable -> None
                        "cooling_on": "False",
                        "defrost_on": "False",
                    },
                    {
                        "reading_id": "SR-POST-01",
                        "zone_id": "ZONE-TEST-01",
                        "timestamp": "2024-10-01 12:30:00",  # After dispatch -> must be excluded
                        "air_temperature_c": "2.0",
                        "produce_surface_temperature_c": "2.5",
                        "relative_humidity_pct": "90.0",
                        "dew_point_c": "0.5",
                        "condensation_flag": "True",
                        "co2_ppm": "13000.0",
                        "o2_pct": "1.9",
                        "cooling_on": "False",
                        "defrost_on": "True",
                    },
                ],
            ),
            "quality_checks": RawTable(
                name="quality_checks",
                source_path=Path("/synthetic/quality_checks.csv"),
                headers=[
                    "check_id",
                    "batch_id",
                    "check_datetime",
                    "stage",
                    "firmness_kg_cm2",
                    "sugar_brix",
                    "defect_pct",
                ],
                rows=[
                    {
                        "check_id": "CHK-H-01",
                        "batch_id": "BAT-SYN-001",
                        "check_datetime": "2024-09-01 09:00:00",
                        "stage": "harvest",
                        "firmness_kg_cm2": "8.5",
                        "sugar_brix": "14.2",
                        "defect_pct": "1.0",
                    },
                    {
                        "check_id": "CHK-PD-01",
                        "batch_id": "BAT-SYN-001",
                        "check_datetime": "2024-10-01 10:00:00",
                        "stage": "pre_dispatch",
                        "firmness_kg_cm2": "7.8",
                        "sugar_brix": "15.0",
                        "defect_pct": "2.5",
                    },
                    {
                        "check_id": "CHK-ARR-01",
                        "batch_id": "BAT-SYN-001",
                        "check_datetime": "2024-10-02 18:00:00",
                        "stage": "arrival",  # Arrival QC -> must be excluded
                        "firmness_kg_cm2": "6.2",
                        "sugar_brix": "15.5",
                        "defect_pct": "12.0",
                    },
                ],
            ),
            "shipments": RawTable(
                name="shipments",
                source_path=Path("/synthetic/shipments.csv"),
                headers=[
                    "shipment_id",
                    "batch_id",
                    "destination_market",
                    "destination_region",
                    "vehicle_type",
                    "planned_departure_datetime",
                    "planned_arrival_datetime",
                    "planned_duration_hours",
                    "actual_departure_datetime",
                    "actual_arrival_datetime",
                    "actual_delay_minutes",
                    "cold_chain_incident",
                    "transit_temp_mean_c",
                ],
                rows=[
                    {
                        "shipment_id": "SHP-SYN-001",
                        "batch_id": "BAT-SYN-001",
                        "destination_market": "Munich",
                        "destination_region": "Western Europe",
                        "vehicle_type": "Reefer Truck",
                        "planned_departure_datetime": "2024-10-01 14:00:00",
                        "planned_arrival_datetime": "2024-10-02 16:00:00",
                        "planned_duration_hours": "26.0",
                        "actual_departure_datetime": "2024-10-01 14:30:00",
                        "actual_arrival_datetime": "2024-10-02 17:15:00",
                        "actual_delay_minutes": "45",
                        "cold_chain_incident": "False",
                        "transit_temp_mean_c": "2.8",
                    }
                ],
            ),
            "historical_quality_outcomes": RawTable(
                name="historical_quality_outcomes",
                source_path=Path("/synthetic/historical_quality_outcomes.csv"),
                headers=[
                    "batch_id",
                    "quality_status",
                    "loss_fraction_pct",
                    "quality_score",
                    "economic_loss_eur",
                ],
                rows=[
                    {
                        "batch_id": "BAT-SYN-001",
                        "quality_status": "optimal",
                        "loss_fraction_pct": "3.2",
                        "quality_score": "88.0",
                        "economic_loss_eur": "450.00",
                    }
                ],
            ),
        },
    )


# ==============================================================================
# Positive Acceptance Tests
# ==============================================================================


def test_supplied_batch_maps_successfully(supplied_snapshot: RawSnapshot) -> None:
    """Test 1: A known supplied batch maps successfully to BatchAssessmentInput."""
    canonical = build_batch_assessment_input(supplied_snapshot, "BAT-000001")
    assert isinstance(canonical, BatchAssessmentInput)
    assert canonical.identity.batch_id == "BAT-000001"
    assert canonical.identity.storage_session_id == "SES-000001"
    assert canonical.identity.zone_id == "ZONE-021"
    assert canonical.identity.facility_id == "FAC-008"


def test_assessment_timestamp_is_dispatch_datetime(supplied_snapshot: RawSnapshot) -> None:
    """Test 2: assessment_timestamp == storage_sessions.dispatch_datetime."""
    canonical = build_batch_assessment_input(supplied_snapshot, "BAT-000001")
    expected_dispatch = datetime.fromisoformat("2024-09-11 15:50:24")
    assert canonical.assessment_context.assessment_timestamp == expected_dispatch


def test_identity_joins_correctly(supplied_snapshot: RawSnapshot) -> None:
    """Test 3: Identity values come from the correct joined entities."""
    canonical = build_batch_assessment_input(supplied_snapshot, "BAT-000001")
    assert canonical.identity.batch_id == "BAT-000001"
    assert canonical.identity.storage_session_id == "SES-000001"
    assert canonical.identity.zone_id == "ZONE-021"
    assert canonical.identity.facility_id == "FAC-008"
    assert canonical.telemetry.zone_id == canonical.identity.zone_id


def test_typed_scalar_fields_parse_correctly(supplied_snapshot: RawSnapshot) -> None:
    """Test 4: Typed scalar fields parse correctly into native Python types."""
    canonical = build_batch_assessment_input(supplied_snapshot, "BAT-000001")

    # Batches
    assert isinstance(canonical.batch.harvest_weight_kg, float)
    assert isinstance(canonical.batch.initial_quality_score, float)
    assert isinstance(canonical.batch.harvest_temperature_c, float)
    assert isinstance(canonical.batch.field_precooled, bool)
    assert canonical.batch.field_precooled is True
    assert isinstance(canonical.batch.harvest_datetime, datetime)

    # Storage
    assert isinstance(canonical.storage.bin_stack_tier, int)
    assert isinstance(canonical.storage.storage_duration_days, int)
    assert isinstance(canonical.storage.entry_datetime, datetime)

    # Facility
    assert isinstance(canonical.facility.capacity_tonnes, int)
    assert isinstance(canonical.facility.commissioned_year, int)
    assert isinstance(canonical.facility.has_controlled_atmosphere, bool)

    # Zone
    assert isinstance(canonical.zone.nominal_capacity_tonnes, int)
    assert isinstance(canonical.zone.target_temperature_c, float)
    assert isinstance(canonical.zone.target_relative_humidity_pct, float)
    assert isinstance(canonical.zone.defrost_cycle_frequency_per_day, int)


def test_quality_checks_harvest_and_pre_dispatch_mapped(supplied_snapshot: RawSnapshot) -> None:
    """Test 5: Exactly harvest and pre_dispatch quality checks are mapped."""
    canonical = build_batch_assessment_input(supplied_snapshot, "BAT-000001")

    assert isinstance(canonical.quality.harvest, StageQualityCheck)
    assert canonical.quality.harvest.check_datetime == datetime.fromisoformat("2024-08-06 13:15:00")
    assert canonical.quality.harvest.firmness_kg_cm2 == 7.32
    assert canonical.quality.harvest.sugar_brix == 13.3
    assert canonical.quality.harvest.defect_pct == 3.4

    assert isinstance(canonical.quality.pre_dispatch, StageQualityCheck)
    assert canonical.quality.pre_dispatch.check_datetime == datetime.fromisoformat("2024-09-11 13:50:24")
    assert canonical.quality.pre_dispatch.firmness_kg_cm2 == 7.57
    assert canonical.quality.pre_dispatch.sugar_brix == 15.6
    assert canonical.quality.pre_dispatch.defect_pct == 1.3


def test_arrival_quality_strictly_absent(supplied_snapshot: RawSnapshot) -> None:
    """Test 6: Arrival QC is strictly absent from BatchAssessmentInput."""
    canonical = build_batch_assessment_input(supplied_snapshot, "BAT-000001")

    # QualityContext contains only harvest and pre_dispatch
    assert set(QualityContext.model_fields.keys()) == {"harvest", "pre_dispatch"}
    assert not hasattr(canonical.quality, "arrival")

    # Dumped dict contains no arrival QC data
    data_dump = canonical.model_dump()
    assert "arrival" not in data_dump["quality"]
    # Check that arrival defect_pct (17.1% for BAT-000001) does not appear in quality
    assert data_dump["quality"]["harvest"]["defect_pct"] != 17.1
    assert data_dump["quality"]["pre_dispatch"]["defect_pct"] != 17.1


def test_telemetry_interval_bounds(supplied_snapshot: RawSnapshot) -> None:
    """Test 7: Telemetry contains only readings satisfying entry_datetime <= timestamp <= dispatch_datetime."""
    canonical = build_batch_assessment_input(supplied_snapshot, "BAT-000001")

    entry = canonical.storage.entry_datetime
    dispatch = canonical.assessment_context.assessment_timestamp

    assert len(canonical.telemetry.readings) > 0
    assert canonical.telemetry.window_start == entry
    assert canonical.telemetry.window_end == dispatch

    for reading in canonical.telemetry.readings:
        assert entry <= reading.timestamp <= dispatch


def test_telemetry_cache_rebuilds_after_append_and_remove() -> None:
    snapshot = _make_synthetic_snapshot()
    first = build_batch_assessment_input(snapshot, "BAT-SYN-001")
    rows = snapshot["sensor_readings"].rows
    added_timestamp = datetime(2024, 9, 15, 12, 0)
    added_row = dict(
        rows[1],
        reading_id="SR-ADDED-01",
        timestamp=added_timestamp.isoformat(),
        air_temperature_c="3.25",
    )
    rows.append(added_row)

    second = build_batch_assessment_input(snapshot, "BAT-SYN-001")

    assert all(r.timestamp != added_timestamp for r in first.telemetry.readings)
    added_readings = [r for r in second.telemetry.readings if r.timestamp == added_timestamp]
    assert len(added_readings) == 1
    assert added_readings[0].air_temperature_c == 3.25
    assert len(second.telemetry.readings) == len(first.telemetry.readings) + 1

    rows.remove(added_row)
    third = build_batch_assessment_input(snapshot, "BAT-SYN-001")
    assert third.telemetry == first.telemetry


def test_telemetry_cache_rebuilds_after_rows_replacement() -> None:
    snapshot = _make_synthetic_snapshot()
    first = build_batch_assessment_input(snapshot, "BAT-SYN-001")
    rows = [dict(r) for r in snapshot["sensor_readings"].rows]
    rows[1]["air_temperature_c"] = "3.25"
    snapshot["sensor_readings"].rows = rows

    second = build_batch_assessment_input(snapshot, "BAT-SYN-001")

    assert first.telemetry.readings[0].air_temperature_c == 1.5
    assert second.telemetry.readings[0].air_temperature_c == 3.25
    assert len(second.telemetry.readings) == len(first.telemetry.readings)


def test_telemetry_structural_missingness_preserved(supplied_snapshot: RawSnapshot) -> None:
    """Test 8: Telemetry readings retain structural None values without zero/mean fabrication."""
    # BAT-000001 is in ZONE-021 (non-CA chamber) -> co2_ppm and o2_pct must be None
    canonical_std = build_batch_assessment_input(supplied_snapshot, "BAT-000001")
    assert len(canonical_std.telemetry.readings) > 0
    for reading in canonical_std.telemetry.readings:
        assert reading.co2_ppm is None
        assert reading.o2_pct is None
        assert reading.produce_surface_temperature_c is not None

    # BAT-000006 is in ZONE-006 (CA chamber with missing surface temp probe)
    canonical_ca = build_batch_assessment_input(supplied_snapshot, "BAT-000006")
    assert len(canonical_ca.telemetry.readings) > 0
    for reading in canonical_ca.telemetry.readings:
        assert reading.produce_surface_temperature_c is None
        assert reading.co2_ppm is not None
        assert reading.o2_pct is not None


def test_planned_logistics_uses_only_planned_fields(supplied_snapshot: RawSnapshot) -> None:
    """Test 9: Planned logistics uses only authorized planned fields."""
    canonical = build_batch_assessment_input(supplied_snapshot, "BAT-000001")
    assert canonical.planned_logistics is not None

    planned = canonical.planned_logistics
    assert planned.shipment_id == "SHP-000001"
    assert planned.destination_market == "Warsaw"
    assert planned.destination_region == "Central Europe"
    assert planned.vehicle_type == "Reefer Truck"
    assert planned.planned_departure_datetime == datetime.fromisoformat("2024-09-11 17:20:24")
    assert planned.planned_arrival_datetime == datetime.fromisoformat("2024-09-12 21:20:24")
    assert planned.planned_duration_hours == 28.0

    # Test that planned_logistics can be None if shipments table is omitted
    snap_no_ship = copy.copy(supplied_snapshot)
    snap_no_ship.tables = dict(supplied_snapshot.tables)
    del snap_no_ship.tables["shipments"]
    canonical_no_ship = build_batch_assessment_input(snap_no_ship, "BAT-000001")
    assert canonical_no_ship.planned_logistics is None


def test_historical_outcomes_absent_from_canonical_model() -> None:
    """Test 10: Historical outcome fields are completely absent from canonical models."""
    dump_keys = set()
    for model_cls in [
        BatchAssessmentInput,
        BatchIdentity,
        AssessmentContext,
        BatchContext,
        StorageContext,
        FacilityContext,
        StorageZoneContext,
        StageQualityCheck,
        QualityContext,
        TelemetryReading,
        TelemetryContext,
        PlannedLogisticsContext,
    ]:
        dump_keys.update(model_cls.model_fields.keys())

    forbidden_historical = {
        "quality_status",
        "loss_fraction_pct",
        "quality_score",
        "economic_loss_eur",
    }
    overlap = dump_keys.intersection(forbidden_historical)
    assert overlap == set(), f"Forbidden historical fields found in models: {overlap}"


def test_realized_transit_fields_absent_from_canonical_model() -> None:
    """Test 11: Realized transit fields are completely absent from PlannedLogisticsContext."""
    logistics_fields = set(PlannedLogisticsContext.model_fields.keys())
    forbidden_realized = {
        "actual_departure_datetime",
        "actual_arrival_datetime",
        "actual_delay_minutes",
        "cold_chain_incident",
        "transit_temp_mean_c",
    }
    overlap = logistics_fields.intersection(forbidden_realized)
    assert overlap == set(), f"Forbidden transit fields found in PlannedLogisticsContext: {overlap}"


def test_canonical_model_rejects_extra_fields() -> None:
    """Test 12: Canonical models reject unexpected extra fields (extra='forbid')."""
    with pytest.raises(ValidationError):
        BatchIdentity(
            batch_id="BAT-01",
            storage_session_id="SES-01",
            facility_id="FAC-01",
            zone_id="ZONE-01",
            unexpected_field="disallowed",
        )

    with pytest.raises(ValidationError):
        PlannedLogisticsContext(
            destination_market="Berlin",
            destination_region="Western Europe",
            vehicle_type="Reefer Truck",
            planned_departure_datetime=datetime(2024, 9, 1, 12, 0),
            planned_arrival_datetime=datetime(2024, 9, 2, 12, 0),
            planned_duration_hours=24.0,
            actual_delay_minutes=30,  # Forbidden field
        )


def test_leakage_invariance_supplied_batch(supplied_snapshot: RawSnapshot) -> None:
    """Test 13: Canonical output is invariant under mutation of forbidden fields."""
    canonical_orig = build_batch_assessment_input(supplied_snapshot, "BAT-000001")

    # Clone snapshot and mutate ONLY forbidden fields
    mutated_snap = copy.copy(supplied_snapshot)
    mutated_snap.tables = dict(supplied_snapshot.tables)

    # 1. Mutate shipments realized fields
    ship_table = copy.copy(supplied_snapshot["shipments"])
    new_ship_rows = []
    for r in ship_table.rows:
        r_copy = dict(r)
        if r_copy.get("batch_id") == "BAT-000001":
            r_copy["actual_delay_minutes"] = "9999"
            r_copy["cold_chain_incident"] = "True"
            r_copy["transit_temp_mean_c"] = "35.5"
            r_copy["actual_departure_datetime"] = "2026-12-31 00:00:00"
            r_copy["actual_arrival_datetime"] = "2026-12-31 23:59:59"
        new_ship_rows.append(r_copy)
    ship_table.rows = new_ship_rows
    mutated_snap.tables["shipments"] = ship_table

    # 2. Mutate historical outcomes
    out_table = copy.copy(supplied_snapshot["historical_quality_outcomes"])
    new_out_rows = []
    for r in out_table.rows:
        r_copy = dict(r)
        if r_copy.get("batch_id") == "BAT-000001":
            r_copy["quality_status"] = "lost"
            r_copy["loss_fraction_pct"] = "100.0"
            r_copy["quality_score"] = "0.0"
            r_copy["economic_loss_eur"] = "999999.00"
        new_out_rows.append(r_copy)
    out_table.rows = new_out_rows
    mutated_snap.tables["historical_quality_outcomes"] = out_table

    # 3. Mutate arrival quality check
    qc_table = copy.copy(supplied_snapshot["quality_checks"])
    new_qc_rows = []
    for r in qc_table.rows:
        r_copy = dict(r)
        if r_copy.get("batch_id") == "BAT-000001" and r_copy.get("stage") == "arrival":
            r_copy["defect_pct"] = "99.9"
            r_copy["firmness_kg_cm2"] = "0.1"
            r_copy["sugar_brix"] = "0.1"
        new_qc_rows.append(r_copy)
    qc_table.rows = new_qc_rows
    mutated_snap.tables["quality_checks"] = qc_table

    canonical_mutated = build_batch_assessment_input(mutated_snap, "BAT-000001")

    assert canonical_orig.model_dump() == canonical_mutated.model_dump()


# ==============================================================================
# Negative / Failure Acceptance Tests
# ==============================================================================


def test_unknown_batch_id_fails_closed(supplied_snapshot: RawSnapshot) -> None:
    """Negative 1: Unknown batch_id raises BatchNotFoundError."""
    with pytest.raises(BatchNotFoundError):
        build_batch_assessment_input(supplied_snapshot, "BAT-NONEXISTENT-999")

    with pytest.raises(BatchNotFoundError):
        build_batch_assessment_input(supplied_snapshot, "")


def test_malformed_numeric_fails_closed() -> None:
    """Negative 2: Malformed required numeric values raise CanonicalValidationError."""
    # Case A: malformed float in batches
    snap = _make_synthetic_snapshot()
    snap["batches"].rows[0]["harvest_weight_kg"] = "not_a_float"
    with pytest.raises(CanonicalValidationError, match="Failed to parse float"):
        build_batch_assessment_input(snap, "BAT-SYN-001")

    # Case B: missing required float in quality_checks
    snap = _make_synthetic_snapshot()
    snap["quality_checks"].rows[0]["firmness_kg_cm2"] = ""
    with pytest.raises(CanonicalValidationError, match="must be a non-null float"):
        build_batch_assessment_input(snap, "BAT-SYN-001")

    # Case C: malformed integer in storage_zones
    snap = _make_synthetic_snapshot()
    snap["storage_zones"].rows[0]["nominal_capacity_tonnes"] = "100.5"  # float string for int
    with pytest.raises(CanonicalValidationError, match="Failed to parse integer"):
        build_batch_assessment_input(snap, "BAT-SYN-001")


def test_malformed_datetime_fails_closed() -> None:
    """Negative 3: Malformed required datetime raises CanonicalValidationError."""
    snap = _make_synthetic_snapshot()
    snap["batches"].rows[0]["harvest_datetime"] = "2024-02-31 99:99:99"
    with pytest.raises(CanonicalValidationError, match="Failed to parse datetime"):
        build_batch_assessment_input(snap, "BAT-SYN-001")

    snap = _make_synthetic_snapshot()
    snap["storage_sessions"].rows[0]["dispatch_datetime"] = "not_a_date"
    with pytest.raises(CanonicalValidationError, match="Failed to parse datetime"):
        build_batch_assessment_input(snap, "BAT-SYN-001")


def test_malformed_boolean_fails_closed() -> None:
    """Negative 4: Malformed boolean representations raise CanonicalValidationError."""
    # Neither 'yes', '1', nor lowercase 'true' are permitted representations
    for bad_bool in ["yes", "1", "true", "t", ""]:
        snap = _make_synthetic_snapshot()
        snap["batches"].rows[0]["field_precooled"] = bad_bool
        with pytest.raises(CanonicalValidationError, match="must be 'True' or 'False'"):
            build_batch_assessment_input(snap, "BAT-SYN-001")


def test_duplicate_cardinality_fails_closed() -> None:
    """Negative 5: Duplicate parent entities or join cardinality violations raise CardinalityError."""
    # Case A: Duplicate batch row
    snap = _make_synthetic_snapshot()
    snap["batches"].rows.append(dict(snap["batches"].rows[0]))
    with pytest.raises(CardinalityError, match="Expected exactly 1 row for batch"):
        build_batch_assessment_input(snap, "BAT-SYN-001")

    # Case B: Duplicate storage session
    snap = _make_synthetic_snapshot()
    snap["storage_sessions"].rows.append(dict(snap["storage_sessions"].rows[0]))
    with pytest.raises(CardinalityError, match="Expected exactly 1 storage session"):
        build_batch_assessment_input(snap, "BAT-SYN-001")

    # Case C: Multiple shipments for a batch
    snap = _make_synthetic_snapshot()
    snap["shipments"].rows.append(dict(snap["shipments"].rows[0]))
    with pytest.raises(CardinalityError, match="Expected at most 1 shipment row"):
        build_batch_assessment_input(snap, "BAT-SYN-001")

    # Case D: Duplicate storage zone
    snap = _make_synthetic_snapshot()
    snap["storage_zones"].rows.append(dict(snap["storage_zones"].rows[0]))
    with pytest.raises(CardinalityError, match="Expected exactly 1 row for zone"):
        build_batch_assessment_input(snap, "BAT-SYN-001")

    # Case E: Duplicate facility
    snap = _make_synthetic_snapshot()
    snap["facilities"].rows.append(dict(snap["facilities"].rows[0]))
    with pytest.raises(CardinalityError, match="Expected exactly 1 row for facility"):
        build_batch_assessment_input(snap, "BAT-SYN-001")


def test_missing_required_parent_fails_closed() -> None:
    """Negative 6: Missing required parent relations raise CardinalityError."""
    # Case A: Missing storage session
    snap = _make_synthetic_snapshot()
    snap["storage_sessions"].rows = []
    with pytest.raises(CardinalityError, match="No storage session found"):
        build_batch_assessment_input(snap, "BAT-SYN-001")

    # Case B: Missing referenced storage zone
    snap = _make_synthetic_snapshot()
    snap["storage_zones"].rows = []
    with pytest.raises(CardinalityError, match="Storage zone 'ZONE-TEST-01'.*not found"):
        build_batch_assessment_input(snap, "BAT-SYN-001")

    # Case C: Missing referenced facility
    snap = _make_synthetic_snapshot()
    snap["facilities"].rows = []
    with pytest.raises(CardinalityError, match="Facility 'FAC-TEST-01'.*not found"):
        build_batch_assessment_input(snap, "BAT-SYN-001")


def test_duplicate_quality_stage_fails_closed() -> None:
    """Negative 7: Duplicate quality checks within the same required stage raise CardinalityError."""
    # Duplicate harvest QC
    snap = _make_synthetic_snapshot()
    dup_harvest = dict(snap["quality_checks"].rows[0])
    snap["quality_checks"].rows.append(dup_harvest)
    with pytest.raises(CardinalityError, match="Expected exactly 1 'harvest' quality check"):
        build_batch_assessment_input(snap, "BAT-SYN-001")

    # Duplicate pre_dispatch QC
    snap = _make_synthetic_snapshot()
    dup_pre_dispatch = dict(snap["quality_checks"].rows[1])
    snap["quality_checks"].rows.append(dup_pre_dispatch)
    with pytest.raises(CardinalityError, match="Expected exactly 1 'pre_dispatch' quality check"):
        build_batch_assessment_input(snap, "BAT-SYN-001")


def test_arrival_only_qc_cannot_substitute_for_pre_dispatch() -> None:
    """Negative 8: Arrival QC cannot substitute for missing pre_dispatch QC."""
    snap = _make_synthetic_snapshot()
    # Remove pre_dispatch QC, leaving harvest and arrival
    snap["quality_checks"].rows = [
        r for r in snap["quality_checks"].rows if r.get("stage") != "pre_dispatch"
    ]
    with pytest.raises(CardinalityError, match="Missing required 'pre_dispatch' quality check"):
        build_batch_assessment_input(snap, "BAT-SYN-001")

    # Also test unexpected stage raises CanonicalValidationError
    snap2 = _make_synthetic_snapshot()
    snap2["quality_checks"].rows[0]["stage"] = "in_transit"
    with pytest.raises(CanonicalValidationError, match="Unexpected quality check stage 'in_transit'"):
        build_batch_assessment_input(snap2, "BAT-SYN-001")


def test_post_dispatch_telemetry_excluded() -> None:
    """Negative 9: Post-dispatch and pre-entry telemetry readings are excluded."""
    snap = _make_synthetic_snapshot()
    # Synthetic snapshot has 4 readings:
    # 1. 11:30:00 (pre-entry) -> excluded
    # 2. 12:00:00 (entry) -> admitted
    # 3. 2024-10-01 12:00:00 (dispatch) -> admitted
    # 4. 2024-10-01 12:30:00 (post-dispatch) -> excluded
    canonical = build_batch_assessment_input(snap, "BAT-SYN-001")

    timestamps = [r.timestamp for r in canonical.telemetry.readings]
    assert len(timestamps) == 2
    assert datetime.fromisoformat("2024-09-01 11:30:00") not in timestamps
    assert datetime.fromisoformat("2024-10-01 12:30:00") not in timestamps
    assert datetime.fromisoformat("2024-09-01 12:00:00") in timestamps
    assert datetime.fromisoformat("2024-10-01 12:00:00") in timestamps


def test_no_silent_imputation_of_empty_channels() -> None:
    """Negative 10: Empty string in nullable telemetry channel must be None, never 0.0 or synthetic average."""
    snap = _make_synthetic_snapshot()
    canonical = build_batch_assessment_input(snap, "BAT-SYN-001")

    # First admitted reading had produce_surface_temperature_c = ""
    r1 = canonical.telemetry.readings[0]
    assert r1.produce_surface_temperature_c is None
    assert r1.produce_surface_temperature_c != 0.0
    assert r1.produce_surface_temperature_c != -1.0

    # Second admitted reading had co2_ppm = "" and o2_pct = ""
    r2 = canonical.telemetry.readings[1]
    assert r2.co2_ppm is None
    assert r2.o2_pct is None
    assert r2.co2_ppm != 0.0
    assert r2.o2_pct != 0.0


def test_strong_leakage_invariance_synthetic_fixtures() -> None:
    """Negative 11: Strong Leakage Invariance on synthetic fixtures.

    Construct two synthetic RawSnapshot fixtures that differ ONLY in forbidden fields:
    - actual_delay_minutes, cold_chain_incident, transit_temp_mean_c,
      actual_departure_datetime, actual_arrival_datetime
    - quality_status, loss_fraction_pct, quality_score, economic_loss_eur
    - post-dispatch telemetry (timestamp > dispatch_datetime)
    - arrival QC (stage == 'arrival')

    Assert:
    build_batch_assessment_input(snapshot_A, batch_id).model_dump()
      == build_batch_assessment_input(snapshot_B, batch_id).model_dump()
    """
    snap_a = _make_synthetic_snapshot()
    snap_b = _make_synthetic_snapshot()

    # Mutate ONLY forbidden fields in snap_b:
    # 1. Realized transit in shipments
    shp_b = snap_b["shipments"].rows[0]
    shp_b["actual_delay_minutes"] = "240"
    shp_b["cold_chain_incident"] = "True"
    shp_b["transit_temp_mean_c"] = "18.5"
    shp_b["actual_departure_datetime"] = "2024-10-01 18:00:00"
    shp_b["actual_arrival_datetime"] = "2024-10-02 22:00:00"

    # 2. Historical outcomes
    out_b = snap_b["historical_quality_outcomes"].rows[0]
    out_b["quality_status"] = "severe_degradation"
    out_b["loss_fraction_pct"] = "34.9"
    out_b["quality_score"] = "45.0"
    out_b["economic_loss_eur"] = "4362.50"

    # 3. Arrival QC
    arr_b = [r for r in snap_b["quality_checks"].rows if r["stage"] == "arrival"][0]
    arr_b["firmness_kg_cm2"] = "1.0"
    arr_b["sugar_brix"] = "99.0"
    arr_b["defect_pct"] = "100.0"

    # 4. Post-dispatch telemetry in sensor_readings
    post_b = [r for r in snap_b["sensor_readings"].rows if r["reading_id"] == "SR-POST-01"][0]
    post_b["air_temperature_c"] = "45.0"
    post_b["dew_point_c"] = "30.0"
    post_b["cooling_on"] = "True"

    # Also add another extreme post-dispatch ping to snap_b
    snap_b["sensor_readings"].rows.append(
        {
            "reading_id": "SR-POST-EXTRA",
            "zone_id": "ZONE-TEST-01",
            "timestamp": "2024-10-05 00:00:00",
            "air_temperature_c": "99.9",
            "produce_surface_temperature_c": "99.9",
            "relative_humidity_pct": "99.9",
            "dew_point_c": "99.9",
            "condensation_flag": "True",
            "co2_ppm": "99999.0",
            "o2_pct": "99.9",
            "cooling_on": "False",
            "defrost_on": "True",
        }
    )

    canonical_a = build_batch_assessment_input(snap_a, "BAT-SYN-001")
    canonical_b = build_batch_assessment_input(snap_b, "BAT-SYN-001")

    # Assert exact model_dump equivalence
    assert canonical_a.model_dump() == canonical_b.model_dump()
