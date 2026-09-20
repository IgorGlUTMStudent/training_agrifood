"""Deterministic mapper from raw snapshot to canonical BatchAssessmentInput (IGR-03).

Strictly adheres to ADR 0002 (Predictive Input Semantics and Temporal Leakage Boundary).
Preserves raw values with strict typed validation without repair, imputation, or analytics.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

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
from app.ingestion.raw_reader import RawSnapshot


class CanonicalMappingError(ValueError):
    """Base error for canonical mapping failures."""


class BatchNotFoundError(CanonicalMappingError):
    """Raised when requested batch_id is not present in raw batches table."""


class CardinalityError(CanonicalMappingError):
    """Raised when unexpected entity cardinality is detected during join."""


class CanonicalValidationError(CanonicalMappingError):
    """Raised when raw field values fail strict type or constraint validation."""


def _parse_non_empty_str(val: Any, field_name: str) -> str:
    if not isinstance(val, str) or val == "":
        raise CanonicalValidationError(
            f"Field '{field_name}' must be a non-empty string, got: {val!r}"
        )
    return val


def _parse_optional_str(val: Any) -> str | None:
    if val is None or val == "":
        return None
    if not isinstance(val, str):
        return str(val)
    return val


def _parse_float(val: Any, field_name: str) -> float:
    if val is None or val == "":
        raise CanonicalValidationError(
            f"Field '{field_name}' must be a non-null float, got: {val!r}"
        )
    try:
        return float(val)
    except (ValueError, TypeError) as e:
        raise CanonicalValidationError(
            f"Failed to parse float for field '{field_name}' from value {val!r}: {e}"
        ) from e


def _parse_optional_float(val: Any, field_name: str) -> float | None:
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError) as e:
        raise CanonicalValidationError(
            f"Failed to parse optional float for field '{field_name}' from value {val!r}: {e}"
        ) from e


def _parse_int(val: Any, field_name: str) -> int:
    if val is None or val == "":
        raise CanonicalValidationError(
            f"Field '{field_name}' must be a non-null integer, got: {val!r}"
        )
    try:
        return int(val)
    except (ValueError, TypeError) as e:
        raise CanonicalValidationError(
            f"Failed to parse integer for field '{field_name}' from value {val!r}: {e}"
        ) from e


def _parse_bool(val: Any, field_name: str) -> bool:
    if val == "True" or val is True:
        return True
    if val == "False" or val is False:
        return False
    raise CanonicalValidationError(
        f"Field '{field_name}' must be 'True' or 'False', got: {val!r}"
    )


def _parse_datetime(val: Any, field_name: str) -> datetime:
    if val is None or val == "":
        raise CanonicalValidationError(
            f"Field '{field_name}' must be a non-null datetime, got: {val!r}"
        )
    try:
        return datetime.fromisoformat(val)
    except (ValueError, TypeError) as e:
        raise CanonicalValidationError(
            f"Failed to parse datetime for field '{field_name}' from value {val!r}: {e}"
        ) from e


def _parse_optional_datetime(val: Any, field_name: str) -> datetime | None:
    if val is None or val == "":
        return None
    try:
        return datetime.fromisoformat(val)
    except (ValueError, TypeError) as e:
        raise CanonicalValidationError(
            f"Failed to parse optional datetime for field '{field_name}' from value {val!r}: {e}"
        ) from e


def build_batch_assessment_input(
    snapshot: RawSnapshot, batch_id: str
) -> BatchAssessmentInput:
    """Build a typed, validated BatchAssessmentInput from a raw snapshot for a single batch.

    Enforces:
    - Authoritative join path: batches -> storage_sessions -> storage_zones -> facilities.
    - Single assessment clock: assessment_context.assessment_timestamp == storage_sessions.dispatch_datetime.
    - Strict temporal boundary: storage.entry_datetime <= telemetry.timestamp <= dispatch_datetime.
    - Stage safety: only harvest and pre_dispatch quality checks admitted; arrival QC excluded.
    - Planned logistics safety: only planned transport fields admitted; actual transit realizations excluded.
    - Historical outcomes excluded entirely.
    - Zero fabrication prohibited: structural missingness preserved as None.
    - Fail-closed on missing parent entities, unexpected cardinality, or malformed data.
    """
    if not isinstance(batch_id, str) or not batch_id:
        raise BatchNotFoundError(f"Invalid batch_id: {batch_id!r}")

    required_tables = [
        "batches",
        "storage_sessions",
        "storage_zones",
        "facilities",
        "quality_checks",
        "sensor_readings",
    ]
    for tbl in required_tables:
        if tbl not in snapshot:
            raise CanonicalMappingError(
                f"Required raw table '{tbl}' is missing from snapshot"
            )

    # Build or retrieve read-only telemetry index by zone_id (Contract Section 7)
    sensor_table = snapshot["sensor_readings"]
    cached_index = getattr(snapshot, "_readings_by_zone_cache", None)
    if cached_index is not None and cached_index[0] is sensor_table.rows:
        readings_by_zone = cached_index[1]
    else:
        readings_by_zone: dict[str, list[dict[str, str]]] = {}
        for r in sensor_table.rows:
            zid = r.get("zone_id")
            if zid:
                readings_by_zone.setdefault(zid, []).append(r)
        try:
            snapshot._readings_by_zone_cache = (sensor_table.rows, readings_by_zone)
        except Exception:
            pass

    # 1. Join batch
    batch_table = snapshot["batches"]
    batch_rows = [r for r in batch_table.rows if r.get("batch_id") == batch_id]
    if len(batch_rows) == 0:
        raise BatchNotFoundError(f"Batch '{batch_id}' not found in batches table")
    if len(batch_rows) > 1:
        raise CardinalityError(
            f"Expected exactly 1 row for batch '{batch_id}' in batches, found {len(batch_rows)}"
        )
    batch_row = batch_rows[0]

    # 2. Join storage session
    session_table = snapshot["storage_sessions"]
    session_rows = [r for r in session_table.rows if r.get("batch_id") == batch_id]
    if len(session_rows) == 0:
        raise CardinalityError(
            f"No storage session found for batch '{batch_id}' in storage_sessions"
        )
    if len(session_rows) > 1:
        raise CardinalityError(
            f"Expected exactly 1 storage session for batch '{batch_id}', found {len(session_rows)}"
        )
    session_row = session_rows[0]

    storage_session_id = _parse_non_empty_str(
        session_row.get("storage_session_id", ""), "storage_session_id"
    )
    zone_id = _parse_non_empty_str(session_row.get("zone_id", ""), "zone_id")
    entry_datetime = _parse_datetime(
        session_row.get("entry_datetime"), "entry_datetime"
    )
    dispatch_datetime = _parse_datetime(
        session_row.get("dispatch_datetime"), "dispatch_datetime"
    )
    planned_dispatch_datetime = _parse_optional_datetime(
        session_row.get("planned_dispatch_datetime"), "planned_dispatch_datetime"
    )
    bin_stack_tier = _parse_int(
        session_row.get("bin_stack_tier"), "bin_stack_tier"
    )
    storage_duration_days = _parse_int(
        session_row.get("storage_duration_days"), "storage_duration_days"
    )

    # 3. Join storage zone
    zone_table = snapshot["storage_zones"]
    zone_rows = [r for r in zone_table.rows if r.get("zone_id") == zone_id]
    if len(zone_rows) == 0:
        raise CardinalityError(
            f"Storage zone '{zone_id}' referenced by session '{storage_session_id}' not found in storage_zones"
        )
    if len(zone_rows) > 1:
        raise CardinalityError(
            f"Expected exactly 1 row for zone '{zone_id}' in storage_zones, found {len(zone_rows)}"
        )
    zone_row = zone_rows[0]

    facility_id = _parse_non_empty_str(
        zone_row.get("facility_id", ""), "facility_id"
    )
    zone_name = _parse_optional_str(zone_row.get("zone_name"))
    zone_type = _parse_non_empty_str(zone_row.get("zone_type", ""), "zone_type")
    nominal_capacity_tonnes = _parse_int(
        zone_row.get("nominal_capacity_tonnes"), "nominal_capacity_tonnes"
    )
    target_temperature_c = _parse_float(
        zone_row.get("target_temperature_c"), "target_temperature_c"
    )
    target_relative_humidity_pct = _parse_float(
        zone_row.get("target_relative_humidity_pct"), "target_relative_humidity_pct"
    )
    cooling_system_type = _parse_non_empty_str(
        zone_row.get("cooling_system_type", ""), "cooling_system_type"
    )
    insulation_quality = _parse_non_empty_str(
        zone_row.get("insulation_quality", ""), "insulation_quality"
    )
    defrost_cycle_frequency_per_day = _parse_int(
        zone_row.get("defrost_cycle_frequency_per_day"),
        "defrost_cycle_frequency_per_day",
    )

    # 4. Join facility
    facility_table = snapshot["facilities"]
    facility_rows = [
        r for r in facility_table.rows if r.get("facility_id") == facility_id
    ]
    if len(facility_rows) == 0:
        raise CardinalityError(
            f"Facility '{facility_id}' referenced by zone '{zone_id}' not found in facilities"
        )
    if len(facility_rows) > 1:
        raise CardinalityError(
            f"Expected exactly 1 row for facility '{facility_id}' in facilities, found {len(facility_rows)}"
        )
    facility_row = facility_rows[0]

    facility_name = _parse_optional_str(facility_row.get("facility_name"))
    region = _parse_non_empty_str(facility_row.get("region", ""), "region")
    district = _parse_non_empty_str(facility_row.get("district", ""), "district")
    facility_type = _parse_non_empty_str(
        facility_row.get("facility_type", ""), "facility_type"
    )
    capacity_tonnes = _parse_int(
        facility_row.get("capacity_tonnes"), "capacity_tonnes"
    )
    commissioned_year = _parse_int(
        facility_row.get("commissioned_year"), "commissioned_year"
    )
    has_controlled_atmosphere = _parse_bool(
        facility_row.get("has_controlled_atmosphere"), "has_controlled_atmosphere"
    )

    # 5. Batch fields
    crop_type = _parse_non_empty_str(batch_row.get("crop_type", ""), "crop_type")
    variety = _parse_non_empty_str(batch_row.get("variety", ""), "variety")
    origin_region = _parse_non_empty_str(
        batch_row.get("origin_region", ""), "origin_region"
    )
    harvest_datetime = _parse_datetime(
        batch_row.get("harvest_datetime"), "harvest_datetime"
    )
    harvest_weight_kg = _parse_float(
        batch_row.get("harvest_weight_kg"), "harvest_weight_kg"
    )
    initial_quality_score = _parse_float(
        batch_row.get("initial_quality_score"), "initial_quality_score"
    )
    harvest_temperature_c = _parse_float(
        batch_row.get("harvest_temperature_c"), "harvest_temperature_c"
    )
    harvest_conditions = _parse_non_empty_str(
        batch_row.get("harvest_conditions", ""), "harvest_conditions"
    )
    field_precooled = _parse_bool(
        batch_row.get("field_precooled"), "field_precooled"
    )

    # 6. Quality checks: harvest and pre_dispatch only (arrival forbidden)
    qc_table = snapshot["quality_checks"]
    qc_rows = [r for r in qc_table.rows if r.get("batch_id") == batch_id]

    harvest_qcs: list[dict[str, str]] = []
    pre_dispatch_qcs: list[dict[str, str]] = []

    for r in qc_rows:
        stg = r.get("stage")
        if stg == "harvest":
            harvest_qcs.append(r)
        elif stg == "pre_dispatch":
            pre_dispatch_qcs.append(r)
        elif stg == "arrival":
            # Explicitly ignored / excluded from canonical input
            continue
        else:
            raise CanonicalValidationError(
                f"Unexpected quality check stage '{stg}' for batch '{batch_id}'"
            )

    if len(harvest_qcs) == 0:
        raise CardinalityError(
            f"Missing required 'harvest' quality check for batch '{batch_id}'"
        )
    if len(harvest_qcs) > 1:
        raise CardinalityError(
            f"Expected exactly 1 'harvest' quality check for batch '{batch_id}', found {len(harvest_qcs)}"
        )

    if len(pre_dispatch_qcs) == 0:
        raise CardinalityError(
            f"Missing required 'pre_dispatch' quality check for batch '{batch_id}'"
        )
    if len(pre_dispatch_qcs) > 1:
        raise CardinalityError(
            f"Expected exactly 1 'pre_dispatch' quality check for batch '{batch_id}', found {len(pre_dispatch_qcs)}"
        )

    h_row = harvest_qcs[0]
    harvest_check = StageQualityCheck(
        check_datetime=_parse_datetime(
            h_row.get("check_datetime"), "harvest.check_datetime"
        ),
        firmness_kg_cm2=_parse_float(
            h_row.get("firmness_kg_cm2"), "harvest.firmness_kg_cm2"
        ),
        sugar_brix=_parse_float(h_row.get("sugar_brix"), "harvest.sugar_brix"),
        defect_pct=_parse_float(h_row.get("defect_pct"), "harvest.defect_pct"),
    )

    pd_row = pre_dispatch_qcs[0]
    pre_dispatch_check = StageQualityCheck(
        check_datetime=_parse_datetime(
            pd_row.get("check_datetime"), "pre_dispatch.check_datetime"
        ),
        firmness_kg_cm2=_parse_float(
            pd_row.get("firmness_kg_cm2"), "pre_dispatch.firmness_kg_cm2"
        ),
        sugar_brix=_parse_float(
            pd_row.get("sugar_brix"), "pre_dispatch.sugar_brix"
        ),
        defect_pct=_parse_float(
            pd_row.get("defect_pct"), "pre_dispatch.defect_pct"
        ),
    )

    # Enforce strict physical chronology invariant (Contract Section 9):
    # T_harvest < T_harvest_qc < T_entry < T_pre_dispatch_qc < T_dispatch
    if not (
        harvest_datetime
        < harvest_check.check_datetime
        < entry_datetime
        < pre_dispatch_check.check_datetime
        < dispatch_datetime
    ):
        raise CanonicalValidationError(
            f"Chronological sequence violation for batch '{batch_id}': "
            f"expected harvest_datetime ({harvest_datetime}) < "
            f"harvest_qc ({harvest_check.check_datetime}) < "
            f"entry_datetime ({entry_datetime}) < "
            f"pre_dispatch_qc ({pre_dispatch_check.check_datetime}) < "
            f"dispatch_datetime ({dispatch_datetime})"
        )

    # 7. Telemetry: bounded by entry_datetime <= timestamp <= dispatch_datetime
    telemetry_readings: list[TelemetryReading] = []
    zone_readings = readings_by_zone.get(zone_id, [])

    for r in zone_readings:
        ts = _parse_datetime(r.get("timestamp"), "sensor_readings.timestamp")
        # Enforce temporal safety: exclude readings outside storage stay interval
        if not (entry_datetime <= ts <= dispatch_datetime):
            continue

        reading = TelemetryReading(
            timestamp=ts,
            air_temperature_c=_parse_float(
                r.get("air_temperature_c"), "air_temperature_c"
            ),
            produce_surface_temperature_c=_parse_optional_float(
                r.get("produce_surface_temperature_c"),
                "produce_surface_temperature_c",
            ),
            relative_humidity_pct=_parse_float(
                r.get("relative_humidity_pct"), "relative_humidity_pct"
            ),
            dew_point_c=_parse_float(r.get("dew_point_c"), "dew_point_c"),
            condensation_flag=_parse_bool(
                r.get("condensation_flag"), "condensation_flag"
            ),
            co2_ppm=_parse_optional_float(r.get("co2_ppm"), "co2_ppm"),
            o2_pct=_parse_optional_float(r.get("o2_pct"), "o2_pct"),
            cooling_on=_parse_bool(r.get("cooling_on"), "cooling_on"),
            defrost_on=_parse_bool(r.get("defrost_on"), "defrost_on"),
        )
        telemetry_readings.append(reading)

    # Sort deterministically by timestamp
    telemetry_readings.sort(key=lambda x: x.timestamp)

    # 8. Planned logistics (optional / conditionally eligible)
    planned_logistics: PlannedLogisticsContext | None = None
    if "shipments" in snapshot:
        shipment_table = snapshot["shipments"]
        shipment_rows = [
            r for r in shipment_table.rows if r.get("batch_id") == batch_id
        ]
        if len(shipment_rows) > 1:
            raise CardinalityError(
                f"Expected at most 1 shipment row for batch '{batch_id}', found {len(shipment_rows)}"
            )
        if len(shipment_rows) == 1:
            s_row = shipment_rows[0]
            planned_logistics = PlannedLogisticsContext(
                shipment_id=_parse_optional_str(s_row.get("shipment_id")),
                destination_market=_parse_non_empty_str(
                    s_row.get("destination_market", ""), "destination_market"
                ),
                destination_region=_parse_non_empty_str(
                    s_row.get("destination_region", ""), "destination_region"
                ),
                vehicle_type=_parse_non_empty_str(
                    s_row.get("vehicle_type", ""), "vehicle_type"
                ),
                planned_departure_datetime=_parse_datetime(
                    s_row.get("planned_departure_datetime"),
                    "planned_departure_datetime",
                ),
                planned_arrival_datetime=_parse_datetime(
                    s_row.get("planned_arrival_datetime"),
                    "planned_arrival_datetime",
                ),
                planned_duration_hours=_parse_float(
                    s_row.get("planned_duration_hours"),
                    "planned_duration_hours",
                ),
            )

    # 9. Return assembled BatchAssessmentInput
    return BatchAssessmentInput(
        identity=BatchIdentity(
            batch_id=batch_id,
            storage_session_id=storage_session_id,
            facility_id=facility_id,
            zone_id=zone_id,
        ),
        assessment_context=AssessmentContext(
            assessment_timestamp=dispatch_datetime,
        ),
        batch=BatchContext(
            crop_type=crop_type,
            variety=variety,
            origin_region=origin_region,
            harvest_datetime=harvest_datetime,
            harvest_weight_kg=harvest_weight_kg,
            initial_quality_score=initial_quality_score,
            harvest_temperature_c=harvest_temperature_c,
            harvest_conditions=harvest_conditions,
            field_precooled=field_precooled,
        ),
        storage=StorageContext(
            entry_datetime=entry_datetime,
            planned_dispatch_datetime=planned_dispatch_datetime,
            bin_stack_tier=bin_stack_tier,
            storage_duration_days=storage_duration_days,
        ),
        facility=FacilityContext(
            facility_name=facility_name,
            region=region,
            district=district,
            facility_type=facility_type,
            capacity_tonnes=capacity_tonnes,
            commissioned_year=commissioned_year,
            has_controlled_atmosphere=has_controlled_atmosphere,
        ),
        zone=StorageZoneContext(
            zone_name=zone_name,
            zone_type=zone_type,
            nominal_capacity_tonnes=nominal_capacity_tonnes,
            target_temperature_c=target_temperature_c,
            target_relative_humidity_pct=target_relative_humidity_pct,
            cooling_system_type=cooling_system_type,
            insulation_quality=insulation_quality,
            defrost_cycle_frequency_per_day=defrost_cycle_frequency_per_day,
        ),
        quality=QualityContext(
            harvest=harvest_check,
            pre_dispatch=pre_dispatch_check,
        ),
        telemetry=TelemetryContext(
            zone_id=zone_id,
            window_start=entry_datetime,
            window_end=dispatch_datetime,
            readings=telemetry_readings,
        ),
        planned_logistics=planned_logistics,
    )
