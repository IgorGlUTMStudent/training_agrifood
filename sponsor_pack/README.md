# AgriFood Commercial Cold Storage & Transport Dataset
**Challenge:** Smart Harvest: Reduce Post-Harvest Losses  
**Publisher:** Moldovan Post-Harvest Logistics Consortium  
**Coverage:** 2024–2025 Agricultural Harvest & Storage Seasons  

---

## 1. Overview

This dataset provides real-world cold-chain monitoring, storage telemetry, and logistics records across 10 commercial post-harvest facilities in the Republic of Moldova. The objective of the challenge is to build predictive models that forecast post-harvest produce quality degradation and commercial loss at the moment of transport dispatch ($T_{dispatch}$), enabling proactive supply-chain interventions.

---

## 2. Relational Architecture & Tables

The dataset is organized as a relational database across 8 core tables:

```
[facilities] ──< [storage_zones] ──< [sensor_readings]
                       │
             [storage_sessions] >── [batches] ──< [quality_checks]
                                       │
                                  [shipments]
                                       │
                         [historical_quality_outcomes]
```

### Table Summary:
1. **`facilities.csv`**: Master registry of commercial cold stores, packinghouses, and cooperative hubs across North, Centre, and South Moldova.
2. **`storage_zones.csv`**: Specifications of individual cold storage rooms, including refrigeration systems, insulation ratings, and setpoints.
3. **`batches.csv`**: Metadata of harvested produce batches (crop, cultivar, harvest weight, field conditions, initial quality score).
4. **`storage_sessions.csv`**: Time-interval linkage between produce batches and storage chambers. Note that multiple batches stored concurrently in the same chamber share identical environmental physics.
5. **`sensor_readings.csv`**: Environmental telemetry logged at a **30-minute sampling interval** for each active chamber (air temperature, fruit surface temperature, relative humidity, dew point, condensation flag, gas levels).
6. **`quality_checks.csv`**: Intermediate physical inspections (firmness, Brix, cosmetic defect %) conducted at harvest, pre-dispatch, and arrival.
7. **`shipments.csv`**: Transport carrier assignments, vehicle types (Reefer, Insulated, Ambient), planned routes, and post-dispatch transit logs.
8. **`historical_quality_outcomes.csv`**: Ground truth outcomes for completed 2024–2025 batches at market delivery (`quality_status`, `loss_fraction_pct`, `quality_score`, `economic_loss_eur`).

---

## 3. Important Temporal Semantics ($T_{assess} = T_{dispatch}$)

When evaluating a historical batch or developing decision models, **you must only use information that would have been available at the assessment timestamp**:
- **Decision Moment ($T_{assess}$):** Defined as the batch's `dispatch_datetime` in `storage_sessions.csv`.
- **Known at Dispatch:** Batch agronomic metadata, ambient harvest weather, complete cold storage telemetry up to $T_{dispatch}$, pre-shipment quality inspection, and planned transport logistics (destination, carrier, vehicle type, planned departure/arrival).
- **Strictly Unknown at Dispatch:** In-transit delays, refrigeration unit breakdowns, en-route telemetry, destination arrival inspections, and final commercial loss outcomes.

> [!IMPORTANT]
> **Public vs Hidden Evaluation Protocol:**
> For a historical prediction made at dispatch time, only information available at or before dispatch should be used.
> While the Public Sponsor Pack contains completed arrival-stage quality checks for historical retrospective analysis, **in the hidden test environment all arrival-stage quality checks are completely withheld**. Machine learning solutions evaluated by the competition platform will have access strictly to harvest-stage and pre-dispatch-stage inspections. Participants must ensure their feature extraction pipelines do not rely on arrival-stage telemetry or inspection data.


---

## 4. Physical Units & Coordinate Standards

- **Timestamps:** Local Moldova time (continuous UTC+3 timeline, matching local civil time EEST throughout active harvest and storage). Formatted as `YYYY-MM-DD HH:MM:SS`.
- **Temperatures:** Degrees Celsius (°C).
- **Humidity:** Relative Humidity percentage (%).
- **Dew Point:** Calculated via the Magnus-Tetens formula.
- **Condensation Flag:** Indicates that the produce surface temperature is at or below the ambient dew point ($T_{surface} \le T_{dew}$), creating free liquid moisture on the produce skin.
- **Weight:** Kilograms (kg).
- **Financial Loss:** Euros (EUR).

---

## 5. Data Dictionary

For complete field definitions, data types, and nullability rules, consult [`data_dictionary.xlsx`](./data_dictionary.xlsx).
