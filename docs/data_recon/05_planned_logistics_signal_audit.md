# VDR-05 — Planned Logistics Signal Decomposition & Proxy Robustness Audit

## Status and provenance

- **Owner:** Viktor — Implementation / Evaluation Agent
- **Repository:** `Slave-of-Skynet/training_agrifood`
- **Assigned Base SHA:** `6d0e4a50c36937f01b769a16a99bfa03af458c66`
- **Actual Base SHA:** `6d0e4a50c36937f01b769a16a99bfa03af458c66` (matches `origin/main` exactly following PR #25 merge).
- **Branch:** `victor/vdr-05-logistics-signal-audit`
- **Status:** DRAFT FOR REVIEW — EVIDENCE ONLY
- **Decision Authority:** NONE (This report produces reproducible empirical evidence for a subsequent Integrator decision gate; it makes no production, architecture, or contract decisions).
- **Execution Script:** `scripts/vdr05_logistics_signal_audit.py`
- **Output Artifacts:**
  - `docs/data_recon/05_planned_logistics_signal_audit_results.json`
  - `docs/data_recon/05_planned_logistics_signal_audit.md` (this report)

---

## Objective

In accepted benchmarks VDR-04A and VDR-04B, the planned-logistics feature family $L = \{\text{destination_market}, \text{destination_region}, \text{vehicle_type}, \text{planned_duration_hours}\}$ was evaluated jointly and found to provide the largest, most consistent incremental predictive and ranking association beyond pre-dispatch operational context $C$.

However, those benchmarks evaluated logistics exclusively as a composite 4-variable block. VDR-05 executes a dedicated decomposition and proxy robustness audit to answer:

1. **Individual Signal:** Which of the four individual planned-logistics fields account for the observed predictive and ranking lift?
2. **Marginal Contribution:** Which fields retain observable contribution once the other three fields are present (leave-one-out)?
3. **Internal Redundancy:** How redundant are the four logistics fields with one another?
4. **Proxy / Confounding Structure:** Are the logistics fields acting as descriptive proxies for facility, cold room, harvest origin, crop variety, or operational season identities?
5. **Robustness:** Does the strong $C+L$ association depend on identity/route/season proxy structure?
6. **Simplification Candidates:** Is a smaller logistics subset reasonable to carry forward for later human decision?

---

## Evidence and decision boundaries

[FACT] This study operates under strict normative boundaries:
- **Decision Authority:** NONE. VDR-05 does not select a production model, does not approve a production feature set, does not alter canonical input schemas, does not remove telemetry from canonical semantics, and does not make causal claims.
- **Fixed Assessment Anchor:** $T_{\text{assess}} \equiv T_{\text{dispatch}} = \text{storage_sessions.dispatch_datetime}$ per ADR 0002.
- **Strict Forbidden Denylist:** Programmatic assertions verified that zero arrival QC checks (`arrival_*`), zero realized transit fields (`actual_*`, `cold_chain_incident`, `transit_temp_mean_c`), zero post-dispatch sensor readings, zero historical settlement outcomes (`quality_status`, `loss_fraction_pct`, `quality_score`, `economic_loss_eur`), and zero surrogate identifiers (`batch_id`, `storage_session_id`, `facility_id`, `zone_id`, `shipment_id`) entered any predictive feature matrix.
- **Deterministic Baseline & Tie Policy:** All rankings resolve ties deterministically by secondary sorting on `batch_id` ascending (label-independent).
- **Optional Semantics:** Per ADR 0003 D4, planned logistics remain conditionally eligible and optional; VDR-05 does not make them mandatory for production operation.
- **Observed Association Only:** All findings describe empirical associations on the supplied synthetic simulation dataset; they do not establish causal transport mechanics or biological degradation laws.

---

## Sources inspected

Committed repository files inspected prior to analysis:
- `docs/decisions/0002-predictive-input-semantics.md` (ADR 0002)
- `docs/decisions/0003-assessment-evaluation-semantics.md` (ADR 0003)
- `docs/data_recon/01_dataset_inventory.md`
- `docs/data_recon/02_temporal_leakage.md`
- `docs/data_recon/03_target_horizon_feasibility.md`
- `docs/data_recon/04_dispatch_predictability.md`
- `docs/data_recon/04_dispatch_predictability_results.json`
- `docs/data_recon/04b_telemetry_ablation.md` (Blob SHA: `8a5e1f7609961697e1a7d125fc3ee3bd7a6cdba1`)
- `docs/data_recon/04b_telemetry_ablation_results.json` (Blob SHA: `61ae3907ac41538dcee25d310182bd07d12b943c`)
- `scripts/vdr04a_predictability.py`
- `scripts/vdr04b_telemetry_ablation.py` (Blob SHA: `f29237816a8b969017d72e66f3de3c9fa60ef242`)
- `docs/evaluation.md`
- `docs/assumptions_unknowns.md`
- `docs/data_contract.md`
- `docs/challenge_canon.md`

> [!NOTE]
> **Observed documentation-reconciliation follow-up for Vladimir:** Some shared documents (`challenge_canon.md`, `assumptions_unknowns.md`, `docs/decisions/0003-assessment-evaluation-semantics.md`) still contain historical statements written prior to VDR-04B stating that $C+L$ (without telemetry) had not yet been evaluated. Per task boundaries, these documents are not modified in VDR-05 and remain flagged for Integrator reconciliation.

---

## Dataset hashes and integrity

[FACT] Pre-analysis integrity checks verified exact dataset invariants:
- `batches.csv`: 1,800 rows (SHA256: `bbaf3cb4064ccdefed5eaca0b3fe7d6303bd918b1abc09a8c27cb20309d6072b`)
- `storage_sessions.csv`: 1,800 rows (SHA256: `f38a99dfeb808eaab3b3d91d0494d303649131ee2d5de9a6efa0da99fdf9e04f`)
- `facilities.csv`: 10 rows (SHA256: `148de414dcff6d601d327ce17414d8b9e04aaa38c6bc0ecbb769be32d6f3a960`)
- `storage_zones.csv`: 25 rows (SHA256: `e2c4b7170c47ab0896ed962c588256e3407d84d30afa758372a704d8085c4ee4`)
- `quality_checks.csv`: 5,400 rows (SHA256: `95ccf7d6d898249f6bf444a874817be74b7ce4338b3099f3bf8687f22fa9b627`)
- `shipments.csv`: 1,800 rows (SHA256: `bfad682700f58936ca383868febd09181bd810e81bd3287fa28d16d204ea9796`)
- `historical_quality_outcomes.csv`: 1,800 rows (SHA256: `567334f44f41b980c67de496736c077dc1d980b4cb02c14ee355597087732606`)
- `sensor_readings.csv`: 669,665 rows (SHA256: `6b27adaf43a6646d32cccddc95872bfed03a6220075d9508ccc54be5bdf9edbb`)

Reconstruction of concurrent chamber occupancy reproduced the accepted structure:
- **157 disjoint chamber-time connected clusters** across 25 storage zones.
- **1,734 out of 1,800 batches (96.33%)** in multi-batch clusters.

---

## Frozen evaluation design

Evaluations strictly follow the established protocols from VDR-04A and VDR-04B:

1. **Protocol P1 (Forward Inter-Season Holdout — Primary):**
   - Training: Season 2024 (900 batches, `dispatch_datetime < 2025-05-01`).
   - Test: Season 2025 (900 batches, `dispatch_datetime >= 2025-05-01`).
2. **Protocol P2 (Chamber-Time Grouped Out-of-Fold — Mandatory Robustness):**
   - 5-Fold `GroupKFold` blocked by the 157 chamber clusters (1,800 OOF predictions).
   - Zero cluster overlap between training and validation splits within any fold.
3. **Models & Hyperparameters:**
   - Linear: `Ridge(alpha=1.0, random_state=42)`
   - Nonlinear: `HistGradientBoostingRegressor(max_iter=100, max_leaf_nodes=31, random_state=42)`
4. **Preprocessing:**
   - Numeric: `SimpleImputer(strategy="median")` + `StandardScaler()`
   - Categorical: `OneHotEncoder(handle_unknown="ignore", sparse_output=False)`
   - Transformers fit strictly on training partitions/folds only.
5. **Target & Metrics:**
   - Offline supervised continuous target: `loss_fraction_pct`.
   - Continuous metrics: MAE, RMSE, $R^2$, Spearman rank correlation.
   - Ranking metrics: Spearman, NDCG@10, NDCG@50, Precision@10, Precision@50, Recall@10, Recall@50 (relevance: historical loss $\ge 15.0\%$).

---

## Exact ten feature families

[FACT] Feature matrices strictly evaluate the ten authorized families:

| # | Family Name | Description | Raw Column Count |
| :-: | :--- | :--- | :-: |
| 1 | `C` | Context family (frozen from VDR-04B) | 37 |
| 2 | `C + destination_market` | Context + Market destination | 38 |
| 3 | `C + destination_region` | Context + Macro destination region | 38 |
| 4 | `C + vehicle_type` | Context + Transport equipment type | 38 |
| 5 | `C + planned_duration_hours` | Context + Planned transit duration | 38 |
| 6 | `C + L` | Full context + Full planned logistics | 41 |
| 7 | `C + L without destination_market` | Leave-out Market ($C + \{R, V, D\}$) | 40 |
| 8 | `C + L without destination_region` | Leave-out Region ($C + \{M, V, D\}$) | 40 |
| 9 | `C + L without vehicle_type` | Leave-out Vehicle ($C + \{M, R, D\}$) | 40 |
| 10 | `C + L without planned_duration_hours` | Leave-out Duration ($C + \{M, R, V\}$) | 40 |

Programmatic assertions verified:
- Telemetry features in predictive matrices: **NO (0)**
- `facility_id` in predictive matrices: **NO (0)**
- `zone_id` in predictive matrices: **NO (0)**
- `batch_id` in predictive matrices: **NO (0)**
- Arrival QC in predictive matrices: **NO (0)**
- Realized transit in predictive matrices: **NO (0)**
- Outcome targets in predictive matrices: **NO (0)**

---

## VDR-04B reproduction gate

[FACT] Before evaluating new subsets or proxy diagnostics, overlapping baselines and families (`C` and `C+L`) were reproduced and compared against the committed historical results in `docs/data_recon/04b_telemetry_ablation_results.json`:

- **Maximum absolute difference across all compared metrics (MAE, RMSE, $R^2$, Spearman, NDCG@10, NDCG@50, Precision@10, Precision@50, Recall@10, Recall@50) across P1 and P2:**
  $$\mathbf{0.00000000 \times 10^0 \quad (\text{diff} < 10^{-15})}$$
- **Replication Status:** `EXACT_OR_NUMERICALLY_EQUIVALENT` (exact numerical parity achieved across all compared metrics).

---

## P1 results

Forward Inter-Season Holdout (Season 2024 train, 900 batches; Season 2025 test, 900 batches):

| Feature Family | Model | MAE | RMSE | $R^2$ | Spearman | NDCG@10 | NDCG@50 | Precision@10 | Precision@50 | Recall@10 | Recall@50 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Crop-Median)** | Heuristic | 8.8842 | 16.2401 | 0.0737 | 0.4497 | 0.2634 | 0.2797 | 0.8000 | 0.5800 | 0.0267 | 0.0967 |
| **1. C** | Ridge | 10.2628 | 16.7147 | 0.0187 | 0.4037 | 0.2269 | 0.2671 | 0.6000 | 0.6200 | 0.0200 | 0.1033 |
| **1. C** | HGB | 10.8628 | 17.2795 | -0.0487 | 0.3227 | 0.2189 | 0.2441 | 0.5000 | 0.6000 | 0.0167 | 0.1000 |
| **2. C + destination_market** | Ridge | 9.5943 | 15.7448 | 0.1293 | 0.5124 | 0.2667 | 0.4100 | 0.9000 | 0.8000 | 0.0300 | 0.1333 |
| **2. C + destination_market** | HGB | 9.1748 | 14.4337 | 0.2683 | 0.4114 | 0.8016 | 0.6584 | 1.0000 | 0.7600 | 0.0333 | 0.1267 |
| **3. C + destination_region** | Ridge | 9.8879 | 16.2007 | 0.0781 | 0.4761 | 0.1595 | 0.2577 | 0.6000 | 0.6400 | 0.0200 | 0.1067 |
| **3. C + destination_region** | HGB | 9.9698 | 15.8713 | 0.1153 | 0.4396 | 0.3413 | 0.3974 | 0.7000 | 0.6800 | 0.0233 | 0.1133 |
| **4. C + vehicle_type** | Ridge | 9.5957 | 15.8018 | 0.1230 | 0.5100 | 0.3556 | 0.4176 | 0.9000 | 0.8400 | 0.0300 | 0.1400 |
| **4. C + vehicle_type** | HGB | 9.0165 | 14.3469 | 0.2770 | 0.4305 | 0.8577 | 0.6477 | 1.0000 | 0.8200 | 0.0333 | 0.1367 |
| **5. C + planned_duration_hours** | Ridge | 10.1938 | 16.4899 | 0.0449 | 0.4455 | 0.1765 | 0.2675 | 0.7000 | 0.6400 | 0.0233 | 0.1067 |
| **5. C + planned_duration_hours** | HGB | 9.1281 | 14.5555 | 0.2559 | 0.4360 | 0.7991 | 0.6405 | 1.0000 | 0.7400 | 0.0333 | 0.1233 |
| **6. C + L (Anchor)** | Ridge | 9.5828 | 15.7708 | 0.1264 | 0.5148 | 0.3173 | 0.4184 | 0.9000 | 0.8400 | 0.0300 | 0.1400 |
| **6. C + L (Anchor)** | HGB | 8.8841 | 14.2411 | 0.2877 | 0.4455 | 0.8695 | 0.6567 | 1.0000 | 0.7800 | 0.0333 | 0.1300 |
| **7. C + L without market** | Ridge | 9.5808 | 15.7822 | 0.1252 | 0.5143 | 0.3705 | 0.4223 | 0.9000 | 0.8400 | 0.0300 | 0.1400 |
| **7. C + L without market** | HGB | 8.8645 | 14.2552 | 0.2863 | 0.4443 | 0.8588 | 0.6642 | 1.0000 | 0.8400 | 0.0333 | 0.1400 |
| **8. C + L without region** | Ridge | 9.5827 | 15.7708 | 0.1264 | 0.5148 | 0.3173 | 0.4154 | 0.9000 | 0.8200 | 0.0300 | 0.1367 |
| **8. C + L without region** | HGB | 8.9840 | 14.3172 | 0.2800 | 0.4300 | 0.8804 | 0.6719 | 1.0000 | 0.7800 | 0.0333 | 0.1300 |
| **9. C + L without vehicle** | Ridge | 9.5981 | 15.7452 | 0.1292 | 0.5123 | 0.2666 | 0.4099 | 0.9000 | 0.8000 | 0.0300 | 0.1333 |
| **9. C + L without vehicle** | HGB | 9.0489 | 14.3635 | 0.2754 | 0.4490 | 0.7403 | 0.6459 | 1.0000 | 0.8000 | 0.0333 | 0.1333 |
| **10. C + L without duration** | Ridge | 9.5828 | 15.7712 | 0.1264 | 0.5148 | 0.3173 | 0.4154 | 0.9000 | 0.8200 | 0.0300 | 0.1367 |
| **10. C + L without duration** | HGB | 8.8029 | 14.0947 | 0.3022 | 0.4558 | 0.8397 | 0.6575 | 1.0000 | 0.8000 | 0.0333 | 0.1333 |

---

## P2 results

Chamber-Time Grouped Out-of-Fold (All Batches, $N=1,800$, 5-Fold `GroupKFold`):

| Feature Family | Model | MAE | RMSE | $R^2$ | Spearman | NDCG@10 | NDCG@50 | Precision@10 | Precision@50 | Recall@10 | Recall@50 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Crop-Median)** | Heuristic | 8.8216 | 15.9096 | 0.0195 | 0.3525 | 0.2533 | 0.2906 | 0.5000 | 0.7600 | 0.0079 | 0.0602 |
| **1. C** | Ridge | 9.2948 | 15.1155 | 0.1150 | 0.4597 | 0.5977 | 0.3965 | 0.8000 | 0.6800 | 0.0127 | 0.0539 |
| **1. C** | HGB | 10.2402 | 16.0025 | 0.0080 | 0.3861 | 0.3069 | 0.2629 | 0.6000 | 0.7000 | 0.0095 | 0.0555 |
| **2. C + destination_market** | Ridge | 8.7421 | 14.1704 | 0.2222 | 0.5358 | 0.6970 | 0.6094 | 1.0000 | 0.9200 | 0.0158 | 0.0729 |
| **2. C + destination_market** | HGB | 8.3641 | 13.5379 | 0.2901 | 0.4902 | 0.8183 | 0.7759 | 1.0000 | 0.9800 | 0.0158 | 0.0777 |
| **3. C + destination_region** | Ridge | 9.0121 | 14.6386 | 0.1699 | 0.5010 | 0.5935 | 0.4591 | 0.7000 | 0.7800 | 0.0111 | 0.0618 |
| **3. C + destination_region** | HGB | 9.4169 | 14.8982 | 0.1402 | 0.4439 | 0.4241 | 0.4823 | 0.7000 | 0.7200 | 0.0111 | 0.0571 |
| **4. C + vehicle_type** | Ridge | 8.7143 | 14.1447 | 0.2250 | 0.5410 | 0.7459 | 0.6578 | 1.0000 | 0.9600 | 0.0158 | 0.0761 |
| **4. C + vehicle_type** | HGB | 8.0766 | 13.1692 | 0.3282 | 0.5041 | 0.8967 | 0.7995 | 1.0000 | 0.9200 | 0.0158 | 0.0729 |
| **5. C + planned_duration_hours** | Ridge | 9.1756 | 14.8465 | 0.1462 | 0.4875 | 0.6022 | 0.4039 | 0.8000 | 0.7800 | 0.0127 | 0.0618 |
| **5. C + planned_duration_hours** | HGB | 8.3782 | 13.5002 | 0.2940 | 0.4816 | 0.8827 | 0.7610 | 1.0000 | 0.9200 | 0.0158 | 0.0729 |
| **6. C + L (Anchor)** | Ridge | 8.7328 | 14.1594 | 0.2234 | 0.5389 | 0.7166 | 0.6490 | 1.0000 | 0.9600 | 0.0158 | 0.0761 |
| **6. C + L (Anchor)** | HGB | 8.2266 | 13.2411 | 0.3208 | 0.4956 | 0.9150 | 0.8103 | 1.0000 | 0.9600 | 0.0158 | 0.0761 |
| **7. C + L without market** | Ridge | 8.7020 | 14.1338 | 0.2262 | 0.5411 | 0.7438 | 0.6501 | 1.0000 | 0.9200 | 0.0158 | 0.0729 |
| **7. C + L without market** | HGB | 8.1413 | 13.1916 | 0.3259 | 0.4967 | 0.9078 | 0.8093 | 1.0000 | 0.9400 | 0.0158 | 0.0745 |
| **8. C + L without region** | Ridge | 8.7326 | 14.1591 | 0.2234 | 0.5389 | 0.7166 | 0.6491 | 1.0000 | 0.9600 | 0.0158 | 0.0761 |
| **8. C + L without region** | HGB | 8.1524 | 13.1955 | 0.3255 | 0.4978 | 0.8975 | 0.7995 | 1.0000 | 0.9600 | 0.0158 | 0.0761 |
| **9. C + L without vehicle** | Ridge | 8.7435 | 14.1705 | 0.2222 | 0.5358 | 0.6970 | 0.6095 | 1.0000 | 0.9200 | 0.0158 | 0.0729 |
| **9. C + L without vehicle** | HGB | 8.4667 | 13.5552 | 0.2882 | 0.4846 | 0.8017 | 0.7757 | 1.0000 | 0.9800 | 0.0158 | 0.0777 |
| **10. C + L without duration** | Ridge | 8.7326 | 14.1593 | 0.2234 | 0.5389 | 0.7166 | 0.6490 | 1.0000 | 0.9600 | 0.0158 | 0.0761 |
| **10. C + L without duration** | HGB | 8.2562 | 13.3187 | 0.3129 | 0.4798 | 0.9044 | 0.7990 | 1.0000 | 0.9400 | 0.0158 | 0.0745 |

---

## Single-field additions

[OBSERVED RESULT] Evaluating individual field lift beyond frozen context ($C \to C + L_i$):

| Added Logistics Field ($L_i$) | Protocol & Model | $\Delta \text{MAE}$ (% loss) | Direction | $\Delta R^2$ | Direction | $\Delta \text{NDCG@10}$ | Direction | Precision@10 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **destination_market** | P1 Linear (`Ridge`) | -0.6685 | favorable | +0.1106 | favorable | +0.0397 | favorable | 0.9000 |
| | P1 Nonlinear (`HGB`) | -1.6880 | favorable | +0.3170 | favorable | +0.5828 | favorable | **1.0000** |
| | P2 Linear (`Ridge`) | -0.5526 | favorable | +0.1072 | favorable | +0.0993 | favorable | **1.0000** |
| | P2 Nonlinear (`HGB`) | -1.8761 | favorable | +0.2820 | favorable | +0.5115 | favorable | **1.0000** |
| **destination_region** | P1 Linear (`Ridge`) | -0.3749 | favorable | +0.0594 | favorable | -0.0674 | adverse | 0.6000 |
| | P1 Nonlinear (`HGB`) | -0.8930 | favorable | +0.1640 | favorable | +0.1225 | favorable | 0.7000 |
| | P2 Linear (`Ridge`) | -0.2827 | favorable | +0.0550 | favorable | -0.0042 | adverse | 0.7000 |
| | P2 Nonlinear (`HGB`) | -0.8233 | favorable | +0.1322 | favorable | +0.1172 | favorable | 0.7000 |
| **vehicle_type** | P1 Linear (`Ridge`) | -0.6671 | favorable | +0.1043 | favorable | +0.1287 | favorable | 0.9000 |
| | P1 Nonlinear (`HGB`) | **-1.8463** | favorable | **+0.3258** | favorable | **+0.6389** | favorable | **1.0000** |
| | P2 Linear (`Ridge`) | -0.5804 | favorable | +0.1100 | favorable | +0.1482 | favorable | **1.0000** |
| | P2 Nonlinear (`HGB`) | **-2.1636** | favorable | **+0.3202** | favorable | **+0.5898** | favorable | **1.0000** |
| **planned_duration_hours** | P1 Linear (`Ridge`) | -0.0690 | favorable | +0.0262 | favorable | -0.0504 | adverse | 0.7000 |
| | P1 Nonlinear (`HGB`) | -1.7347 | favorable | +0.3046 | favorable | +0.5803 | favorable | **1.0000** |
| | P2 Linear (`Ridge`) | -0.1191 | favorable | +0.0312 | favorable | +0.0045 | favorable | 0.8000 |
| | P2 Nonlinear (`HGB`) | -1.8620 | favorable | +0.2860 | favorable | +0.5758 | favorable | **1.0000** |

Key findings from single-field additions:
1. **`vehicle_type` produces the largest single-field incremental predictive and ranking lift** across both protocols. Under nonlinear modeling (HGB), adding `vehicle_type` alone reduces MAE by $1.85$ (P1) and $2.16$ (P2) percentage points, elevates $R^2$ by $+0.326$ (P1) and $+0.320$ (P2), elevates NDCG@10 by $+0.639$ (P1) and $+0.590$ (P2), and achieves 100% Precision@10.
2. **`destination_market` is the second strongest single field**, providing comparable gains ($R^2$ lift $+0.317$ in P1 HGB, $+0.282$ in P2 HGB; NDCG@10 lift $+0.583$ in P1 HGB, $+0.512$ in P2 HGB).
3. **`planned_duration_hours` exhibits pronounced model-dependent behavior**: it provides substantial nonlinear lift in HGB ($R^2$ lift $+0.305$ in P1, $+0.286$ in P2), but negligible linear lift in Ridge ($R^2$ lift only $+0.026$ in P1, $+0.031$ in P2; adverse NDCG@10 delta in P1).
4. **`destination_region` is consistently the weakest single field**, producing less than half the $R^2$ lift of market or vehicle, and resulting in adverse or near-neutral NDCG@10 deltas under linear models.

---

## Leave-one-out contributions

[OBSERVED RESULT] Evaluating marginal contribution of each field once the other three fields are present ($C + (L - L_i) \to C + L$):

| Omitted Logistics Field ($L_i$) | Protocol & Model | $\Delta \text{MAE}$ (% loss) | Direction | $\Delta R^2$ | Direction | $\Delta \text{NDCG@10}$ | Direction |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **destination_market** | P1 Linear (`Ridge`) | +0.0020 | adverse | +0.0013 | favorable | -0.0532 | adverse |
| | P1 Nonlinear (`HGB`) | +0.0196 | adverse | +0.0014 | favorable | +0.0107 | favorable |
| | P2 Linear (`Ridge`) | +0.0309 | adverse | -0.0028 | adverse | -0.0272 | adverse |
| | P2 Nonlinear (`HGB`) | +0.0853 | adverse | -0.0051 | adverse | +0.0072 | favorable |
| **destination_region** | P1 Linear (`Ridge`) | +0.0001 | adverse | +0.0000 | favorable | +0.0000 | **neutral** |
| | P1 Nonlinear (`HGB`) | -0.0999 | favorable | +0.0076 | favorable | -0.0109 | adverse |
| | P2 Linear (`Ridge`) | +0.0003 | adverse | -0.0000 | adverse | +0.0000 | **neutral** |
| | P2 Nonlinear (`HGB`) | +0.0742 | adverse | -0.0047 | adverse | +0.0175 | favorable |
| **vehicle_type** | P1 Linear (`Ridge`) | -0.0153 | favorable | -0.0028 | adverse | +0.0507 | favorable |
| | P1 Nonlinear (`HGB`) | **-0.1649** | favorable | **+0.0123** | favorable | **+0.1292** | favorable |
| | P2 Linear (`Ridge`) | -0.0107 | favorable | +0.0012 | favorable | +0.0196 | favorable |
| | P2 Nonlinear (`HGB`) | **-0.2401** | favorable | **+0.0326** | favorable | **+0.1133** | favorable |
| **planned_duration_hours** | P1 Linear (`Ridge`) | +0.0000 | adverse | +0.0000 | favorable | +0.0000 | **neutral** |
| | P1 Nonlinear (`HGB`) | +0.0811 | adverse | -0.0146 | adverse | +0.0298 | favorable |
| | P2 Linear (`Ridge`) | +0.0003 | adverse | -0.0000 | adverse | +0.0000 | **neutral** |
| | P2 Nonlinear (`HGB`) | -0.0295 | favorable | +0.0080 | favorable | +0.0106 | favorable |

Key findings from leave-one-out testing:
1. **`vehicle_type` shows the clearest and most consistent positive leave-one-out ranking contribution**, especially under HGB. Restoring `vehicle_type` to $C + \{\text{market}, \text{region}, \text{duration}\}$ improves NDCG@10 by $+0.1292$ in P1 HGB and $+0.1133$ in P2 HGB, and reduces MAE by $-0.1649$ (P1) and $-0.2401$ (P2) percentage points.
2. **The remaining three fields show smaller and mixed marginal effects.** For example, restoring `destination_market` is slightly favorable for P1 HGB NDCG@10 ($+0.0107$) but adverse for P1 Ridge ($-0.0532$); P2 effects are also mixed ($\Delta \text{NDCG@10} = +0.0072$ in HGB, $-0.0272$ in Ridge). `planned_duration_hours` and `destination_region` are closer to numerical equality in several configurations, particularly Ridge ($\Delta \text{NDCG@10} = 0.0000$), but are not uniformly favorable across models and metrics.

---

## Internal logistics redundancy

[FACT] Quantitative evaluation of collinearity and redundancy among the four planned-logistics fields:

### 1. Categorical Normalized Mutual Information (NMI)
- $\text{NMI}(\text{destination_market}, \text{destination_region}) = \mathbf{0.7830}$
- $\text{NMI}(\text{destination_market}, \text{vehicle_type}) = \mathbf{0.4859}$
- $\text{NMI}(\text{destination_region}, \text{vehicle_type}) = \mathbf{0.3390}$

### 2. Planned Duration Variance Decomposition ($\eta^2$)
- $\eta^2(\text{planned_duration_hours} \mid \text{destination_market}) = \mathbf{1.0000}$ (100.0% of duration variance is explained by destination market; 8 groups).
- $\eta^2(\text{planned_duration_hours} \mid \text{destination_region}) = \mathbf{0.9657}$ (96.57% of duration variance is explained by macro destination region; 4 groups).
- $\eta^2(\text{planned_duration_hours} \mid \text{vehicle_type}) = \mathbf{0.5312}$ (53.12% of duration variance is explained by vehicle type; 3 groups).

### 3. Compact Contingency Evidence

[FACT] Cross-tabulation of `destination_market` against `destination_region`, `planned_duration_hours`, and `vehicle_type`:

| Destination Market | Destination Region | Planned Duration (h) | Total Batches ($N$) | Ambient Truck | Insulated Van | Reefer Truck |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Berlin** | Western Europe | **38.0** | 251 | 0 | 7 | 244 |
| **Brașov** | Romania | **16.0** | 205 | 0 | 7 | 198 |
| **Bucharest** | Romania | **14.0** | 211 | 0 | 2 | 209 |
| **Bălți Wholesale** | Domestic | **5.0** | 219 | 204 | 0 | 15 |
| **Chișinău Local** | Domestic | **4.0** | 238 | 0 | 221 | 17 |
| **Iași** | Romania | **8.0** | 230 | 0 | 216 | 14 |
| **Prague** | Central Europe | **32.0** | 237 | 0 | 10 | 227 |
| **Warsaw** | Central Europe | **28.0** | 209 | 0 | 4 | 205 |
| **Total** | | | **1,800** | **204** | **467** | **1,129** |

[OBSERVED RESULT] Analytical implications of internal redundancy:
- **Deterministic Functional Mapping:** In this simulation dataset, `destination_market` maps deterministically 1-to-1 to `planned_duration_hours` ($\eta^2 = 1.0000$). Each city has an invariant transit duration.
- **Strict Geographic Hierarchy:** Each `destination_market` belongs strictly to exactly one `destination_region` ($\text{NMI} = 0.7830$).
- **Observed vehicle-route allocation pattern:** `Ambient Truck` is utilized **exclusively for Bălți Wholesale domestic routes** ($5.0\text{ hours}$, 204 batches total; exactly 0 ambient shipments cross national borders or go to Chișinău Local). Long-haul routes to Central and Western Europe ($\ge 28\text{ hours}$) are serviced almost exclusively ($>95\%$) by `Reefer Truck`.

---

## Proxy diagnostics

[FACT] Descriptive association diagnostics evaluating whether planned logistics fields act as confounding proxies for operational context or biological identity:

### 1. Categorical NMI against Diagnostic Variables ($N=1,800$)

| Logistics Field | Diagnostic Variable | Cardinality (Logistics vs Diagnostic) | Normalized Mutual Information (NMI) |
| :--- | :--- | :---: | :---: |
| **vehicle_type** | `crop_type` | 3 vs 8 | 0.0286 |
| **destination_market** | `variety` | 8 vs 34 | 0.0275 |
| **vehicle_type** | `variety` | 3 vs 34 | 0.0257 |
| **destination_market** | `zone_id` | 8 vs 25 | 0.0190 |
| **destination_region** | `variety` | 4 vs 34 | 0.0159 |
| **vehicle_type** | `zone_id` | 3 vs 25 | 0.0094 |
| **destination_market** | `facility_id` | 8 vs 10 | 0.0090 |
| **destination_market** | `district` | 8 vs 10 | 0.0090 |
| **destination_region** | `zone_id` | 4 vs 25 | 0.0089 |
| **destination_market** | `crop_type` | 8 vs 8 | 0.0086 |
| **vehicle_type** | `zone_type` | 3 vs 4 | 0.0062 |
| **destination_region** | `crop_type` | 4 vs 8 | 0.0057 |
| **destination_market** | `zone_type` | 8 vs 4 | 0.0046 |
| **destination_region** | `facility_id` | 4 vs 10 | 0.0041 |
| **destination_region** | `district` | 4 vs 10 | 0.0041 |
| **destination_market** | `harvest_conditions` | 8 vs 4 | 0.0032 |
| **destination_market** | `facility_type` | 8 vs 4 | 0.0031 |
| **destination_market** | `region` | 8 vs 3 | 0.0029 |
| **vehicle_type** | `facility_id` | 3 vs 10 | 0.0029 |
| **vehicle_type** | `district` | 3 vs 10 | 0.0029 |
| **destination_region** | `harvest_conditions` | 4 vs 4 | 0.0027 |
| **destination_region** | `zone_type` | 4 vs 4 | 0.0022 |
| **destination_region** | `facility_type` | 4 vs 4 | 0.0022 |
| **destination_market** | `origin_region` | 8 vs 3 | 0.0021 |
| **vehicle_type** | `facility_type` | 3 vs 4 | 0.0019 |
| **destination_region** | `region` | 4 vs 3 | 0.0017 |
| **vehicle_type** | `harvest_conditions` | 3 vs 4 | 0.0013 |
| **destination_region** | `origin_region` | 4 vs 3 | 0.0012 |
| **destination_market** | `operational_season` | 8 vs 2 | 0.0010 |
| **vehicle_type** | `region` | 3 vs 3 | 0.0009 |
| **vehicle_type** | `origin_region` | 3 vs 3 | 0.0009 |
| **destination_region** | `operational_season` | 4 vs 2 | 0.0007 |
| **vehicle_type** | `operational_season` | 3 vs 2 | 0.0002 |

### 2. Planned Duration Variance Explained ($\eta^2$) against Diagnostic Variables

| Diagnostic Variable | Number of Groups ($k$) | $\eta^2$ Proportion of Variance Explained |
| :--- | :---: | :---: |
| `variety` | 34 | 0.0205 |
| `zone_id` | 25 | 0.0102 |
| `district` | 10 | 0.0042 |
| `facility_id` | 10 | 0.0042 |
| `crop_type` | 8 | 0.0040 |
| `region` | 3 | 0.0022 |
| `origin_region` | 3 | 0.0016 |
| `facility_type` | 4 | 0.0014 |
| `zone_type` | 4 | 0.0012 |
| `operational_season` | 2 | 0.0010 |
| `harvest_conditions` | 4 | 0.0007 |

---

## Crop/site/season association findings

[OBSERVED RESULT] Detailed inspection of the diagnostic evidence yields clear factual findings:

1. **Low observed association with facility and chamber:**
   - $\text{NMI}(\text{destination_market}, \text{facility_id}) = 0.0090$, $\text{NMI}(\text{destination_market}, \text{zone_id}) = 0.0190$.
   - Planned duration $\eta^2$ against `facility_id` is $0.0042$, and against `zone_id` is $0.0102$.
   - Diagnostic associations with facility and zone identifiers are low across both categorical NMI and duration variance decomposition.
2. **Low observed association with crop and variety:**
   - $\text{NMI}(\text{vehicle_type}, \text{crop_type}) = 0.0286$, $\text{NMI}(\text{destination_market}, \text{crop_type}) = 0.0086$, $\text{NMI}(\text{destination_market}, \text{variety}) = 0.0275$.
   - Duration $\eta^2$ against `crop_type` is $0.0040$, and against `variety` is $0.0205$. Measured association between logistics fields and crop/variety identities is low across all diagnostic pairings.
3. **Low observed association with operational season:**
   - Observed association with `operational_season` was small in the measured diagnostics: $\text{NMI} \le 0.0010$ across the categorical logistics fields, and $\eta^2(\text{planned_duration_hours} \mid \text{operational_season}) = 0.0010$. These diagnostics do not establish identical seasonal distributions.

---

## Interpretation Q1-Q6

### Q1: Which individual fields show observed incremental signal beyond C?
[OBSERVED RESULT] All four planned-logistics fields show observed incremental predictive and ranking association when added individually to context $C$. However, the magnitude varies substantially:
- **`vehicle_type`** provides the strongest and most consistent standalone incremental lift across both P1 and P2 (P1 HGB: $\Delta R^2 = +0.3258$, $\Delta \text{NDCG@10} = +0.6389$, Precision@10 = $1.00$; P2 HGB: $\Delta R^2 = +0.3202$, $\Delta \text{NDCG@10} = +0.5898$, Precision@10 = $1.00$).
- **`destination_market`** is the second strongest single field (P1 HGB: $\Delta R^2 = +0.3170$, $\Delta \text{NDCG@10} = +0.5828$; P2 HGB: $\Delta R^2 = +0.2820$, $\Delta \text{NDCG@10} = +0.5115$).
- **`planned_duration_hours`** exhibits strong nonlinear lift in HGB ($\Delta R^2 = +0.3046$ P1 / $+0.2860$ P2, $\Delta \text{NDCG@10} = +0.5803$ P1 / $+0.5758$ P2), but negligible linear lift in Ridge ($\Delta R^2 = +0.0262$ P1 / $+0.0312$ P2; adverse NDCG@10 delta in P1).
- **`destination_region`** provides the weakest standalone lift ($\Delta R^2 = +0.1640$ P1 / $+0.1322$ P2 in HGB; $\Delta \text{NDCG@10} = +0.1225$ P1 / $+0.1172$ P2).

### Q2: Which fields retain observable contribution once the other three logistics fields are present?
[OBSERVED RESULT] `vehicle_type` shows the clearest and most consistent positive leave-one-out ranking contribution, especially under HGB:
- Restoring `vehicle_type` to $C + \{M, R, D\}$ improves P1 HGB NDCG@10 from $0.7403$ to $0.8695$ ($\Delta = +0.1292$) and P2 HGB NDCG@10 from $0.8017$ to $0.9150$ ($\Delta = +0.1133$), with MAE reductions of $-0.1649$ (P1) and $-0.2401$ (P2) percentage points.
- The remaining three fields show smaller and mixed marginal effects. For example, restoring `destination_market` is slightly favorable for P1 HGB NDCG@10 ($+0.0107$) but adverse for P1 Ridge ($-0.0532$); P2 effects are also mixed. `planned_duration_hours` and `destination_region` are closer to numerical equality in several configurations, particularly Ridge ($\Delta \text{NDCG@10} = 0.0000$), but are not uniformly favorable across models and metrics.

### Q3: Which fields appear redundant with one another in this simulation dataset?
[OBSERVED RESULT] `destination_market` and `planned_duration_hours` contain deterministic redundancy in this simulation dataset, with $\eta^2 = 1.0000$ for duration grouped by market. `destination_market` is also associated with `destination_region` ($\text{NMI} = 0.7830$), with $\eta^2 = 0.9657$ for duration grouped by region. By contrast, `vehicle_type` shows observed internal association values of $\text{NMI} = 0.4859$ with destination market, $\text{NMI} = 0.3390$ with destination region, and $\eta^2 = 0.5312$ for duration grouped by vehicle type (reflecting route-level vehicle allocations such as ambient trucks used exclusively on domestic routes), indicating that it contributes a different observed logistics dimension under these diagnostics without calling independence proven.

### Q4: Which logistics fields are descriptively associated with crop/site/zone/operational-season identity?
[OBSERVED RESULT] Observed NMI and $\eta^2$ values between logistics fields and the examined crop, facility, zone, or operational season labels were low across all measured pairings:
- Observed categorical NMIs against facility ID, zone ID, facility type, region, district, crop type, variety, harvest conditions, and operational season were all $\le 0.0286$.
- Observed duration $\eta^2$ values against these diagnostic variables were all $\le 0.0205$.

### Q5: Does the strong C+L result appear potentially dependent on identity/route/season proxy structure?
[INFERENCE] Classification: **`NO CLEAR SUPPORT IN THESE DIAGNOSTICS`**.
- The tested descriptive NMI/eta² diagnostics provide no clear support for strong association with the examined facility/zone/crop/operational-season labels. This does not prove absence of proxy structure or generalisation risk.
- While the empirical associations align with transport attributes (refrigeration type and transit duration), potential proxy mechanisms or unmeasured confounding outside these specific variables cannot be excluded without further out-of-domain evaluation.

### Q6: Is a smaller logistics subset reasonable to carry forward as a candidate for later human review?
[RECOMMENDATION] Classification: **`Candidate for later human decision`**.
- `vehicle_type` plus one route/duration representative may be carried forward as a candidate for later subset evaluation/decision; VDR-05 did not directly evaluate that 2-field subset.
- Under P2 HGB, $C + \text{vehicle_type}$ alone achieves $\text{NDCG@10} = 0.8967$, $R^2 = +0.3282$, and $\text{MAE} = 8.0766$ (compared to full $C+L$ with $\text{NDCG@10} = 0.9150$, $R^2 = +0.3208$, and $\text{MAE} = 8.2266$).
- Retaining all 4 variables introduces deterministic redundancy (with $\eta^2 = 1.0000$ between market and duration) and high internal association. However, this is strictly a candidate for a later human Integrator decision gate (Phase B / VLD-02B) and does **not** constitute an approved production feature subset.

---

## What the evidence supports

[OBSERVED RESULT]
1. The largest observed predictive and ranking lift among individual planned-logistics fields is associated with **`vehicle_type`**, with individual contributions also observed from route attributes (**`destination_market`**, **`planned_duration_hours`**).
2. `destination_market` and `planned_duration_hours` contain deterministic redundancy ($\eta^2 = 1.0000$); in linear models and leave-one-out testing, marginal differences between them are small or mixed.
3. `destination_region` provides the smallest observed standalone lift and near-zero marginal contribution in several leave-one-out configurations.
4. The tested descriptive NMI and $\eta^2$ diagnostics provide no clear support for strong association between logistics fields and the examined facility, zone, crop, or operational-season labels.
5. `vehicle_type` plus one route/duration representative may be carried forward as a candidate for later subset evaluation/decision based on the observed standalone, leave-one-out, and redundancy evidence; VDR-05 did not directly evaluate that 2-field subset.

---

## What the evidence does NOT support

[FACT]
1. The evidence does **NOT** support removing `planned_logistics` or `telemetry` from the canonical input contract (ADR 0002 / ADR 0003).
2. The evidence does **NOT** support a causal claim that vehicle selection or market destination causes produce spoilage.
3. The evidence does **NOT** prove model generalizability to completely unseen logistics corridors or external transport carriers.
4. The evidence does **NOT** authorize a production feature selection or production model architecture.
5. The evidence does **NOT** support financial or food-waste savings claims.

---

## Remaining UNKNOWNs

[UNKNOWN]
- Why `Ambient Truck` is confined exclusively to the Bălți Wholesale destination market ($N=204$) while Chișinău Local uses Insulated Van and Reefer Truck (whether route-specific operational practice, packaging difference, or simulation artifact).
- Whether unmeasured proxy structures exist outside the crop/site/zone/operational-season diagnostic labels tested in VDR-05.
- How models would perform under real-world operational deviations where the actual transit vehicle or route deviates from the planned booking.

---

## Risks and limitations

[SIMULATION]
1. **Simulation-data structural limitation:** [OBSERVED RESULT][SIMULATION] In the supplied simulation dataset, planned_duration_hours is deterministic within destination_market in the observed 1,800 rows (eta² = 1.0000, zero observed within-market duration variance); real-world logistics exhibit transit duration variance due to traffic, weather, and customs delays.
2. **Deterministic Vehicle Allocations:** Ambient trucks are confined exclusively to domestic routes ($N=204$), conflating ambient equipment with short transit duration.
3. **Non-Exhaustive Search:** Only the 10 pre-specified feature families were evaluated; arbitrary combinatoric feature selection was strictly avoided.

---

## Reproduction commands

To independently reproduce the complete VDR-05 evidence package from clean repository state:

```powershell
.\.venv\Scripts\python.exe scripts/vdr05_logistics_signal_audit.py `
  --data-dir sponsor_pack/data `
  --output docs/data_recon/05_planned_logistics_signal_audit_results.json `
  --historical-vdr04b docs/data_recon/04b_telemetry_ablation_results.json
```

Verify SHA256 hash determinism:

```powershell
Get-FileHash docs/data_recon/05_planned_logistics_signal_audit_results.json -Algorithm SHA256
```
