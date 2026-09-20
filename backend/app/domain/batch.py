"""Canonical domain models for batch assessment input (IGR-03).

Defined per ADR 0002 (Predictive Input Semantics and Temporal Leakage Boundary).
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ContractModel(BaseModel):
    """Base contract model strictly forbidding undeclared extra fields."""

    model_config = ConfigDict(extra="forbid")


class BatchIdentity(ContractModel):
    """Authoritative identity section for a batch assessment input."""

    batch_id: str = Field(..., min_length=1)
    storage_session_id: str = Field(..., min_length=1)
    facility_id: str = Field(..., min_length=1)
    zone_id: str = Field(..., min_length=1)


class AssessmentContext(ContractModel):
    """Single authoritative assessment anchor clock."""

    assessment_timestamp: datetime


class BatchContext(ContractModel):
    """Produce intake attributes fixed at or prior to harvest."""

    crop_type: str = Field(..., min_length=1)
    variety: str = Field(..., min_length=1)
    origin_region: str = Field(..., min_length=1)
    harvest_datetime: datetime
    harvest_weight_kg: float
    initial_quality_score: float
    harvest_temperature_c: float
    harvest_conditions: str = Field(..., min_length=1)
    field_precooled: bool


class StorageContext(ContractModel):
    """Storage stay parameters known at dispatch."""

    entry_datetime: datetime
    planned_dispatch_datetime: datetime | None = None
    bin_stack_tier: int
    storage_duration_days: int


class FacilityContext(ContractModel):
    """Static facility / site infrastructure context."""

    facility_name: str | None = None
    region: str = Field(..., min_length=1)
    district: str = Field(..., min_length=1)
    facility_type: str = Field(..., min_length=1)
    capacity_tonnes: int
    commissioned_year: int
    has_controlled_atmosphere: bool


class StorageZoneContext(ContractModel):
    """Static storage zone / chamber infrastructure context."""

    zone_name: str | None = None
    zone_type: str = Field(..., min_length=1)
    nominal_capacity_tonnes: int
    target_temperature_c: float
    target_relative_humidity_pct: float
    cooling_system_type: str = Field(..., min_length=1)
    insulation_quality: str = Field(..., min_length=1)
    defrost_cycle_frequency_per_day: int


class StageQualityCheck(ContractModel):
    """Physical inspection measurements for a single authorized stage."""

    check_datetime: datetime
    firmness_kg_cm2: float
    sugar_brix: float
    defect_pct: float


class QualityContext(ContractModel):
    """Quality inspections available at or before dispatch (harvest and pre_dispatch)."""

    harvest: StageQualityCheck
    pre_dispatch: StageQualityCheck


class TelemetryReading(ContractModel):
    """Single raw environmental reading within the storage stay interval."""

    timestamp: datetime
    air_temperature_c: float
    produce_surface_temperature_c: float | None = None
    relative_humidity_pct: float
    dew_point_c: float
    condensation_flag: bool
    co2_ppm: float | None = None
    o2_pct: float | None = None
    cooling_on: bool
    defrost_on: bool


class TelemetryContext(ContractModel):
    """Telemetry readings bounded by storage stay interval."""

    zone_id: str = Field(..., min_length=1)
    window_start: datetime
    window_end: datetime
    readings: list[TelemetryReading] = Field(default_factory=list)


class PlannedLogisticsContext(ContractModel):
    """Pre-scheduled logistics parameters known at dispatch."""

    shipment_id: str | None = None
    destination_market: str = Field(..., min_length=1)
    destination_region: str = Field(..., min_length=1)
    vehicle_type: str = Field(..., min_length=1)
    planned_departure_datetime: datetime
    planned_arrival_datetime: datetime
    planned_duration_hours: float


class BatchAssessmentInput(ContractModel):
    """Canonical input contract for predictive batch assessment at dispatch."""

    identity: BatchIdentity
    assessment_context: AssessmentContext
    batch: BatchContext
    storage: StorageContext
    facility: FacilityContext
    zone: StorageZoneContext
    quality: QualityContext
    telemetry: TelemetryContext
    planned_logistics: PlannedLogisticsContext | None = None
