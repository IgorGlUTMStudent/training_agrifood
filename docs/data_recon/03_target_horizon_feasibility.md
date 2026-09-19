# VDR-03 Target and Deterioration-Horizon Feasibility

**Owner:** Viktor — Data & Evaluation Owner
**Repository:** `Slave-of-Skynet/training_agrifood`
**Task type:** Evidence-producing Data & Evaluation reconnaissance
**Assigned base commit:** `f9ca1d7bd29940e6b925884c7becae65dc921f7c`
**Actual starting commit:** `b382834eb73acbcd416000048d0074cf3b78d8df` (descendant of assigned base via PR #15 VLD-R2 post-VDR-02 reconciliation; final authorization of base remains an Integrator decision)
**Branch:** `victor/vdr-03-target-horizon-feasibility`
**Status:** DRAFT FOR REVIEW — Decision-ready evidence on target candidates and deterioration-horizon feasibility

---

## Executive summary

[FACT] The supplied training dataset contains four candidate outcome fields in `historical_quality_outcomes.csv` for all 1,800 batches: `quality_status`, `loss_fraction_pct`, `quality_score`, and `economic_loss_eur`. There are 0 missing values across all four fields.

[FACT] Empirical testing demonstrates that candidate outcome fields exhibit specific mathematical and statistical dependencies:
1. The proposed intervals (`optimal`: $[0.0\%, 5.0\%)$, `degraded`: $[5.0\%, 15.0\%)$, `severe_degradation`: $[15.0\%, 35.0\%)$, `lost`: $[35.0\%, 100.0\%]$) reproduce all 1,800 observed rows of `quality_status` from `loss_fraction_pct` with zero mismatches in the supplied snapshot.
2. `economic_loss_eur` is deterministically reproduced in this snapshot from `loss_fraction_pct`, `harvest_weight_kg`, and inferred crop-specific unit price via the formula: $\text{round}\left( \text{harvest\_weight\_kg} \times \frac{\text{loss\_fraction\_pct}}{100} \times P_{\text{crop}}, 2 \right)$ with 0 differences $> 0.01$ EUR (maximum absolute difference across all 1,800 batches is 0.000000 EUR), where $P_{\text{crop}}$ is an inferred constant price per crop (apples: 0.65, apricots: 1.10, pears: 0.95, plums: 0.75, raspberries: 3.10, strawberries: 2.40, table_grapes: 1.25, tomatoes: 0.85 EUR/kg).
3. `quality_score` has an observed Pearson correlation of $r = -0.972695$ with `loss_fraction_pct`. Under a fitted linear specification ($\text{quality\_score} = 95.4137 - 1.3059 \times \text{loss\_fraction\_pct}$), $R^2 = 0.946135$ with RMS residual = 5.0066 and maximum residual = 34.2255.
4. Physical inspection variables in `quality_checks.csv` at arrival (`firmness_kg_cm2`, `sugar_brix`, `defect_pct`) and field intake score (`batches.initial_quality_score`) have weak linear correlations with candidate outcomes:
   - `loss_fraction_pct`: arrival firmness $r = +0.020822$, arrival Brix $r = +0.003859$, arrival defect % $r = -0.003303$, initial quality score $r = -0.024139$.
   - `quality_score`: arrival firmness $r = -0.026284$, arrival Brix $r = -0.008493$, arrival defect % $r = +0.011226$, initial quality score $r = +0.039173$.
   - `economic_loss_eur`: arrival firmness $r = +0.007824$, arrival Brix $r = +0.007819$, arrival defect % $r = -0.004120$, initial quality score $r = -0.040336$.

[FACT] 78 values equal the observed minimum of 5.0 and 36 values equal the observed maximum of 98.5.

[INFERENCE] These concentrations are consistent with possible boundary clipping or saturation.

[UNKNOWN] The exact quality_score generation rule is undocumented.

[FACT] Quality inspections occur at exactly three discrete checkpoints per batch:
- `harvest`: exactly $T_{\text{harvest}} + 1.0\text{ h}$ (1,800 records)
- `pre_dispatch`: exactly $T_{\text{dispatch}} - 2.0\text{ h}$ (1,800 records)
- `arrival`: exactly $T_{\text{actual\_arrival}}$ (1,800 records)
There are 0 intermediate quality inspections during storage or transit.

[FACT] The dataset has a nominal 30-minute telemetry cadence, with sampling gaps/skips previously identified by VDR-01. Available telemetry covers environmental/chamber telemetry, including produce-surface temperature, but not a direct biological deterioration-state measurement. Produce-surface temperature indicates thermal boundary conditions rather than a biological deterioration-onset event.

[FACT] No exact deterioration-onset timestamp is observed.

[INFERENCE] Current evidence cannot support an exact continuous deterioration-horizon value.

[DECISION REQUIRED] Runtime handling of the nullable deterioration_horizon field remains a later integration/product decision.

[RECOMMENDATION] Do not expose an exact deterioration countdown without additional evidence and an accepted event definition. Treat arrival-condition prediction at dispatch as a feasible candidate semantic for later evaluation design, while final target selection remains a later Integrator target decision.

---

## Scope and decision boundary

This report produces factual, decision-ready reconnaissance for:
1. Historical outcome usability and distribution.
2. Dependencies, derivations, and statistical relationships among candidate outcome fields.
3. Prediction cutoff alignment with $T_{\text{assess}} \equiv T_{\text{dispatch}}$.
4. Observability of produce deterioration onset.
5. Feasibility and limitations of deterioration horizon semantics.

### Decision Boundary (What this report does NOT do)
- **Does NOT select the production target** (remains a later Integrator target decision).
- **Does NOT select a classification task or define binary risk thresholds** (binary risk remains undefined).
- **Does NOT choose an evaluation metric** (deferred to VDR-04).
- **Does NOT choose an evaluation split or baseline** (deferred to VDR-04).
- **Does NOT select a model family or train any model**.
- **Does NOT define arbitrary agronomic decay thresholds** or invent deterioration timestamps.
- **Does NOT redefine feature admission or declare feature families safe** (feature admission is governed by accepted ADR 0002 based on VDR-02 evidence).
- **Does NOT alter repository contracts, dependencies, or source code**.

---

## Sources inspected

All analyses were executed programmatically against raw data files and repository documentation:
1. `sponsor_pack/data/historical_quality_outcomes.csv` (1,800 rows)
2. `sponsor_pack/data/quality_checks.csv` (5,400 rows)
3. `sponsor_pack/data/batches.csv` (1,800 rows)
4. `sponsor_pack/data/storage_sessions.csv` (1,800 rows)
5. `sponsor_pack/data/shipments.csv` (1,800 rows)
6. `sponsor_pack/data/sensor_readings.csv` (669,665 rows)
7. `sponsor_pack/data/data_dictionary.xlsx` (Sheet `Data_Dictionary`, 74 rows)
8. `sponsor_pack/brief/Training Challenge #3 — AgriFood.md`
9. `sponsor_pack/README.md`
10. `docs/data_contract.md` (reinspected: output schema, `RiskAssessment`, nullable `deterioration_horizon`)
11. `docs/evaluation.md` (reinspected: $T_{\text{assess}} \equiv T_{\text{dispatch}}$, deterministic baseline hierarchy, split considerations)
12. `docs/domain_rules.md` (reinspected: domain-rule guard, unvalidated state, rule admission register)
13. `docs/data_recon/01_dataset_inventory.md` (accepted VDR-01)
14. `docs/data_recon/02_temporal_leakage.md` (accepted VDR-02)
15. `docs/decisions/0002-predictive-input-semantics.md` (accepted ADR 0002 inspected via origin/main)
16. `docs/challenge_canon.md`
17. `docs/assumptions_unknowns.md`
18. `docs/integration_contract.md`

---

## Historical outcome inventory

[FACT] `historical_quality_outcomes.csv` contains 1,800 rows at batch grain (`batch_id` PK, 1:1 join with `batches.csv`). Zero rows contain null or missing values.

The table below summarizes the profile of all four candidate outcome fields:

| Field | Storage Type | Documented Meaning (`data_dictionary.xlsx`) | Observed Range / Categories | Missingness | Distribution Profile |
|---|---|---|---|---|---|
| `quality_status` | `string` | Commercial grading classification at market | `optimal`, `degraded`, `severe_degradation`, `lost` | 0 / 1,800 (0.0%) | `degraded`: 620 (34.44%)<br>`optimal`: 549 (30.50%)<br>`severe_degradation`: 516 (28.67%)<br>`lost`: 115 (6.39%) |
| `loss_fraction_pct` | `float` | Percentage of harvest weight condemned/lost (%) | 0.40% to 95.44% | 0 / 1,800 (0.0%) | Min: 0.40%<br>P25: 4.27%<br>Median: 9.83%<br>Mean: 14.33% (std: 16.07%)<br>P75: 18.00%<br>P90: 26.42%<br>Max: 95.44% |
| `quality_score` | `float` | Composite quality index at arrival (score 0–100) | 5.0 to 98.5 | 0 / 1,800 (0.0%) | Min: 5.0<br>P25: 68.9<br>Median: 82.6<br>Mean: 76.70 (std: 21.58)<br>P75: 92.2<br>P90: 95.5<br>Max: 98.5 |
| `economic_loss_eur` | `float` | Calculated financial loss based on market value (EUR) | 12.35 to 7,794.86 EUR | 0 / 1,800 (0.0%) | Min: 12.35<br>P25: 222.03<br>Median: 488.57<br>Mean: 766.04 (std: 892.49)<br>P75: 969.34<br>P90: 1,629.60<br>Max: 7,794.86<br>Total: 1,378,872.97 EUR |

*Note on Percentile Method:* Medians are computed via standard-library `statistics.median`. P25, P75, and P90 percentiles are computed via linear interpolation between nearest ranks ($k = (n - 1) \times p$), consistent with `statistics.quantiles(..., method='inclusive')`, NIST, and NumPy/pandas defaults.

[FACT] Per-crop distribution of candidate outcomes:

| Crop | Batches | Loss Fraction Mean (Median) | Quality Score Mean (Median) | Mean Economic Loss (EUR) | Total Economic Loss (EUR) | Status Counts (opt / deg / sev / lost) |
|---|---|---|---|---|---|---|
| `apples` | 673 | 8.94% (5.08%) | 84.37 (90.50) | 545.49 | 367,117.86 | 332 / 223 / 94 / 24 |
| `apricots` | 60 | 22.30% (14.59%) | 66.61 (75.10) | 984.92 | 59,095.19 | 8 / 24 / 19 / 9 |
| `pears` | 114 | 13.82% (8.07%) | 76.92 (86.60) | 1,080.17 | 123,139.23 | 36 / 42 / 27 / 9 |
| `plums` | 350 | 14.80% (10.73%) | 76.27 (81.50) | 692.89 | 242,511.58 | 94 / 129 / 106 / 21 |
| `raspberries` | 50 | 24.63% (20.58%) | 62.26 (64.35) | 1,008.51 | 50,425.50 | 2 / 10 / 33 / 5 |
| `strawberries` | 63 | 20.56% (17.71%) | 66.91 (69.40) | 927.81 | 58,451.80 | 4 / 19 / 35 / 5 |
| `table_grapes` | 310 | 16.96% (14.66%) | 71.52 (74.50) | 1,090.35 | 338,008.03 | 42 / 118 / 129 / 21 |
| `tomatoes` | 180 | 21.64% (15.47%) | 68.44 (73.60) | 778.47 | 140,123.78 | 31 / 55 / 73 / 21 |
| **Total** | **1,800** | **14.33% (9.83%)** | **76.70 (82.60)** | **766.04** | **1,378,872.97** | **549 / 620 / 516 / 115** |

---

## Outcome provenance and timing

[FACT] `historical_quality_outcomes.csv` contains no timestamp column.

[FACT] According to `data_dictionary.xlsx` and operational semantics, all four historical quality outcome fields represent final delivery evaluations conducted upon arrival at the destination market ($t \ge T_{\text{actual\_arrival}} > T_{\text{dispatch}}$).

[FACT] In all 1,800 batches, $T_{\text{actual\_arrival}} > T_{\text{dispatch}}$. Transit duration ($T_{\text{actual\_arrival}} - T_{\text{dispatch}}$) spans 5.07 to 50.51 hours (median 17.85 hours, mean 21.40 hours).

[FACT] The prediction cutoff established in accepted VDR-02 is:
$$\mathbf{T_{\text{assess}} \equiv T_{\text{dispatch}} = \text{storage_sessions.dispatch_datetime}}$$

[INFERENCE] In supervised learning, a candidate label $y$ describes an outcome realized in the future relative to prediction time $T_{\text{assess}}$. The fact that candidate outcomes occur after $T_{\text{dispatch}}$ makes them temporally eligible as ground-truth labels for retrospective training, but strictly prohibits them from being used as prediction input features at $T_{\text{dispatch}}$.

---

## Relationships and redundancy among outcome fields

Empirical testing reveals exact derivations and statistical dependencies among candidate outcome fields.

### 1. `quality_status` $\leftrightarrow$ `loss_fraction_pct` (Snapshot Boundary Mapping)

[FACT] The proposed interval rule:
$$\text{quality\_status} = \begin{cases} \text{optimal} & \text{if } 0.0\% \le \text{loss\_fraction_pct} < 5.0\% \\ \text{degraded} & \text{if } 5.0\% \le \text{loss\_fraction_pct} < 15.0\% \\ \text{severe\_degradation} & \text{if } 15.0\% \le \text{loss\_fraction_pct} < 35.0\% \\ \text{lost} & \text{if } 35.0\% \le \text{loss\_fraction_pct} \le 100.0\% \end{cases}$$
reproduces all 1,800 observed rows with **zero mismatches in the supplied snapshot**.

| Category | Loss Fraction Range Observed | Interval Rule | Count | % of Dataset |
|---|---|---|---|---|
| `optimal` | $[0.40\%, 4.99\%]$ | $[0.0\%, 5.0\%)$ | 549 | 30.50% |
| `degraded` | $[5.00\%, 14.98\%]$ | $[5.0\%, 15.0\%)$ | 620 | 34.44% |
| `severe_degradation` | $[15.00\%, 34.72\%]$ | $[15.0\%, 35.0\%)$ | 516 | 28.67% |
| `lost` | $[35.35\%, 95.44\%]$ | $[35.0\%, 100.0\%]$ | 115 | 6.39% |

[INFERENCE] In this historical dataset, `quality_status` contains no information beyond what is already determined by `loss_fraction_pct`. It represents a discrete categorization of `loss_fraction_pct`.

[UNKNOWN] Whether this mapping constitutes a universal commercial standard or an artifact of snapshot data generation is not established by the inspected sources. Behavior outside the observed ranges is unverified.

### 2. `economic_loss_eur` $\leftrightarrow$ `loss_fraction_pct` & `batches` (Crop Price Provenance and Accounting Formula)

[FACT] Empirical testing demonstrates that `economic_loss_eur` is deterministically reproduced in this snapshot from `loss_fraction_pct`, `harvest_weight_kg`, and inferred crop-specific unit price via the formula:
$$\text{economic\_loss\_eur} = \text{round}\left( \text{harvest\_weight\_kg} \times \frac{\text{loss\_fraction\_pct}}{100} \times P_{\text{crop}}, 2 \right)$$
matching raw values with **maximum absolute difference = 0.000000 EUR** (0 differences $> 0.01$ EUR) across all 1,800 batches.

[FACT] Crop-specific unit prices were inferred from the supplied snapshot by dividing `economic_loss_eur` by lost mass where `loss_fraction_pct` was nonzero:
$$\text{price} = \frac{\text{economic\_loss\_eur}}{\text{harvest\_weight\_kg} \times (\text{loss\_fraction\_pct} / 100)}$$
The empirical price inference summary per crop:

| Crop Type | Batches Used ($n$) | Min Inferred Price | Max Inferred Price | Mean Inferred Price | Rounded Unit Price ($P_{\text{crop}}$) | Max Formula Diff (EUR) |
|---|---|---|---|---|---|---|
| `apples` | 673 | 0.649822 | 0.650056 | 0.649999 | **0.65 EUR/kg** | 0.000000 |
| `apricots` | 60 | 1.099864 | 1.100030 | 1.099996 | **1.10 EUR/kg** | 0.000000 |
| `pears` | 114 | 0.949964 | 0.950112 | 0.950002 | **0.95 EUR/kg** | 0.000000 |
| `plums` | 350 | 0.749913 | 0.750133 | 0.750001 | **0.75 EUR/kg** | 0.000000 |
| `raspberries` | 50 | 3.099940 | 3.100148 | 3.100003 | **3.10 EUR/kg** | 0.000000 |
| `strawberries` | 63 | 2.399936 | 2.400072 | 2.399998 | **2.40 EUR/kg** | 0.000000 |
| `table_grapes` | 310 | 1.249938 | 1.250057 | 1.250000 | **1.25 EUR/kg** | 0.000000 |
| `tomatoes` | 180 | 0.849964 | 0.850193 | 0.850004 | **0.85 EUR/kg** | 0.000000 |

[FACT] Crop-specific unit prices were inferred from the supplied snapshot by dividing economic_loss_eur by lost mass where loss_fraction_pct was nonzero.

[FACT] The inferred values reproduce economic_loss_eur across the supplied snapshot within the reported rounding tolerance.

[INFERENCE] The deterministic accounting relationship indicates that `economic_loss_eur` does not provide independent outcome information beyond `loss_fraction_pct`, batch mass, and inferred crop price in this snapshot.

[RECOMMENDATION] Do not treat `economic_loss_eur` as a direct predictive target without a later human decision establishing that semantic.

[UNKNOWN] The external business provenance and future production validity of these inferred prices are not established.

### 3. `quality_score` $\leftrightarrow$ `loss_fraction_pct` (Fitted Specification, Bounds, Residuals)

[FACT] Analysis of `quality_score` relative to `loss_fraction_pct` shows:
- **Observed Pearson correlation**: $r = -0.972695$.
- **Fitted linear specification**: $\text{quality\_score} = 95.4137 + (-1.3059) \times \text{loss\_fraction\_pct}$.
- **Coefficient of determination**: $R^2 = 0.946135$.
- **Residual behavior**: root-mean-square residual $= 5.0066$, maximum absolute residual $= 34.2255$.
- **Exact deterministic derivation**: An exact deterministic mathematical formula was **not** established. The relationship exhibits residual scatter around the fitted trend.

[FACT] 78 values equal the observed minimum of 5.0 and 36 values equal the observed maximum of 98.5.

[INFERENCE] These concentrations are consistent with possible boundary clipping or saturation.

[UNKNOWN] The exact quality_score generation rule is undocumented.

### 4. Correlation with Physical Inspection Checkpoints (`quality_checks.csv`) and Initial Score

[FACT] Observed Pearson correlations between historical outcome fields, arrival physical measurements (`arrival` stage), and field intake score:

| Outcome Field | Arrival Firmness (`kg/cm²`) | Arrival Brix (`°Brix`) | Arrival Defect % (`defect_pct`) | Field Intake Score (`batches.initial_quality_score`) |
|---|---|---|---|---|
| `loss_fraction_pct` | $+0.020822$ | $+0.003859$ | $-0.003303$ | $-0.024139$ |
| `quality_score` | $-0.026284$ | $-0.008493$ | $+0.011226$ | $+0.039173$ |
| `economic_loss_eur` | $+0.007824$ | $+0.007819$ | $-0.004120$ | $-0.040336$ |

[INFERENCE] These results demonstrate that physical sample measurements at arrival and baseline intake scores have weak linear associations with commercial loss outcomes in this snapshot.

[UNKNOWN] The business process or data generation mechanism explaining this weak association is not documented by the inspected evidence.

---

## Candidate target feasibility matrix

The matrix below summarizes evidence for candidate outcome fields without selecting a production target:

| Candidate | Source Table / Field | Observed Stage | Type | Completeness | Derivation / Dependency | Relation to Operator Question | Candidate-Label Support | Leakage at $T_{\text{dispatch}}$ | Important Limitations | Decision Still Required (Later Target/Evaluation Gate) |
|---|---|---|---|---|---|---|---|---|---|---|
| `loss_fraction_pct` | `historical_quality_outcomes` | Post-transit (Arrival) | Continuous (0.0–100.0%) | 100.0% (0 missing) | Continuous loss field in snapshot; underlies status and economic loss formulas | Quantifies physical batch loss percentage | **SUPPORTED AS A CANDIDATE** | Eligible only as a retrospective candidate label; fatal target leakage if used as a T_dispatch input feature | Right-skewed distribution (median 9.83%, mean 14.33%, max 95.44%); continuous evaluation requires accepted continuous semantics | Final target selection remains a later Integrator target decision |
| `quality_status` | `historical_quality_outcomes` | Post-transit (Arrival) | Categorical / Ordinal (4 classes) | 100.0% (0 missing) | Deterministically derived from `loss_fraction_pct` across 4 intervals in snapshot | Classifies degradation severity tiers | **SUPPORTED AS A CANDIDATE** | Eligible only as a retrospective candidate label; fatal target leakage if used as a T_dispatch input feature | Coarse discretization; class imbalance (`lost` is 6.39%, `optimal` 30.50%, `degraded` 34.44%, `severe_degradation` 28.67%); categorical evaluation requires accepted categorical semantics | Final target selection and task framing remain a later target/evaluation gate decision |
| `quality_score` | `historical_quality_outcomes` | Post-transit (Arrival) | Continuous bounded (0–100) | 100.0% (0 missing) | Statistically associated with loss fraction ($r = -0.9727$, $R^2 = 0.9461$ under linear fit) | Represents composite arrival quality score | **SUPPORTED WITH LIMITATIONS** | Eligible only as a retrospective candidate label; fatal target leakage if used as a T_dispatch input feature | 78 values equal 5.0 and 36 values equal 98.5 (consistent with possible boundary clipping or saturation); non-deterministic residual scatter; continuous evaluation requires accepted continuous semantics | Target suitability remains a later Integrator target decision |
| `economic_loss_eur` | `historical_quality_outcomes` | Post-transit (Calculated) | Monetary / Continuous (EUR) | 100.0% (0 missing) | Deterministically derived ($\text{weight} \times \text{loss} \times P_{\text{crop}}$) | Measures financial consequence of loss | [INFERENCE] Does not provide independent outcome information beyond `loss_fraction_pct`, batch mass, and inferred crop price; [RECOMMENDATION] Do not treat as direct predictive target without a later human decision establishing that semantic | Eligible only as a retrospective candidate label; fatal target leakage if used as a T_dispatch input feature | Entangles produce degradation with batch weight and crop price; conflates volume with decay; does not provide independent outcome information beyond `loss_fraction_pct`, batch mass, and inferred crop price | Decision on whether financial conversion belongs in decision layer post-prediction |

---

## Target timing relative to T_dispatch

Accepted VDR-02 establishes that the operational prediction cutoff is:
$$\mathbf{T_{\text{assess}} \equiv T_{\text{dispatch}} = \text{storage_sessions.dispatch_datetime}}$$

### Detailed Timing Audit

The table below classifies field observation timing relative to $T_{\text{dispatch}}$. For feature eligibility rules and admission constraints, see accepted ADR 0002 (`docs/decisions/0002-predictive-input-semantics.md`), with underlying temporal and leakage evidence established in VDR-02 (`docs/data_recon/02_temporal_leakage.md`). VDR-03 investigates candidate target and horizon feasibility and does not redefine feature admission or declare entire table families safe as model inputs.

| Field Family | Observation Timing | Available by $T_{\text{dispatch}}$? | Usage as Prediction Feature ($x$) | Usage as Supervised Label ($y$) | Temporal / Leakage Classification |
|---|---|---|---|---|---|
| `batches.*` (intake descriptors) | $T_{\text{harvest}}$ to $T_{\text{entry}}$ | Observed by $T_{\text{dispatch}}$ ($t < T_{\text{dispatch}}$) | Governed by accepted ADR 0002; VDR-02 provides the underlying temporal/leakage evidence | NO | Historical intake context |
| `storage_sessions.*` (storage metadata) | $T_{\text{entry}}$ to $T_{\text{dispatch}}$ | Observed by $T_{\text{dispatch}}$ ($t \le T_{\text{dispatch}}$) | Governed by accepted ADR 0002; VDR-02 provides the underlying temporal/leakage evidence | NO | Cold storage operational parameters |
| `storage_sessions.dispatch_datetime` | $T_{\text{dispatch}}$ | Observed at $T_{\text{dispatch}}$ ($t = T_{\text{dispatch}}$) | Governed by accepted ADR 0002; VDR-02 provides the underlying temporal/leakage evidence | Context timestamp (assessment clock) | Assessment milestone defining $T_{\text{assess}} \equiv T_{\text{dispatch}}$ |
| `facilities.*` / `storage_zones.*` | Prior to dispatch | Observed by $T_{\text{dispatch}}$ ($t < T_{\text{dispatch}}$) | Governed by accepted ADR 0002; VDR-02 provides the underlying temporal/leakage evidence | NO | Facility physical specifications |
| `quality_checks` (`stage='harvest'`) | $T_{\text{harvest}} + 1.0\text{ h}$ | Observed by $T_{\text{dispatch}}$ ($t < T_{\text{dispatch}}$) | Governed by accepted ADR 0002; VDR-02 provides the underlying temporal/leakage evidence | NO | Intake inspection checkpoint |
| `quality_checks` (`stage='pre_dispatch'`) | $T_{\text{dispatch}} - 2.0\text{ h}$ | Observed by $T_{\text{dispatch}}$ ($t < T_{\text{dispatch}}$) | Governed by accepted ADR 0002; VDR-02 provides the underlying temporal/leakage evidence | NO | Pre-dispatch inspection checkpoint |
| `sensor_readings.*` ($t \le T_{\text{dispatch}}$) | Storage session duration | Observed by $T_{\text{dispatch}}$ ($t \le T_{\text{dispatch}}$) | Governed by accepted ADR 0002; VDR-02 provides the underlying temporal/leakage evidence | NO | Chamber environmental time-series |
| `shipments.planned_*` (planned route/market) | Prior to dispatch | Known/planned at dispatch per sponsor; predictive eligibility remains conditional on operational stability/immutability as specified by ADR 0002 | Governed by accepted ADR 0002; VDR-02 provides the underlying temporal/leakage evidence | NO | Planned logistics context (conditional on operational stability) |
| `shipments.actual_*` (transit actuals/incidents) | Post-dispatch ($t > T_{\text{dispatch}}$) | Observed after $T_{\text{dispatch}}$ | Strictly forbidden (ADR 0002 / VDR-02) | NO | Future transit actuals |
| `quality_checks` (`stage='arrival'`) | $T_{\text{actual\_arrival}}$ | Observed after $T_{\text{dispatch}}$ | Strictly forbidden (ADR 0002 / VDR-02) | Retrospective inspection check | Future inspection check |
| `historical_quality_outcomes.*` (all 4 fields) | Market arrival / post-transit | Observed after $T_{\text{dispatch}}$ | Strictly forbidden (ADR 0002 / VDR-02) | **CANDIDATE GROUND TRUTH ($y$)** | Eligible only as a retrospective candidate label; fatal target leakage if used as a T_dispatch input feature |

[FACT] All candidate outcomes are realized post-dispatch. They are eligible only as retrospective candidate labels; fatal target leakage if used as a T_dispatch input feature.

---

## Observed quality checkpoints

[FACT] The dataset contains exactly 5,400 rows in `quality_checks.csv`, comprising three stages for every one of the 1,800 batches (1:3 batch-to-check grain):

1. **Harvest Stage (`harvest`)**:
   - Count: 1,800 records (100.0%)
   - Timing: Exactly $T_{\text{harvest}} + 1.0\text{ h}$ for all 1,800 batches (unique offset: 1.0 h).
2. **Pre-dispatch Stage (`pre_dispatch`)**:
   - Count: 1,800 records (100.0%)
   - Timing: Exactly $T_{\text{dispatch}} - 2.0\text{ h}$ for all 1,800 batches (unique offset: 2.0 h).
3. **Arrival Stage (`arrival`)**:
   - Count: 1,800 records (100.0%)
   - Timing: Exactly $T_{\text{actual\_arrival}}$ for all 1,800 batches (unique offset: 0.0 h).

[FACT] There are 0 batches with fewer or more than 3 checks. There are 0 intermediate quality inspections during storage or during transit.

### Inter-Checkpoint Durations

| Checkpoint Interval | Min | P25 | Median | P75 | Max | Mean | Std Dev | Unit |
|---|---|---|---|---|---|---|---|---|
| Harvest QC $\to$ Pre-dispatch QC | 2.98 | 19.13 | 54.09 | 92.36 | 175.02 | 59.89 | 43.74 | Days |
| Pre-dispatch QC $\to$ Arrival QC | 7.07 | 11.54 | 19.85 | 35.77 | 52.51 | 23.40 | 12.60 | Hours |
| Harvest QC $\to$ Arrival QC | 3.36 | 20.31 | 55.15 | 93.97 | 176.75 | 60.86 | 43.75 | Days |

### Measurement Trajectory Statistics

The table below tracks physical measurement values across the three inspection stages:

| Metric | Stage | Min | P25 | Median | P75 | Max | Mean | Std Dev | Direction across Lifecycle |
|---|---|---|---|---|---|---|---|---|---|
| **Firmness** (`kg/cm²`) | `harvest` | 6.50 | 6.98 | 7.49 | 8.00 | 8.50 | 7.50 | 0.58 | Baseline intake firmness |
| | `pre_dispatch` | 5.00 | 5.70 | 6.41 | 7.09 | 7.80 | 6.41 | 0.81 | Declines during storage ($\Delta_{\text{mean}} = -1.09$) |
| | `arrival` | 4.00 | 4.78 | 5.62 | 6.43 | 7.20 | 5.62 | 0.93 | Declines during transit ($\Delta_{\text{mean}} = -0.79$) |
| **Sugar Content** (`°Brix`) | `harvest` | 11.00 | 12.40 | 13.80 | 15.10 | 16.50 | 13.77 | 1.58 | Baseline intake brix |
| | `pre_dispatch` | 11.50 | 12.90 | 14.40 | 15.60 | 17.00 | 14.28 | 1.58 | Increases during storage ($\Delta_{\text{mean}} = +0.51$) |
| | `arrival` | 11.50 | 12.90 | 14.30 | 15.80 | 17.20 | 14.34 | 1.66 | Stable in transit ($\Delta_{\text{mean}} = +0.06$) |
| **Defect Percentage** (`%`) | `harvest` | 0.50% | 1.30% | 2.20% | 3.10% | 4.00% | 2.21% | 0.99% | Baseline intake surface defects |
| | `pre_dispatch` | 1.00% | 2.80% | 4.70% | 6.50% | 8.50% | 4.71% | 2.16% | Increases in storage ($\Delta_{\text{mean}} = +2.50\%$) |
| | `arrival` | 1.50% | 5.60% | 9.90% | 14.00% | 18.00% | 9.84% | 4.74% | Increases in transit ($\Delta_{\text{mean}} = +5.14\%$) |

[FACT] Trajectory delta direction counts:
- Firmness declines between harvest and pre-dispatch in 1,516 batches (84.2%), is unchanged in 6 batches (0.3%), and increases in 278 batches (15.4%).
- Firmness declines between pre-dispatch and arrival in 1,300 batches (72.2%), is unchanged in 3 batches (0.2%), and increases in 497 batches (27.6%).
- Sugar content (Brix) increases between harvest and pre-dispatch in 1,057 batches (58.7%), is unchanged in 27 batches (1.5%), and decreases in 716 batches (39.8%).
- Sugar content (Brix) increases between pre-dispatch and arrival in 879 batches (48.8%), is unchanged in 34 batches (1.9%), and decreases in 887 batches (49.3%).
- Defect percentage increases between harvest and pre-dispatch in 1,477 batches (82.1%), is unchanged in 12 batches (0.7%), and decreases in 311 batches (17.3%).
- Defect percentage increases between pre-dispatch and arrival in 1,452 batches (80.7%), is unchanged in 10 batches (0.6%), and decreases in 338 batches (18.8%).

[INFERENCE] Aggregate checkpoint measurements show mean changes in the expected degradation directions (mean softening, mean defect accumulation).

[UNKNOWN] The causes of individual non-monotonic changes in firmness, Brix, or defect percentage across checkpoints are not established by the supplied evidence.

---

## Deterioration-onset observability

[FACT] Auditing the dataset for deterioration onset yields:
1. **No exact deterioration-onset timestamp is observed**: There is no timestamp column representing deterioration onset in any table.
2. **Discrete checkpoint sampling**: Quality is observed only at three discrete checkpoints per batch separated by weeks or months in storage and hours in transit.
3. **Environmental telemetry vs biological state**: [FACT] The dataset has a nominal 30-minute telemetry cadence, with sampling gaps/skips previously identified by VDR-01. `sensor_readings.csv` captures environmental/chamber telemetry, including produce-surface temperature, but not a direct biological deterioration-state measurement. Produce-surface temperature reflects thermal chamber-produce heat exchange rather than a biological degradation label.
4. **Pre-dispatch defect state**: Defect percentages at pre-dispatch already range from 1.0% to 8.5% (median 4.70%), indicating that minor surface defects exist prior to dispatch.
5. **Additional evaluation limitation (204-batch telemetry gap)**: Exactly 204 batches experience pre-dispatch telemetry gaps (median 24.40 days) because chamber logging ends on 2025-12-31 while their dispatch occurs in 2026. This gap represents an additional evaluation and feature-engineering limitation, but is not the fundamental reason exact deterioration onset is unobserved (exact onset is unobserved across all 1,800 batches regardless of telemetry coverage).

[INFERENCE] Exact deterioration onset is not identifiable from the supplied observations. Current evidence cannot support an exact continuous deterioration-horizon value.

[DECISION REQUIRED] Runtime handling of the nullable deterioration_horizon field remains a later integration/product decision.

[RECOMMENDATION] Do not expose an exact deterioration countdown without additional evidence and an accepted event definition.

---

## Deterioration-horizon feasibility matrix

The table below evaluates candidate analytical formulations of "deterioration horizon" as evidence for later decisions:

| Horizon Formulation | Analytical Semantics | Required Ground Truth | Observable in Data? | Feasibility Classification | Justification & Limitations |
|---|---|---|---|---|---|
| **1. Exact Time-to-Deterioration** | Predict exact elapsed time $\Delta t$ or timestamp $T_{\text{start}}$ when produce begins deteriorating | Ground truth $T_{\text{deterioration\_start}}$ timestamp | **NO** (0 records exist) | **NOT SUPPORTABLE BY CURRENT EVIDENCE** | No continuous biological monitoring; quality checked only at 3 discrete checkpoints; exact onset is not identifiable from the supplied observations. |
| **2. Interval-Censored Deterioration** | Predict whether deterioration onset falls within an interval $[T_1, T_2]$ (e.g., storage vs transit) | Validated threshold $\theta$ on quality degradation delta | **CONDITIONALLY** (checkpoints exist, threshold undefined) | **CONDITIONALLY SUPPORTABLE** | The checkpoints bound observation periods. They would bound a deterioration event only after an accepted event definition or domain-validated threshold. |
| **3. Arrival Condition Prediction at Dispatch** | At $T_{\text{dispatch}}$, predict final delivery outcome at arrival (`quality_status` or `loss_fraction_pct`) | Final outcome at arrival (`historical_quality_outcomes`) | **YES** (100% observed at arrival) | **SUPPORTED AS A CANDIDATE SEMANTIC** | Aligns with prediction boundary $T_{\text{assess}} \equiv T_{\text{dispatch}}$; uses verified complete ground truth labels; addresses batch risk at arrival. |
| **4. Risk by Future Checkpoint** | Predict probability of exceeding quality defect threshold by arrival inspection | Quality check defect % or firmness at arrival | **YES** (1,800 arrival checks observed) | **CONDITIONALLY SUPPORTABLE** | Exactly 1,800 arrival measurements are retrospectively observed, but a threshold-defined risk event is conditionally supportable only after an accepted event definition or domain-validated threshold. |

---

## Implications for later evaluation

While VDR-03 does not select an evaluation metric, split, or model, the evidence imposes specific constraints on later evaluation design (VDR-04):

1. **Target Selection Constraints**:
   - Categorical evaluation requires accepted categorical semantics; multi-class availability is observed from the four `quality_status` categories (class distribution: `lost` is 6.39%, `optimal` 30.50%, `degraded` 34.44%, `severe_degradation` 28.67%).
   - [UNKNOWN] Binary risk semantics and any associated threshold remain undefined and require a later decision.
   - Continuous evaluation requires accepted continuous semantics; `loss_fraction_pct` is an observed continuous candidate label with a right-skewed distribution (median 9.83%, mean 14.33%, max 95.44%).
   - Time-to-event evaluation requires an observed/accepted event and time origin.
   - `economic_loss_eur` is deterministically reproduced in this snapshot from `loss_fraction_pct`, `harvest_weight_kg`, and inferred crop-specific unit price. It does not provide independent outcome information beyond `loss_fraction_pct`, batch mass, and inferred crop price.
2. **Contract Handling of Horizon Field**:
   - In `docs/data_contract.md`, the output model defines `deterioration_horizon: Optional[DeteriorationHorizon] = None`.
   - [FACT] No exact deterioration-onset timestamp is observed.
   - [INFERENCE] Current evidence cannot support an exact continuous deterioration-horizon value.
   - [DECISION REQUIRED] Runtime handling of the nullable deterioration_horizon field remains a later integration/product decision.
3. **Leakage-Proof Evaluation Protocol**:
   - In accordance with `docs/evaluation.md`, prediction time is fixed at $T_{\text{assess}} \equiv T_{\text{dispatch}}$. All post-dispatch information (actual departure, transit actuals, transit incidents, arrival QC, destination outcomes) must be barred from input features.
4. **Baseline Hierarchy**:
   - `docs/evaluation.md` requires implementing a deterministic baseline before evaluating learned models.

---

## Decision inputs for later target/evaluation gates

This report provides the following decision inputs for the Integrator and Project Brain:

1. **[DECISION REQUIRED] Candidate Target Formulation**:
   - Whether `loss_fraction_pct` (continuous), `quality_status` (multi-class categorical), or another formulation will be selected as the production target contract.
2. **[DECISION REQUIRED] Deterioration Horizon Semantics**:
   - [FACT] No exact deterioration-onset timestamp is observed.
   - [INFERENCE] Current evidence cannot support an exact continuous deterioration-horizon value.
   - [DECISION REQUIRED] Runtime handling of the nullable deterioration_horizon field remains a later integration/product decision.
3. **[DECISION REQUIRED] Economic Loss Handling**:
   - [INFERENCE] The deterministic accounting relationship indicates that `economic_loss_eur` does not provide independent outcome information beyond `loss_fraction_pct`, batch mass, and inferred crop price in this snapshot.
   - [RECOMMENDATION] Do not treat `economic_loss_eur` as a direct predictive target without a later human decision establishing that semantic.
   - Whether the deterministic historical accounting relationship should be used in a future decision layer remains an integration/product decision.

---

## Resolved UNKNOWNs

[FACT] VDR-03 formally resolves the following open items from `docs/assumptions_unknowns.md`:

1. **Relationships and redundancy among historical outcomes** (Table row 14 & 17):
   - **Resolved**: The proposed intervals reproduce `quality_status` from `loss_fraction_pct` at $[5.0\%, 15.0\%, 35.0\%]$ with 0 mismatches across 1,800 batches in this snapshot.
   - **Resolved**: `economic_loss_eur` is deterministically reproduced in this snapshot from `loss_fraction_pct`, `harvest_weight_kg`, and inferred crop-specific unit price via an exact accounting formula matching to 0.000000 EUR.
2. **Observability of deterioration onset** (Table row 15):
   - **Resolved**: No explicit deterioration onset timestamp exists in the dataset. Quality is checked only at 3 discrete operational stages.
3. **Target availability relative to $T_{\text{dispatch}}$** (Table row 13):
   - **Resolved**: All four candidate outcomes are realized post-transit at market arrival. They are valid retrospective labels $y$, but strictly forbidden as prediction inputs $x$.

---

## Remaining UNKNOWNs

The following items remain UNKNOWN and require future human/integrator decisions:

1. **Production Target Selection**: Which candidate target formulation (`loss_fraction_pct`, `quality_status`, or other) will be adopted (remains a later Integrator target decision).
2. **Exact Quality Score Generation Mechanism**: The exact mathematical or operational generation rule for `quality_score` is undocumented.
3. **External Business Provenance and Future Validity of Inferred Crop Prices**: The external commercial basis and future operational validity of inferred crop prices ($P_{\text{crop}}$) are unverified beyond this snapshot.
4. **Provenance of Quality Status Thresholds**: Whether the exact threshold boundaries for `quality_status` ($5.0\%$, $15.0\%$, $35.0\%$) reflect external agricultural market standards or dataset-specific quantization remains unknown.
5. **Agronomic Event Definitions or Thresholds**: Whether domain experts can supply crop-specific biological thresholds to define interval degradation events during storage (`docs/domain_rules.md`).
6. **Runtime Behavior for Nullable Deterioration Horizon**: The runtime handling and downstream behavior for the nullable `deterioration_horizon` field remains a later integration/product decision.
7. **Evaluation/Split Policy for the 204 Telemetry-Truncated Batches**: How the 204 batches with pre-dispatch telemetry gaps should be handled in train/test splits remains a decision for subsequent evaluation protocol design in VDR-04.

---

## New UNKNOWNs

The following new questions were uncovered during VDR-03 reconnaissance:

1. **Weak Association of Sample QC with Market Condemnation**: Why arrival physical sample measurements in `quality_checks.csv` (`firmness_kg_cm2`, `sugar_brix`, `defect_pct`) have near-zero linear correlation ($r \approx 0$) with commercial loss percentage (`loss_fraction_pct`), `quality_score`, and `economic_loss_eur` in this snapshot.
2. **Historical Status Threshold Provenance**: Whether the exact bin boundaries for `quality_status` ($5.0\%$, $15.0\%$, $35.0\%$) reflect external agricultural market norms or synthetic dataset quantization.

---

## Risks / limitations

1. **Risk of Target Leakage**: Because historical outcome fields are present in the dataset, automated feature generation must strictly filter out outcome fields and post-dispatch transit actuals.
2. **Floor Distortion in `quality_score`**: The concentration of 78 batches at 5.0 in `quality_score` creates non-linear distortion for batches with high loss.
3. **Class Imbalance**: In `quality_status`, the `lost` category represents only 6.39% of the dataset (115 batches).

---

## Reproduction and evidence

All statistical calculations, distributions, correlations, formula verifications, and timing audits were executed using Python standard library scripts directly on raw sponsor data files.

- **Exact script location:** `C:\Users\victo\.gemini\antigravity\brain\4b755a2c-a26f-44bb-8e5f-edcb5e01bcad\scratch\vdr03_reproduce_all.py`
- **Exact command executed:** `python C:\Users\victo\.gemini\antigravity\brain\4b755a2c-a26f-44bb-8e5f-edcb5e01bcad\scratch\vdr03_reproduce_all.py`
- **Exit code:** `0`
- **Percentile method:** Linear interpolation between nearest ranks ($k = (n - 1) \times p$), equivalent to `statistics.quantiles(..., method='inclusive')` and NIST / R Type 7 / NumPy default. Medians are calculated using standard-library `statistics.median`.

### Complete Standard-Library Reproduction Script

```python
import csv
import math
import os
from collections import Counter, defaultdict
from datetime import datetime
from statistics import median

data_dir = r"C:\Users\victo\.gemini\antigravity\scratch\training_agrifood\sponsor_pack\data"

with open(os.path.join(data_dir, "historical_quality_outcomes.csv"), "r", encoding="utf-8") as f:
    outcomes = {r['batch_id']: r for r in csv.DictReader(f)}

with open(os.path.join(data_dir, "batches.csv"), "r", encoding="utf-8") as f:
    batches = {r['batch_id']: r for r in csv.DictReader(f)}

with open(os.path.join(data_dir, "storage_sessions.csv"), "r", encoding="utf-8") as f:
    sessions = {r['batch_id']: r for r in csv.DictReader(f)}

with open(os.path.join(data_dir, "shipments.csv"), "r", encoding="utf-8") as f:
    shipments = {r['batch_id']: r for r in csv.DictReader(f)}

with open(os.path.join(data_dir, "quality_checks.csv"), "r", encoding="utf-8") as f:
    qchecks = list(csv.DictReader(f))

def percentile(s, p):
    # Linear interpolation between nearest ranks (equivalent to statistics.quantiles method='inclusive' / NIST / R Type 7)
    n = len(s)
    if n == 1:
        return s[0]
    k = (n - 1) * p
    i = int(k)
    f = k - i
    if i + 1 < n:
        return (1.0 - f) * s[i] + f * s[i + 1]
    return s[-1]

def dist_stats(vals):
    s = sorted(vals)
    n = len(s)
    mean = sum(s) / n
    std = math.sqrt(sum((x - mean)**2 for x in s) / (n - 1)) if n > 1 else 0.0
    return {
        'count': n,
        'min': round(s[0], 2),
        'p25': round(percentile(s, 0.25), 2),
        'median': round(median(s), 2),
        'p75': round(percentile(s, 0.75), 2),
        'p90': round(percentile(s, 0.90), 2),
        'max': round(s[-1], 2),
        'mean': round(mean, 2),
        'std': round(std, 2)
    }

def pearson(x, y):
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    c = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    sx = math.sqrt(sum((xi - mx)**2 for xi in x))
    sy = math.sqrt(sum((yi - my)**2 for yi in y))
    return c / (sx * sy) if (sx * sy) > 0 else 0.0

# 1. Row counts and missingness
print("=== 1. ROW COUNTS AND MISSINGNESS ===")
print(f"historical_quality_outcomes: {len(outcomes)} rows")
for col in ['quality_status', 'loss_fraction_pct', 'quality_score', 'economic_loss_eur']:
    miss = sum(1 for r in outcomes.values() if r[col] == "" or r[col] is None)
    print(f"  missing {col}: {miss}")

# 2. Historical outcome distributions and percentiles
print("\n=== 2. HISTORICAL OUTCOME DISTRIBUTIONS ===")
for col in ['loss_fraction_pct', 'quality_score', 'economic_loss_eur']:
    vals = [float(r[col]) for r in outcomes.values()]
    st = dist_stats(vals)
    print(f"{col}: min={st['min']}, p25={st['p25']}, median={st['median']}, p75={st['p75']}, p90={st['p90']}, max={st['max']}, mean={st['mean']}, std={st['std']}")
econ_sum = sum(float(r['economic_loss_eur']) for r in outcomes.values())
print(f"economic_loss_eur total: {econ_sum:.2f} EUR")

st_counts = Counter(r['quality_status'] for r in outcomes.values())
for k in ['optimal', 'degraded', 'severe_degradation', 'lost']:
    cnt = st_counts[k]
    print(f"quality_status {k}: {cnt} ({cnt/len(outcomes)*100:.2f}%)")

# 3. Per-crop outcome statistics
print("\n=== 3. PER-CROP OUTCOME STATISTICS ===")
crops = sorted(list(set(b['crop_type'] for b in batches.values())))
for crop in crops:
    c_bids = [bid for bid, b in batches.items() if b['crop_type'] == crop]
    c_losses = [float(outcomes[bid]['loss_fraction_pct']) for bid in c_bids]
    c_scores = [float(outcomes[bid]['quality_score']) for bid in c_bids]
    c_econs = [float(outcomes[bid]['economic_loss_eur']) for bid in c_bids]
    c_st = Counter(outcomes[bid]['quality_status'] for bid in c_bids)
    c_loss_st = dist_stats(c_losses)
    c_score_st = dist_stats(c_scores)
    print(f"Crop {crop} (n={len(c_bids)}):")
    print(f"  loss_pct: mean={c_loss_st['mean']}, median={c_loss_st['median']}")
    print(f"  quality_score: mean={c_score_st['mean']}, median={c_score_st['median']}")
    print(f"  economic_loss_eur: mean={sum(c_econs)/len(c_econs):.2f}, sum={sum(c_econs):.2f}")
    print(f"  status counts (opt/deg/sev/lost): {c_st['optimal']} / {c_st['degraded']} / {c_st['severe_degradation']} / {c_st['lost']}")

# 4. Inferred crop prices and economic loss formula
print("\n=== 4. INFERRED CROP PRICES AND ECONOMIC LOSS FORMULA ===")
inferred_prices = defaultdict(list)
for bid, r in outcomes.items():
    b = batches[bid]
    crop = b['crop_type']
    w_kg = float(b['harvest_weight_kg'])
    loss_f = float(r['loss_fraction_pct']) / 100.0
    econ = float(r['economic_loss_eur'])
    lost_kg = w_kg * loss_f
    if lost_kg > 0:
        price = econ / lost_kg
        inferred_prices[crop].append(price)

crop_prices = {}
for crop in crops:
    p_list = inferred_prices[crop]
    p_min = min(p_list)
    p_max = max(p_list)
    p_mean = sum(p_list) / len(p_list)
    rounded_set = set(round(p, 4) for p in p_list)
    unit_p = round(p_mean, 2)
    crop_prices[crop] = unit_p
    print(f"  {crop:12}: n={len(p_list)}, min={p_min:.6f}, max={p_max:.6f}, mean={p_mean:.6f}, rounded(2)={unit_p}, unique rounded(4) count={len(rounded_set)}")

max_econ_diff = max(
    abs(float(r['economic_loss_eur']) - round(float(batches[bid]['harvest_weight_kg']) * (float(r['loss_fraction_pct']) / 100.0) * crop_prices[batches[bid]['crop_type']], 2))
    for bid, r in outcomes.items()
)
diffs_gt_001 = sum(
    1 for bid, r in outcomes.items()
    if abs(float(r['economic_loss_eur']) - round(float(batches[bid]['harvest_weight_kg']) * (float(r['loss_fraction_pct']) / 100.0) * crop_prices[batches[bid]['crop_type']], 2)) > 0.01
)
print(f"economic_loss_eur max abs diff: {max_econ_diff:.6f} EUR (diffs > 0.01 EUR: {diffs_gt_001})")

# 5. quality_status boundary mapping
print("\n=== 5. QUALITY_STATUS BOUNDARY MAPPING ===")
mismatches = 0
status_loss_ranges = defaultdict(list)
for bid, r in outcomes.items():
    loss = float(r['loss_fraction_pct'])
    st = r['quality_status']
    status_loss_ranges[st].append(loss)
    expected = 'optimal' if loss < 5.0 else ('degraded' if loss < 15.0 else ('severe_degradation' if loss < 35.0 else 'lost'))
    if st != expected:
        mismatches += 1
print(f"quality_status mismatches: {mismatches} / {len(outcomes)}")
for st in ['optimal', 'degraded', 'severe_degradation', 'lost']:
    vl = status_loss_ranges[st]
    print(f"  {st:18}: n={len(vl)} ({len(vl)/len(outcomes)*100:.2f}%), observed min={min(vl):.2f}%, max={max(vl):.2f}%")

# 6. quality_score correlation, fitted linear specification, R^2, bounds
print("\n=== 6. QUALITY_SCORE CORRELATION, FIT, BOUNDS ===")
loss_vals = [float(r['loss_fraction_pct']) for r in outcomes.values()]
score_vals = [float(r['quality_score']) for r in outcomes.values()]
n = len(loss_vals)
mean_l = sum(loss_vals) / n
mean_s = sum(score_vals) / n
cov = sum((l - mean_l) * (s - mean_s) for l, s in zip(loss_vals, score_vals)) / (n - 1)
var_l = sum((l - mean_l)**2 for l in loss_vals) / (n - 1)
var_s = sum((s - mean_s)**2 for s in score_vals) / (n - 1)
r_pearson = cov / (math.sqrt(var_l) * math.sqrt(var_s))
slope = cov / var_l
intercept = mean_s - slope * mean_l
residuals = [s - (intercept + slope * l) for l, s in zip(loss_vals, score_vals)]
rmse = math.sqrt(sum(res**2 for res in residuals) / n)
max_abs_res = max(abs(res) for res in residuals)
r_squared = (cov**2) / (var_l * var_s)

min_score_bids = [bid for bid, r in outcomes.items() if float(r['quality_score']) == 5.0]
max_score_bids = [bid for bid, r in outcomes.items() if float(r['quality_score']) == 98.5]
min_score_losses = [float(outcomes[bid]['loss_fraction_pct']) for bid in min_score_bids]
max_score_losses = [float(outcomes[bid]['loss_fraction_pct']) for bid in max_score_bids]

print(f"quality_score vs loss_fraction_pct: r={r_pearson:.6f}, R2={r_squared:.6f}")
print(f"  fit: quality_score = {intercept:.4f} + ({slope:.4f}) * loss_fraction_pct")
print(f"  RMS residual={rmse:.4f}, max_abs_res={max_abs_res:.4f}")
print(f"  score==5.0 count={len(min_score_bids)}, loss range=[{min(min_score_losses):.2f}%, {max(min_score_losses):.2f}%]")
print(f"  score==98.5 count={len(max_score_bids)}, loss range=[{min(max_score_losses):.2f}%, {max(max_score_losses):.2f}%]")

# 7. Quality check correlations (including initial_quality_score and economic_loss_eur)
print("\n=== 7. QUALITY CHECK CORRELATIONS ===")
by_batch_stage = defaultdict(dict)
for q in qchecks:
    by_batch_stage[q['batch_id']][q['stage']] = q

arr_firmness = [float(by_batch_stage[bid]['arrival']['firmness_kg_cm2']) for bid in outcomes]
arr_brix = [float(by_batch_stage[bid]['arrival']['sugar_brix']) for bid in outcomes]
arr_defects = [float(by_batch_stage[bid]['arrival']['defect_pct']) for bid in outcomes]
init_scores = [float(batches[bid]['initial_quality_score']) for bid in outcomes]
econ_losses = [float(outcomes[bid]['economic_loss_eur']) for bid in outcomes]

print(f"corr(loss, arr_firmness):    {pearson(loss_vals, arr_firmness):.6f}")
print(f"corr(loss, arr_brix):        {pearson(loss_vals, arr_brix):.6f}")
print(f"corr(loss, arr_defects):     {pearson(loss_vals, arr_defects):.6f}")
print(f"corr(loss, initial_score):   {pearson(loss_vals, init_scores):.6f}")
print(f"corr(score, arr_firmness):   {pearson(score_vals, arr_firmness):.6f}")
print(f"corr(score, arr_brix):       {pearson(score_vals, arr_brix):.6f}")
print(f"corr(score, arr_defects):    {pearson(score_vals, arr_defects):.6f}")
print(f"corr(score, initial_score):  {pearson(score_vals, init_scores):.6f}")
print(f"corr(econ, arr_firmness):    {pearson(econ_losses, arr_firmness):.6f}")
print(f"corr(econ, arr_brix):        {pearson(econ_losses, arr_brix):.6f}")
print(f"corr(econ, arr_defects):     {pearson(econ_losses, arr_defects):.6f}")
print(f"corr(econ, initial_score):   {pearson(econ_losses, init_scores):.6f}")

# 8. Checkpoint measurement distributions and offsets
print("\n=== 8. CHECKPOINT MEASUREMENTS AND OFFSETS ===")
stage_counts = Counter(q['stage'] for q in qchecks)
print(f"Checkpoint counts: {dict(stage_counts)}")
for stg in ['harvest', 'pre_dispatch', 'arrival']:
    for m in ['firmness_kg_cm2', 'sugar_brix', 'defect_pct']:
        v = [float(by_batch_stage[b][stg][m]) for b in outcomes]
        s = dist_stats(v)
        print(f"  {stg:12} {m:15}: min={s['min']}, p25={s['p25']}, median={s['median']}, p75={s['p75']}, max={s['max']}, mean={s['mean']}, std={s['std']}")

dt_fmt = "%Y-%m-%d %H:%M:%S"
harv_offsets = [(datetime.strptime(by_batch_stage[b]['harvest']['check_datetime'], dt_fmt) - datetime.strptime(batches[b]['harvest_datetime'], dt_fmt)).total_seconds() / 3600.0 for b in outcomes]
pre_offsets = [(datetime.strptime(sessions[b]['dispatch_datetime'], dt_fmt) - datetime.strptime(by_batch_stage[b]['pre_dispatch']['check_datetime'], dt_fmt)).total_seconds() / 3600.0 for b in outcomes]
arr_offsets = [(datetime.strptime(by_batch_stage[b]['arrival']['check_datetime'], dt_fmt) - datetime.strptime(shipments[b]['actual_arrival_datetime'], dt_fmt)).total_seconds() / 3600.0 for b in outcomes]
print(f"QC offsets unique: harv={set(harv_offsets)}, pre={set(pre_offsets)}, arr={set(arr_offsets)}")

# 9. Lifecycle interval distributions and trajectory deltas
print("\n=== 9. INTERVALS AND TRAJECTORY DELTAS ===")
h_to_p_days = [(datetime.strptime(by_batch_stage[b]['pre_dispatch']['check_datetime'], dt_fmt) - datetime.strptime(by_batch_stage[b]['harvest']['check_datetime'], dt_fmt)).total_seconds() / 86400.0 for b in outcomes]
p_to_a_hours = [(datetime.strptime(by_batch_stage[b]['arrival']['check_datetime'], dt_fmt) - datetime.strptime(by_batch_stage[b]['pre_dispatch']['check_datetime'], dt_fmt)).total_seconds() / 3600.0 for b in outcomes]
h_to_a_days = [(datetime.strptime(by_batch_stage[b]['arrival']['check_datetime'], dt_fmt) - datetime.strptime(by_batch_stage[b]['harvest']['check_datetime'], dt_fmt)).total_seconds() / 86400.0 for b in outcomes]

s_hp = dist_stats(h_to_p_days)
s_pa = dist_stats(p_to_a_hours)
s_ha = dist_stats(h_to_a_days)
print(f"Harvest QC -> Pre-dispatch QC (days): min={s_hp['min']}, p25={s_hp['p25']}, median={s_hp['median']}, p75={s_hp['p75']}, max={s_hp['max']}, mean={s_hp['mean']}, std={s_hp['std']}")
print(f"Pre-dispatch QC -> Arrival QC (hours): min={s_pa['min']}, p25={s_pa['p25']}, median={s_pa['median']}, p75={s_pa['p75']}, max={s_pa['max']}, mean={s_pa['mean']}, std={s_pa['std']}")
print(f"Harvest QC -> Arrival QC (days):       min={s_ha['min']}, p25={s_ha['p25']}, median={s_ha['median']}, p75={s_ha['p75']}, max={s_ha['max']}, mean={s_ha['mean']}, std={s_ha['std']}")

delta_firm_h_p = [float(by_batch_stage[b]['pre_dispatch']['firmness_kg_cm2']) - float(by_batch_stage[b]['harvest']['firmness_kg_cm2']) for b in outcomes]
delta_firm_p_a = [float(by_batch_stage[b]['arrival']['firmness_kg_cm2']) - float(by_batch_stage[b]['pre_dispatch']['firmness_kg_cm2']) for b in outcomes]
delta_brix_h_p = [float(by_batch_stage[b]['pre_dispatch']['sugar_brix']) - float(by_batch_stage[b]['harvest']['sugar_brix']) for b in outcomes]
delta_brix_p_a = [float(by_batch_stage[b]['arrival']['sugar_brix']) - float(by_batch_stage[b]['pre_dispatch']['sugar_brix']) for b in outcomes]
delta_def_h_p = [float(by_batch_stage[b]['pre_dispatch']['defect_pct']) - float(by_batch_stage[b]['harvest']['defect_pct']) for b in outcomes]
delta_def_p_a = [float(by_batch_stage[b]['arrival']['defect_pct']) - float(by_batch_stage[b]['pre_dispatch']['defect_pct']) for b in outcomes]

s_df_hp = dist_stats(delta_firm_h_p)
s_df_pa = dist_stats(delta_firm_p_a)
s_db_hp = dist_stats(delta_brix_h_p)
s_db_pa = dist_stats(delta_brix_p_a)
s_dd_hp = dist_stats(delta_def_h_p)
s_dd_pa = dist_stats(delta_def_p_a)

print(f"Delta Firmness (Pre - Harv): neg={sum(1 for d in delta_firm_h_p if d < -1e-5)}, zero={sum(1 for d in delta_firm_h_p if abs(d) <= 1e-5)}, pos={sum(1 for d in delta_firm_h_p if d > 1e-5)} | mean={s_df_hp['mean']}")
print(f"Delta Firmness (Arr - Pre):  neg={sum(1 for d in delta_firm_p_a if d < -1e-5)}, zero={sum(1 for d in delta_firm_p_a if abs(d) <= 1e-5)}, pos={sum(1 for d in delta_firm_p_a if d > 1e-5)} | mean={s_df_pa['mean']}")
print(f"Delta Brix (Pre - Harv):     neg={sum(1 for d in delta_brix_h_p if d < -1e-5)}, zero={sum(1 for d in delta_brix_h_p if abs(d) <= 1e-5)}, pos={sum(1 for d in delta_brix_h_p if d > 1e-5)} | mean={s_db_hp['mean']}")
print(f"Delta Brix (Arr - Pre):      neg={sum(1 for d in delta_brix_p_a if d < -1e-5)}, zero={sum(1 for d in delta_brix_p_a if abs(d) <= 1e-5)}, pos={sum(1 for d in delta_brix_p_a if d > 1e-5)} | mean={s_db_pa['mean']}")
print(f"Delta Defect % (Pre - Harv): neg={sum(1 for d in delta_def_h_p if d < -1e-5)}, zero={sum(1 for d in delta_def_h_p if abs(d) <= 1e-5)}, pos={sum(1 for d in delta_def_h_p if d > 1e-5)} | mean={s_dd_hp['mean']}")
print(f"Delta Defect % (Arr - Pre):  neg={sum(1 for d in delta_def_p_a if d < -1e-5)}, zero={sum(1 for d in delta_def_p_a if abs(d) <= 1e-5)}, pos={sum(1 for d in delta_def_p_a if d > 1e-5)} | mean={s_dd_pa['mean']}")

# 10. Intermediate checks and outcome timing
print("\n=== 10. INTERMEDIATE CHECKS AND OUTCOME TIMING ===")
checks_per_batch = Counter(q['batch_id'] for q in qchecks)
print(f"Batches with exactly 3 checks: {sum(1 for cnt in checks_per_batch.values() if cnt == 3)} / {len(batches)}")
print(f"Batches with < 3 or > 3 checks: {sum(1 for cnt in checks_per_batch.values() if cnt != 3)}")

post_dispatch_arr = sum(1 for b in outcomes if datetime.strptime(shipments[b]['actual_arrival_datetime'], dt_fmt) > datetime.strptime(sessions[b]['dispatch_datetime'], dt_fmt))
print(f"Batches where actual_arrival > dispatch: {post_dispatch_arr} / {len(outcomes)}")
transit_hours = [(datetime.strptime(shipments[b]['actual_arrival_datetime'], dt_fmt) - datetime.strptime(sessions[b]['dispatch_datetime'], dt_fmt)).total_seconds() / 3600.0 for b in outcomes]
s_tr = dist_stats(transit_hours)
print(f"Transit duration (actual_arrival - dispatch): min={s_tr['min']}, p25={s_tr['p25']}, median={s_tr['median']}, p75={s_tr['p75']}, max={s_tr['max']}, mean={s_tr['mean']}, std={s_tr['std']}")

# 11. Sensor cutoff and truncated batches analysis
print("\n=== 11. SENSOR CUTOFF AND TRUNCATED BATCHES ===")
sensor_count = 0
min_ts = None
max_ts = None

with open(os.path.join(data_dir, "sensor_readings.csv"), "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    assert "timestamp" in header, "Missing expected 'timestamp' column in header"
    ts_idx = header.index("timestamp")
    for row in reader:
        sensor_count += 1
        ts = row[ts_idx]
        if min_ts is None or ts < min_ts:
            min_ts = ts
        if max_ts is None or ts > max_ts:
            max_ts = ts

print(f"sensor_readings row count: {sensor_count}")
print(f"min(timestamp): {min_ts}")
print(f"max(timestamp): {max_ts}")

trunc_bids = [bid for bid, s in sessions.items() if s['dispatch_datetime'] > max_ts]
print(f"Total batches dispatched after sensor cutoff ({max_ts}): {len(trunc_bids)}")
trunc_crops = Counter(batches[bid]['crop_type'] for bid in trunc_bids)
print(f"Truncated batch crops: {dict(trunc_crops)}")
trunc_harv_years = Counter(batches[bid]['harvest_datetime'][:4] for bid in trunc_bids)
trunc_disp_years = Counter(sessions[bid]['dispatch_datetime'][:4] for bid in trunc_bids)
print(f"Harvest years: {dict(trunc_harv_years)}, Dispatch years: {dict(trunc_disp_years)}")
trunc_harv_dates = [batches[bid]['harvest_datetime'] for bid in trunc_bids]
trunc_disp_dates = [sessions[bid]['dispatch_datetime'] for bid in trunc_bids]
print(f"Harvest date range: {min(trunc_harv_dates)} to {max(trunc_harv_dates)}")
print(f"Dispatch date range: {min(trunc_disp_dates)} to {max(trunc_disp_dates)}")

cutoff_dt = datetime.strptime(max_ts, dt_fmt)
gaps_days = [(datetime.strptime(sessions[bid]['dispatch_datetime'], dt_fmt) - cutoff_dt).total_seconds() / 86400.0 for bid in trunc_bids]
s_gap = dist_stats(gaps_days)
print(f"Pre-dispatch telemetry gap (days): count={s_gap['count']}, min={s_gap['min']}, median={s_gap['median']}, max={s_gap['max']}, mean={s_gap['mean']}, std={s_gap['std']}")
```

### Concise Actual Outputs

```text
=== 1. ROW COUNTS AND MISSINGNESS ===
historical_quality_outcomes: 1800 rows
  missing quality_status: 0
  missing loss_fraction_pct: 0
  missing quality_score: 0
  missing economic_loss_eur: 0

=== 2. HISTORICAL OUTCOME DISTRIBUTIONS ===
loss_fraction_pct: min=0.4, p25=4.27, median=9.83, p75=18.0, p90=26.42, max=95.44, mean=14.33, std=16.07
quality_score: min=5.0, p25=68.9, median=82.6, p75=92.2, p90=95.5, max=98.5, mean=76.7, std=21.58
economic_loss_eur: min=12.35, p25=222.03, median=488.57, p75=969.34, p90=1629.6, max=7794.86, mean=766.04, std=892.49
economic_loss_eur total: 1378872.97 EUR
quality_status optimal: 549 (30.50%)
quality_status degraded: 620 (34.44%)
quality_status severe_degradation: 516 (28.67%)
quality_status lost: 115 (6.39%)

=== 3. PER-CROP OUTCOME STATISTICS ===
Crop apples (n=673):
  loss_pct: mean=8.94, median=5.08
  quality_score: mean=84.37, median=90.5
  economic_loss_eur: mean=545.49, sum=367117.86
  status counts (opt/deg/sev/lost): 332 / 223 / 94 / 24
Crop apricots (n=60):
  loss_pct: mean=22.3, median=14.59
  quality_score: mean=66.61, median=75.1
  economic_loss_eur: mean=984.92, sum=59095.19
  status counts (opt/deg/sev/lost): 8 / 24 / 19 / 9
Crop pears (n=114):
  loss_pct: mean=13.82, median=8.07
  quality_score: mean=76.92, median=86.6
  economic_loss_eur: mean=1080.17, sum=123139.23
  status counts (opt/deg/sev/lost): 36 / 42 / 27 / 9
Crop plums (n=350):
  loss_pct: mean=14.8, median=10.73
  quality_score: mean=76.27, median=81.5
  economic_loss_eur: mean=692.89, sum=242511.58
  status counts (opt/deg/sev/lost): 94 / 129 / 106 / 21
Crop raspberries (n=50):
  loss_pct: mean=24.63, median=20.58
  quality_score: mean=62.26, median=64.35
  economic_loss_eur: mean=1008.51, sum=50425.50
  status counts (opt/deg/sev/lost): 2 / 10 / 33 / 5
Crop strawberries (n=63):
  loss_pct: mean=20.56, median=17.71
  quality_score: mean=66.91, median=69.4
  economic_loss_eur: mean=927.81, sum=58451.80
  status counts (opt/deg/sev/lost): 4 / 19 / 35 / 5
Crop table_grapes (n=310):
  loss_pct: mean=16.96, median=14.66
  quality_score: mean=71.52, median=74.5
  economic_loss_eur: mean=1090.35, sum=338008.03
  status counts (opt/deg/sev/lost): 42 / 118 / 129 / 21
Crop tomatoes (n=180):
  loss_pct: mean=21.64, median=15.47
  quality_score: mean=68.44, median=73.6
  economic_loss_eur: mean=778.47, sum=140123.78
  status counts (opt/deg/sev/lost): 31 / 55 / 73 / 21

=== 4. INFERRED CROP PRICES AND ECONOMIC LOSS FORMULA ===
  apples      : n=673, min=0.649822, max=0.650056, mean=0.649999, rounded(2)=0.65, unique rounded(4) count=4
  apricots    : n=60, min=1.099864, max=1.100030, mean=1.099996, rounded(2)=1.1, unique rounded(4) count=2
  pears       : n=114, min=0.949964, max=0.950112, mean=0.950002, rounded(2)=0.95, unique rounded(4) count=2
  plums       : n=350, min=0.749913, max=0.750133, mean=0.750001, rounded(2)=0.75, unique rounded(4) count=3
  raspberries : n=50, min=3.099940, max=3.100148, mean=3.100003, rounded(2)=3.1, unique rounded(4) count=3
  strawberries: n=63, min=2.399936, max=2.400072, mean=2.399998, rounded(2)=2.4, unique rounded(4) count=3
  table_grapes: n=310, min=1.249938, max=1.250057, mean=1.250000, rounded(2)=1.25, unique rounded(4) count=3
  tomatoes    : n=180, min=0.849964, max=0.850193, mean=0.850004, rounded(2)=0.85, unique rounded(4) count=3
economic_loss_eur max abs diff: 0.000000 EUR (diffs > 0.01 EUR: 0)

=== 5. QUALITY_STATUS BOUNDARY MAPPING ===
quality_status mismatches: 0 / 1800
  optimal           : n=549 (30.50%), observed min=0.40%, max=4.99%
  degraded          : n=620 (34.44%), observed min=5.00%, max=14.98%
  severe_degradation: n=516 (28.67%), observed min=15.00%, max=34.72%
  lost              : n=115 (6.39%), observed min=35.35%, max=95.44%

=== 6. QUALITY_SCORE CORRELATION, FIT, BOUNDS ===
quality_score vs loss_fraction_pct: r=-0.972695, R2=0.946135
  fit: quality_score = 95.4137 + (-1.3059) * loss_fraction_pct
  RMS residual=5.0066, max_abs_res=34.2255
  score==5.0 count=78, loss range=[54.44%, 95.44%]
  score==98.5 count=36, loss range=[0.40%, 1.77%]

=== 7. QUALITY CHECK CORRELATIONS ===
corr(loss, arr_firmness):    0.020822
corr(loss, arr_brix):        0.003859
corr(loss, arr_defects):     -0.003303
corr(loss, initial_score):   -0.024139
corr(score, arr_firmness):   -0.026284
corr(score, arr_brix):       -0.008493
corr(score, arr_defects):    0.011226
corr(score, initial_score):  0.039173
corr(econ, arr_firmness):    0.007824
corr(econ, arr_brix):        0.007819
corr(econ, arr_defects):     -0.004120
corr(econ, initial_score):   -0.040336

=== 8. CHECKPOINT MEASUREMENTS AND OFFSETS ===
Checkpoint counts: {'harvest': 1800, 'pre_dispatch': 1800, 'arrival': 1800}
  harvest      firmness_kg_cm2: min=6.5, p25=6.98, median=7.49, p75=8.0, max=8.5, mean=7.5, std=0.58
  harvest      sugar_brix     : min=11.0, p25=12.4, median=13.8, p75=15.1, max=16.5, mean=13.77, std=1.58
  harvest      defect_pct     : min=0.5, p25=1.3, median=2.2, p75=3.1, max=4.0, mean=2.21, std=0.99
  pre_dispatch firmness_kg_cm2: min=5.0, p25=5.7, median=6.41, p75=7.09, max=7.8, mean=6.41, std=0.81
  pre_dispatch sugar_brix     : min=11.5, p25=12.9, median=14.4, p75=15.6, max=17.0, mean=14.28, std=1.58
  pre_dispatch defect_pct     : min=1.0, p25=2.8, median=4.7, p75=6.5, max=8.5, mean=4.71, std=2.16
  arrival      firmness_kg_cm2: min=4.0, p25=4.78, median=5.62, p75=6.43, max=7.2, mean=5.62, std=0.93
  arrival      sugar_brix     : min=11.5, p25=12.9, median=14.3, p75=15.8, max=17.2, mean=14.34, std=1.66
  arrival      defect_pct     : min=1.5, p25=5.6, median=9.9, p75=14.0, max=18.0, mean=9.84, std=4.74
QC offsets unique: harv={1.0}, pre={2.0}, arr={0.0}

=== 9. INTERVALS AND TRAJECTORY DELTAS ===
Harvest QC -> Pre-dispatch QC (days): min=2.98, p25=19.13, median=54.09, p75=92.36, max=175.02, mean=59.89, std=43.74
Pre-dispatch QC -> Arrival QC (hours): min=7.07, p25=11.54, median=19.85, p75=35.77, max=52.51, mean=23.4, std=12.6
Harvest QC -> Arrival QC (days):       min=3.36, p25=20.31, median=55.15, p75=93.97, max=176.75, mean=60.86, std=43.75
Delta Firmness (Pre - Harv): neg=1516, zero=6, pos=278 | mean=-1.09
Delta Firmness (Arr - Pre):  neg=1300, zero=3, pos=497 | mean=-0.79
Delta Brix (Pre - Harv):     neg=716, zero=27, pos=1057 | mean=0.51
Delta Brix (Arr - Pre):      neg=887, zero=34, pos=879 | mean=0.06
Delta Defect % (Pre - Harv): neg=311, zero=12, pos=1477 | mean=2.5
Delta Defect % (Arr - Pre):  neg=338, zero=10, pos=1452 | mean=5.14

=== 10. INTERMEDIATE CHECKS AND OUTCOME TIMING ===
Batches with exactly 3 checks: 1800 / 1800
Batches with < 3 or > 3 checks: 0
Batches where actual_arrival > dispatch: 1800 / 1800
Transit duration (actual_arrival - dispatch): min=5.07, p25=9.54, median=17.85, p75=33.77, max=50.51, mean=21.4, std=12.6

=== 11. SENSOR CUTOFF AND TRUNCATED BATCHES ===
sensor_readings row count: 669665
min(timestamp): 2024-05-19 00:00:00
max(timestamp): 2025-12-31 23:30:00
Total batches dispatched after sensor cutoff (2025-12-31 23:30:00): 204
Truncated batch crops: {'apples': 189, 'pears': 14, 'table_grapes': 1}
Harvest years: {'2025': 204}, Dispatch years: {'2026': 204}
Harvest date range: 2025-08-22 07:00:00 to 2025-10-25 13:15:00
Dispatch date range: 2026-01-01 12:49:48 to 2026-04-03 12:30:36
Pre-dispatch telemetry gap (days): count=204, min=0.56, median=24.4, max=92.54, mean=29.01, std=21.42
```
