# VDR-06A: Deterministic Baseline Evaluation Harness & Application Parity

**Document Type**: EVIDENCE / IMPLEMENTATION PARITY AUDIT
**Epistemic Status**: NOT CANON BY ITSELF (Evaluation artifact verifying application implementation against historical baseline evidence; does not establish production deployment readiness or canonize learned model behavior)
**Task ID**: VDR-06A
**Domain**: Data & Evaluation / Analytics Architecture
**Owner**: Viktor (Data & Evaluation Owner)
**Integrator / Reviewer**: Vladimir (Project Brain / Integrator)
**Status**: DRAFT FOR REVIEW — PARITY VERIFIED (`PASS`)
**Results Artifact**: [`docs/data_recon/06a_baseline_evaluation_results.json`](06a_baseline_evaluation_results.json) (SHA256: `ca27c8486dd9ec7bcfff8fe313ae9ff289851ec4715bd50025db38813d40e586`)
**Executable Harness**: [`scripts/vdr06a_baseline_evaluation.py`](../../scripts/vdr06a_baseline_evaluation.py) (SHA256: `4f5ea5dcb49a5dcfff67316e4459b71776258bcc1703c033a57d9133b57d2caa`)
**Base Commit**: `6447d0884ec5a64bc2112f9c72d00e42cba3cd01`

---

## 1. Objective

The objective of **VDR-06A** is to construct an independent, deterministic evaluation harness that executes the **current application baseline implementation**:
```
backend/app/analytics/crop_median_baseline.py
```
through the **authoritative canonical ingestion and domain mapping pipeline**:
```
read_raw_snapshot()
  → build_batch_assessment_input()
  → BatchAssessmentInput
  → fit_crop_median_baseline()
  → predict_loss_fraction_pct()
```
and strictly verify numerical, ranking, and partition parity against the accepted historical **VDR-04A** crop-median baseline evidence (`docs/data_recon/04_dispatch_predictability_results.json`).

This harness verifies implementation fidelity between application code and research evidence. It is strictly baseline-only:
- Zero learned models (no Ridge, HistGradientBoosting, Random Forest, or neural networks).
- Zero feature engineering (no tabular feature matrices $F_0, F_1, F_2, F_3, C, C+L$).
- Zero modifications to backend application code, schema definitions, or historical evidence.

---

## 2. Exact Implementation Under Test

The harness evaluates the exact application baseline implementation located at:
- File: `backend/app/analytics/crop_median_baseline.py`
- Training Entrypoint: `app.analytics.crop_median_baseline.fit_crop_median_baseline(records: Sequence[CropMedianTrainingRecord]) -> CropMedianBaseline`
- Inference Entrypoint: `app.analytics.crop_median_baseline.predict_loss_fraction_pct(baseline: CropMedianBaseline, input_data: BatchAssessmentInput) -> float`

The data ingestion path under test uses the canonical application ingestion modules:
- Raw Ingestion: `app.ingestion.raw_reader.read_raw_snapshot(data_dir: Path) -> RawSnapshot`
- Canonical Mapper: `app.ingestion.canonical_mapper.build_batch_assessment_input(snapshot: RawSnapshot, batch_id: str) -> BatchAssessmentInput`

The baseline algorithm computes the median `loss_fraction_pct` per `crop_type` on the training partition. At inference time, it extracts `input_data.batch.crop_type.strip()`, looks up the fitted median, and falls back to `baseline.global_median` only if the crop was unseen during training.

---

## 3. Dataset Integrity & Provenance

The harness evaluates on the authoritative sponsor dataset (`sponsor_pack/data`). Dataset integrity is verified via a mandatory fail-closed gate comparing SHA256 digests against accepted VDR-04A metadata:

| Dataset Table | Expected SHA256 (`VDR-04A`) | Actual SHA256 | Match | Record Count | Structural / Key Invariant | Status |
| :--- | :--- | :--- | :---: | :---: | :--- | :---: |
| `batches.csv` | `bbaf3cb4064ccdefed5eaca0b3fe7d63...` | `bbaf3cb4064ccdefed5eaca0b3fe7d63...` | True | 1,800 | `batch_id` PK is unique | **PASS** |
| `storage_sessions.csv` | `f38a99dfeb808eaab3b3d91d0494d303...` | `f38a99dfeb808eaab3b3d91d0494d303...` | True | 1,800 | Exactly 1 session per batch (1:1) | **PASS** |
| `facilities.csv` | `148de414dcff6d601d327ce17414d8b9...` | `148de414dcff6d601d327ce17414d8b9...` | True | 10 | `facility_id` PK is unique | **PASS** |
| `storage_zones.csv` | `e2c4b7170c47ab0896ed962c588256e3...` | `e2c4b7170c47ab0896ed962c588256e3...` | True | 25 | `zone_id` PK is unique | **PASS** |
| `quality_checks.csv` | `95ccf7d6d898249f6bf444a874817be7...` | `95ccf7d6d898249f6bf444a874817be7...` | True | 5,400 | Exactly 3 checks per batch (1 harvest, 1 pre-dispatch, 1 arrival) | **PASS** |
| `shipments.csv` | `bfad682700f58936ca383868febd0918...` | `bfad682700f58936ca383868febd0918...` | True | 1,800 | Exactly 1 shipment per batch (1:1) | **PASS** |
| `historical_quality_outcomes.csv` | `567334f44f41b980c67de496736c077d...` | `567334f44f41b980c67de496736c077d...` | True | 1,800 | Exactly 1 outcome per batch (1:1) | **PASS** |
| `sensor_readings.csv` | `6b27adaf43a6646d32cccddc95872bfe...` | `6b27adaf43a6646d32cccddc95872bfe...` | True | 669,665 | Telemetry readings for storage zones | **PASS** |

### Snapshot Diagnostics & Fail-Closed Gate
- **RawSnapshot Diagnostics**: Checked immediately after `read_raw_snapshot`.
- **Diagnostic Issues Count**: `0`
- **Blocking Errors (`has_errors()`)**: `False`
- **Snapshot Validity (`is_valid()`)**: `True` (`PASS`)
- If any diagnostic issue or hash mismatch occurs, the runner aborts with non-zero exit code, stopping evaluation before processing.

---

## 4. Training vs. Inference Boundary & Leakage Controls

### Boundary Specification
Historical outcomes used for fitting labels:
YES — training partitions only

Historical outcomes used for held-out evaluation labels:
YES

Historical outcomes present in BatchAssessmentInput:
NO

Historical outcomes passed to predict_loss_fraction_pct():
NO

Post-dispatch transit realizations passed to prediction:
NO

Arrival QC passed to prediction:
NO

Inference input:
canonical BatchAssessmentInput

Application baseline inference field:
batch_input.batch.crop_type only

### Pre-dispatch Information Horizon & Leakage Controls
The baseline prediction is evaluated strictly at the pre-dispatch decision gate:
1. **Input Object**: Inference is performed exclusively on canonical `BatchAssessmentInput` objects constructed from pre-dispatch and storage data.
2. **Target Outcome Absence**: Automated assertions verify that no post-dispatch realization or target outcome fields are accessible:
   - Zero target outcome fields: `loss_fraction_pct`, `quality_status`, `quality_score`, `economic_loss_eur`.
   - Zero transit realizations: `actual_departure_datetime`, `actual_arrival_datetime`, `actual_delay_minutes`, `cold_chain_incident`, `transit_temp_mean_c`.
   - Zero destination inspection checks: `arrival_firmness_kg_cm2`, `arrival_sugar_brix`, `arrival_defect_pct`, `arrival_check_datetime`.
3. **Chamber-Time Clustering**:
   - Reconstructed **157** disjoint chamber-time connected components within storage zones.
   - **1,734 out of 1,800** batches reside in multi-batch clusters, demonstrating dense temporal and environmental co-location.

---

## 5. Protocol P1: Forward Inter-Season Holdout

Protocol P1 reproduces the accepted forward inter-season holdout:
Season 2024 training and held-out Season 2025 evaluation.
- **Training Set (Season 2024)**: 900 batches (`dispatch_datetime < 2025-05-01`).
- **Test Set (Season 2025)**: 900 batches (`dispatch_datetime >= 2025-05-01`).
- **Seasonal Hiatus**: 43.97 days between seasons.

### Fitted Application Crop Medians (Season 2024)
- **Apples**: `6.4400%`
- **Apricots**: `17.5300%`
- **Pears**: `9.2600%`
- **Plums**: `11.7550%`
- **Raspberries**: `21.1350%`
- **Strawberries**: `16.0100%`
- **Table Grapes**: `14.7600%`
- **Tomatoes**: `15.5650%`
- **Global Median Fallback**: `11.0850%`

### P1 Prediction Coverage & Integrity
- Test batch count: `900`
- Prediction count: `900`
- Unique prediction IDs: `900`
- Missing / NaN / Infinite predictions: `0`

### P1 Performance Results

| Metric Group | Metric | Value | Reference Parity ($\Delta$) | Status |
| :--- | :--- | :--- | :---: | :---: |
| **Continuous** | MAE | **8.884177777777778** | 0.0 | **PASS** |
| | RMSE | **16.240119991346535** | 0.0 | **PASS** |
| | $R^2$ | **0.07365195166545258** | 0.0 | **PASS** |
| | Spearman Correlation | **0.44969670620334207** | 0.0 | **PASS** |
| **Ranking & Retrieval** | NDCG@10 | **0.2633852692946556** | 0.0 | **PASS** |
| | NDCG@50 | **0.2796628426602165** | 0.0 | **PASS** |
| | Precision@10 | **0.8000** | 0.0 | **PASS** |
| | Precision@50 | **0.5800** | 0.0 | **PASS** |
| | Recall@10 | **0.02666666666666667** | 0.0 | **PASS** |
| | Recall@50 | **0.09666666666666666** | 0.0 | **PASS** |
| | Tie Policy | Predicted loss DESC, `batch_id` ASC | — | Verified |

---

## 6. Protocol P2: 5-Fold Grouped Out-of-Fold (Blocked by Chamber Clusters)

Protocol P2 evaluates cross-validation under strict chamber-time cluster blocking:
- **Group Blocking**: 157 disjoint chamber-time clusters.
- **Partitioning**: 5-fold `GroupKFold` on 1,800 batches.
- **Validation Fold Sizes**: Exactly 360 batches per fold (1,800 total OOF predictions).
- **Cluster Overlap Assertion**: `0` overlapping clusters between train and validation in all 5 folds.
- **Unseen Crop Fallbacks**: Exactly `0` in every fold (all 8 crops are represented in training in each fold).

### Fold-Level Verification

| Fold | Train Size | Val Size | Train Clusters | Val Clusters | Cluster Overlap | Unseen Fallbacks | MAE | RMSE | $R^2$ | Spearman |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fold 1** | 1,440 | 360 | 126 | 31 | **0** | **0** | 9.0316 | 16.2988 | 0.0493 | 0.4114 |
| **Fold 2** | 1,440 | 360 | 126 | 31 | **0** | **0** | 7.3681 | 13.2087 | 0.0708 | 0.4634 |
| **Fold 3** | 1,440 | 360 | 126 | 31 | **0** | **0** | 8.0640 | 15.1038 | 0.0387 | 0.4425 |
| **Fold 4** | 1,440 | 360 | 126 | 31 | **0** | **0** | 10.1193 | 17.3688 | -0.0683 | 0.2567 |
| **Fold 5** | 1,440 | 360 | 124 | 33 | **0** | **0** | 9.5252 | 17.1948 | 0.0005 | 0.3424 |

### P2 Prediction Coverage & Invariants
- Total OOF predictions: `1,800`
- Unique prediction IDs: `1,800`
- Minimum assignment count per batch: `1`
- Maximum assignment count per batch: `1`
- All canonical batch IDs covered exactly once: `True`
- Missing / NaN / Infinite predictions: `0`

### Aggregate Out-of-Fold Performance Results

| Metric Group | Metric | Value | Reference Parity ($\Delta$) | Status |
| :--- | :--- | :--- | :---: | :---: |
| **Continuous** | MAE | **8.821641666666668** | 0.0 | **PASS** |
| | RMSE | **15.909637923196813** | 0.0 | **PASS** |
| | $R^2$ | **0.019510293642311827** | 0.0 | **PASS** |
| | Spearman Correlation | **0.3525332515058982** | 0.0 | **PASS** |
| **Ranking & Retrieval** | NDCG@10 | **0.25326891956791114** | 0.0 | **PASS** |
| | NDCG@50 | **0.2906104251088262** | 0.0 | **PASS** |
| | Precision@10 | **0.5000** | 0.0 | **PASS** |
| | Precision@50 | **0.7600** | 0.0 | **PASS** |
| | Recall@10 | **0.00792393026941363** | 0.0 | **PASS** |
| | Recall@50 | **0.060221870047543584** | 0.0 | **PASS** |
| | Tie Policy | Predicted loss DESC, `batch_id` ASC | — | Verified |

---

## 7. Protocol P3: Random Split Diagnostic (NON-DEFENSIBLE)

> [!WARNING]
> **EPISTEMIC NOTICE: NON-DEFENSIBLE DIAGNOSTIC**
> Protocol P3 is an unblocked 80/20 random partition (`random_seed=42`). It is reported solely as a negative diagnostic demonstrating the degree of environmental leakage present in unblocked splits. It is NOT a candidate protocol for evaluation.

- **Split Configuration**: 1,440 training batches, 360 test batches.
- **Cluster Leakage**: **340 of 360 test batches (94.44%)** share a cold storage chamber-time cluster with batches in the training set.
- **Application Baseline Performance**:
  - MAE: **9.041944444444445**
  - RMSE: **16.024629654240236**
  - $R^2$: **-0.015299308570619896**
  - Spearman: **0.3634347306932793**
  - NDCG@10: **0.25957860221549467**, NDCG@50: **0.38293857391478175**
  - Precision@10: **0.9000**, Precision@50: **0.5800**
  - Recall@10: **0.06666666666666667**, Recall@50: **0.21481481481481482**
- **Diagnostic Finding**: The 94.44% chamber-cluster overlap means P3 does not preserve the accepted chamber isolation boundary and therefore remains a NON-DEFENSIBLE DIAGNOSTIC.

---

## 8. VDR-04A Parity Verification Matrix

The primary acceptance gate of VDR-06A is numerical and ranking parity between the current application baseline implementation (`backend/app/analytics/crop_median_baseline.py`) and historical VDR-04A evidence (`docs/data_recon/04_dispatch_predictability_results.json`).

Parity tolerance threshold: $|\Delta| \le 10^{-9}$.

| Protocol | Metric | VDR-04A Reference | VDR-06A Application | Absolute Difference | Status |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **P1 Holdout** | MAE | 8.884177777777778 | 8.884177777777778 | **0.0** | **PASS** |
| **P1 Holdout** | RMSE | 16.240119991346535 | 16.240119991346535 | **0.0** | **PASS** |
| **P1 Holdout** | $R^2$ | 0.07365195166545258 | 0.07365195166545258 | **0.0** | **PASS** |
| **P1 Holdout** | Spearman | 0.44969670620334207 | 0.44969670620334207 | **0.0** | **PASS** |
| **P1 Holdout** | NDCG@10 | 0.2633852692946556 | 0.2633852692946556 | **0.0** | **PASS** |
| **P1 Holdout** | NDCG@50 | 0.2796628426602165 | 0.2796628426602165 | **0.0** | **PASS** |
| **P1 Holdout** | Precision@10 | 0.8000000000000000 | 0.8000000000000000 | **0.0** | **PASS** |
| **P1 Holdout** | Precision@50 | 0.5800000000000000 | 0.5800000000000000 | **0.0** | **PASS** |
| **P1 Holdout** | Recall@10 | 0.02666666666666667 | 0.02666666666666667 | **0.0** | **PASS** |
| **P1 Holdout** | Recall@50 | 0.09666666666666666 | 0.09666666666666666 | **0.0** | **PASS** |
| **P2 Grouped OOF** | MAE | 8.821641666666668 | 8.821641666666668 | **0.0** | **PASS** |
| **P2 Grouped OOF** | RMSE | 15.909637923196813 | 15.909637923196813 | **0.0** | **PASS** |
| **P2 Grouped OOF** | $R^2$ | 0.019510293642311827 | 0.019510293642311827 | **0.0** | **PASS** |
| **P2 Grouped OOF** | Spearman | 0.3525332515058982 | 0.3525332515058982 | **0.0** | **PASS** |
| **P2 Grouped OOF** | NDCG@10 | 0.25326891956791114 | 0.25326891956791114 | **0.0** | **PASS** |
| **P2 Grouped OOF** | NDCG@50 | 0.2906104251088262 | 0.2906104251088262 | **0.0** | **PASS** |
| **P2 Grouped OOF** | Precision@10 | 0.5000000000000000 | 0.5000000000000000 | **0.0** | **PASS** |
| **P2 Grouped OOF** | Precision@50 | 0.7600000000000000 | 0.7600000000000000 | **0.0** | **PASS** |
| **P2 Grouped OOF** | Recall@10 | 0.00792393026941363 | 0.00792393026941363 | **0.0** | **PASS** |
| **P2 Grouped OOF** | Recall@50 | 0.060221870047543584 | 0.060221870047543584 | **0.0** | **PASS** |

**Parity Verdict**: **PASS** across all 20 evaluated metrics. All differences are exactly $0.0$, demonstrating complete equivalence between the current application baseline implementation and historical research evidence.

---

## 9. Leakage & Integrity Verification

1. **Deterministic Reproducibility**:
   - Two consecutive execution runs generated bitwise-identical output (`SHA256: ca27c8486dd9ec7bcfff8fe313ae9ff289851ec4715bd50025db38813d40e586`).
2. **Snapshot Diagnostics Integrity Gate**:
   - Automated check halts immediately if `RawSnapshot.diagnostics.has_errors()` is `True` or `is_valid()` is `False`.
3. **Dataset Hash Verification Gate**:
   - Automated check halts immediately if any of the 8 dataset table hashes differ from VDR-04A accepted metadata.
4. **Target Leakage Assertion**:
   - Inspection of canonical `BatchAssessmentInput` keys confirms absence of all outcome and post-dispatch fields.
5. **Exact-Once OOF Partition Coverage**:
   - Out-of-fold prediction counts verify that every batch in the dataset is evaluated exactly once in validation (`min_count=1`, `max_count=1`, `nan_count=0`).

---

## 10. Epistemic Status & Interpretation Boundaries

1. **Baseline-Only Scope**:
   This audit evaluates exclusively the single-variable median baseline (`crop_type` median). It does not evaluate, tune, or deploy learned multi-feature models.
2. **Explanatory Limit of Baseline**:
   The observed crop-median baseline fit yields P1 R² = 0.07365195166545258 and P2 R² = 0.019510293642311827.
3. **No Unwarranted Inferences**:
   No claims are made regarding whether learned models will outperform this baseline on unmeasured operational conditions or whether specific tabular features will yield incremental predictive power. Such determinations remain subject to empirical verification under future task specifications.
4. **Parity Verification Only**:
   Passing parity confirms that the application codebase faithfully reproduces the baseline behavior established in VDR-04A. It does not certify that the baseline itself is sufficient for commercial operational dispatch decisions.

---

## 11. Remaining UNKNOWNs

- Whether this baseline behavior transfers to external/non-simulation operational data.
- Calibration/reliability of any future predictive engine remains unestablished here.
- Selection of any learned engine or production serving architecture is outside VDR-06A and requires separate authorization.

---

## 12. Reproduction Command

To execute the independent baseline evaluation harness and regenerate the results artifact:

```powershell
.\.venv\Scripts\python.exe scripts/vdr06a_baseline_evaluation.py `
  --data-dir sponsor_pack/data `
  --historical-vdr04a docs/data_recon/04_dispatch_predictability_results.json `
  --output docs/data_recon/06a_baseline_evaluation_results.json
```

Safe scratch example for exploratory reproduction checks (exploratory and reproduction checks should use scratch output and must not overwrite accepted evidence unintentionally):

```powershell
.\.venv\Scripts\python.exe scripts/vdr06a_baseline_evaluation.py `
  --data-dir sponsor_pack/data `
  --historical-vdr04a docs/data_recon/04_dispatch_predictability_results.json `
  --output "$env:TEMP\vdr06a-scratch-results.json"
```
