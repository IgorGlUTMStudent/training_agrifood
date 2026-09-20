"""Structural manifest defining expected physical schemas, keys, and relations for the raw sponsor pack."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class ForeignKeySpec:
    """Specification of a direct referential foreign key constraint."""

    child_column: str
    parent_table: str
    parent_column: str


@dataclass(frozen=True)
class TableSpec:
    """Specification of expected physical file structure and relational keys for a raw table."""

    table_name: str
    filename: str
    expected_headers: Tuple[str, ...]
    pk_column: str
    expected_row_count: int
    fk_relations: Tuple[ForeignKeySpec, ...] = field(default_factory=tuple)


TABLE_MANIFEST: dict[str, TableSpec] = {
    "facilities": TableSpec(
        table_name="facilities",
        filename="facilities.csv",
        expected_headers=(
            "facility_id",
            "facility_name",
            "region",
            "district",
            "facility_type",
            "capacity_tonnes",
            "commissioned_year",
            "has_controlled_atmosphere",
        ),
        pk_column="facility_id",
        expected_row_count=10,
    ),
    "storage_zones": TableSpec(
        table_name="storage_zones",
        filename="storage_zones.csv",
        expected_headers=(
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
        ),
        pk_column="zone_id",
        expected_row_count=25,
        fk_relations=(
            ForeignKeySpec(
                child_column="facility_id",
                parent_table="facilities",
                parent_column="facility_id",
            ),
        ),
    ),
    "batches": TableSpec(
        table_name="batches",
        filename="batches.csv",
        expected_headers=(
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
        ),
        pk_column="batch_id",
        expected_row_count=1800,
    ),
    "storage_sessions": TableSpec(
        table_name="storage_sessions",
        filename="storage_sessions.csv",
        expected_headers=(
            "storage_session_id",
            "batch_id",
            "zone_id",
            "entry_datetime",
            "dispatch_datetime",
            "planned_dispatch_datetime",
            "bin_stack_tier",
            "storage_duration_days",
        ),
        pk_column="storage_session_id",
        expected_row_count=1800,
        fk_relations=(
            ForeignKeySpec(
                child_column="batch_id",
                parent_table="batches",
                parent_column="batch_id",
            ),
            ForeignKeySpec(
                child_column="zone_id",
                parent_table="storage_zones",
                parent_column="zone_id",
            ),
        ),
    ),
    "sensor_readings": TableSpec(
        table_name="sensor_readings",
        filename="sensor_readings.csv",
        expected_headers=(
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
        ),
        pk_column="reading_id",
        expected_row_count=669665,
        fk_relations=(
            ForeignKeySpec(
                child_column="zone_id",
                parent_table="storage_zones",
                parent_column="zone_id",
            ),
        ),
    ),
    "quality_checks": TableSpec(
        table_name="quality_checks",
        filename="quality_checks.csv",
        expected_headers=(
            "check_id",
            "batch_id",
            "check_datetime",
            "stage",
            "firmness_kg_cm2",
            "sugar_brix",
            "defect_pct",
        ),
        pk_column="check_id",
        expected_row_count=5400,
        fk_relations=(
            ForeignKeySpec(
                child_column="batch_id",
                parent_table="batches",
                parent_column="batch_id",
            ),
        ),
    ),
    "shipments": TableSpec(
        table_name="shipments",
        filename="shipments.csv",
        expected_headers=(
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
        ),
        pk_column="shipment_id",
        expected_row_count=1800,
        fk_relations=(
            ForeignKeySpec(
                child_column="batch_id",
                parent_table="batches",
                parent_column="batch_id",
            ),
        ),
    ),
    "historical_quality_outcomes": TableSpec(
        table_name="historical_quality_outcomes",
        filename="historical_quality_outcomes.csv",
        expected_headers=(
            "batch_id",
            "quality_status",
            "loss_fraction_pct",
            "quality_score",
            "economic_loss_eur",
        ),
        pk_column="batch_id",
        expected_row_count=1800,
        fk_relations=(
            ForeignKeySpec(
                child_column="batch_id",
                parent_table="batches",
                parent_column="batch_id",
            ),
        ),
    ),
}
