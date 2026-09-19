# ADR 0002: Predictive Input Semantics and Temporal Leakage Boundary

- Status: Accepted
- Date: 2026-09-19
- Decision Owner: Vladimir (Integrator)

## Context
Following the acceptance of VDR-01 (Dataset Inventory) and VDR-02 (Temporal Chronology and Leakage Audit), the repository requires an authoritative, self-contained canonical input contract (`BatchAssessmentInput`) to govern the transition from raw CSV tables to predictive analytics. Application code currently contains no input model, and `docs/data_contract.md` records input semantics as undefined. The sponsor challenge imposes a strict assessment moment: $T_{assess} \equiv T_{dispatch} = \text{storage_sessions.dispatch_datetime}$. Furthermore, downstream transit events, destination arrival inspections, and final commercial outcomes are present in historical training files but represent severe future/target leakage if admitted at inference time.

## Decision

### 1. Semantic Grain & Assessment Anchor
- `BatchAssessmentInput` represents a single harvested produce batch at its dispatch assessment moment $T_{dispatch}$ (conclusion of cold storage stay, immediately prior to outbound transport loading).
- The contract carries a single authoritative assessment clock:
  `assessment_context.assessment_timestamp: datetime`
  sourced strictly from `storage_sessions.dispatch_datetime`. No secondary competing clock is introduced.

### 2. Controlled Field Eligibility Taxonomy
All 73 raw CSV table-field pairs are classified into a mutually exclusive 7-class taxonomy:
1. `PREDICTIVE_ELIGIBLE` (25 fields): Observable and fixed at or before $T_{dispatch}$; authorized candidate features.
2. `STAGE_CONDITIONAL` (4 fields): Raw inspection measurements (`check_datetime`, `firmness_kg_cm2`, `sugar_brix`, `defect_pct`) whose eligibility is conditioned strictly by `quality_checks.stage`. Rows with `stage in ('harvest', 'pre_dispatch')` are authorized; rows with `stage == 'arrival'` are strictly FORBIDDEN future data.
3. `CONDITIONALLY_ELIGIBLE` (16 fields): Available before dispatch but subject to operational assumptions (planned logistics) or physical room conditions (gas sensors in CA rooms, surface temp in ZONE-006, equipment states).
4. `CONTEXT_ONLY` (10 fields): Required for identity, provenance, joins, or UI display; strictly prohibited from being used directly as model features.
5. `LABEL_OR_EVALUATION_ONLY` (4 fields): Historical outcomes in `historical_quality_outcomes.csv`; strictly forbidden from inference input; admitted only on the training/evaluation target side.
6. `FORBIDDEN_FUTURE` (5 fields): Post-dispatch transit realizations in `shipments.csv`; strictly forbidden from inference input.
7. `RAW_ONLY / NOT NEEDED IN CANONICAL INPUT` (9 fields): Surrogate keys (`reading_id`, `check_id`) and duplicate foreign keys used strictly for join/integrity verification during ingestion.

### 3. Authoritative Canonical Pseudo-Schema
A canonical `BatchAssessmentInput` must implement this structure:
- `identity`:
  - `batch_id: str` [CONTEXT_ONLY; source: `batches.batch_id`]
  - `storage_session_id: str` [CONTEXT_ONLY; source: `storage_sessions.storage_session_id`]
  - `facility_id: str` [CONTEXT_ONLY; source: `facilities.facility_id`]
  - `zone_id: str` [CONTEXT_ONLY; source: `storage_zones.zone_id`]
- `assessment_context`:
  - `assessment_timestamp: datetime` [CONTEXT_ONLY; single anchor clock; source: `storage_sessions.dispatch_datetime`]
- `batch`:
  - `crop_type: str` [PREDICTIVE_ELIGIBLE; source: `batches.crop_type`]
  - `variety: str` [PREDICTIVE_ELIGIBLE; source: `batches.variety`]
  - `origin_region: str` [PREDICTIVE_ELIGIBLE; source: `batches.origin_region`]
  - `harvest_datetime: datetime` [PREDICTIVE_ELIGIBLE; source: `batches.harvest_datetime`]
  - `harvest_weight_kg: float` [PREDICTIVE_ELIGIBLE; source: `batches.harvest_weight_kg`]
  - `initial_quality_score: float` [PREDICTIVE_ELIGIBLE; source: `batches.initial_quality_score`]
  - `harvest_temperature_c: float` [PREDICTIVE_ELIGIBLE; source: `batches.harvest_temperature_c`]
  - `harvest_conditions: str` [PREDICTIVE_ELIGIBLE; source: `batches.harvest_conditions`]
  - `field_precooled: bool` [PREDICTIVE_ELIGIBLE; source: `batches.field_precooled`]
- `storage`:
  - `entry_datetime: datetime` [PREDICTIVE_ELIGIBLE; source: `storage_sessions.entry_datetime`]
  - `planned_dispatch_datetime: datetime?` [CONDITIONALLY_ELIGIBLE; source: `storage_sessions.planned_dispatch_datetime`]
  - `bin_stack_tier: int` [PREDICTIVE_ELIGIBLE; source: `storage_sessions.bin_stack_tier`]
  - `storage_duration_days: int` [PREDICTIVE_ELIGIBLE; source: `storage_sessions.storage_duration_days`]
  *(dispatch_datetime is an alias to assessment_context.assessment_timestamp)*
- `facility`:
  - `facility_name: str?` [CONTEXT_ONLY; source: `facilities.facility_name`]
  - `region: str` [PREDICTIVE_ELIGIBLE; source: `facilities.region`]
  - `district: str` [PREDICTIVE_ELIGIBLE; source: `facilities.district`; note 1:1 facility proxy risk]
  - `facility_type: str` [PREDICTIVE_ELIGIBLE; source: `facilities.facility_type`]
  - `capacity_tonnes: int` [PREDICTIVE_ELIGIBLE; source: `facilities.capacity_tonnes`]
  - `commissioned_year: int` [PREDICTIVE_ELIGIBLE; source: `facilities.commissioned_year`]
  - `has_controlled_atmosphere: bool` [PREDICTIVE_ELIGIBLE; source: `facilities.has_controlled_atmosphere`]
- `zone`:
  - `zone_name: str?` [CONTEXT_ONLY; source: `storage_zones.zone_name`]
  - `zone_type: str` [PREDICTIVE_ELIGIBLE; source: `storage_zones.zone_type`]
  - `nominal_capacity_tonnes: int` [PREDICTIVE_ELIGIBLE; source: `storage_zones.nominal_capacity_tonnes`]
  - `target_temperature_c: float` [PREDICTIVE_ELIGIBLE; source: `storage_zones.target_temperature_c`]
  - `target_relative_humidity_pct: float` [PREDICTIVE_ELIGIBLE; source: `storage_zones.target_relative_humidity_pct`]
  - `cooling_system_type: str` [PREDICTIVE_ELIGIBLE; source: `storage_zones.cooling_system_type`]
  - `insulation_quality: str` [PREDICTIVE_ELIGIBLE; source: `storage_zones.insulation_quality`]
  - `defrost_cycle_frequency_per_day: int` [PREDICTIVE_ELIGIBLE; source: `storage_zones.defrost_cycle_frequency_per_day`]
- `quality`:
  - `harvest: StageQualityCheck` [STAGE_CONDITIONAL; source: `quality_checks` where `stage='harvest'`]
    - `check_datetime: datetime`
    - `firmness_kg_cm2: float`
    - `sugar_brix: float`
    - `defect_pct: float`
  - `pre_dispatch: StageQualityCheck` [STAGE_CONDITIONAL; source: `quality_checks` where `stage='pre_dispatch'`]
    - `check_datetime: datetime`
    - `firmness_kg_cm2: float`
    - `sugar_brix: float`
    - `defect_pct: float`
- `telemetry`:
  - `zone_id: str` [CONTEXT_ONLY; structural alias to `identity.zone_id`]
  - `window_start: datetime` [CONTEXT_ONLY; derived bound = `storage.entry_datetime`]
  - `window_end: datetime` [CONTEXT_ONLY; derived bound = `assessment_context.assessment_timestamp`]
  - `readings: list[TelemetryReading]` [CONDITIONALLY_ELIGIBLE; bounded strictly by `entry_datetime <= timestamp <= dispatch_datetime`]:
    - `timestamp: datetime` [CONTEXT_ONLY; time index]
    - `air_temperature_c: float` [CONDITIONALLY_ELIGIBLE]
    - `produce_surface_temperature_c: float?` [CONDITIONALLY_ELIGIBLE; 100% null in ZONE-006]
    - `relative_humidity_pct: float` [CONDITIONALLY_ELIGIBLE]
    - `dew_point_c: float` [CONDITIONALLY_ELIGIBLE]
    - `condensation_flag: bool` [CONDITIONALLY_ELIGIBLE; source flag with compound trigger]
    - `co2_ppm: float?` [CONDITIONALLY_ELIGIBLE; 100% null in non-CA rooms]
    - `o2_pct: float?` [CONDITIONALLY_ELIGIBLE; 100% null in non-CA rooms]
    - `cooling_on: bool` [CONDITIONALLY_ELIGIBLE]
    - `defrost_on: bool` [CONDITIONALLY_ELIGIBLE]
- `planned_logistics: PlannedLogisticsContext?` [CONDITIONALLY_ELIGIBLE / RECOMMENDATION: OPTIONAL]:
  - `shipment_id: str?` [CONTEXT_ONLY; source: `shipments.shipment_id`]
  - `destination_market: str` [CONDITIONALLY_ELIGIBLE; source: `shipments.destination_market`]
  - `destination_region: str` [CONDITIONALLY_ELIGIBLE; source: `shipments.destination_region`]
  - `vehicle_type: str` [CONDITIONALLY_ELIGIBLE; source: `shipments.vehicle_type`]
  - `planned_departure_datetime: datetime` [CONDITIONALLY_ELIGIBLE; source: `shipments.planned_departure_datetime`]
  - `planned_arrival_datetime: datetime` [CONDITIONALLY_ELIGIBLE; source: `shipments.planned_arrival_datetime`]
  - `planned_duration_hours: float` [CONDITIONALLY_ELIGIBLE; source: `shipments.planned_duration_hours`]

### 4. Normative Raw-to-Canonical Field Mapping Matrix (73 Fields)

| # | Source Table | Raw Field | Eligibility Class | Authoritative Canonical Destination / Action | Temporal / Predicate Rule | Nullability / Missingness Rule |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `facilities` | `facility_id` | `CONTEXT_ONLY` | `identity.facility_id` | Static site metadata | Required; non-null string |
| 2 | `facilities` | `facility_name` | `CONTEXT_ONLY` | `facility.facility_name` | Static site metadata | Optional; non-null string |
| 3 | `facilities` | `region` | `PREDICTIVE_ELIGIBLE` | `facility.region` | Static site metadata | Required; non-null string |
| 4 | `facilities` | `district` | `PREDICTIVE_ELIGIBLE` | `facility.district` | Static site metadata; note 1:1 facility proxy | Required; non-null string |
| 5 | `facilities` | `facility_type` | `PREDICTIVE_ELIGIBLE` | `facility.facility_type` | Static site metadata | Required; non-null string |
| 6 | `facilities` | `capacity_tonnes` | `PREDICTIVE_ELIGIBLE` | `facility.capacity_tonnes` | Static site metadata | Required; integer |
| 7 | `facilities` | `commissioned_year` | `PREDICTIVE_ELIGIBLE` | `facility.commissioned_year` | Static site metadata | Required; integer year |
| 8 | `facilities` | `has_controlled_atmosphere` | `PREDICTIVE_ELIGIBLE` | `facility.has_controlled_atmosphere` | Static site metadata | Required; boolean |
| 9 | `storage_zones` | `zone_id` | `CONTEXT_ONLY` | `identity.zone_id` | Static room metadata | Required; non-null string |
| 10 | `storage_zones` | `facility_id` | `RAW_ONLY / NOT NEEDED` | None (Join verification with `facilities.facility_id`) | Static room metadata | Ingestion join check only |
| 11 | `storage_zones` | `zone_name` | `CONTEXT_ONLY` | `zone.zone_name` | Static room metadata | Optional; non-null string |
| 12 | `storage_zones` | `zone_type` | `PREDICTIVE_ELIGIBLE` | `zone.zone_type` | Static room metadata | Required; non-null string |
| 13 | `storage_zones` | `nominal_capacity_tonnes` | `PREDICTIVE_ELIGIBLE` | `zone.nominal_capacity_tonnes` | Static room metadata | Required; integer |
| 14 | `storage_zones` | `target_temperature_c` | `PREDICTIVE_ELIGIBLE` | `zone.target_temperature_c` | Static room metadata | Required; float |
| 15 | `storage_zones` | `target_relative_humidity_pct` | `PREDICTIVE_ELIGIBLE` | `zone.target_relative_humidity_pct` | Static room metadata | Required; float |
| 16 | `storage_zones` | `cooling_system_type` | `PREDICTIVE_ELIGIBLE` | `zone.cooling_system_type` | Static room metadata | Required; non-null string |
| 17 | `storage_zones` | `insulation_quality` | `PREDICTIVE_ELIGIBLE` | `zone.insulation_quality` | Static room metadata | Required; non-null string |
| 18 | `storage_zones` | `defrost_cycle_frequency_per_day` | `PREDICTIVE_ELIGIBLE` | `zone.defrost_cycle_frequency_per_day` | Static room metadata | Required; integer |
| 19 | `batches` | `batch_id` | `CONTEXT_ONLY` | `identity.batch_id` | Intake milestone; authoritative ID | Required; non-null string |
| 20 | `batches` | `crop_type` | `PREDICTIVE_ELIGIBLE` | `batch.crop_type` | Fixed at harvest | Required; non-null string |
| 21 | `batches` | `variety` | `PREDICTIVE_ELIGIBLE` | `batch.variety` | Fixed at harvest | Required; non-null string |
| 22 | `batches` | `origin_region` | `PREDICTIVE_ELIGIBLE` | `batch.origin_region` | Fixed at harvest | Required; non-null string |
| 23 | `batches` | `harvest_datetime` | `PREDICTIVE_ELIGIBLE` | `batch.harvest_datetime` | $T_{harvest} < T_{entry} < T_{dispatch}$ | Required; datetime |
| 24 | `batches` | `harvest_weight_kg` | `PREDICTIVE_ELIGIBLE` | `batch.harvest_weight_kg` | Measured at intake | Required; float |
| 25 | `batches` | `initial_quality_score` | `PREDICTIVE_ELIGIBLE` | `batch.initial_quality_score` | Evaluated at harvest intake | Required; float |
| 26 | `batches` | `harvest_temperature_c` | `PREDICTIVE_ELIGIBLE` | `batch.harvest_temperature_c` | Measured at harvest | Required; float |
| 27 | `batches` | `harvest_conditions` | `PREDICTIVE_ELIGIBLE` | `batch.harvest_conditions` | Recorded at harvest | Required; non-null string |
| 28 | `batches` | `field_precooled` | `PREDICTIVE_ELIGIBLE` | `batch.field_precooled` | Applied prior to storage | Required; boolean |
| 29 | `storage_sessions` | `storage_session_id` | `CONTEXT_ONLY` | `identity.storage_session_id` | Entry milestone | Required; non-null string |
| 30 | `storage_sessions` | `batch_id` | `RAW_ONLY / NOT NEEDED` | None (Join verification with `batches.batch_id`) | Entry milestone | Ingestion join check only |
| 31 | `storage_sessions` | `zone_id` | `RAW_ONLY / NOT NEEDED` | None (Join verification with `storage_zones.zone_id`) | Entry milestone | Ingestion join check only |
| 32 | `storage_sessions` | `entry_datetime` | `PREDICTIVE_ELIGIBLE` | `storage.entry_datetime` | $T_{entry} < T_{dispatch}$ | Required; datetime |
| 33 | `storage_sessions` | `dispatch_datetime` | `CONTEXT_ONLY` | `assessment_context.assessment_timestamp` | Defines $T_{assess} \equiv T_{dispatch}$; single clock | Required; datetime |
| 34 | `storage_sessions` | `planned_dispatch_datetime` | `CONDITIONALLY_ELIGIBLE` | `storage.planned_dispatch_datetime` | Available in snapshot; conditional on intake target immutability | Optional; nullable datetime |
| 35 | `storage_sessions` | `bin_stack_tier` | `PREDICTIVE_ELIGIBLE` | `storage.bin_stack_tier` | Assigned at chamber loading | Required; integer |
| 36 | `storage_sessions` | `storage_duration_days` | `PREDICTIVE_ELIGIBLE` | `storage.storage_duration_days` | Known at dispatch ($T_{dispatch} - T_{entry}$) | Required; integer |
| 37 | `sensor_readings` | `reading_id` | `RAW_ONLY / NOT NEEDED` | None (Surrogate key) | Generated by logger | Ingestion artifact only |
| 38 | `sensor_readings` | `zone_id` | `RAW_ONLY / NOT NEEDED` | None (Join verification against session: `sensor_readings.zone_id == storage_sessions.zone_id`; parent-zone verified via `storage_sessions.zone_id -> storage_zones.zone_id`) | Must match `storage_sessions.zone_id` for active batch stay interval | Ingestion join check only |
| 39 | `sensor_readings` | `timestamp` | `CONTEXT_ONLY` | `telemetry.readings[].timestamp` | Strictly $T_{entry} \le t \le T_{dispatch}$ | Required in reading; datetime |
| 40 | `sensor_readings` | `air_temperature_c` | `CONDITIONALLY_ELIGIBLE` | `telemetry.readings[].air_temperature_c` | Strictly $T_{entry} \le t \le T_{dispatch}$ | Required in reading; float |
| 41 | `sensor_readings` | `produce_surface_temperature_c` | `CONDITIONALLY_ELIGIBLE` | `telemetry.readings[].produce_surface_temperature_c` | Strictly $T_{entry} \le t \le T_{dispatch}$ | Nullable float (100% null in ZONE-006) |
| 42 | `sensor_readings` | `relative_humidity_pct` | `CONDITIONALLY_ELIGIBLE` | `telemetry.readings[].relative_humidity_pct` | Strictly $T_{entry} \le t \le T_{dispatch}$ | Required in reading; float |
| 43 | `sensor_readings` | `dew_point_c` | `CONDITIONALLY_ELIGIBLE` | `telemetry.readings[].dew_point_c` | Strictly $T_{entry} \le t \le T_{dispatch}$ | Required in reading; float |
| 44 | `sensor_readings` | `condensation_flag` | `CONDITIONALLY_ELIGIBLE` | `telemetry.readings[].condensation_flag` | Strictly $T_{entry} \le t \le T_{dispatch}$ | Required in reading; boolean |
| 45 | `sensor_readings` | `co2_ppm` | `CONDITIONALLY_ELIGIBLE` | `telemetry.readings[].co2_ppm` | Strictly $T_{entry} \le t \le T_{dispatch}$ | Nullable float (100% null in non-CA) |
| 46 | `sensor_readings` | `o2_pct` | `CONDITIONALLY_ELIGIBLE` | `telemetry.readings[].o2_pct` | Strictly $T_{entry} \le t \le T_{dispatch}$ | Nullable float (100% null in non-CA) |
| 47 | `sensor_readings` | `cooling_on` | `CONDITIONALLY_ELIGIBLE` | `telemetry.readings[].cooling_on` | Strictly $T_{entry} \le t \le T_{dispatch}$ | Required in reading; boolean |
| 48 | `sensor_readings` | `defrost_on` | `CONDITIONALLY_ELIGIBLE` | `telemetry.readings[].defrost_on` | Strictly $T_{entry} \le t \le T_{dispatch}$ | Required in reading; boolean |
| 49 | `quality_checks` | `check_id` | `RAW_ONLY / NOT NEEDED` | None (Surrogate key) | Assigned at inspection | Ingestion artifact only |
| 50 | `quality_checks` | `batch_id` | `RAW_ONLY / NOT NEEDED` | None (Join verification with `batches.batch_id`) | Known at inspection | Ingestion join check only |
| 51 | `quality_checks` | `check_datetime` | `STAGE_CONDITIONAL` | `quality[stage].check_datetime` | H/PD: eligible; Arrival: FORBIDDEN | Required in stage check; datetime |
| 52 | `quality_checks` | `stage` | `CONTEXT_ONLY` | `quality[stage]` (Structural key) | Stage discriminator | Ingestion filter: H and PD only |
| 53 | `quality_checks` | `firmness_kg_cm2` | `STAGE_CONDITIONAL` | `quality[stage].firmness_kg_cm2` | H/PD: eligible; Arrival: FORBIDDEN | Required in stage check; float |
| 54 | `quality_checks` | `sugar_brix` | `STAGE_CONDITIONAL` | `quality[stage].sugar_brix` | H/PD: eligible; Arrival: FORBIDDEN | Required in stage check; float |
| 55 | `quality_checks` | `defect_pct` | `STAGE_CONDITIONAL` | `quality[stage].defect_pct` | H/PD: eligible; Arrival: FORBIDDEN | Required in stage check; float |
| 56 | `shipments` | `shipment_id` | `CONTEXT_ONLY` | `planned_logistics.shipment_id` | Assigned at booking | Optional; nullable string |
| 57 | `shipments` | `batch_id` | `RAW_ONLY / NOT NEEDED` | None (Join verification with `batches.batch_id`) | Known at booking | Ingestion join check only |
| 58 | `shipments` | `destination_market` | `CONDITIONALLY_ELIGIBLE` | `planned_logistics.destination_market` | Known at dispatch per sponsor; conditional on destination/booking fixed before release | Required in logistics; non-null string |
| 59 | `shipments` | `destination_region` | `CONDITIONALLY_ELIGIBLE` | `planned_logistics.destination_region` | Known at dispatch per sponsor; conditional on destination/booking fixed before release | Required in logistics; non-null string |
| 60 | `shipments` | `vehicle_type` | `CONDITIONALLY_ELIGIBLE` | `planned_logistics.vehicle_type` | Known at dispatch per sponsor; conditional on vehicle assignment fixed before dispatch | Required in logistics; non-null string |
| 61 | `shipments` | `planned_departure_datetime` | `CONDITIONALLY_ELIGIBLE` | `planned_logistics.planned_departure_datetime` | Known/planned at dispatch per sponsor; operational stability remains conditional | Required in logistics; datetime |
| 62 | `shipments` | `planned_arrival_datetime` | `CONDITIONALLY_ELIGIBLE` | `planned_logistics.planned_arrival_datetime` | Known/planned at dispatch per sponsor; operational stability remains conditional | Required in logistics; datetime |
| 63 | `shipments` | `planned_duration_hours` | `CONDITIONALLY_ELIGIBLE` | `planned_logistics.planned_duration_hours` | Known/planned at dispatch per sponsor; operational stability remains conditional | Required in logistics; float |
| 64 | `shipments` | `actual_departure_datetime` | `FORBIDDEN_FUTURE` | None (Excluded from inference) | Realized post-dispatch | FORBIDDEN from canonical input |
| 65 | `shipments` | `actual_arrival_datetime` | `FORBIDDEN_FUTURE` | None (Excluded from inference) | Realized post-dispatch | FORBIDDEN from canonical input |
| 66 | `shipments` | `actual_delay_minutes` | `FORBIDDEN_FUTURE` | None (Excluded from inference) | Realized upon delivery | FORBIDDEN from canonical input |
| 67 | `shipments` | `cold_chain_incident` | `FORBIDDEN_FUTURE` | None (Excluded from inference) | Realized in transit | FORBIDDEN from canonical input |
| 68 | `shipments` | `transit_temp_mean_c` | `FORBIDDEN_FUTURE` | None (Excluded from inference) | Realized in transit | FORBIDDEN from canonical input |
| 69 | `historical_quality_outcomes` | `batch_id` | `RAW_ONLY / NOT NEEDED` | None (Join verification with `batches.batch_id`) | Evaluated post-arrival | Evaluation join key only |
| 70 | `historical_quality_outcomes` | `quality_status` | `LABEL_OR_EVALUATION_ONLY` | None (Evaluation target only) | Evaluated at destination | FORBIDDEN from inference input |
| 71 | `historical_quality_outcomes` | `loss_fraction_pct` | `LABEL_OR_EVALUATION_ONLY` | None (Evaluation target only) | Evaluated at destination | FORBIDDEN from inference input |
| 72 | `historical_quality_outcomes` | `quality_score` | `LABEL_OR_EVALUATION_ONLY` | None (Evaluation target only) | Evaluated at destination | FORBIDDEN from inference input |
| 73 | `historical_quality_outcomes` | `economic_loss_eur` | `LABEL_OR_EVALUATION_ONLY` | None (Evaluation target only) | Calculated post-delivery | FORBIDDEN from inference input |

### 5. Telemetry Join and Bounding Rules
- Telemetry joins strictly via `sensor_readings.zone_id == storage_sessions.zone_id`.
- Lower bound: `timestamp >= storage_sessions.entry_datetime`. Out-of-stay readings are excluded.
- Upper bound: `timestamp <= storage_sessions.dispatch_datetime`. Post-dispatch readings are strictly forbidden.
- Telemetry is represented as raw typed eligible readings. Feature engineering (rolling windows, degree hours, aggregation) is explicitly deferred to downstream analytics tasks.

### 6. Explicit Missingness Representation
- Missing sensor channels (surface temp in ZONE-006, CO2/O2 in non-CA rooms) are represented explicitly as `None` / `null`.
- Zero-fabrication is strictly prohibited: `None` must not be replaced with `0.0`, `-1.0`, or synthetic averages during ingestion.

### 7. Negative Contract
The following data must NEVER enter `BatchAssessmentInput`:
- Destination arrival quality checks (`quality_checks` where `stage = 'arrival'`).
- Post-dispatch transit realizations (`actual_departure_datetime`, `actual_arrival_datetime`, `actual_delay_minutes`, `cold_chain_incident`, `transit_temp_mean_c`).
- Historical commercial outcomes (`historical_quality_outcomes.*`).
- Telemetry logged after dispatch (`timestamp > dispatch_datetime`).

## Consequences
- Backend task IGR-03 can construct typed Pydantic models in `backend/app/domain/batch.py` and CSV mappers in `backend/app/ingestion/` without inventing semantics or risking temporal leakage.
- VLD-02A does not unblock target selection, deterioration semantics, evaluation split selection, feature-engineering policy, baseline selection, or learned-model work. Those areas remain unresolved and may proceed only through their own evidence-backed contracts and decision gates (VDR-03, VDR-04, and subsequent bounded tasks as applicable).
