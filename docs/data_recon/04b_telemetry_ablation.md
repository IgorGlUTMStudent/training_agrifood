# VDR-04B — Telemetry Marginal Value Ablation under Planned Logistics

## Status and provenance

- **Owner:** Viktor — Implementation / Evaluation Agent
- **Repository:** `Slave-of-Skynet/training_agrifood`
- **Assigned Base SHA:** `0c31f947386233badc9122c9cd374fd0c38c1140`
- **Actual Base SHA:** `0c31f947386233badc9122c9cd374fd0c38c1140` (matches `origin/main` exactly)
- **Branch:** `victor/vdr-04b-telemetry-ablation`
- **Status:** DRAFT FOR REVIEW — EVIDENCE ONLY
- **Decision Authority:** NONE (This report produces reproducible empirical evidence for a subsequent Integrator decision gate; it makes no production, architecture, or contract decisions).
- **Execution Script:** `scripts/vdr04b_telemetry_ablation.py`
- **Output Artifacts:**
  - `docs/data_recon/04b_telemetry_ablation_results.json` (SHA256: `1FED77EA0CAC9730340B9D4D27B91BD4BACD960E3EB76492BEB83AAA4E016806`)
  - `docs/data_recon/04b_telemetry_ablation.md` (this report)

---

## Objective

This study answers one specific analytical question:

> **Does pre-dispatch storage telemetry provide material incremental predictive or ranking value once planned logistics are already present?**

In accepted benchmark VDR-04A, three feature sets were evaluated:
- `C` (Context alone, F1)
- `C+T` (Context + Telemetry, F2)
- `C+T+L` (Context + Telemetry + Planned Logistics, F3)

VDR-04A established that adding telemetry to context alone ($C \to C+T$) provided no stable material lift, while the jointly tested family with planned logistics ($C+T+L$) provided substantial ranking and predictive lift. However, VDR-04A did not evaluate:
- `C+L` (Context + Planned Logistics **without** telemetry)

VDR-04B completes the required $2 \times 2$ ablation experiment:

| | No Planned Logistics | + Planned Logistics |
| :--- | :---: | :---: |
| **No Telemetry** | **C** (Context, 37 cols) | **C+L** (New Ablation, 41 cols) |
| **+ Telemetry** | **C+T** (Context+Telemetry, 114 cols) | **C+T+L** (Context+Telemetry+Logistics, 118 cols) |

The **primary comparison** is:
$$\mathbf{(C+T+L) \text{ versus } (C+L)}$$
This isolates the observed marginal association of pre-dispatch telemetry once planned logistics are already accounted for.

---

## Canonical constraints

All feature engineering, batch alignments, and model evaluations strictly respect the canonical rules established in **ADR 0002** and **ADR 0003**:

1. **Prediction Moment Cutoff:** $T_{\text{assess}} \equiv T_{\text{dispatch}} = \text{storage_sessions.dispatch_datetime}$.
2. **Forbidden Column Denylist:**
   - Arrival inspections: `arrival_firmness_kg_cm2`, `arrival_sugar_brix`, `arrival_defect_pct`, `arrival_check_datetime`.
   - Post-dispatch transit realizations: `actual_departure_datetime`, `actual_arrival_datetime`, `actual_delay_minutes`, `cold_chain_incident`, `transit_temp_mean_c`.
   - Historical commercial outcomes (strictly label/evaluation side): `quality_status`, `loss_fraction_pct`, `quality_score`, `economic_loss_eur`.
   - Identifiers: `batch_id`, `storage_session_id`, `facility_id`, `zone_id`, `shipment_id`, `reading_id`, `check_id`, `facility_name`, `zone_name` are never admitted into predictive matrices $X$.
3. **Planned Logistics Boundary:** Strictly limited to the 4 fields observable prior to transport dispatch:
   `destination_market`, `destination_region`, `vehicle_type`, `planned_duration_hours`.
   Per ADR 0003 D4, planned logistics remain **optional / conditionally eligible**; they are not assumed to be universally mandatory for production operation.
4. **Primary Supervised Target:** Offline regression target is `loss_fraction_pct`. Ranking evaluation uses continuous loss for NDCG and historical $\ge 15.0\%$ for Precision@k and Recall@k.

---

## Sources inspected

Prior to implementation, the following repository files were inspected:
- `sponsor_pack/brief/Training Challenge #3 — AgriFood.md`
- `sponsor_pack/README.md`
- `docs/decisions/0002-predictive-input-semantics.md`
- `docs/decisions/0003-assessment-evaluation-semantics.md`
- `docs/data_recon/01_dataset_inventory.md`
- `docs/data_recon/02_temporal_leakage.md`
- `docs/data_recon/03_target_horizon_feasibility.md`
- `docs/data_recon/04_dispatch_predictability.md`
- `docs/data_recon/04_dispatch_predictability_results.json`
- `docs/evaluation.md`
- `docs/challenge_canon.md`
- `docs/data_contract.md`
- `docs/assumptions_unknowns.md`
- `scripts/vdr04a_predictability.py`

---

## Reproduction environment

All experiments were executed in an isolated local virtual environment (`.venv`) without modifying any repository configuration, manifests (`backend/pyproject.toml`), lockfiles, or frontend packages.

- **OS:** Windows (AMD64)
- **Python:** `3.11.9`
- **NumPy:** `2.4.6`
- **Pandas:** `3.0.6`
- **Scikit-learn:** `1.9.1`
- **SciPy:** `1.17.1`
- **Random Seed:** `42` (fixed across all models and splits)

---

## Dataset integrity and alignment

[FACT] The pre-analysis integrity gate verified all 8 sponsor CSV tables with zero missing files and matching SHA256 hashes:
- `batches.csv` (1,800 rows): `bbaf3cb4064ccdefed5eaca0b3fe7d6303bd918b1abc09a8c27cb20309d6072b`
- `storage_sessions.csv` (1,800 rows): `f38a99dfeb808eaab3b3d91d0494d303649131ee2d5de9a6efa0da99fdf9e04f`
- `facilities.csv` (10 rows): `148de414dcff6d601d327ce17414d8b9e04aaa38c6bc0ecbb769be32d6f3a960`
- `storage_zones.csv` (25 rows): `e2c4b7170c47ab0896ed962c588256e3407d84d30afa758372a704d8085c4ee4`
- `quality_checks.csv` (5,400 rows): `95ccf7d6d898249f6bf444a874817be74b7ce4338b3099f3bf8687f22fa9b627`
- `shipments.csv` (1,800 rows): `bfad682700f58936ca383868febd09181bd810e81bd3287fa28d16d204ea9796`
- `historical_quality_outcomes.csv` (1,800 rows): `567334f44f41b980c67de496736c077dc1d980b4cb02c14ee355597087732606`
- `sensor_readings.csv` (669,665 rows): `6b27adaf43a6646d32cccddc95872bfed03a6220075d9508ccc54be5bdf9edbb`

[FACT] Batch-level relational invariants:
- `batch_id` primary key uniqueness: 100.0% (1,800 unique IDs).
- Strict 1:1:1:1 alignment across batches, sessions, shipments, outcomes, and telemetry records.
- Exactly 1,800 harvest checks and 1,800 pre-dispatch checks joined by `batch_id`.
- Reconstructed 157 disjoint chamber-time clusters (1,734 batches in multi-batch clusters).

---

## Experiment design

The experiment follows a strict $2 \times 2$ factorial structure:
1. **$C$ (Context alone):** 37 features (VDR-04A F1 equivalent).
2. **$C+T$ (Context + Telemetry):** 114 features (VDR-04A F2 equivalent).
3. **$C+L$ (Context + Planned Logistics):** 41 features (**new ablation**).
4. **$C+T+L$ (Context + Telemetry + Planned Logistics):** 118 features (VDR-04A F3 equivalent).

---

## Feature-family definitions

### 1. Context Family ($C$, 37 features)
- **Numeric (27 features):** `harvest_weight_kg`, `initial_quality_score`, `harvest_temperature_c`, `field_precooled`, `harvest_month`, `harvest_hour`, `bin_stack_tier`, `storage_duration_days`, `entry_month`, `dispatch_month`, `dispatch_hour`, `capacity_tonnes`, `commissioned_year`, `has_controlled_atmosphere`, `nominal_capacity_tonnes`, `target_temperature_c`, `target_relative_humidity_pct`, `defrost_cycle_frequency_per_day`, `harvest_firmness_kg_cm2`, `harvest_sugar_brix`, `harvest_defect_pct`, `pre_dispatch_firmness_kg_cm2`, `pre_dispatch_sugar_brix`, `pre_dispatch_defect_pct`, `delta_firmness`, `delta_sugar_brix`, `delta_defect_pct`.
- **Categorical (10 features):** `crop_type`, `variety`, `origin_region`, `harvest_conditions`, `cooling_system_type`, `insulation_quality`, `zone_type`, `facility_type`, `region`, `district`.

### 2. Telemetry Family ($T$, 77 features)
Bounded strictly by $T_{\text{entry}} \le \text{timestamp} \le T_{\text{dispatch}}$:
- `telemetry_reading_count` (1 feature).
- 6 continuous channels (`air_temperature_c`, `produce_surface_temperature_c`, `relative_humidity_pct`, `dew_point_c`, `co2_ppm`, `o2_pct`) $\times$ 10 summary statistics (`missing_frac`, `mean`, `std`, `min`, `max`, `p10`, `p90`, `first`, `last`, `slope_per_day`) = 60 features.
- Setpoint deviations: Air temperature deviations (`signed_dev_mean`, `abs_dev_mean`, `abs_dev_max`, `frac_above_target`, `frac_below_target`) = 5 features; Relative humidity deviations (`signed_dev_mean`, `abs_dev_mean`, `abs_dev_max`, `frac_above_target`, `frac_below_target`) = 5 features.
- Binary duty cycles (`condensation_flag`, `cooling_on`, `defrost_on`) $\times$ 2 (`frac_true`, `transitions`) = 6 features.

### 3. Planned Logistics Family ($L$, 4 features)
- **Categorical (3 features):** `destination_market`, `destination_region`, `vehicle_type`.
- **Numeric (1 feature):** `planned_duration_hours`.

### Boundary and Invariant Assertions
Programmatic assertions verified:
- $C+L$ contains **exactly zero** telemetry columns: $\text{cols}(C+L) \cap \text{cols}(T) = \emptyset$.
- $C+T+L$ and $C+L$ differ **strictly and exclusively** by the 77 telemetry columns: $\text{cols}(C+T+L) \setminus \text{cols}(C+L) = \text{cols}(T)$.
- Zero forbidden columns from the denylist enter any of the four matrices.

---

## Evaluation protocols

- **Protocol P1 — Primary Forward Inter-Season Holdout:**
  - Training: Season 2024 (dispatches 2024-05-25 to 2025-04-11, 900 batches).
  - Testing: Season 2025 (dispatches 2025-05-25 to 2026-04-03, 900 batches).
  - Hiatus between seasons: 43.97 days; zero cross-season chamber overlaps.
- **Protocol P2 — Mandatory Secondary Robustness (Chamber-Time Grouped OOF):**
  - 5-fold `GroupKFold` grouped strictly by the 157 chamber-time clusters across all 1,800 batches.
  - Held-out predictions aggregated over all 1,800 batches.
  - Fold-level results preserved for all 5 folds to examine stability.
- **Protocol P3 (Random Split):** Confirmed as a NON-DEFENSIBLE DIAGNOSTIC due to 94.44% chamber-cluster leakage; strictly excluded from supporting any conclusion.

---

## Models and preprocessing

- **Linear candidate:** `Ridge(alpha=1.0, random_state=42)`
- **Non-linear candidate:** `HistGradientBoostingRegressor(max_iter=100, max_leaf_nodes=31, random_state=42)`
- **Preprocessing:**
  - Numeric: `SimpleImputer(strategy="median")` + `StandardScaler()`
  - Categorical: `OneHotEncoder(handle_unknown="ignore", sparse_output=False)`
  - **Fitted strictly and exclusively on the training partition/fold.** No test labels or test features were ever exposed to preprocessing fitting.
- **Deterministic Baseline:**
  - Crop-conditioned training median `loss_fraction_pct`, with global training median fallback for unseen crop.
  - Fitted exclusively on training labels for P1 and each P2 fold.

---

## VDR-04A replication check

[FACT] Before evaluating the new $C+L$ ablation, all overlapping feature families ($C \equiv \text{F1}$, $C+T \equiv \text{F2}$, $C+T+L \equiv \text{F3}$) were reproduced and compared against the committed historical results in `docs/data_recon/04_dispatch_predictability_results.json`.

- **Maximum absolute difference across all metrics (MAE, RMSE, R², Spearman, NDCG@10, NDCG@50, Precision@10, Precision@50, Recall@10, Recall@50) across P1 and P2:**
  $$\mathbf{0.00000000 \times 10^0 \quad (\text{diff} < 10^{-15})}$$
- **Replication Status:** `EXACT_OR_NUMERICALLY_EQUIVALENT` (bit-for-bit parity achieved).

---

## P1 results

Forward Inter-Season Holdout (Season 2024 train, 900 batches; Season 2025 test, 900 batches):

| Feature Set | Model | MAE | RMSE | R² | Spearman | NDCG@10 | NDCG@50 | Precision@10 | Precision@50 | Recall@10 | Recall@50 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline** | *Crop-Median* | 8.8842 | 16.2401 | 0.0737 | 0.4497 | 0.2634 | 0.2797 | 0.8000 | 0.5800 | 0.0267 | 0.0967 |
| **C** | Ridge | 10.2628 | 16.7147 | 0.0187 | 0.4037 | 0.2269 | 0.2671 | 0.6000 | 0.6200 | 0.0200 | 0.1033 |
| **C** | HGB | 10.8628 | 17.2795 | -0.0487 | 0.3227 | 0.2189 | 0.2441 | 0.5000 | 0.6000 | 0.0167 | 0.1000 |
| **C+T** | Ridge | 10.8984 | 17.0319 | -0.0189 | 0.3461 | 0.2464 | 0.2866 | 0.7000 | 0.6000 | 0.0233 | 0.1000 |
| **C+T** | HGB | 10.5039 | 16.9173 | -0.0052 | 0.3336 | 0.2003 | 0.2554 | 0.6000 | 0.6000 | 0.0200 | 0.1000 |
| **C+L** | Ridge | 9.5828 | 15.7708 | 0.1264 | 0.5148 | 0.3173 | 0.4184 | 0.9000 | 0.8400 | 0.0300 | 0.1400 |
| **C+L** | HGB | **8.8841** | **14.2411** | **0.2877** | 0.4455 | 0.8695 | **0.6567** | **1.0000** | 0.7800 | **0.0333** | 0.1300 |
| **C+T+L** | Ridge | 10.4529 | 16.1798 | 0.0805 | 0.4557 | 0.3414 | 0.4421 | 0.9000 | 0.8000 | 0.0300 | 0.1333 |
| **C+T+L** | HGB | 8.9664 | 14.3185 | 0.2799 | **0.4600** | **0.8831** | 0.6491 | **1.0000** | **0.8600** | **0.0333** | **0.1433** |

---

## P2 results

Chamber-Time Grouped Out-of-Fold (5 folds, 157 clusters, 1,800 batches aggregated):

| Feature Set | Model | MAE | RMSE | R² | Spearman | NDCG@10 | NDCG@50 | Precision@10 | Precision@50 | Recall@10 | Recall@50 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline** | *Crop-Median* | 8.8216 | 15.9096 | 0.0195 | 0.3525 | 0.2533 | 0.2906 | 0.5000 | 0.7600 | 0.0079 | 0.0602 |
| **C** | Ridge | 9.2948 | 15.1155 | 0.1150 | 0.4597 | 0.5977 | 0.3965 | 0.8000 | 0.6800 | 0.0127 | 0.0539 |
| **C** | HGB | 10.2402 | 16.0025 | 0.0080 | 0.3861 | 0.3069 | 0.2629 | 0.6000 | 0.7000 | 0.0095 | 0.0555 |
| **C+T** | Ridge | 10.0792 | 15.5923 | 0.0582 | 0.3606 | 0.5847 | 0.3733 | 0.9000 | 0.6400 | 0.0143 | 0.0507 |
| **C+T** | HGB | 10.4525 | 16.2498 | -0.0229 | 0.3328 | 0.1998 | 0.2089 | 0.6000 | 0.6400 | 0.0095 | 0.0507 |
| **C+L** | Ridge | **8.7328** | **14.1594** | **0.2234** | **0.5389** | 0.7166 | **0.6490** | **1.0000** | **0.9600** | **0.0158** | **0.0761** |
| **C+L** | HGB | **8.2266** | **13.2411** | **0.3208** | **0.4956** | **0.9150** | **0.8103** | **1.0000** | **0.9600** | **0.0158** | **0.0761** |
| **C+T+L** | Ridge | 9.5944 | 14.7404 | 0.1583 | 0.4454 | 0.6960 | 0.5674 | **1.0000** | 0.9200 | **0.0158** | 0.0729 |
| **C+T+L** | HGB | 8.7567 | 13.7329 | 0.2695 | 0.3911 | 0.8888 | 0.7955 | **1.0000** | **0.9600** | **0.0158** | **0.0761** |

---

## Fold-level consistency

Fold-by-fold comparison for the primary question: **$C+T+L$ versus $C+L$ (Telemetry lift under logistics)**:

### 1. HistGradientBoostingRegressor (Non-linear)
| Fold | C+L MAE | C+T+L MAE | $\Delta$ MAE | C+L R² | C+T+L R² | $\Delta$ R² | C+L NDCG@10 | C+T+L NDCG@10 | $\Delta$ NDCG@10 | C+L Sp | C+T+L Sp | $\Delta$ Sp |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 8.1880 | 8.4732 | **+0.2852** (worse) | 0.3945 | 0.3803 | **-0.0142** (worse) | 0.9341 | 0.9263 | **-0.0078** (worse) | 0.5578 | 0.4337 | **-0.1241** (worse) |
| **2** | 8.2028 | 8.8524 | **+0.6497** (worse) | 0.1688 | 0.0955 | **-0.0733** (worse) | 0.5999 | 0.5977 | **-0.0022** (worse) | 0.4343 | 0.3493 | **-0.0850** (worse) |
| **3** | 7.6297 | 8.9770 | **+1.3473** (worse) | 0.3985 | 0.2915 | **-0.1070** (worse) | 0.9014 | 0.8655 | **-0.0359** (worse) | 0.5411 | 0.4152 | **-0.1260** (worse) |
| **4** | 8.6815 | 9.0685 | **+0.3870** (worse) | 0.2521 | 0.2173 | **-0.0348** (worse) | 0.7936 | 0.8030 | **+0.0094** | 0.4621 | 0.3954 | **-0.0667** (worse) |
| **5** | 8.4311 | 8.4125 | **-0.0186** | 0.3326 | 0.2874 | **-0.0453** (worse) | 0.8523 | 0.8484 | **-0.0039** (worse) | 0.4743 | 0.3863 | **-0.0881** (worse) |

- **R² Direction:** Degraded in **5 out of 5 folds** when telemetry is added.
- **Spearman Rank Correlation:** Degraded in **5 out of 5 folds** when telemetry is added.
- **NDCG@10:** Degraded in **4 out of 5 folds** when telemetry is added.
- **MAE:** Degraded (increased error) in **4 out of 5 folds** when telemetry is added.

### 2. Ridge (Linear)
| Fold | C+L MAE | C+T+L MAE | $\Delta$ MAE | C+L R² | C+T+L R² | $\Delta$ R² | C+L NDCG@10 | C+T+L NDCG@10 | $\Delta$ NDCG@10 | C+L Sp | C+T+L Sp | $\Delta$ Sp |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 9.0045 | 10.9110 | **+1.9065** | 0.2263 | 0.1131 | **-0.1132** | 0.5484 | 0.5167 | **-0.0318** | 0.6069 | 0.4771 | **-0.1298** |
| **2** | 7.8784 | 8.2797 | **+0.4012** | 0.2700 | 0.2107 | **-0.0593** | 0.7755 | 0.7882 | **+0.0127** | 0.5563 | 0.4877 | **-0.0687** |
| **3** | 8.1400 | 9.6521 | **+1.5122** | 0.2662 | 0.1610 | **-0.1052** | 0.6864 | 0.5797 | **-0.1067** | 0.5330 | 0.4087 | **-0.1244** |
| **4** | 9.1191 | 9.5628 | **+0.4437** | 0.1922 | 0.1410 | **-0.0512** | 0.7014 | 0.6185 | **-0.0829** | 0.4727 | 0.4212 | **-0.0514** |
| **5** | 9.5222 | 9.5667 | **+0.0444** | 0.1653 | 0.1593 | **-0.0060** | 0.7096 | 0.5860 | **-0.1236** | 0.4767 | 0.4668 | **-0.0098** |

- **R² Direction:** Degraded in **5 out of 5 folds**.
- **Spearman Rank Correlation:** Degraded in **5 out of 5 folds**.
- **MAE:** Degraded in **5 out of 5 folds**.
- **NDCG@10:** Degraded in **4 out of 5 folds**.

---

## Telemetry marginal value without logistics

**Comparison: $C \to C+T$ (Delta: $(C+T) - C$)**

- **Under P1 (Inter-Season):**
  - Ridge: MAE increases by +0.6356 pp (10.2628 to 10.8984); R² drops by -0.0376 (0.0187 to -0.0189).
  - HGB: MAE decreases by -0.3589 pp (10.8628 to 10.5039); R² shifts from -0.0487 to -0.0052 (both negative R²; worse than trivial crop baseline).
- **Under P2 (Grouped OOF):**
  - Ridge: MAE increases by +0.7845 pp (9.2948 to 10.0792); R² drops by -0.0567 (0.1150 to 0.0582); NDCG@10 drops from 0.5977 to 0.5847.
  - HGB: MAE increases by +0.2123 pp (10.2402 to 10.4525); R² drops by -0.0309 (0.0080 to -0.0229); NDCG@10 drops by -0.1071 (0.3069 to 0.1998).

[OBSERVED RESULT] Without planned logistics, pre-dispatch telemetry aggregates produce **no stable material incremental predictive or ranking lift** beyond context alone, confirming the historical VDR-04A finding.

---

## Logistics marginal value without telemetry

**Comparison: $C \to C+L$ (Delta: $(C+L) - C$)**

- **Under P1 (Inter-Season):**
  - Ridge: MAE improves by **-0.6800 pp** (10.2628 to 9.5828); R² jumps by **+0.1077** (0.0187 to 0.1264); Spearman increases by **+0.1111**; NDCG@10 increases by **+0.0904** (0.2269 to 0.3173); Precision@10 increases from 0.60 to 0.90 (+0.3000).
  - HGB: MAE improves by **-1.9788 pp** (10.8628 to 8.8841); R² leaps by **+0.3364** (-0.0487 to +0.2877); NDCG@10 surges by **+0.6506** (0.2189 to **0.8695**); Precision@10 surges from 0.50 to **1.0000** (+0.5000).
- **Under P2 (Grouped OOF):**
  - Ridge: MAE improves by **-0.5619 pp** (9.2948 to 8.7328); R² increases by **+0.1084** (0.1150 to 0.2234); NDCG@10 improves by **+0.1189** (0.5977 to 0.7166); Precision@10 reaches **1.0000**.
  - HGB: MAE improves by **-2.0136 pp** (10.2402 to 8.2266); R² leaps by **+0.3128** (0.0080 to **0.3208**); NDCG@10 surges by **+0.6081** (0.3069 to **0.9150**); Precision@10 reaches **1.0000**.

[OBSERVED RESULT] Most of the observed incremental lift is associated with adding the planned-logistics family (`destination_market`, `destination_region`, `vehicle_type`, `planned_duration_hours`) under these tested configurations. This strong predictive association occurs in the absence of any telemetry features.

---

## Telemetry marginal value with logistics

**PRIMARY COMPARISON: $C+L \to C+T+L$ (Delta: $(C+T+L) - (C+L)$)**

This is the central test of whether telemetry adds material value once planned logistics are present.

### 1. Protocol P1 (Forward Inter-Season Holdout)
- **Ridge (Linear):**
  - Continuous metrics **degrade**: MAE increases by **+0.8701 pp** (9.5828 to 10.4529); RMSE increases by +0.4090 pp; R² drops by **-0.0459** (0.1264 to 0.0805); Spearman drops by -0.0590 (0.5148 to 0.4557).
  - Ranking metrics: NDCG@10 changes slightly (+0.0241, 0.3173 to 0.3414); Precision@10 is identical (0.9000); Precision@50 degrades (-0.0400, 0.8400 to 0.8000).
- **HGB (Non-linear):**
  - Continuous metrics: MAE slightly increases / worsens (+0.0823 pp, 8.8841 to 8.9664); RMSE slightly worsens (+0.0774 pp); R² slightly drops (-0.0078, 0.2877 to 0.2799).
  - Ranking metrics: Spearman changes negligibly (+0.0145, 0.4455 to 0.4600); NDCG@10 shows a minor delta of +0.0137 (0.8695 to 0.8831); NDCG@50 slightly drops (-0.0076, 0.6567 to 0.6491); Precision@10 is saturated at 1.0000 in both; Precision@50 improves (+0.0800, 0.7800 to 0.8600).

### 2. Protocol P2 (Chamber-Time Grouped OOF — Mandatory Robustness)
- **Ridge (Linear):**
  - Continuous metrics **substantially degrade across the entire dataset**: MAE increases by **+0.8616 pp** (8.7328 to 9.5944); RMSE increases by +0.5811 pp; R² drops by **-0.0650** (0.2234 to 0.1583); Spearman drops by **-0.0935** (0.5389 to 0.4454).
  - Ranking metrics **degrade**: NDCG@10 drops from 0.7166 to 0.6960 (-0.0206); NDCG@50 drops from 0.6490 to 0.5674 (-0.0816); Precision@50 drops from 0.9600 to 0.9200 (-0.0400).
- **HGB (Non-linear):**
  - Continuous metrics **consistently degrade**: MAE increases by **+0.5301 pp** (8.2266 to 8.7567); RMSE increases by +0.4918 pp; R² drops by **-0.0514** (0.3208 to 0.2695); Spearman drops by **-0.1046** (0.4956 to 0.3911).
  - Ranking metrics **degrade**: NDCG@10 drops from **0.9150 to 0.8888** (-0.0262); NDCG@50 drops from **0.8103 to 0.7955** (-0.0149); Precision@10 is identical (1.0000); Precision@50 is identical (0.9600).

[OBSERVED RESULT] Under the tested aggregate telemetry representation and fixed model configurations, telemetry shows **no stable observed marginal lift** once planned logistics are present. Protocol P2 shows broadly consistent degradation across both model families and folds (HGB R² drops by -0.0514, NDCG@10 drops by -0.0262), while Protocol P1 HGB shows small positive deltas on selected ranking metrics (NDCG@10 +0.0137, Spearman +0.0145, Precision@50 +0.0800, Recall@50 +0.0133) alongside slightly worse continuous-loss metrics (MAE +0.0823 pp, RMSE +0.0774 pp, R² -0.0078).

---

## Raw prediction vs clipped runtime-score diagnostic

Per ADR 0003 D2, runtime scoring clips predicted loss into $[0, 100]$:
$$\text{risk.score} = \frac{\text{clip}(\hat{y}, 0, 100)}{100}$$
Ordered operationally by `(risk.score DESC, batch_id ASC)`.

[FACT] Empirical diagnostic results across all 900 P1 test batches and all 1,800 P2 OOF batches:

| Protocol | Feature Family | Model | Predictions $< 0$ | Predictions $> 100$ | Ties Introduced | Rank Spearman (Raw vs Clipped) | Rank Pos Changed | Top 10 Overlap | Top 50 Overlap |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **P1** | $C$ | Ridge | 13 | 0 | 12 | 0.999999 | 11 | 10 / 10 | 50 / 50 |
| **P1** | $C$ | HGB | 5 | 0 | 4 | 1.000000 | 4 | 10 / 10 | 50 / 50 |
| **P1** | $C+T$ | Ridge | 47 | 0 | 46 | 0.999869 | 47 | 10 / 10 | 50 / 50 |
| **P1** | $C+T$ | HGB | 1 | 0 | 0 | 1.000000 | 0 | 10 / 10 | 50 / 50 |
| **P1** | $C+L$ | Ridge | 20 | 0 | 19 | 0.999988 | 20 | 10 / 10 | 50 / 50 |
| **P1** | $C+L$ | HGB | 4 | 0 | 3 | 1.000000 | 4 | 10 / 10 | 50 / 50 |
| **P1** | $C+T+L$ | Ridge | 64 | 0 | 63 | 0.999584 | 64 | 10 / 10 | 50 / 50 |
| **P1** | $C+T+L$ | HGB | 0 | 0 | 0 | 1.000000 | 0 | 10 / 10 | 50 / 50 |
| **P2** | $C$ | Ridge | 5 | 0 | 4 | 1.000000 | 2 | 10 / 10 | 50 / 50 |
| **P2** | $C$ | HGB | 3 | 0 | 2 | 1.000000 | 2 | 10 / 10 | 50 / 50 |
| **P2** | $C+T$ | Ridge | 26 | 0 | 25 | 0.999997 | 25 | 10 / 10 | 50 / 50 |
| **P2** | $C+T$ | HGB | 4 | 0 | 3 | 1.000000 | 3 | 10 / 10 | 50 / 50 |
| **P2** | $C+L$ | Ridge | 40 | 0 | 39 | 0.999990 | 39 | 10 / 10 | 50 / 50 |
| **P2** | $C+L$ | HGB | 2 | 0 | 1 | 1.000000 | 0 | 10 / 10 | 50 / 50 |
| **P2** | $C+T+L$ | Ridge | 41 | 0 | 40 | 0.999991 | 39 | 10 / 10 | 50 / 50 |
| **P2** | $C+T+L$ | HGB | 1 | 0 | 0 | 1.000000 | 0 | 10 / 10 | 50 / 50 |

### Key Diagnostic Findings:
1. **[FACT] All observed out-of-bounds predictions were below 0%; no predictions exceeded 100%.** Clipping these negative predictions to 0 introduced ties and some low-risk-tail rank-position changes, while top-10 and top-50 membership remained unchanged in all tested configurations.
2. **Prioritisation Frontiers Unchanged:** Across all tested configurations, **100% of top-10 batches and 100% of top-50 batches are identical between raw predictions and clipped runtime scores** (`10/10` and `50/50` overlap across all models and families).
3. **Rank Correlation:** Spearman rank correlation between raw array order and operational clipped order is $\ge 0.999584$ for Ridge and $1.000000$ for HGB.

---

## Interpretation

### Q1: Does telemetry add observed predictive/ranking value without logistics?

**Answer:** No stable observed lift under the tested aggregate representation and fixed model configurations.

C vs C+T is mixed on individual P1 metrics but does not show a stable improvement across P1/P2 and both model families. In linear models, error metrics deteriorate; in non-linear models under P1, R² shifts from -0.0487 to -0.0052 (remaining negative, worse than the crop-median baseline), while under P2, HGB ranking drops from 0.3069 to 0.1998 NDCG@10.

### Q2: Does planned logistics add observed value without telemetry?

**Answer:** Strong positive observed association under the tested P1/P2 configurations.

C+L improves the reported continuous and ranking metrics relative to C across the tested model/protocol comparisons. This is predictive association in the supplied simulation dataset, not evidence that the logistics fields causally cause post-harvest loss. In P1 HGB, R² shifts from -0.0487 to +0.2877, and NDCG@10 increases from 0.2189 to 0.8695. In P2 HGB, R² shifts from 0.0080 to 0.3208, and NDCG@10 increases from 0.3069 to 0.9150. Most of the observed incremental lift is associated with adding the planned-logistics family under these tested configurations.

### Q3 (PRIMARY): Does telemetry add observed value once planned logistics are present?
**Answer:**
Under the tested aggregate telemetry representation and fixed model configurations, telemetry shows **no stable observed marginal lift** once planned logistics are present.
- In **Protocol P2 (Chamber-Time Grouped OOF)**: Protocol P2 shows broadly consistent degradation across both model families and folds. Adding the 77 telemetry features degrades HGB continuous metrics (MAE increases from 8.2266 to 8.7567 [+0.5301 pp], R² drops from 0.3208 to 0.2695 [-0.0514]) and ranking metrics (NDCG@10 drops from 0.9150 to 0.8888 [-0.0262], Spearman drops from 0.4956 to 0.3911 [-0.1046]). For Ridge, degradation is also consistent (R² drops from 0.2234 to 0.1583 [-0.0650], NDCG@10 drops from 0.7166 to 0.6960 [-0.0206]).
- In **Protocol P1 (Forward Inter-Season Holdout)**: Ridge continuous metrics degrade (MAE increases from 9.5828 to 10.4529 [+0.8701 pp], R² drops from 0.1264 to 0.0805 [-0.0459]), while HGB shows small positive deltas on selected ranking metrics (NDCG@10 increases from 0.8695 to 0.8831 [+0.0137], Spearman from 0.4455 to 0.4600 [+0.0145], Precision@50 from 0.7800 to 0.8600 [+0.0800], Recall@50 from 0.1300 to 0.1433 [+0.0133]) alongside slightly worse continuous-loss metrics (MAE increases from 8.8841 to 8.9664 [+0.0823 pp], RMSE increases from 14.2411 to 14.3185 [+0.0774 pp], R² drops from 0.2877 to 0.2799 [-0.0078]).

### Q4: Are findings consistent across Ridge, HistGradientBoostingRegressor, P1, and P2?
**Answer:**
Findings are consistent in demonstrating the absence of a stable, robust lift from telemetry once planned logistics are present:
- In P2, degradation is consistent across both model families and across all 5 individual folds for R² and Spearman.
- In P1, Ridge continuous metrics degrade, while HGB ranking deltas are small and mixed with slightly worse continuous metrics.
- In both protocols and both model families, the $C+L$ model with only 41 features performs strongly compared to the $C+T+L$ model with 118 features.

### Q5: Does the evidence support proposing feature-set simplification for a later decision?
**Classification:** `SUPPORTED AS CANDIDATE FOR LATER DECISION`

$C+L$ is supported as a candidate for later learned-feature simplification because it improves the tested continuous metrics and performs strongly under the mandatory P2 robustness protocol, while some P1 HGB ranking metrics still favor $C+T+L$. The evidence therefore supports feature simplification as a candidate for a later decision, not a claim that telemetry has zero predictive value. Any simplification decision remains for a later Integrator gate.

> [!IMPORTANT]
> **Boundary Note:** This classification is an evidence-grounded recommendation for a subsequent human Integrator gate (e.g., VLD-02C / ADR). It does **NOT** authorize removing telemetry from the canonical `BatchAssessmentInput` contract (ADR 0002), nor does it declare a production feature subset.

---

## What the evidence supports

1. **[OBSERVED RESULT]** Under the mandatory P2 chamber-time grouped robustness protocol, the $C+L$ feature family (41 features: context + 4 planned logistics) achieves strong overall predictive and ranking performance ($R^2 = 0.3208$, $\text{NDCG@10} = 0.9150$, $\text{Precision@10} = 1.0000$ under P2 HGB), outperforming $C+T+L$ on continuous metrics and ranking metrics.
2. **[OBSERVED RESULT]** Adding 77 pre-dispatch telemetry features to $C+L$ shows no stable observed marginal lift: Protocol P2 shows broadly consistent degradation across both model families and folds, while Protocol P1 HGB exhibits small positive deltas on selected ranking metrics alongside slightly worse continuous-loss metrics.
3. **[OBSERVED RESULT]** Runtime clipping introduces ties and changes some rank positions in the low-risk tail for several model/family combinations, but it does not change top-10 or top-50 membership in any tested P1/P2 configuration. Therefore the tested clipping behavior does not change membership at the evaluated top-K prioritisation frontiers.
4. **[OBSERVED RESULT]** Zero predictive leakage occurred: $T_{\text{assess}} \equiv T_{\text{dispatch}}$ was strictly enforced, no arrival QC, in-transit telemetry, realized transit outcomes, or historical outcome labels entered features, and preprocessing was fit exclusively on training folds.

---

## What the evidence does NOT support

1. Does **NOT** prove that telemetry is useless in biological produce storage generally.
2. Does **NOT** prove that planned logistics causally cause produce degradation.
3. Does **NOT** authorize removing telemetry from canonical domain contracts (`BatchAssessmentInput`).
4. Does **NOT** prove that missing telemetry is universally safe in real-world commercial farming.
5. Does **NOT** select a production model, production risk thresholds, or alert rules.
6. Does **NOT** prove that food waste is reduced or financial savings are achieved.

---

## Remaining UNKNOWNs

- Whether alternative telemetry representations (e.g., custom cumulative degree-hour stress metrics, moving-average filters, or deep sequence models) could extract latent biological signal not captured by standard aggregates.
- The degree of site/facility proxy confounding embedded in planned logistics routes.
- How models perform on unseen crop types or outside the Republic of Moldova.
- Operational operator workflow, capacity constraints, and intervention costs.

---

## Risks and limitations

- **Synthetic / Simulation Source:** All data originates from a simulated challenge environment; findings must not be generalized to commercial agriculture without real-world validation.
- **Logistics optionality:** Planned logistics remain conditionally eligible / optional in canonical semantics. `C` provides an evaluated no-logistics reference in this experiment, but VDR-04B does not define production fallback behavior, engine routing, or missing-logistics handling.
- **Telemetry truncation remains a confound / UNKNOWN:** Season 2025 contains 204 batches with truncated telemetry histories. VDR-04B preserves those batches under the accepted evaluation protocol but does not isolate truncation as a causal explanation for telemetry performance. The present ablation therefore does not establish whether truncation explains any portion of the observed telemetry result.

---

## Reproduction commands

To reproduce the exact numerical results and JSON artifact from repository root:

```powershell
.\.venv\Scripts\python.exe scripts/vdr04b_telemetry_ablation.py `
  --data-dir sponsor_pack/data `
  --output docs/data_recon/04b_telemetry_ablation_results.json `
  --historical-vdr04a docs/data_recon/04_dispatch_predictability_results.json
```

Verify bit-for-bit SHA256 hash determinism:

```powershell
Get-FileHash docs/data_recon/04b_telemetry_ablation_results.json -Algorithm SHA256
```

Expected SHA256 digest: `1FED77EA0CAC9730340B9D4D27B91BD4BACD960E3EB76492BEB83AAA4E016806`.
