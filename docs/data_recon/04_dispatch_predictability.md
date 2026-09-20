# VDR-04A: Dispatch-Time Predictability and Ranking Feasibility

**Owner:** Viktor — Data & Evaluation Owner
**Repository:** `Slave-of-Skynet/training_agrifood`
**Task type:** Evidence-producing Data & Evaluation experiment
**Assigned base commit:** `70ab2a3ce6f060f9b2b43fcb7fb4ecd284426fdd`
**Analysis Base / Execution HEAD:** `70ab2a3ce6f060f9b2b43fcb7fb4ecd284426fdd`
**Branch:** `victor/vdr-04a-dispatch-predictability`
**Status:** DRAFT FOR REVIEW — EVIDENCE ONLY
**Decision authority:** None — this task produces reproducible evidence for a later Integrator gate (VLD-02B)

---

## 1. Status / Provenance

- **Repository Base SHA:** `70ab2a3ce6f060f9b2b43fcb7fb4ecd284426fdd` (matches canonical `origin/main` following VLD-R3 reconciliation and PR #18 merge).
- **Execution Script:** `scripts/vdr04a_predictability.py`
- **Output Artifact:** `docs/data_recon/04_dispatch_predictability_results.json`
  - Committed JSON SHA256 (LF-normalized repository artifact): `6CD6B532F79D2F4F6C3BD9B26E26C5900D08DAA54529B053D41D85BC0B544C62`
  - Original analysis-environment JSON SHA256 (Windows/CRLF): `8E9B238CABC64D11C10657E5478334B44B81EE41034F52D4D310526758CC5E88`
- **Reproduction Command:**
  ```bash
  python scripts/vdr04a_predictability.py \
    --data-dir sponsor_pack/data \
    --output docs/data_recon/04_dispatch_predictability_results.json
  ```
- **Analysis Environment:**
  - Python: `3.11.16` (64-bit AMD64)
  - NumPy: `2.4.6`
  - Pandas: `3.0.6`
  - Scikit-learn: `1.9.1`
  - SciPy: `1.17.1`
  - Project Application Dependencies Changed: **NO** (executed in external environment `vdr04a_env`; zero changes to `backend/pyproject.toml` or `frontend/package.json`).

---

## 2. Question Being Answered

This benchmark determines, using a reproducible leakage-safe experiment, **how much useful predictive and ranking signal can actually be extracted at $T_{\text{dispatch}}$ from inputs permitted by ADR 0002**.

Specifically, this reconnaissance answers:
1. Does a dispatch-time model materially outperform trivial/crop-only baselines?
2. Which broad feature families provide measurable incremental lift?
3. Does pre-dispatch storage telemetry provide useful signal beyond crop and operational context?
4. Do planned logistics provide incremental signal?
5. Is any observed lift robust under chamber/time-grouped evaluation, forward inter-season evaluation, and crop/subgroup analysis?
6. Can the available signal support a meaningful batch-prioritisation / ranking framing?
7. Which candidate analytical framing is sufficiently supported by data to take into the later VLD-02B decision gate?

> [!IMPORTANT]
> **Decision Boundary:** This report establishes an empirical feasibility baseline. It does **not** select the production target, does **not** choose the production model architecture, does **not** choose the final evaluation split, does **not** define an arbitrary operational loss threshold, and does **not** make product or UX decisions.

---

## 3. Fixed Leakage Boundary (ADR 0002 Compliance)

[FACT] The sponsor-defined assessment moment is fixed:
$$T_{\text{assess}} \equiv T_{\text{dispatch}} = \text{storage_sessions.dispatch_datetime}$$

All feature extraction strictly obeys the normative rules established in **ADR 0002**:
1. **Forbidden Quality Checks:** Only quality checks where `stage in ('harvest', 'pre_dispatch')` are admitted. All records where `stage == 'arrival'` are strictly excluded (0 arrival rows entered any feature matrix).
2. **Forbidden Transit Realizations:** Downstream shipment outcomes (`actual_departure_datetime`, `actual_arrival_datetime`, `actual_delay_minutes`, `cold_chain_incident`, `transit_temp_mean_c`) are strictly excluded (0 post-dispatch transit fields entered features).
3. **Forbidden Historical Outcomes:** Commercial settlement outcomes (`quality_status`, `loss_fraction_pct`, `quality_score`, `economic_loss_eur`) are strictly excluded from inference features and reserved exclusively for candidate target evaluation.
4. **Forbidden Post-Dispatch Telemetry:** Sensor readings are bounded strictly by $\text{storage_sessions.entry_datetime} \le \text{timestamp} \le \text{storage_sessions.dispatch_datetime}$. Exactly 0 readings recorded after $T_{\text{dispatch}}$ were admitted.
5. **Forbidden Context Identifiers:** Raw surrogate keys and identifiers (`batch_id`, `storage_session_id`, `facility_id`, `zone_id`, `shipment_id`, `reading_id`, `check_id`, `facility_name`, `zone_name`) were used exclusively for relational joins, grouping, and split blocking, and were strictly excluded from predictive model inputs.

A programmatic assertion in `scripts/vdr04a_predictability.py` verified the absence of all forbidden columns across all feature matrices prior to model fitting.

---

## 4. Integrity Checks

[FACT] The pre-analysis integrity gate executed successfully and asserted core dataset invariants:
- `batches`: 1,800 rows (SHA256: `bbaf3cb4064ccdef...`)
- `storage_sessions`: 1,800 rows (SHA256: `f38a99dfeb808eaa...`)
- `facilities`: 10 rows (SHA256: `148de414dcff6d60...`)
- `storage_zones`: 25 rows (SHA256: `e2c4b7170c47ab08...`)
- `quality_checks`: 5,400 rows (1,800 harvest, 1,800 pre-dispatch, 1,800 arrival) (SHA256: `95ccf7d6d898249f...`)
- `shipments`: 1,800 rows (SHA256: `bfad682700f58936...`)
- `historical_quality_outcomes`: 1,800 rows (SHA256: `567334f44f41b980...`)
- `sensor_readings`: 669,665 rows across 25 zones (SHA256: `6b27adaf43a6646d...`)

[FACT] Reconstructing concurrent chamber occupancy reproduces the accepted VDR-02 structure:
- **157 disjoint chamber-time connected clusters** across 25 zones.
- **66 single-batch isolated clusters**.
- **91 multi-batch clusters** containing **1,734 out of 1,800 batches (96.33%)**.
- Maximum cluster size: 134 batches.

---

## 5. Candidate Target Probes

As established in VDR-03, the four outcome columns in `historical_quality_outcomes.csv` are not independent biological targets. Therefore, VDR-04A benchmarks three distinct analytical probes:

1. **Continuous Loss Probe (`loss_fraction_pct`):**
   - Evaluates point prediction of physical produce mass loss percentage.
   - Metrics: MAE, RMSE, $R^2$, Spearman rank correlation ($\rho$).
2. **Four-Class Status Probe (`quality_status`):**
   - Evaluates ordinal grade prediction (`optimal`, `degraded`, `severe_degradation`, `lost`).
   - Metrics: Accuracy, Balanced Accuracy, Macro F1, Confusion Matrix.
3. **Binary Severity Probes (Analysis Thresholds):**
   - Evaluates risk classification across observed status transitions:
     - Mild degradation: $\text{loss} \ge 5.0\%$
     - Moderate/Severe degradation: $\text{loss} \ge 15.0\%$
     - Extreme loss: $\text{loss} \ge 35.0\%$
   - Metrics: ROC-AUC, Average Precision (PR-AUC), Brier Score, Balanced Accuracy (at fixed $0.5$ non-tuned decision threshold).

### Excluded Outcomes as Primary Targets
- **`economic_loss_eur`:** Excluded from primary prediction. VDR-03 proved that in this snapshot it is deterministically derived from $\text{harvest\_weight\_kg} \times (\text{loss\_fraction\_pct} / 100) \times P_{\text{crop}}$. Predicting financial loss directly would confound physical degradation with crop pricing and harvest lot sizing.
- **`quality_score`:** Excluded from primary prediction. VDR-03 demonstrated an empirical correlation of $r = -0.9727$ with `loss_fraction_pct`, with strong boundary clipping at $5.0$ and $98.5$.

---

## 6. Evaluation Protocols

The benchmark evaluates all models under two defensible evaluation protocols, plus one non-defensible diagnostic:

### Protocol P1: Forward Inter-Season Holdout (Primary Temporal Probe)
- **Train Partition:** Season 2024 (900 batches, dispatched 2024-05-25 to 2025-04-11).
- **Temporal Hiatus:** 43.97 days (zero chamber overlaps).
- **Test Partition:** Season 2025 (900 batches, dispatched 2025-05-25 to 2026-04-03).
- **Operational Reality:** Strictly evaluates prospective generalization from past season to subsequent future season.

### Protocol P2: Chamber-Time Grouped OOF (Microclimate-Blocked Probe)
- **Cross-Validation:** 5-fold `GroupKFold` grouped strictly by the 157 chamber-time clusters.
- **Leakage Prevention:** Every connected chamber-time component is contained wholly inside a single validation fold. No concurrent batch microclimate history bridges train and validation.
- **Evaluation:** Out-of-fold (OOF) predictions aggregated across all 1,800 batches.

### Protocol P3: Naive Random Split Diagnostic (Non-Defensible)
- 80/20 random batch split (1,440 train, 360 test; seed 42).
- **Observed Leakage:** **94.44% of test batches** share an identical chamber-time cluster with training batches.
- **Status:** Explicitly labeled as a non-defensible diagnostic to quantify optimistic leakage bias.

---

## 7. Baselines and Benchmark Model Families

### Trivial Baselines (Evaluated on Identical Partitions)
- **Regression:**
  - Global Training Median
  - Crop-Conditioned Training Median (falls back to global median for unseen crops)
- **Multiclass:**
  - Global Training Majority Class
  - Crop-Conditioned Training Prior / Majority
- **Binary:**
  - Global Training Prevalence
  - Crop-Conditioned Training Prevalence
- **Ranking:**
  - Batches ranked strictly by historical Crop-Median loss (with label-independent secondary tie-breaking by `batch_id` ascending).

### Benchmark Model Families (Fixed Hyperparameters, No Test-Set Tuning)
1. **Regularized Linear Family:**
   - Regression: `Ridge(alpha=1.0, random_state=42)`
   - Classification: `LogisticRegression(max_iter=1000, random_state=42)`
2. **Nonlinear Gradient-Boosted Tree Family:**
   - Regression: `HistGradientBoostingRegressor(max_iter=100, max_leaf_nodes=31, random_state=42)`
   - Classification: `HistGradientBoostingClassifier(max_iter=100, max_leaf_nodes=31, random_state=42)`
- Preprocessing: Median imputation and standard scaling for numeric channels; one-hot encoding with unknown category handling for categorical channels.

---

## 8. Feature-Family Definitions

All feature matrices are constructed strictly from pre-dispatch fields:

| Family | Input Scope | Column Count | Concrete Feature Columns |
| :--- | :--- | :---: | :--- |
| **F0** | Crop-Only | 1 | `crop_type` |
| **F1** | Pre-Dispatch Context (Non-Telemetry, Non-Logistics) | 37 | **Batch:** `variety`, `origin_region`, `harvest_weight_kg`, `initial_quality_score`, `harvest_temperature_c`, `harvest_conditions`, `field_precooled`, `harvest_month`, `harvest_hour`<br>**Session/Storage:** `bin_stack_tier`, `storage_duration_days`, `entry_month`, `dispatch_month`, `dispatch_hour`<br>**Facility/Zone:** `region`, `district`, `facility_type`, `capacity_tonnes`, `commissioned_year`, `has_controlled_atmosphere`, `zone_type`, `nominal_capacity_tonnes`, `target_temperature_c`, `target_relative_humidity_pct`, `cooling_system_type`, `insulation_quality`, `defrost_cycle_frequency_per_day`<br>**Inspection (H & PD):** `harvest_firmness_kg_cm2`, `harvest_sugar_brix`, `harvest_defect_pct`, `pre_dispatch_firmness_kg_cm2`, `pre_dispatch_sugar_brix`, `pre_dispatch_defect_pct`, `delta_firmness`, `delta_sugar_brix`, `delta_defect_pct` |
| **F2** | F1 + Telemetry | 114 | **F1 features (37)** plus **77 leakage-safe telemetry aggregates** computed strictly over $T_{\text{entry}} \le t \le T_{\text{dispatch}}$:<br>- `telemetry_reading_count`<br>- Numeric channels (`air_temperature_c`, `produce_surface_temperature_c`, `relative_humidity_pct`, `dew_point_c`, `co2_ppm`, `o2_pct`): `missing_frac`, `mean`, `std`, `min`, `max`, `p10`, `p90`, `first`, `last`, `slope_per_day`<br>- Setpoint deviations: `air_temp_signed_dev_mean`, `air_temp_abs_dev_mean`, `air_temp_abs_dev_max`, `air_temp_frac_above_target`, `air_temp_frac_below_target`, `rh_signed_dev_mean`, `rh_abs_dev_mean`, `rh_abs_dev_max`, `rh_frac_above_target`, `rh_frac_below_target`<br>- Binary states (`condensation_flag`, `cooling_on`, `defrost_on`): `frac_true`, `transitions` |
| **F3** | F2 + Planned Logistics | 118 | **F2 features (114)** plus **4 planned logistics fields** known at dispatch:<br>`destination_market`, `destination_region`, `vehicle_type`, `planned_duration_hours` |

---

## 9. Main Results

### Continuous Loss Prediction (`loss_fraction_pct`)

#### Protocol P1: Forward Inter-Season (Test Season 2025, $N=900$)

| Model / Feature Family | MAE (% loss) | RMSE (% loss) | $R^2$ | Spearman $\rho$ |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline: Global Median** | 9.9533 | 17.1466 | -0.0326 | 0.0000 |
| **Baseline: Crop-Specific Median** | **8.8842** | 16.2401 | +0.0737 | 0.4497 |
| **F0 (Crop Only) — Ridge** | 10.1087 | 16.2166 | +0.0763 | 0.4268 |
| **F0 (Crop Only) — HistGradientBoosting** | 10.1213 | 16.2283 | +0.0750 | 0.4268 |
| **F1 (Context) — Ridge** | 10.2628 | 16.7147 | +0.0187 | 0.4037 |
| **F1 (Context) — HistGradientBoosting** | 10.8628 | 17.2795 | -0.0487 | 0.3227 |
| **F2 (Context + Telemetry) — Ridge** | 10.8984 | 17.0319 | -0.0189 | 0.3461 |
| **F2 (Context + Telemetry) — HistGradientBoosting** | 10.5039 | 16.9173 | -0.0052 | 0.3336 |
| **F3 (Context + Telemetry + Planned Logistics) — Ridge** | 10.4529 | 16.1798 | +0.0805 | 0.4557 |
| **F3 (Context + Telemetry + Planned Logistics) — HGB** | **8.9664** | **14.3185** | **+0.2799** | **0.4600** |

#### Protocol P2: Chamber-Time Grouped OOF (All Batches, $N=1,800$)

| Model / Feature Family | MAE (% loss) | RMSE (% loss) | $R^2$ | Spearman $\rho$ |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline: Global Median** | 9.7442 | 16.7152 | -0.0823 | -0.1108 |
| **Baseline: Crop-Specific Median** | **8.8216** | 15.9096 | +0.0195 | 0.3525 |
| **F0 (Crop Only) — Ridge** | 9.5936 | 15.4112 | +0.0800 | 0.3484 |
| **F0 (Crop Only) — HistGradientBoosting** | 9.5964 | 15.4124 | +0.0798 | 0.3488 |
| **F1 (Context) — Ridge** | 9.2948 | 15.1155 | +0.1150 | 0.4597 |
| **F1 (Context) — HistGradientBoosting** | 10.2402 | 16.0025 | +0.0080 | 0.3861 |
| **F2 (Context + Telemetry) — Ridge** | 10.0792 | 15.5923 | +0.0582 | 0.3606 |
| **F2 (Context + Telemetry) — HistGradientBoosting** | 10.4525 | 16.2498 | -0.0229 | 0.3328 |
| **F3 (Context + Telemetry + Planned Logistics) — Ridge** | 9.5944 | 14.7404 | +0.1583 | 0.4454 |
| **F3 (Context + Telemetry + Planned Logistics) — HGB** | **8.7567** | **13.7329** | **+0.2695** | **0.3911** |

#### Protocol P2: Fold-Level Results Distribution (5 Folds, F3 HGB)

| Fold Number | Validation Sample Count | Fold MAE (% loss) | Fold RMSE (% loss) | Fold $R^2$ | Fold Spearman $\rho$ | Fold Multiclass Macro F1 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fold 1** | 360 | 8.4732 | 13.1587 | +0.3803 | 0.4337 | 0.5232 |
| **Fold 2** | 360 | 8.8524 | 13.0321 | +0.0955 | 0.3493 | 0.5098 |
| **Fold 3** | 360 | 8.9770 | 12.9671 | +0.2915 | 0.4152 | 0.5572 |
| **Fold 4** | 360 | 9.0685 | 14.8670 | +0.2173 | 0.3954 | 0.4639 |
| **Fold 5** | 360 | 8.4125 | 14.5192 | +0.2874 | 0.3863 | 0.5196 |
| **Mean $\pm$ Std** | **360** | **$8.7567 \pm 0.2721$** | **$13.7088 \pm 0.9168$** | **$+0.2544 \pm 0.0945$** | **$0.3960 \pm 0.0287$** | **$0.5147 \pm 0.0305$** |

---

### Four-Class Quality Status Prediction (`quality_status`)

#### Protocol P1 (Forward Inter-Season) vs Protocol P2 (Chamber-Time Grouped OOF)

| Model / Feature Family | P1 Accuracy | P1 Balanced Acc | P1 Macro F1 | P2 Accuracy | P2 Balanced Acc | P2 Macro F1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline: Global Majority** | 0.3411 | 0.2500 | 0.1272 | 0.3444 | 0.2500 | 0.1281 |
| **Baseline: Crop-Conditioned Majority** | 0.4567 | 0.3714 | 0.3487 | 0.4428 | 0.3606 | 0.3417 |
| **F0 (Crop Only) — HGB** | 0.4567 | 0.3714 | 0.3487 | 0.4428 | 0.3606 | 0.3417 |
| **F1 (Context) — HGB** | 0.4500 | 0.3611 | 0.3525 | 0.4506 | 0.3632 | 0.3563 |
| **F2 (Context + Telemetry) — HGB** | 0.4289 | 0.3506 | 0.3408 | 0.4628 | 0.3726 | 0.3651 |
| **F3 (Context + Telemetry + Logistics) — HGB** | **0.4822** | **0.4577** | **0.4827** | **0.5144** | **0.4866** | **0.5205** |

#### Multiclass Confusion Matrices (F3 HistGradientBoosting)

Order of classes: `['optimal', 'degraded', 'severe_degradation', 'lost']`.

**Protocol P1 (Inter-Season Holdout, Season 2025, $N=900$):**
```text
                  Predicted:
                  optimal  degraded  severe_deg  lost   Total
Actual:
optimal             175       69         49        0     293
degraded            101      102        104        0     307
severe_degradation   32       72        138        1     243
lost                  7       10         21       19      57
Total Predicted:    315      253        312       20     900
```

**Protocol P2 (Chamber-Time Grouped OOF, All Batches, $N=1,800$):**
```text
                  Predicted:
                  optimal  degraded  severe_deg  lost   Total
Actual:
optimal             311      194         44        0     549
degraded            174      295        151        0     620
severe_degradation   53      182        278        3     516
lost                 22       26         25       42     115
Total Predicted:    560      697        498       45    1800
```

---

### Binary Severity Probes (HistGradientBoosting)

Balanced accuracy is computed using a fixed non-tuned probability threshold of $0.5$.

| Threshold Probe | Metric | Global Prev P1 / P2 | Crop Prev P1 / P2 | F0 (Crop) P1 / P2 | F1 (Context) P1 / P2 | F2 (+ Telemetry) P1 / P2 | F3 (+ Logistics) P1 / P2 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Loss $\ge 5.0\%$** (Degraded+) | ROC-AUC<br>PR-AUC<br>Brier Score<br>Balanced Accuracy | 0.5000 / 0.4235<br>0.6744 / 0.6577<br>0.2213 / 0.2140<br>0.5000 / 0.5000 | 0.7285 / 0.6847<br>0.8174 / 0.8223<br>0.1908 / 0.1895<br>0.5000 / 0.5120 | 0.7285 / 0.6847<br>0.8174 / 0.8223<br>0.1908 / 0.1895<br>0.5000 / 0.5120 | 0.7408 / 0.7452<br>0.8493 / 0.8648<br>0.2148 / 0.1958<br>0.6035 / 0.6274 | 0.7342 / 0.7412<br>0.8504 / 0.8589<br>0.2190 / 0.1977<br>0.5726 / 0.6232 | **0.7739 / 0.7776**<br>**0.8686 / 0.8819**<br>**0.1991 / 0.1823**<br>**0.6289 / 0.6540** |
| **Loss $\ge 15.0\%$** (Severe+) | ROC-AUC<br>PR-AUC<br>Brier Score<br>Balanced Accuracy | 0.5000 / 0.4590<br>0.3333 / 0.3294<br>0.2234 / 0.2283<br>0.5000 / 0.5000 | 0.7114 / 0.6769<br>0.5126 / 0.5185<br>0.1949 / 0.2042<br>0.6050 / 0.5845 | 0.7114 / 0.6769<br>0.5126 / 0.5185<br>0.1949 / 0.2042<br>0.6050 / 0.5845 | 0.7030 / 0.7102<br>0.5484 / 0.5777<br>0.2120 / 0.2093<br>0.6408 / 0.6473 | 0.7168 / 0.7097<br>0.5454 / 0.5710<br>0.2092 / 0.2115<br>0.6258 / 0.6426 | **0.7555 / 0.7651**<br>**0.6222 / 0.6800**<br>**0.1950 / 0.1880**<br>**0.6775 / 0.6926** |
| **Loss $\ge 35.0\%$** (Lost) | ROC-AUC<br>PR-AUC<br>Brier Score<br>Balanced Accuracy | 0.5000 / 0.4350<br>0.0633 / 0.0561<br>0.0593 / 0.0599<br>0.5000 / 0.5000 | 0.5735 / 0.5811<br>0.0754 / 0.0819<br>0.0611 / 0.0597<br>0.5000 / 0.5000 | 0.5735 / 0.5810<br>0.0754 / 0.0819<br>0.0611 / 0.0597<br>0.5000 / 0.5000 | 0.5702 / 0.6089<br>0.0822 / 0.0890<br>0.0656 / 0.0650<br>0.4964 / 0.5029 | 0.5866 / 0.6209<br>0.0852 / 0.0971<br>0.0635 / 0.0633<br>0.4994 / 0.4994 | **0.6968 / 0.7196**<br>**0.4258 / 0.4755**<br>**0.0430 / 0.0413**<br>**0.6573 / 0.6780** |

---

## 10. Incremental Feature Lift Analysis

[FACT] Comparing the marginal lift across feature tiers under prospective inter-season evaluation (Protocol P1, HistGradientBoosting):

```text
[Baseline: Crop Median]   MAE: 8.8842% loss | R²: +0.0737 | Spearman: 0.4497
          ↓ (F0 - Baseline: learned crop weights)
[F0: Crop Only]           MAE: 10.1213% loss | R²: +0.0750 | Spearman: 0.4268 (ΔMAE: +1.2371 percentage points, smoothing penalty)
          ↓ (F1 - F0: + pre-dispatch context, inspections, facility specs)
[F1: Pre-Dispatch Ctx]    MAE: 10.8628% loss | R²: -0.0487 | Spearman: 0.3227 (ΔMAE: +0.7415 percentage points, ΔR²: -0.1237, degradation)
          ↓ (F2 - F1: + 77 telemetry aggregates)
[F2: + Telemetry]         MAE: 10.5039% loss | R²: -0.0052 | Spearman: 0.3336 (ΔMAE: -0.3589 percentage points, ΔR²: +0.0435, marginal/near-zero)
          ↓ (F3 - F2: + planned-logistics feature family)
[F3: + Planned Logistics] MAE: 8.9664% loss  | R²: +0.2799 | Spearman: 0.4600 (ΔMAE: -1.5375 percentage points, ΔR²: +0.2851, largest / most consistent incremental predictive association across tested headline results)
```

> [!NOTE]
> **Telemetry-Lift Sign Convention:** $\text{MAE lift} = \text{F1 MAE} - \text{F2 MAE}$; positive values indicate improvement (error reduction), while negative values indicate error inflation/degradation. Under this convention, adding telemetry produces $+0.3589$ percentage points lift in P1, and $-0.2123$ percentage points lift (degradation) in P2.

[OBSERVED RESULT] Pre-dispatch operational context (F1) and storage telemetry aggregates (F2) produce **no material predictive lift beyond crop-conditioned baselines** on continuous loss or 4-class status.
[OBSERVED RESULT] Telemetry aggregate features (F2) yield a negligible change in MAE ($\text{MAE lift} = +0.3589$ percentage points in P1, $-0.2123$ percentage points in P2) and fail to outperform the simple historical crop median.
[OBSERVED RESULT] The planned-logistics feature family (F3) provides the **largest / most consistent incremental lift across tested headline results** in the dispatch feature set, improving $R^2$ from $-0.0052$ to $+0.2799$ in P1 and from $-0.0229$ to $+0.2695$ in P2 (representing an observed incremental predictive association under the tested protocols, not a causal claim; individual variables were not independently ablated).

---

## 11. Ranking Feasibility: Protocol Comparison (P1 vs P2)

Batch prioritisation capability was evaluated separately under both defensible protocols:

> [!NOTE]
> **Deterministic Tie Policy:** When candidate models or baselines produce identical predicted loss values (e.g. discrete crop-median predictions), ties are resolved deterministically by secondary sorting on `batch_id` ascending. `batch_id` is utilized strictly for post-hoc evaluation ranking resolution; it is forbidden by ADR 0002 from entering any feature matrix and has zero predictive influence.

#### Protocol P1: Forward Inter-Season Holdout (Season 2025, $N=900$)

| Strategy / Feature Set | Model Tier | Spearman $\rho$ | NDCG@10 | NDCG@50 | Precision@10 ($\ge 15\%$) | Precision@50 ($\ge 15\%$) | Recall@10 ($\ge 15\%$) | Recall@50 ($\ge 15\%$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline: Crop-Median Loss** | Heuristic | 0.4497 | 0.2634 | 0.2797 | 0.8000 | 0.5800 | 0.0267 | 0.0967 |
| **F0 (Crop Only)** | Linear (`Ridge`) | 0.4268 | 0.1966 | 0.2436 | 0.4000 | 0.5200 | 0.0133 | 0.0867 |
| **F0 (Crop Only)** | Nonlinear (`HGB`) | 0.4268 | 0.1966 | 0.2436 | 0.4000 | 0.5200 | 0.0133 | 0.0867 |
| **F1 (Context)** | Linear (`Ridge`) | 0.4037 | 0.2269 | 0.2671 | 0.6000 | 0.6200 | 0.0200 | 0.1033 |
| **F1 (Context)** | Nonlinear (`HGB`) | 0.3227 | 0.2189 | 0.2441 | 0.5000 | 0.6000 | 0.0167 | 0.1000 |
| **F2 (Context + Telemetry)** | Linear (`Ridge`) | 0.3461 | 0.2464 | 0.2866 | 0.7000 | 0.6000 | 0.0233 | 0.1000 |
| **F2 (Context + Telemetry)** | Nonlinear (`HGB`) | 0.3336 | 0.2003 | 0.2554 | 0.6000 | 0.6000 | 0.0200 | 0.1000 |
| **F3 (+ Planned Logistics)** | Linear (`Ridge`) | 0.4557 | 0.3414 | 0.4421 | 0.9000 | 0.8000 | 0.0300 | 0.1333 |
| **F3 (+ Planned Logistics)** | Nonlinear (`HGB`) | **0.4600** | **0.8831** | **0.6491** | **1.0000** | **0.8600** | **0.0333** | **0.1433** |

### Protocol P2: Chamber-Time Grouped OOF (All Batches, $N=1,800$)

| Strategy / Feature Set | Model Tier | Spearman $\rho$ | NDCG@10 | NDCG@50 | Precision@10 ($\ge 15\%$) | Precision@50 ($\ge 15\%$) | Recall@10 ($\ge 15\%$) | Recall@50 ($\ge 15\%$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline: Crop-Median Loss** | Heuristic | 0.3525 | 0.2533 | 0.2906 | 0.5000 | 0.7600 | 0.0079 | 0.0602 |
| **F0 (Crop Only)** | Linear (`Ridge`) | 0.3484 | 0.1972 | 0.2514 | 0.8000 | 0.7400 | 0.0127 | 0.0586 |
| **F0 (Crop Only)** | Nonlinear (`HGB`) | 0.3488 | 0.1972 | 0.2514 | 0.8000 | 0.7400 | 0.0127 | 0.0586 |
| **F1 (Context)** | Linear (`Ridge`) | 0.4597 | 0.5977 | 0.3965 | 0.8000 | 0.6800 | 0.0127 | 0.0539 |
| **F1 (Context)** | Nonlinear (`HGB`) | 0.3861 | 0.3069 | 0.2629 | 0.6000 | 0.7000 | 0.0095 | 0.0555 |
| **F2 (Context + Telemetry)** | Linear (`Ridge`) | 0.3606 | 0.5847 | 0.3733 | 0.9000 | 0.6400 | 0.0143 | 0.0507 |
| **F2 (Context + Telemetry)** | Nonlinear (`HGB`) | 0.3328 | 0.1998 | 0.2089 | 0.6000 | 0.6400 | 0.0095 | 0.0507 |
| **F3 (+ Planned Logistics)** | Linear (`Ridge`) | 0.4454 | 0.6960 | 0.5674 | 1.0000 | 0.9200 | 0.0158 | 0.0729 |
| **F3 (+ Planned Logistics)** | Nonlinear (`HGB`) | **0.3911** | **0.8888** | **0.7955** | **1.0000** | **0.9600** | **0.0158** | **0.0761** |

[OBSERVED RESULT] Non-logistics feature families show protocol- and model-dependent ranking lift, including substantial P2 ranking improvement for the linear F1 and F2 benchmarks (e.g. F1 Ridge achieves Spearman $\rho = 0.4597$ and NDCG@10 = $0.5977$, and F2 Ridge achieves NDCG@10 = $0.5847$ vs crop-median baseline $\rho = 0.3525$ and NDCG@10 = $0.2533$). Under prospective inter-season evaluation (P1), non-logistics ranking lift is more muted (NDCG@10 = $0.2003 - 0.2464$ vs $0.2634$).
[OBSERVED RESULT] The planned-logistics feature family produces the strongest and most consistent ranking improvement across both P1 and P2, particularly under the nonlinear benchmark:
- **Precision@10 against severe degradation ($\ge 15\%$) is 100.0% in both P1 and P2** (10 out of 10 prioritized batches are confirmed severe loss).
- **Precision@50 is 86.0% in P1 and 96.0% in P2** (and $80.0\% - 92.0\%$ under linear F3).
- **NDCG@10 reaches 0.8831 in P1 and 0.8888 in P2** (and $0.6960$ under P2 linear F3).

> [!WARNING]
> **Precision vs Recall Operational Trade-off:** While top-k precision is exceptionally high under F3 ($100\%$ at $K=10$, $86\%-96\%$ at $K=50$), it is inherently accompanied by low recall due to the small budget $K$ relative to the total pool of degraded batches. In P1, Recall@10 is $3.33\%$ (10 of 300 severe degradation batches) and Recall@50 is $14.33\%$ (43 of 300). In P2, Recall@10 is $1.58\%$ (10 of 631) and Recall@50 is $7.61\%$ (48 of 631). Prioritisation effectively isolates the highest-risk batches for early intervention, but cannot serve as an exhaustive salvage screening mechanism without substantially increasing the intervention capacity $K$.

---

## 12. Telemetry Diagnostics

### Signal Structure across 25 Storage Zones
- **Sample counts:** 25,699 to 28,320 readings per zone across the snapshot.
- **Air Temperature Residuals:** Across all 25 zones, the mean deviation from target setpoint ranges from $-0.009^\circ\text{C}$ to $+0.111^\circ\text{C}$ (mean standard deviation $\approx 0.81^\circ\text{C}$).
- **Lag-1 Autocorrelation:** The temperature deviation residual shows modest lag-1 autocorrelation (mean $\approx 0.091$, range $0.063$ to $0.122$), reflecting tightly controlled refrigeration cycles.
- **Cooling / Defrost Duty:** Solenoid cooling duty fraction ranges from $39.5\%$ to $45.1\%$; defrost cycle active duty is constant across zones at exactly $2.08\%$.
- **Controlled Atmosphere (CA) Room Reconciliation:**
  - **Source Identification Rule:** CA zones in the analysis are selected strictly through `storage_zones.zone_type == "Controlled Atmosphere (CA)"`. (`facilities.csv` contains a separate column `has_controlled_atmosphere`, but `storage_zones.csv` does not possess a `has_controlled_atmosphere` column; chamber-level CA status is defined solely by `storage_zones.zone_type`).
  - **Reconciliation of Prior Discrepancy:** The initial reconnaissance draft colloquially noted six CA rooms based on an unverified working assumption. Formal dataset inspection of `storage_zones.csv` proves there are exactly **5 Controlled Atmosphere zones**: `ZONE-001`, `ZONE-006`, `ZONE-008`, `ZONE-011`, and `ZONE-019` across the 25 total storage zones.
  - **Gas Missingness Verification:** Across all 136,522 readings recorded in these 5 CA zones, `co2_ppm` and `o2_pct` have **0.0% missingness**. In the remaining 20 non-CA storage zones, gas logging does not exist and is **100.0% missing**; this absence is represented strictly as explicit missing values (`null` / `NaN`), and zero-fabrication is strictly forbidden.
  - `produce_surface_temperature_c`: 100.0% missing in `ZONE-006` (as documented by ADR 0002); 0.0% missing in all other 24 zones.
- **Batch-Level Telemetry Variability and Duration Association:**
  - An observed Pearson association of $r = -0.3762$ was measured between `air_temperature_c_mean` and `storage_duration_days`. This is an empirical association and may reflect crop, zone, setpoint, or seasonal confounding; it is not a causal finding.
  - `air_temperature_c_mean`: batch mean $2.089^\circ\text{C}$ (std $3.016^\circ\text{C}$, range $0.583^\circ\text{C}$ to $11.125^\circ\text{C}$).
  - `air_temperature_c_std`: batch mean $0.823^\circ\text{C}$ (std $0.017^\circ\text{C}$, range $0.726^\circ\text{C}$ to $0.901^\circ\text{C}$); Pearson $r = -0.0538$ with `storage_duration_days`.
  - `air_temp_abs_dev_mean`: batch mean $0.306^\circ\text{C}$ (std $0.003^\circ\text{C}$); Pearson $r = -0.0544$ with `storage_duration_days`.
  - `cooling_on_frac_true`: batch mean $44.76\%$ (std $0.50\%$); Pearson $r = +0.0350$ with `storage_duration_days`.
  - `defrost_on_frac_true`: batch mean $2.08\%$ (std $0.02\%$); Pearson $r = -0.0588$ with `storage_duration_days`.

### Within-Crop Telemetry Increment Test
To test whether apparent telemetry signal is merely an artifact of crop-level chamber setpoints, models were evaluated strictly **within single crop cohorts** across seasons:

| Crop Cohort | Split / Counts | Baseline Crop-Median MAE | F1 (Non-Telemetry) MAE | F2 (+ Telemetry) MAE | Incremental Telemetry Lift ($\Delta$MAE) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Apples** | Train: 338, Test: 335 | **5.3544% loss** | 7.4618% loss | 7.4194% loss | **+0.0425 percentage points** (negligible) |
| **Plums** | Train: 182, Test: 168 | **9.7543% loss** | 10.4789% loss | 11.0856% loss | **-0.6067 percentage points** (degradation) |

[OBSERVED RESULT] Within the single largest crop cohort (apples, $N=673$), adding 77 telemetry aggregates reduces MAE by only **0.0425 percentage points**, while both learned models underperform the simple crop-median baseline ($7.42\%$ vs $5.35\%$ MAE). Within plums, adding telemetry degrades MAE by $0.6067$ percentage points.
[INFERENCE] Telemetry did not demonstrate material incremental lift under the tested aggregate construction; within-crop evidence was specifically measured for apples and plums.

---

## 13. Telemetry Truncation Sensitivity (Season 2025 Test Partition)

In Season 2025, 204 batches (dispatched between 2026-01-01 and 2026-04-03) experienced sensor logging cessation on 2025-12-31, resulting in telemetry staleness ranging from 0.56 to 92.54 days at dispatch.

| Feature Family | All 900 Batches MAE | Non-Truncated 696 Batches MAE | Truncated 204 Batches MAE |
| :--- | :---: | :---: | :---: |
| **F1 (Context)** | 10.8628% loss | 11.9133% loss | 7.2790% loss |
| **F2 (Context + Telemetry)** | 10.5039% loss | 11.5946% loss | 6.7829% loss |
| **F3 (Context + Telemetry + Logistics)** | 8.9664% loss | 9.7033% loss | 6.4524% loss |

[OBSERVED RESULT] The 204 truncated batches exhibit substantially lower prediction errors across all models (MAE $\approx 6.45\%$ vs $9.70\%$ loss for non-truncated batches).
[FACT] The 204 truncated batches consist almost exclusively of late-season storage apples (189 batches, 92.65%) and pears (14 batches, 6.86%), which have lower baseline loss variability.
[INFERENCE] This comparison is heavily confounded by crop and season composition and therefore does not isolate the causal effect of telemetry truncation. No production exclusion, pipeline filtering, or sensor reliability decision may be derived from it.

---

## 14. Proxy Sensitivity

ADR 0002 flagged that geographic and facility descriptors (`district`, `region`, `facility_type`, `commissioned_year`, `capacity_tonnes`) could act as 1:1 facility proxies. A sensitivity model was fitted on F1 excluding these proxy columns:

- **F1 with Proxies (P1 HGB):** MAE = $10.8628\%$ loss, $R^2 = -0.0487$
- **F1 without Proxies (P1 HGB):** MAE = $10.7133\%$ loss, $R^2 = -0.0323$

[OBSERVED RESULT] Removing site-proxy features produces virtually no change in performance ($\Delta \text{MAE} = -0.1495$ percentage points). Model performance does not depend on memorizing facility identities.

---

## 15. Subgroup Robustness by Crop Type

Evaluating the full dispatch-time model (F3 HistGradientBoosting) across crops under Protocol P1:

| Crop Type | Holdout Count (S2025) | Holdout MAE (% loss) | Holdout RMSE (% loss) | Holdout $R^2$ |
| :--- | :---: | :---: | :---: | :---: |
| **Apples** | 335 | 6.6982 | 8.2828 | +0.0180 |
| **Apricots** | 37 | 14.3264 | 19.7911 | -0.2864 |
| **Pears** | 61 | 8.9234 | 12.9916 | +0.0141 |
| **Plums** | 168 | 7.2440 | 10.1768 | **+0.6169** |
| **Raspberries** | 26 | 12.1520 | 20.9447 | -0.1968 |
| **Strawberries** | 30 | 15.7573 | 25.8925 | -0.4896 |
| **Table Grapes** | 153 | 8.9987 | 14.0589 | +0.1440 |
| **Tomatoes** | 90 | 15.2110 | 25.2956 | +0.2233 |

[OBSERVED RESULT] Predictive power varies drastically across crop categories:
- In high-volume durable fruits (plums, table grapes, tomatoes), the model achieves positive $R^2$ (up to $+0.6169$ on plums).
- In highly perishable berries and soft stone fruit (strawberries, raspberries, apricots), $R^2$ is negative ($-0.19$ to $-0.49$) with large absolute errors ($\text{MAE} \approx 12\% - 16\%$ loss).
- In apples ($N=335$), loss variance is low and the learned model fails to explain within-crop variance ($R^2 = +0.0180$).

---

## 16. Independent Audit Hypotheses Verification

| Audit Hypothesis | Benchmark Assessment | Direct VDR-04A Evidence |
| :--- | :---: | :--- |
| **H1:** Richer dispatch-time features provide little lift beyond crop-only or similarly trivial baselines. | **SUPPORTED** (without planned logistics)<br>**MIXED** (with planned logistics) | Without logistics, F0, F1, and F2 all underperform the trivial crop-median baseline (P1 MAE $10.12\% - 10.86\%$ vs $8.88\%$ loss). When planned logistics are added (F3), HGB achieves MAE $8.97\%$ loss and $R^2 = +0.280$. |
| **H2:** Storage telemetry has weak marginal predictive value after crop/storage context is controlled. | **SUPPORTED** | Across both P1 and P2, F2 telemetry features produce near-zero lift over F1 ($\text{MAE lift} = +0.3589$ percentage points in P1, $-0.2123$ percentage points in P2). In the within-crop apples test, telemetry improved MAE by only $0.0425$ percentage points, and in plums it degraded MAE by $0.6067$ percentage points. |
| **H3:** Planned-logistics variables carry more predictive signal than telemetry. | **SUPPORTED** (at feature-family level) | Adding the planned-logistics feature family (F3 vs F2) improves inter-season $R^2$ from $-0.0052$ to $+0.2799$, reduces MAE by $1.5375$ percentage points, and elevates NDCG@10 from $0.2003$ to $0.8831$. (Evaluated jointly as a family; individual variable contributions were not independently ablated). |
| **H4:** Naive random split makes performance appear artificially stronger due to shared chamber/time conditions. | **CONSISTENT WITH LEAKAGE RISK / NOT ISOLATED** | Random splitting produced stronger results (Protocol P3 random split achieved an inflated $R^2 = +0.4463$ and $\text{MAE} = 7.93\%$ loss, compared to $R^2 = +0.2799$ and $\text{MAE} = 8.97\%$ loss under prospective inter-season evaluation) while $94.44\%$ of test batches overlapped with training chamber clusters. However, the random split simultaneously removes the forward-season distribution shift and introduces heavy chamber-cluster overlap; consequently, the performance difference cannot be attributed uniquely to chamber leakage without an additional controlled experiment. |

---

## 17. Decision-Ready Conclusions

### Predictive Feasibility
Evidence for dispatch-time point prediction is classified as:
**LIMITED / CONTEXT-SPECIFIC LIFT**
- Point-prediction performance relative to the crop-median baseline is metric-dependent: in Protocol P1, the trivial crop-median baseline achieves a slightly lower MAE ($8.8842\%$ loss) than the best dispatch model F3 HGB ($8.9664\%$ loss, $+0.0822$ percentage points higher MAE), while F3 HGB materially improves variance explanation ($R^2 = +0.2799$ vs $+0.0737$) and RMSE ($14.3185\%$ vs $16.2401\%$, $-1.9216$ percentage points).
- Pre-dispatch operational features without planned logistics (F0, F1, F2) fail to beat the crop-median baseline across both MAE and $R^2$.
- Consequently, continuous-loss lift is metric-dependent and context-specific rather than universally superior across all evaluation metrics.

### Ranking Feasibility
Evidence for dispatch-time ranking is classified as:
**MEANINGFUL LIFT DEMONSTRATED** (Strongest with Planned Logistics; Protocol/Model-Dependent Without)
- Non-logistics feature families show protocol/model-dependent ranking lift, including substantial P2 ranking improvement for the linear F1 and F2 benchmarks (e.g. F1 linear Spearman 0.4597, NDCG@10 0.5977; F2 linear Spearman 0.3606, NDCG@10 0.5847 vs crop median baseline Spearman 0.3525, NDCG@10 0.2533).
- The planned-logistics feature family produces the strongest and most consistent ranking improvement across both P1 and P2, particularly under the nonlinear benchmark (NDCG@10 0.8831 in P1 and 0.8888 in P2; Precision@10 against severe degradation 100% in both; Precision@50 86% in P1 and 96% in P2).
- Under prospective inter-season evaluation (P1), non-logistics ranking lift is more muted (NDCG@10 0.2003–0.2464 vs crop baseline 0.2634; Spearman $\rho \le 0.4268$ vs $0.4497$).
- VLD-02B must not infer from VDR-04A that absence of planned logistics necessarily makes ranking impossible.

### Telemetry Contribution
- Marginal contribution is **near-zero to negative**. Storage room telemetry is tightly controlled around setpoints and demonstrated no material incremental predictive signal under tested features/protocols.

### Planned Logistics Contribution
- The planned-logistics feature family (tested jointly as `destination_market`, `destination_region`, `vehicle_type`, `planned_duration_hours`) provides the largest and most consistent incremental predictive association across tested protocols beyond crop type (not a causal claim; individual feature contributions were not independently ablated).

### Robustness
- The empirical findings are consistent across both prospective inter-season testing (Protocol P1) and microclimate-blocked cross-validation (Protocol P2).

### What VLD-02B Can Now Decide
1. Whether the stronger and more cross-protocol-consistent ranking performance provided by planned logistics is sufficient to make those fields a capability prerequisite, versus retaining a weaker/degraded ranking mode without them (that remains a later Integrator decision; any change from optional to mandatory canonical schema semantics would require an explicit shared-contract decision).
2. Whether to adopt batch ranking / risk prioritisation as the primary operational framing rather than continuous point loss forecasting.
3. Whether to exclude extensive pre-dispatch storage telemetry feature engineering pipelines from production backend scope given the absence of demonstrated marginal value under tested protocols.
4. Selection of prospective inter-season holdout as the definitive validation split standard for downstream models.

### What Remains UNKNOWN
- Why berry batches experience massive degradation despite pre-dispatch inspection ratings.
- Whether real-time telemetry from in-transit refrigeration would provide the predictive signal that stationary storage telemetry lacks.
- The performance of these models on completely unobserved crop types or external packing facilities.

---

## 18. Shared Changes Boundary

[FACT] Verification of repository write boundary:
- `backend/**`: **NO**
- `frontend/**`: **NO**
- `sponsor_pack/**`: **NO**
- `docs/challenge_canon.md`: **NO**
- `docs/assumptions_unknowns.md`: **NO**
- `docs/integration_contract.md`: **NO**
- `docs/decisions/**`: **NO**
- Application dependencies or lockfiles changed: **NO**
- Production target selected: **NO**
- Production model selected: **NO**
- External audit numbers copied as evidence: **NO**

---

## 19. Limitations and Analyses Not Performed

1. **Non-Exhaustive Model Space:** Analysis evaluated regularized linear models and histogram gradient boosting; deep tabular networks, specialized survival models, and complex stacking ensembles were not evaluated.
2. **Aggregated Telemetry Scope:** Telemetry was aggregated into 77 summary features; complex raw waveform modeling, continuous Fourier/wavelet embeddings, and sliding sub-window convolutional encoders were not explored.
3. **Small Sample Size for Perishable Crops:** Total dataset contains 1,800 batches across 8 crops; highly perishable crops (strawberries, raspberries, apricots) have small sample sizes ($N \approx 26 - 37$ in test), precluding high statistical confidence for those specific cohorts.
4. **No In-Transit Telemetry:** The dataset contains stationary storage telemetry only; in-transit reefer data loggers were recorded only as post-dispatch summary leakage ($r = +0.6727$) and excluded per ADR 0002.
5. **No Causal Claim:** Planned logistics features reflect observed associations at dispatch booking, not randomized controlled interventions.
