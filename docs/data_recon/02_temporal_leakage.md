# VDR-02 Temporal Semantics and Leakage Audit

**Owner:** Viktor — Data & Evaluation Owner
**Repository:** `Slave-of-Skynet/training_agrifood`
**Task Type:** Corrective Pass on VDR-02 (Post-RCA Targeted Repair)
**Base Commit:** `20021656028392a420561c6dc2a0f5434835081f`
**Target Document:** `docs/data_recon/02_temporal_leakage.md`
**Evaluation Cutoff Boundary:** $T_{assess} \equiv T_{dispatch} = \text{storage_sessions.dispatch_datetime}$

---

## Executive summary

This audit establishes the formal temporal prediction contract and information-leakage boundary for the Agrifood Cold-Chain prediction system. Production decision-support models operate at the moment a produce batch concludes its cold-storage stay and is released for transport ($T_{dispatch}$). At this inference horizon, downstream transit events, transit telemetry, and receiving inspections do not yet exist. Including future features in training generates anachronistic data leakage and produces artificially optimistic offline evaluations.

```
+---------------------------------------------------------------------------------------------------------+
|                                    TEMPORAL INFORMATION BOUNDARY                                        |
|                                                                                                         |
|   PRE-DISPATCH STORAGE PHASE (AVAILABLE / PAST)             POST-DISPATCH TRANSIT PHASE (LEAKAGE / FUTURE)
|                                                                                                         |
|   Harvest -> Inbound QC -> Cold Chamber -> Pre-Dispatch QC |-> Planned Dep -> Actual Dep -> Transit -> Arrival
|                                                            |                                            |
|                                                            |-> T_assess = storage_sessions.dispatch_datetime
+---------------------------------------------------------------------------------------------------------+
```

### Key Audit Findings
1. **Lifecycle Sequence Monotonicity `[FACT]`**: Across all 1,800 batches in `sponsor_pack/data/`, events follow an ordered physical actual-event sequence with **0 sequence violations**:
     $$\mathbf{T_{harvest} < T_{harvest\_qc} < T_{entry} < T_{pre\_dispatch\_qc} < T_{dispatch} \le T_{actual\_departure} < T_{actual\_arrival} = T_{arrival\_qc}}$$
     Administrative schedule milestones (`planned_dispatch`, `planned_departure`, `planned_arrival`) represent operational planning targets and are treated separately from this physical monotonic event progression.
2. **Pre-Dispatch Telemetry Coverage & 2026 Truncation `[FACT]`**:
   - For **1,596 batches** (88.67%), sensor telemetry is continuously available up to dispatch; maximum telemetry staleness at dispatch is **29.4 minutes** (mean **14.5 minutes**), ensuring 100% coverage within the standard 30-minute logging cadence.
   - For **204 batches** (11.33%), telemetry logging terminates globally on `2025-12-31 23:30:00`, while dispatch occurs between 2026-01-01 and 2026-04-03. Pre-dispatch staleness ranges from **0.56 to 92.54 days** (mean **29.01 days**, median **24.40 days**).
   - The 204 truncated batches consist of: **189 apples (92.65%)**, **14 pears (6.86%)**, and **1 table grapes (0.49%)**.
3. **Severe Post-Dispatch Target Contamination `[FACT]`**:
   - Downstream transit features in `shipments.csv` strongly leak post-dispatch shocks. Specifically, `cold_chain_incident` has a Pearson correlation of **$r = +0.7961$** with `loss_fraction_pct`, and `transit_temp_mean_c` has **$r = +0.6727$**.
4. **Spatio-Temporal Concurrency & Environmental Leakage `[FACT]`**:
   - 1,734 out of 1,800 batches (96.33%) share storage chambers concurrently with other batches (37,861 pairwise overlapping stays forming 157 disjoint chamber-time clusters across 25 zones).
   - In standard randomized 80/20 train/test splits, an average of **95.79% of test batches** share an identical chamber microclimate cluster with training batches.
5. **Split Reconnaissance Trade-Offs `[FACT]` / `[RECOMMENDATION]`**:
   - A naive chronological 70/30 dispatch split causes catastrophic seasonal crop shift: summer crops (`strawberries`, `raspberries`, `apricots`, `tomatoes`) drop to **0.0% in test**, while `apples` inflate from 27.1% to 61.3%.
   - The dataset contains two distinct annual production cycles (**Season 2024**: 900 batches; **Season 2025**: 900 batches) separated by a **43.97-day hiatus** with **0 cross-season chamber overlaps**.

---

## Scope and sources

This audit evaluated all 8 raw sponsor tables committed in `sponsor_pack/data/`:
- `batches.csv` (1,800 rows, 10 columns)
- `storage_sessions.csv` (1,800 rows, 8 columns)
- `shipments.csv` (1,800 rows, 13 columns)
- `historical_quality_outcomes.csv` (1,800 rows, 5 columns)
- `sensor_readings.csv` (669,665 rows, 12 columns)
- `quality_checks.csv` (5,400 rows, 7 columns)
- `storage_zones.csv` (25 rows, 10 columns)
- `facilities.csv` (10 rows, 8 columns)

All field names, categories, crop counts, and numerical metrics in this document are programmatically verified against `sponsor_pack/data/` without ungrounded generative recall.

---

## Prediction-time contract

### T_assess = T_dispatch
The assessment boundary is formally defined as:
$$\mathbf{T_{assess} \equiv T_{dispatch} = \text{storage_sessions.dispatch_datetime}}$$
This timestamp marks the completion of the cold-storage warehousing phase and packaging release, immediately following `pre_dispatch` quality inspection and prior to road carrier loading.

### Known at dispatch
Information physically observable or contractually fixed at or prior to $T_{dispatch}$:
- Batch intake attributes recorded at harvest (`crop_type`, `variety`, `origin_region`, `harvest_datetime`, `harvest_weight_kg`, `initial_quality_score`, `harvest_temperature_c`, `harvest_conditions`, `field_precooled`).
- Static storage zone and facility infrastructure (`zone_type`, `nominal_capacity_tonnes`, `target_temperature_c`, `target_relative_humidity_pct`, `cooling_system_type`, `insulation_quality`, `defrost_cycle_frequency_per_day`, `facility_type`, `capacity_tonnes`, `commissioned_year`, `has_controlled_atmosphere`).
- Session warehouse parameters (`storage_session_id`, `zone_id`, `entry_datetime`, `dispatch_datetime`, `bin_stack_tier`, `storage_duration_days`).
- Quality check measurements from stages `harvest` (at intake) and `pre_dispatch` (completed 2.00h prior to dispatch).
- In-chamber sensor time-series bounded strictly by $\text{entry_datetime} \le \text{timestamp} \le \text{dispatch_datetime}$.
- Pre-scheduled logistics targets (`destination_market`, `destination_region`, `vehicle_type`, `planned_departure_datetime`, `planned_arrival_datetime`, `planned_duration_hours`, `planned_dispatch_datetime`).

### Future / forbidden information
Information realized strictly post-$T_{dispatch}$ ($t > T_{dispatch}$):
- Actual loading and transit timing (`actual_departure_datetime`, `actual_arrival_datetime`, `actual_delay_minutes`).
- In-transit vehicle telemetry and environmental shocks (`transit_temp_mean_c`, `cold_chain_incident`).
- Destination quality inspection scores (`quality_checks` with `stage='arrival'`).
- Post-arrival economic outcomes and loss records (`historical_quality_outcomes.*`).
- Sensor readings logged after dispatch ($	ext{timestamp} > 	ext{dispatch_datetime}$).

---

## Observed lifecycle

### Timestamp registry `[FACT]`
Across all sponsor tables, timestamps fall into two strictly separated categories: **Physical Actual-Event Milestones** and **Administrative Planning Targets**.

#### A. Physical Actual-Event Milestones
These 8 timestamps record physical lifecycle events in order of occurrence:

| Sequence | Table | Field Name | Stage / Operational Meaning | Event Nature |
|:---:|:---|:---|:---|:---:|
| 1 | `batches.csv` | `harvest_datetime` | Moment crop was picked in the field | Physical raw timestamp |
| 2 | `quality_checks.csv` | `check_datetime` (`stage='harvest'`) | Inbound facility intake quality inspection | Physical raw timestamp |
| 3 | `storage_sessions.csv` | `entry_datetime` | Chamber doors sealed; cold storage begins | Physical raw timestamp |
| 4 | `quality_checks.csv` | `check_datetime` (`stage='pre_dispatch'`) | Final pre-shipment quality inspection | Physical raw timestamp |
| 5 | `storage_sessions.csv` | `dispatch_datetime` | Cold storage ends; batch release ($T_{dispatch}$) | Physical raw timestamp |
| 6 | `shipments.csv` | `actual_departure_datetime` | Transport carrier departs loading dock | Physical raw timestamp |
| 7 | `shipments.csv` | `actual_arrival_datetime` | Transport carrier arrives at destination dock | Physical raw timestamp |
| 8 | `quality_checks.csv` | `check_datetime` (`stage='arrival'`) | Inbound receiving inspection at destination | Coincident event ($T_{arrival\_qc} = T_{actual\_arr}$) |

#### B. Administrative Schedule Targets
These 3 timestamps represent administrative planning schedules and must **NOT** be treated as part of the physical monotonic event sequence:
- `storage_sessions.csv.planned_dispatch_datetime`: Commercial target date for dispatch established at warehouse intake.
- `shipments.csv.planned_departure_datetime`: Scheduled carrier departure time booked with logistics transport.
- `shipments.csv.planned_arrival_datetime`: Scheduled customer/destination delivery appointment.

### Ordering and offsets `[FACT]`
Evaluated across all 1,800 batches via `test_timeline.py`:

| Milestone Delta | Min Offset | Median Offset | Mean Offset | Max Offset | Regularity / Observed Behavior |
|:---|:---:|:---:|:---:|:---:|:---|
| `harvest` $\rightarrow$ `harvest_qc` | +1.00 h | +1.00 h | +1.00 h | +1.00 h | **Deterministic**: Exactly 60 min for 100% of batches |
| `harvest_qc` $\rightarrow$ `entry_datetime` | +1.50 h | +3.78 h | +3.72 h | +6.00 h | Intake handling and pre-cooling latency |
| `harvest` $\rightarrow$ `entry_datetime` | +2.50 h | +4.78 h | +4.72 h | +7.00 h | Total harvest-to-storage intake time |
| `entry` $\rightarrow$ `pre_dispatch_qc` | +14.00 h | +1,294.00 h | +1,433.44 h | +4,198.00 h | Duration in storage before inspection |
| `pre_dispatch_qc` $\rightarrow$ `dispatch` | +2.00 h | +2.00 h | +2.00 h | +2.00 h | **Deterministic**: Exactly 120 min for 100% of batches |
| `entry` $\rightarrow$ `dispatch_datetime` | 3.00 d | 54.00 d | 59.81 d | 175.00 d | Total cold storage stay |
| `dispatch` $\rightarrow$ `planned_departure` | +1.00 h | +1.96 h | +1.99 h | +3.00 h | Administrative scheduled dock staging |
| `dispatch` $\rightarrow$ `actual_departure` | +1.00 h | +2.53 h | +2.58 h | +4.99 h | Physical pallet staging & vehicle loading |
| `planned_dep` $\rightarrow$ `actual_departure` | 0.00 min | +20.00 min | +35.47 min | +120.00 min | Loading delay |
| `planned_arr` $\rightarrow$ `actual_arrival` | 0.00 min | +20.00 min | +61.71 min | +835.00 min | Transit delay |
| `dispatch` $\rightarrow$ `actual_arrival` | +5.07 h | +17.85 h | +21.40 h | +50.51 h | Post-dispatch transit duration |
| `actual_arrival` $\rightarrow$ `arrival_qc` | 0.00 min | 0.00 min | 0.00 min | 0.00 min | **Deterministic**: Exact timestamp coincidence |

### Equal-time / anomalous cases `[FACT]`
1. `actual_arrival_datetime` vs `arrival_qc.check_datetime`: Exactly **1,800 out of 1,800 batches (100.0%)** have identical timestamps ($T_{arrival\_qc} = T_{actual\_arr}$). Receiving inspections are logged simultaneously upon arrival.
2. `storage_sessions.dispatch_datetime` vs `storage_sessions.planned_dispatch_datetime`:
   - Dispatched earlier than planned: **599 batches** (33.28%), delta: -1.00 to -0.01 days.
   - Dispatched later than planned: **308 batches** (17.11%), delta: +0.01 to +1.00 days.
   - Dispatched exactly on planned time: **893 batches** (49.61%).
3. `shipments.actual_departure_datetime` vs `shipments.planned_departure_datetime`:
   - Exact departure on schedule: **396 batches** (22.00%).
   - Delayed departure: **1,404 batches** (78.00%), delta: +1 to +120 minutes.
4. Total lifecycle ordering violations: **0 violations** across all 1,800 batches.

---

## Field-level availability matrix

Every raw and derived field across all 8 sponsor tables is classified below:

| Source | Actual Field | Raw / Derived | Available at $T_{dispatch}$? | Leakage Status | Safe Predictive Use? | Evidence / Timing Rule |
|:---|:---|:---:|:---:|:---:|:---:|:---|
| `batches.csv` | `batch_id` | Raw | YES | No leakage | Identifier only | Unique key assigned at intake |
| `batches.csv` | `crop_type` | Raw | YES | No leakage | Safe | Biological species known at harvest |
| `batches.csv` | `variety` | Raw | YES | No leakage | Safe | Cultivar name known at harvest |
| `batches.csv` | `origin_region` | Raw | YES | No leakage | Safe | Growing region known at harvest |
| `batches.csv` | `harvest_datetime` | Raw | YES | No leakage | Safe | Occurs before storage entry |
| `batches.csv` | `harvest_weight_kg` | Raw | YES | No leakage | Safe | Measured on facility scale at intake |
| `batches.csv` | `initial_quality_score` | Raw | YES | No leakage | Safe | Field intake index recorded at intake |
| `batches.csv` | `harvest_temperature_c` | Raw | YES | No leakage | Safe | Ambient temperature at harvest |
| `batches.csv` | `harvest_conditions` | Raw | YES | No leakage | Safe | Weather conditions at harvest |
| `batches.csv` | `field_precooled` | Raw | YES | No leakage | Safe | Pre-cooling status prior to chamber entry |
| `storage_sessions.csv` | `storage_session_id` | Raw | YES | No leakage | Identifier only | Session key assigned at entry |
| `storage_sessions.csv` | `batch_id` | Raw | YES | No leakage | Identifier only | Foreign key to batch |
| `storage_sessions.csv` | `zone_id` | Raw | YES | No leakage | Safe | Chamber assignment at entry |
| `storage_sessions.csv` | `entry_datetime` | Raw | YES | No leakage | Safe | Sealed chamber timestamp |
| `storage_sessions.csv` | `dispatch_datetime` | Raw | YES | No leakage | Safe | Boundary timestamp ($T_{dispatch}$) |
| `storage_sessions.csv` | `planned_dispatch_datetime` | Raw | YES | No leakage | CONDITIONAL | Safe if recorded at intake and immutable |
| `storage_sessions.csv` | `bin_stack_tier` | Raw | YES | No leakage | Safe | Physical rack tier in cold chamber |
| `storage_sessions.csv` | `storage_duration_days` | Derived | YES | No leakage | Safe | $\text{dispatch} - \text{entry}$ in days; known at dispatch |
| `storage_zones.csv` | `zone_id` | Raw | YES | No leakage | Identifier only | Room identifier |
| `storage_zones.csv` | `facility_id` | Raw | YES | No leakage | Identifier only | Facility foreign key |
| `storage_zones.csv` | `zone_name` | Raw | YES | No leakage | Not relevant | Human-readable room descriptor |
| `storage_zones.csv` | `zone_type` | Raw | YES | No leakage | Safe | Chamber technology (Standard vs CA) |
| `storage_zones.csv` | `nominal_capacity_tonnes`| Raw | YES | No leakage | Safe | Static physical capacity |
| `storage_zones.csv` | `target_temperature_c` | Raw | YES | No leakage | Safe | Prescribed room temperature setpoint |
| `storage_zones.csv` | `target_relative_humidity_pct`| Raw | YES | No leakage | Safe | Prescribed humidity setpoint |
| `storage_zones.csv` | `cooling_system_type` | Raw | YES | No leakage | Safe | Static refrigeration system architecture |
| `storage_zones.csv` | `insulation_quality` | Raw | YES | No leakage | Safe | Envelope insulation rating |
| `storage_zones.csv` | `defrost_cycle_frequency_per_day`| Raw | YES | No leakage | Safe | Automated daily defrost schedule |
| `facilities.csv` | `facility_id` | Raw | YES | No leakage | Identifier only | Facility identifier |
| `facilities.csv` | `facility_name` | Raw | YES | No leakage | Not relevant | Descriptive commercial name |
| `facilities.csv` | `region` | Raw | YES | No leakage | Safe | Geographic macro-region in Moldova |
| `facilities.csv` | `district` | Raw | YES | No leakage | Safe | Administrative district (Raion) |
| `facilities.csv` | `facility_type` | Raw | YES | No leakage | Safe | Operational type (Cold Store, Packinghouse, Hub) |
| `facilities.csv` | `capacity_tonnes` | Raw | YES | No leakage | Safe | Total nominal facility storage capacity |
| `facilities.csv` | `commissioned_year` | Raw | YES | No leakage | Safe | Construction / modernization year |
| `facilities.csv` | `has_controlled_atmosphere` | Raw | YES | No leakage | Safe | CA capability indicator |
| `quality_checks.csv` (`harvest`) | `check_id`, `batch_id` | Raw | YES | No leakage | Identifier only | Intake check identifier |
| `quality_checks.csv` (`harvest`) | `check_datetime` | Raw | YES | No leakage | Safe | Occurs 1.00h after harvest |
| `quality_checks.csv` (`harvest`) | `stage` | Raw | YES | No leakage | Safe | Intake inspection stage indicator |
| `quality_checks.csv` (`harvest`) | `firmness_kg_cm2` | Raw | YES | No leakage | Safe | Baseline firmness at harvest intake |
| `quality_checks.csv` (`harvest`) | `sugar_brix` | Raw | YES | No leakage | Safe | Baseline sugar content at harvest intake |
| `quality_checks.csv` (`harvest`) | `defect_pct` | Raw | YES | No leakage | Safe | Surface defect percentage at harvest intake |
| `quality_checks.csv` (`pre_dispatch`) | `check_id`, `batch_id` | Raw | YES | No leakage | Identifier only | Pre-dispatch check identifier |
| `quality_checks.csv` (`pre_dispatch`) | `check_datetime` | Raw | YES | No leakage | Safe | Occurs exactly 2.00h before dispatch |
| `quality_checks.csv` (`pre_dispatch`) | `stage` | Raw | YES | No leakage | Safe | Pre-dispatch stage indicator |
| `quality_checks.csv` (`pre_dispatch`) | `firmness_kg_cm2` | Raw | YES | No leakage | Safe | Pre-dispatch warehouse firmness |
| `quality_checks.csv` (`pre_dispatch`) | `sugar_brix` | Raw | YES | No leakage | Safe | Pre-dispatch warehouse brix |
| `quality_checks.csv` (`pre_dispatch`) | `defect_pct` | Raw | YES | No leakage | Safe | Pre-dispatch warehouse defect percentage |
| `quality_checks.csv` (`arrival`) | `*` (all columns) | Raw | NO | FUTURE LEAKAGE | FORBIDDEN | Occurs at receiving dock post-transit |
| `sensor_readings.csv` | `reading_id`, `zone_id` | Raw | CONDITIONAL | No leakage | Identifier only | Must match session zone |
| `sensor_readings.csv` | `timestamp` | Raw | CONDITIONAL | Boundary check | Safe | Must satisfy $\text{entry} \le t \le \text{dispatch}$ |
| `sensor_readings.csv` | `air_temperature_c` | Raw | CONDITIONAL | Boundary check | Safe | In-storage air temperature telemetry |
| `sensor_readings.csv` | `produce_surface_temperature_c`| Raw| CONDITIONAL | Boundary check | Safe | In-storage surface temp (NULL in ZONE-006) |
| `sensor_readings.csv` | `relative_humidity_pct` | Raw | CONDITIONAL | Boundary check | Safe | In-storage relative humidity |
| `sensor_readings.csv` | `dew_point_c` | Raw | CONDITIONAL | Boundary check | Safe | In-storage dew point |
| `sensor_readings.csv` | `condensation_flag` | Raw | CONDITIONAL | Boundary check | Safe | In-storage condensation detection |
| `sensor_readings.csv` | `co2_ppm` | Raw | CONDITIONAL | Boundary check | Safe | In-storage CO2 (NULL in non-CA rooms) |
| `sensor_readings.csv` | `o2_pct` | Raw | CONDITIONAL | Boundary check | Safe | In-storage O2 (NULL in non-CA rooms) |
| `sensor_readings.csv` | `cooling_on` | Raw | CONDITIONAL | Boundary check | Safe | Chiller solenoid operational state |
| `sensor_readings.csv` | `defrost_on` | Raw | CONDITIONAL | Boundary check | Safe | Evaporator defrost cycle state |
| `sensor_readings.csv` ($t > T_{dispatch}$) | `*` (all columns) | Raw | NO | FUTURE LEAKAGE | FORBIDDEN | Telemetry recorded after batch dispatch |
| `shipments.csv` | `shipment_id`, `batch_id` | Raw | YES | No leakage | Identifier only | Shipment key |
| `shipments.csv` | `destination_market` | Raw | CONDITIONAL | No leakage | Safe | Pre-booked destination city |
| `shipments.csv` | `destination_region` | Raw | CONDITIONAL | No leakage | Safe | Pre-booked destination region |
| `shipments.csv` | `vehicle_type` | Raw | CONDITIONAL | No leakage | Safe | Booked transport vehicle classification |
| `shipments.csv` | `planned_departure_datetime` | Raw | CONDITIONAL | No leakage | Safe | Scheduled carrier departure target |
| `shipments.csv` | `planned_arrival_datetime` | Raw | CONDITIONAL | No leakage | Safe | Scheduled carrier arrival target |
| `shipments.csv` | `planned_duration_hours` | Raw | CONDITIONAL | No leakage | Safe | Estimated road transit duration |
| `shipments.csv` | `actual_departure_datetime` | Raw | NO | FUTURE LEAKAGE | FORBIDDEN | Occurs 1.0h to 5.0h after dispatch |
| `shipments.csv` | `actual_arrival_datetime` | Raw | NO | FUTURE LEAKAGE | FORBIDDEN | Occurs 5.1h to 50.5h after dispatch |
| `shipments.csv` | `actual_delay_minutes` | Derived | NO | FUTURE LEAKAGE | FORBIDDEN | Delay realized after loading/transit |
| `shipments.csv` | `cold_chain_incident` | Raw | NO | FUTURE LEAKAGE | FORBIDDEN | Refrigeration failure in transit ($r = +0.7961$) |
| `shipments.csv` | `transit_temp_mean_c` | Raw | NO | FUTURE LEAKAGE | FORBIDDEN | In-transit vehicle data-logger ($r = +0.6727$) |
| `historical_quality_outcomes.csv` | `batch_id` | Raw | YES | No leakage | Identifier only | Foreign key to batch |
| `historical_quality_outcomes.csv` | `quality_status` | Raw | NO | TARGET LEAKAGE | FORBIDDEN | Candidate categorical outcome / target; final target deferred to VDR-03 |
| `historical_quality_outcomes.csv` | `loss_fraction_pct` | Raw | NO | TARGET LEAKAGE | FORBIDDEN | Candidate continuous outcome / target; final target deferred to VDR-03 |
| `historical_quality_outcomes.csv` | `quality_score` | Raw | NO | TARGET LEAKAGE | FORBIDDEN | Destination inspection score (inverse of loss) |
| `historical_quality_outcomes.csv` | `economic_loss_eur` | Derived | NO | TARGET LEAKAGE | FORBIDDEN | Downstream financial settlement outcome in Euros |

---

## Sensor cutoff audit

### Valid telemetry window
The telemetry join must enforce both upper and lower boundaries:
$$\text{storage_sessions.zone_id} == \text{sensor_readings.zone_id} \quad \land \quad \text{entry_datetime} \le \text{timestamp} \le \text{dispatch_datetime}$$

### Dispatch staleness `[FACT]`
Measuring the interval between the latest valid sensor reading ($t \le T_{dispatch}$) and $T_{dispatch}$:
- **Non-Truncated Batches ($N=1,596$, 88.67%)**:
  - Min staleness: **0.0 minutes**
  - Median staleness: **14.4 minutes**
  - Mean staleness: **14.5 minutes**
  - Max staleness: **29.4 minutes**
  - **100.00%** of non-truncated batches have telemetry within the 30-minute logging window.

### 2026 truncation `[FACT]`
- Sensor logging stops globally at `2025-12-31 23:30:00`.
- **204 batches (11.33%)** dispatch between `2026-01-01 13:38:24` and `2026-04-03 12:30:36`.
- Staleness range for truncated batches: **0.56 to 92.54 days** (median **24.40 days**, mean **29.01 days**).
- **Actual Crop Composition of the 204 Truncated Batches**:
  - `apples`: **189 batches** (92.65%)
  - `pears`: **14 batches** (6.86%)
  - `table_grapes`: **1 batch** (0.49%)
- *Implication `[INFERENCE]`*: Because telemetry is missing for up to 3 months preceding dispatch, naive aggregation (e.g. mean storage temperature) computes early-stage conditions rather than pre-dispatch conditions.

### Unsafe future-reading join risk `[FACT]`
If an engineer joins sensor readings on `zone_id` and `entry_datetime <= timestamp` without checking `timestamp <= dispatch_datetime`:
- **Contaminated Batches**: **1,596 out of 1,800 batches (88.67%)** ingest future readings recorded after batch dispatch.
- **Future Readings per Batch Statistics (Denominator Clarification)**:
  - Across **all 1,800 batches**: min = **0**, max = **28,043**, mean = **11,518.7 readings** (the 204 batches dispatched in 2026 have 0 future readings due to telemetry cessation on 2025-12-31).
  - Across the **1,596 contaminated batches**: min = **7**, max = **28,043**, median = **16,446**, mean = **12,991.0 readings**.
- This creates massive backward leakage of subsequent batch refrigeration cycles into earlier batches.

---

## Derived-feature leakage

Features derived across the $T_{dispatch}$ boundary introduce silent contamination:
1. `storage_sessions.storage_duration_days` `[FACT]`: Derived as $(\text{dispatch_datetime} - \text{entry_datetime})$ in integer days. This is available at dispatch time and has Pearson correlation $r = -0.1924$ with loss fraction.
2. `shipments.actual_delay_minutes` `[FACT]`: Derived as $(\text{actual_departure_datetime} - \text{planned_departure_datetime})$. This is realized after dock staging ($t > T_{dispatch}$) and constitutes future leakage.
3. `historical_quality_outcomes.economic_loss_eur` `[FACT]`: Derived from `loss_fraction_pct` and batch commercial value. This is a downstream monetary outcome and strictly forbidden.

---

## Shared-environment leakage

### Chamber overlap `[FACT]`
Commercial cold stores operate multi-batch occupancy:
- **1,734 out of 1,800 batches (96.33%)** concurrently share a room with at least one other batch.
- Only **66 batches (3.67%)** occupy a chamber in isolation.
- Total pairwise overlapping stays in the dataset: **37,861 pairs**.

### Chamber-time clusters `[FACT]`
By computing connected components on concurrent batch stays within each storage zone:
- Across the 25 storage zones, concurrent stays form **157 disjoint chamber-time clusters**.
- 66 clusters are single isolated batches.
- 91 clusters are multi-batch components containing up to **134 batches** (mean: 11.46 batches, mean duration: 60.4 days).
- 48 clusters (30.6%) contain multiple distinct crop types residing in the same chamber.

### Random split contamination risk `[FACT]` / `[INFERENCE]`
- **FACT**: In 100 iterations of random 80/20 train/test splits, a mean of **95.79% of test batches** (range: 93.33% to 97.78%) belong to a chamber-time cluster present in the training set.
- **INFERENCE**: Batches in the same cluster share identical refrigeration cycling, evaporator defrost spikes, and door-opening thermal disturbances. In a random split, the model risks memorizing specific room-level microclimate trajectories rather than learning generalizable degradation functions.

---

## Target / post-dispatch contamination paths

Evaluating correlations of candidate predictors with `loss_fraction_pct` and `quality_score`:

| Feature Name | Source Table | Availability at $T_{dispatch}$ | Pearson $r$ with `loss_fraction_pct` | Pearson $r$ with `quality_score` | Causal / Operational Status |
|:---|:---|:---:|:---:|:---:|:---|
| `cold_chain_incident` | `shipments.csv` | NO (Post-dispatch) | **+0.7961** | **-0.7753** | **Direct Shock Leakage**: In-transit refrigeration failure |
| `transit_temp_mean_c` | `shipments.csv` | NO (Post-dispatch) | **+0.6727** | **-0.6674** | **Direct Measurement Leakage**: In-transit reefer data logger |
| `harvest_weight_kg` | `batches.csv` | YES (Pre-dispatch) | -0.2225 | +0.2330 | Legitimate pre-dispatch predictor |
| `harvest_temperature_c`| `batches.csv` | YES (Pre-dispatch) | +0.2053 | -0.2060 | Legitimate pre-dispatch predictor |
| `storage_duration_days`| `storage_sessions.csv`| YES (Pre-dispatch)| -0.1924 | +0.1818 | Legitimate pre-dispatch predictor |
| `planned_duration_hours`| `shipments.csv` | CONDITIONAL | -0.1828 | +0.1933 | Legitimate if scheduled prior to dispatch |
| `actual_delay_minutes` | `shipments.csv` | NO (Post-dispatch) | +0.0794 | -0.0868 | Post-dispatch departure/transit delay |
| `pre_dispatch` brix | `quality_checks.csv` | YES (Pre-dispatch) | +0.0604 | -0.0724 | Legitimate pre-dispatch inspection |
| `field_precooled` | `batches.csv` | YES (Pre-dispatch) | -0.0350 | +0.0420 | Legitimate pre-dispatch intake status |
| `bin_stack_tier` | `storage_sessions.csv`| YES (Pre-dispatch)| +0.0311 | -0.0290 | Legitimate chamber positioning |
| `initial_quality_score`| `batches.csv` | YES (Pre-dispatch) | -0.0241 | +0.0392 | Legitimate intake quality score |
| `pre_dispatch` defect %| `quality_checks.csv` | YES (Pre-dispatch) | -0.0210 | +0.0238 | Legitimate pre-dispatch inspection |
| `arrival` firmness | `quality_checks.csv` | NO (Post-dispatch) | +0.0208 | -0.0263 | **Forbidden**: Measured at destination dock |
| `harvest` firmness | `quality_checks.csv` | YES (Pre-dispatch) | -0.0177 | +0.0124 | Legitimate intake inspection |

*Target Mechanism `[INFERENCE]`*: `cold_chain_incident` and `transit_temp_mean_c` are strongly associated post-dispatch variables and severe leakage proxies for final loss. However, because they occur after dispatch, including them would convert a pre-dispatch risk assessment task into an unrealistic post-facto transit diagnostic.

---

## Split reconnaissance

### Random batch split `[FACT]` / `[RECOMMENDATION]`
- **FACT**: Yields balanced crop counts, but 95.79% of test batches share microclimate clusters with training batches.
- **RECOMMENDATION**: Unacceptable as primary evaluation split due to spatio-temporal leakage.

### Chronological split `[FACT]` / `[RECOMMENDATION]`
- **FACT**: Sorting by `dispatch_datetime` with a 70/30 cutoff (Cutoff: `2025-10-27 12:47:24`, Train = 1,260, Test = 540):
  - `strawberries`: Train = 63 (5.0%), Test = **0 (0.0%)**
  - `raspberries`: Train = 50 (4.0%), Test = **0 (0.0%)**
  - `apricots`: Train = 60 (4.8%), Test = **0 (0.0%)**
  - `tomatoes`: Train = 180 (14.3%), Test = **0 (0.0%)**
  - `plums`: Train = 327 (26.0%), Test = 23 (4.3%)
  - `table_grapes`: Train = 184 (14.6%), Test = 126 (23.3%)
  - `apples`: Train = 342 (27.1%), Test = **331 (61.3%)**
  - `pears`: Train = 54 (4.3%), Test = 60 (11.1%)
  - Truncated batches in test set: **204 / 540 (37.8%)**.
- **RECOMMENDATION**: A single prospective chronological cutoff suffers severe seasonal crop disappearance and class imbalance.

### Grouped / chamber-cluster split `[FACT]` / `[INFERENCE]` / `[RECOMMENDATION]`
- **FACT**: Cluster-blocked splitting can keep the same observed chamber-time connected component from appearing in both train and test.
- **INFERENCE**: Preventing connected chamber-time clusters from bridging across splits reduces this leakage risk by preventing the exact same observed chamber-time connected component from appearing in both train and test; residual zone- or facility-level similarity may remain.
- **RECOMMENDATION**: Strong candidate for cross-validation within seasons, provided crop balance is maintained across folds.

### Inter-season candidate `[FACT]` / `[RECOMMENDATION]`
- **FACT**: Two complete operational seasons exist in the data:
  - **Season 2024** ($N=900$): Dispatches from `2024-05-25 13:39:36` to `2025-04-11 16:24:00`.
  - **Hiatus**: **43.97 days** (facility clear of active dispatches from April 11 to May 25, 2025).
  - **Season 2025** ($N=900$): Dispatches from `2025-05-25 15:35:24` to `2026-04-03 12:30:36`.
  - **Cross-Season Overlaps**: **0 pairwise overlaps** across seasons.
  - **Crop Comparison Across Seasons**:
    - `apples`: S2024 = 338 (37.56%), S2025 = 335 (37.22%)
    - `plums`: S2024 = 182 (20.22%), S2025 = 168 (18.67%)
    - `table_grapes`: S2024 = 157 (17.44%), S2025 = 153 (17.00%)
    - `tomatoes`: S2024 = 90 (10.00%), S2025 = 90 (10.00%)
    - `pears`: S2024 = 53 (5.89%), S2025 = 61 (6.78%)
    - `apricots`: S2024 = 23 (2.56%), S2025 = 37 (4.11%)
    - `strawberries`: S2024 = 33 (3.67%), S2025 = 30 (3.33%)
    - `raspberries`: S2024 = 24 (2.67%), S2025 = 26 (2.89%)
  - **Truncation Concentration**: All 204 truncated batches are in Season 2025 (22.67% of Season 2025).
- **RECOMMENDATION**: Highly viable prospective evaluation candidate. VDR-04 must establish an explicit policy for handling the 204 truncated batches in Season 2025 test evaluation.

### Hybrid candidates `[RECOMMENDATION]`
- Combine inter-seasonal testing with chamber-cluster blocking within training to simultaneously address temporal holdout and microclimate leakage.

---

## Definitely safe input families

The following input families are physically and administratively fixed at or before $T_{dispatch}$:
1. **Batch Intake Descriptors**: `batches.crop_type`, `batches.variety`, `batches.origin_region`, `batches.harvest_datetime`, `batches.harvest_weight_kg`, `batches.initial_quality_score`, `batches.harvest_temperature_c`, `batches.harvest_conditions`, `batches.field_precooled`.
2. **Session Storage Context**: `storage_sessions.entry_datetime`, `storage_sessions.dispatch_datetime`, `storage_sessions.bin_stack_tier`, `storage_sessions.storage_duration_days`.
3. **Storage Room Specifications**: `storage_zones.zone_type`, `storage_zones.nominal_capacity_tonnes`, `storage_zones.target_temperature_c`, `storage_zones.target_relative_humidity_pct`, `storage_zones.cooling_system_type`, `storage_zones.insulation_quality`, `storage_zones.defrost_cycle_frequency_per_day`.
4. **Facility Infrastructure**: `facilities.region`, `facilities.district`, `facilities.facility_type`, `facilities.capacity_tonnes`, `facilities.commissioned_year`, `facilities.has_controlled_atmosphere`.
5. **Intake & Pre-Dispatch QC**: `quality_checks` measurements (`firmness_kg_cm2`, `sugar_brix`, `defect_pct`) for `stage='harvest'` and `stage='pre_dispatch'`.

---

## Conditionally safe input families

Permissible only under strict operational assumptions:
1. `storage_sessions.planned_dispatch_datetime`: Safe if verified as immutable target established at intake.
2. `shipments.destination_market`, `shipments.destination_region`: Safe if contractual delivery destination is locked before release.
3. `shipments.vehicle_type`: Safe if transport carrier mode is booked prior to dispatch.
4. `shipments.planned_departure_datetime`, `shipments.planned_arrival_datetime`, `shipments.planned_duration_hours`: Safe as baseline route expectations.
5. `sensor_readings.*`: Safe **only** when filtered by $\text{entry_datetime} \le \text{timestamp} \le \text{dispatch_datetime}$ and matched by `zone_id`.

---

## Definitely forbidden prediction inputs

Strictly prohibited from training feature stores:
1. `historical_quality_outcomes.loss_fraction_pct` (Post-arrival outcome / candidate target).
2. `historical_quality_outcomes.quality_status` (Post-arrival outcome / candidate target).
3. `historical_quality_outcomes.quality_score` (Destination inspection score / post-arrival outcome).
4. `historical_quality_outcomes.economic_loss_eur` (Downstream financial outcome).
5. `quality_checks.*` where `stage='arrival'` (Receiving dock inspection).
6. `shipments.actual_departure_datetime` (Post-dispatch event).
7. `shipments.actual_arrival_datetime` (Post-dispatch event).
8. `shipments.actual_delay_minutes` (Post-dispatch outcome).
9. `shipments.cold_chain_incident` (Post-dispatch transit failure shock).
10. `shipments.transit_temp_mean_c` (Post-dispatch transit temperature).
11. `sensor_readings.*` where $\text{timestamp} > \text{dispatch_datetime}$ (Future chamber readings).

---

## Remaining UNKNOWNs

1. `[UNKNOWN]`: Whether sensor logging after `2025-12-31 23:30:00` ceased due to hardware failure, commercial contract expiration, or an export cutoff artifact.
2. `[UNKNOWN]`: Whether logistics plans (`vehicle_type`, `planned_duration_hours`) are frequently rescheduled within the final 2 hours prior to departure in live operations.

---

## Implications for VDR-03

1. **Target Selection**: `[RECOMMENDATION]` `loss_fraction_pct` and `quality_status` are leading candidate targets for investigation in VDR-03. VDR-02 does not select the final target. `economic_loss_eur` remains described as a downstream/derived monetary outcome.
2. **Missingness & Outlier Rules**: Must account for ZONE-006 missing `produce_surface_temperature_c` and non-CA rooms having 100% NULL `co2_ppm` / `o2_pct`.
3. **Telemetry Truncation Context**: `[RECOMMENDATION]` VDR-03 should account for the 204 telemetry-truncated batches when assessing target usability and deterioration evidence. The final feature imputation/masking policy is deferred to later feature-engineering/evaluation design.

---

## Implications for VDR-04

1. **Splitting Architecture**:
   - Random splits are invalid due to 95.79% chamber-cluster leakage.
   - Naive chronological dispatch splits are invalid due to summer crop disappearance.
   - Inter-seasonal split (Season 2024 train vs Season 2025 test) or Grouped Cluster-Blocked splits are the primary viable candidates.
2. **Truncation Handling in Evaluation**: If Season 2025 is the test set, VDR-04 must determine whether the 204 truncated batches are evaluated with imputed telemetry, evaluated on pre-storage features only, or stratified into a separate sub-evaluation.

---

## Risks and limitations

- **Operational Generalizability**: In-sample training may over-index on the 25 specific storage zones and 10 facilities present in the dataset.
- **Sensor Calibration**: Variations between sensors across chambers could introduce site-specific biases.

---

## Reproduction and evidence

All snippets run independently from repository root using standard Python 3.

### Snippet 1: Lifecycle Sequence & Milestone Verification
```python
import csv
from datetime import datetime

batches = {r['batch_id']: r for r in csv.DictReader(open('sponsor_pack/data/batches.csv', encoding='utf-8'))}
sessions = {r['batch_id']: r for r in csv.DictReader(open('sponsor_pack/data/storage_sessions.csv', encoding='utf-8'))}
shipments = {r['batch_id']: r for r in csv.DictReader(open('sponsor_pack/data/shipments.csv', encoding='utf-8'))}
qc_by_batch = {b: {} for b in batches}
for r in csv.DictReader(open('sponsor_pack/data/quality_checks.csv', encoding='utf-8')):
    qc_by_batch[r['batch_id']][r['stage']] = r

parse = lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

violations = 0
equal_arrival = 0
for b_id, b in batches.items():
    t_h = parse(b['harvest_datetime'])
    t_hqc = parse(qc_by_batch[b_id]['harvest']['check_datetime'])
    t_ent = parse(sessions[b_id]['entry_datetime'])
    t_pqc = parse(qc_by_batch[b_id]['pre_dispatch']['check_datetime'])
    t_disp = parse(sessions[b_id]['dispatch_datetime'])
    t_adep = parse(shipments[b_id]['actual_departure_datetime'])
    t_aarr = parse(shipments[b_id]['actual_arrival_datetime'])
    t_aqc = parse(qc_by_batch[b_id]['arrival']['check_datetime'])

    # Verify actual physical event sequence: harvest < harvest_qc < entry < pre_dispatch_qc < dispatch <= actual_departure < actual_arrival = arrival_qc
    seq = [t_h, t_hqc, t_ent, t_pqc, t_disp, t_adep, t_aarr]
    if not (t_h < t_hqc < t_ent < t_pqc < t_disp <= t_adep < t_aarr == t_aqc):
        violations += 1
    if t_aqc == t_aarr:
        equal_arrival += 1

print(f"Snippet 1 - Batches: {len(batches)}, Sequence Violations: {violations}")
print(f"Snippet 1 - Arrival QC == Actual Arrival Cases: {equal_arrival} / {len(batches)}")
```

### Snippet 2: Telemetry Cutoff & Staleness
```python
import csv
from datetime import datetime
from collections import defaultdict

sessions_by_zone = defaultdict(list)
sessions = {}
with open('sponsor_pack/data/storage_sessions.csv', 'r', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        b_id = r['batch_id']
        ent = datetime.strptime(r['entry_datetime'], '%Y-%m-%d %H:%M:%S')
        disp = datetime.strptime(r['dispatch_datetime'], '%Y-%m-%d %H:%M:%S')
        sessions[b_id] = (ent, disp)
        sessions_by_zone[r['zone_id']].append((ent, disp, b_id))

max_sensor_ts = {}
future_counts = defaultdict(int)
with open('sponsor_pack/data/sensor_readings.csv', 'r', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        ts = datetime.strptime(r['timestamp'], '%Y-%m-%d %H:%M:%S')
        for ent, disp, b_id in sessions_by_zone[r['zone_id']]:
            if ent <= ts <= disp:
                if b_id not in max_sensor_ts or ts > max_sensor_ts[b_id]:
                    max_sensor_ts[b_id] = ts
            elif ts > disp:
                future_counts[b_id] += 1

normal_gaps, trunc_gaps = [], []
trunc_date = datetime(2025, 12, 31, 23, 30)
for b_id, (ent, disp) in sessions.items():
    last_ts = max_sensor_ts.get(b_id)
    gap_hours = (disp - last_ts).total_seconds() / 3600.0 if last_ts else None
    if disp > trunc_date:
        trunc_gaps.append(gap_hours)
    else:
        normal_gaps.append(gap_hours)

print(f"Snippet 2 - Non-truncated (N={len(normal_gaps)}), Max Staleness: {max(normal_gaps)*60:.1f}m (All <= 30m: {all(g*60 <= 30 for g in normal_gaps)})")
print(f"Snippet 2 - Truncated (N={len(trunc_gaps)}), Range: {min(trunc_gaps)/24:.2f} to {max(trunc_gaps)/24:.2f} days (Mean: {sum(trunc_gaps)/len(trunc_gaps)/24:.2f} days)")
contam_counts = [future_counts[b] for b in sessions if future_counts[b] > 0]
print(f"Snippet 2 - Unconstrained future readings: contaminated={len(contam_counts)}/{len(sessions)}, contaminated min={min(contam_counts)}, max={max(contam_counts)}")
```

### Snippet 3: Chamber Overlap & Cluster Simulation
```python
import csv, random
from datetime import datetime
from collections import defaultdict

sessions = list(csv.DictReader(open('sponsor_pack/data/storage_sessions.csv', encoding='utf-8')))
parent = {s['batch_id']: s['batch_id'] for s in sessions}
def find(i):
    if parent[i] == i: return i
    parent[i] = find(parent[i])
    return parent[i]
def union(i, j):
    ri, rj = find(i), find(j)
    if ri != rj: parent[ri] = rj

by_zone = defaultdict(list)
for s in sessions:
    by_zone[s['zone_id']].append({
        'batch_id': s['batch_id'],
        'entry': datetime.strptime(s['entry_datetime'], '%Y-%m-%d %H:%M:%S'),
        'dispatch': datetime.strptime(s['dispatch_datetime'], '%Y-%m-%d %H:%M:%S')
    })

overlaps = 0
for zid, z_sessions in by_zone.items():
    z_sessions.sort(key=lambda x: x['entry'])
    for i in range(len(z_sessions)):
        for j in range(i + 1, len(z_sessions)):
            if z_sessions[j]['entry'] < z_sessions[i]['dispatch']:
                union(z_sessions[i]['batch_id'], z_sessions[j]['batch_id'])
                overlaps += 1
            else:
                break

clusters = set(find(s['batch_id']) for s in sessions)
print(f"Snippet 3 - Overlaps: {overlaps}, Disjoint Clusters: {len(clusters)}")

leak_pcts = []
all_bids = [s['batch_id'] for s in sessions]
for seed in range(100):
    rng = random.Random(seed)
    shuffled = list(all_bids)
    rng.shuffle(shuffled)
    train_clusters = set(find(b) for b in shuffled[:1440])
    leaked = sum(1 for b in shuffled[1440:] if find(b) in train_clusters)
    leak_pcts.append(leaked / len(shuffled[1440:]) * 100.0)

print(f"Snippet 3 - Mean 80/20 Random Split Cluster Overlap: {sum(leak_pcts)/len(leak_pcts):.2f}%")
```

### Snippet 4: Post-Dispatch Feature Correlations & Truncated Loss
```python
import csv, math
from datetime import datetime

outcomes = {r['batch_id']: float(r['loss_fraction_pct']) for r in csv.DictReader(open('sponsor_pack/data/historical_quality_outcomes.csv', encoding='utf-8'))}
shipments = {r['batch_id']: (1.0 if r['cold_chain_incident'].lower() == 'true' else 0.0, float(r['transit_temp_mean_c'])) for r in csv.DictReader(open('sponsor_pack/data/shipments.csv', encoding='utf-8'))}
sessions = {r['batch_id']: datetime.strptime(r['dispatch_datetime'], '%Y-%m-%d %H:%M:%S') for r in csv.DictReader(open('sponsor_pack/data/storage_sessions.csv', encoding='utf-8'))}

def pearson_r(x, y):
    n = len(x)
    mx, my = sum(x)/n, sum(y)/n
    cov = sum((xi - mx)*(yi - my) for xi, yi in zip(x, y))
    return cov / math.sqrt(sum((xi - mx)**2 for xi in x) * sum((yi - my)**2 for yi in y))

losses = [outcomes[b] for b in outcomes]
incidents = [shipments[b][0] for b in outcomes]
temps = [shipments[b][1] for b in outcomes]

trunc_date = datetime(2025, 12, 31, 23, 30)
trunc_losses = [outcomes[b] for b, d in sessions.items() if d > trunc_date]
normal_losses = [outcomes[b] for b, d in sessions.items() if d <= trunc_date]

print(f"Snippet 4 - Pearson r(cold_chain_incident, loss): {pearson_r(incidents, losses):.4f}")
print(f"Snippet 4 - Pearson r(transit_temp_mean_c, loss): {pearson_r(temps, losses):.4f}")
print(f"Snippet 4 - Normal Loss Mean: {sum(normal_losses)/len(normal_losses):.2f}%, Truncated Loss Mean: {sum(trunc_losses)/len(trunc_losses):.2f}%")
```

### Snippet 5: Season Partition & Crop Balance
```python
import csv
from datetime import datetime
from collections import Counter

batches = {r['batch_id']: r['crop_type'] for r in csv.DictReader(open('sponsor_pack/data/batches.csv', encoding='utf-8'))}
sessions = list(csv.DictReader(open('sponsor_pack/data/storage_sessions.csv', encoding='utf-8')))
sessions.sort(key=lambda s: datetime.strptime(s['dispatch_datetime'], '%Y-%m-%d %H:%M:%S'))

s2024 = sessions[:900]
s2025 = sessions[900:]

c2024 = Counter(batches[s['batch_id']] for s in s2024)
c2025 = Counter(batches[s['batch_id']] for s in s2025)

trunc_cutoff = datetime(2025, 12, 31, 23, 30)
trunc_crops = Counter(batches[s['batch_id']] for s in sessions if datetime.strptime(s['dispatch_datetime'], '%Y-%m-%d %H:%M:%S') > trunc_cutoff)

print(f"Snippet 5 - Season 2024 (N={len(s2024)}): {dict(c2024)}")
print(f"Snippet 5 - Season 2025 (N={len(s2025)}): {dict(c2025)}")
print(f"Snippet 5 - Truncated Crops (N={sum(trunc_crops.values())}): {dict(trunc_crops)}")
```
