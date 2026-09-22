# VDR-06B Runtime Release Parity & Held-Out Cohort Audit

**Document Type**: EVIDENCE / RUNTIME RELEASE PARITY AUDIT
**Epistemic Status**: NOT CANON BY ITSELF (Evaluation artifact verifying runtime release implementation against historical baseline evidence; does not establish production deployment readiness, calibration, or external validity)
**Task ID**: VDR-06B
**Domain**: Data & Evaluation / Analytics Architecture
**Owner**: Viktor (Data & Evaluation Owner)
**Integrator / Reviewer**: Vladimir (Project Brain / Integrator)
**Status**: DRAFT FOR PROJECT BRAIN REVIEW
**Results Artifact**: [`docs/data_recon/06b_runtime_release_parity_results.json`](06b_runtime_release_parity_results.json) (SHA256: `9128024b198e3492be988ed5b58d20b4f277063ef0959354b9fefbb9a8e60cb7`)
**Executable Harness**: [`scripts/vdr06b_runtime_release_parity.py`](../../scripts/vdr06b_runtime_release_parity.py) (SHA256: `e6431e1188f682b3ec26473a9ff7511bc25dffccdba0cea3905653722650b079`)
**Base Commit**: `fc71c67356704c2b33d0c4c5c28afc09c4007560`
**Committed Audit Harness Commit**: `2c841939a68f360ae8854900f9fe3a0800fde37d`

---

## 1. Status / epistemic boundary

This document is an independent **EVIDENCE / RUNTIME RELEASE PARITY AUDIT** for task VDR-06B. It evaluates the integrated RBS-01 runtime release against the accepted VDR-06A baseline evidence and ADR 0005 specifications.

This audit is:
- Strictly baseline parity verification between the real dataset-backed FastAPI HTTP serving pipeline and accepted research evidence.
- Strictly baseline-only: zero learned models, zero feature engineering, zero API redesign.
- NOT canon by itself; it does not establish production readiness, deployment readiness, or commercial viability.
- Notice: `SIMULATION / training challenge dataset / deterministic baseline / not production deployment`.

---

## 2. Audit objective

The core objective of **VDR-06B** is to answer the primary architectural verification question:
*Does the actual dataset-backed FastAPI release behave, for the complete eligible held-out cohort, like the deterministic baseline release that was accepted and integrated?*

The audited runtime chain spans:
```text
accepted pinned dataset (sponsor_pack/data)
  +
accepted runtime artifact (backend/artifacts/baseline-crop-median-v1-p1-s2024.json)
  → FastAPI lifespan (create_app)
  → runtime initialization (initialize_runtime)
  → GET /api/v1/assessments/{batch_id}
  → canonical mapper (build_batch_assessment_input)
  → deterministic baseline service (build_baseline_assessment)
  → serialized RiskAssessment JSON
  → independent VDR-06B parity audit
```

---

## 3. Repository and evidence identity

- **Repository**: `Slave-of-Skynet/training_agrifood`
- **Starting/Base SHA**: `fc71c67356704c2b33d0c4c5c28afc09c4007560`
- **Task Branch**: `victor/vdr-06b-runtime-release-parity`
- **Pinned Raw Dataset**: `sponsor_pack/data` (8 tables, all matching accepted SHA256 hashes)
- **Committed Runtime Artifact**: `backend/artifacts/baseline-crop-median-v1-p1-s2024.json`
- **Accepted Reference Evidence**: `docs/data_recon/06a_baseline_evaluation_results.json` (SHA256: `ca27c8486dd9ec7bcfff8fe313ae9ff289851ec4715bd50025db38813d40e586`)

---

## 4. Runtime release under test

The runtime release executes the integrated RBS-01 single-batch assessment path:
- **Application Factory**: `app.main.create_app()` using FastAPI lifespan context.
- **Runtime Initialization**: `app.runtime.context.initialize_runtime()` loading pinned dataset and baseline artifact via environment variables:
  - `SMART_HARVEST_DATA_DIR`
  - `SMART_HARVEST_BASELINE_ARTIFACT`
- **HTTP Endpoint**: `GET /api/v1/assessments/{batch_id}`
- **Health Endpoint**: `GET /api/v1/health`
- **Release Identifiers**:
  - `algorithm_family`: `baseline-crop-median-v1`
  - `engine_version`: `baseline-crop-median-v1-p1-s2024`
  - `source_dataset_id`: `training-agrifood-snapshot-v1`
  - `simulation`: `true`
  - `notice`: `SIMULATION / training challenge dataset / deterministic baseline / not production deployment`

---

## 5. Independent reference construction

To ensure complete epistemic independence and prevent circular verification:
1. **No Runtime Cohort Helpers**: The audit does NOT call `app.runtime.artifact.partition_membership()` or access `runtime.training_ids` / `runtime.held_out_ids` to define expected cohorts.
2. **Raw File Ingestion**: Cohorts are parsed independently and directly from `sponsor_pack/data/batches.csv` and `sponsor_pack/data/storage_sessions.csv`.
3. **Independent Expected Scores**: Expected scores are derived solely from raw `batches.csv` `crop_type` and the committed release artifact JSON without calling `predict_loss_fraction_pct()`, `predict_risk_score()`, or `build_baseline_assessment()`.
4. **Historical Outcome Isolation**: `historical_quality_outcomes.csv` is NOT accessed during cohort construction, API query execution, or expected score calculation. It is ingested strictly in the retrospective evaluation step after all 900 API responses have been collected and verified.

---

## 6. Cohort membership verification

Independent cohort parsing from raw data confirms exact alignment with ADR 0005 D1 specifications:

| Metric / Invariant | Expected | Actual | Status |
| :--- | :---: | :---: | :---: |
| Total Batches in `batches.csv` | 1,800 | 1,800 | **PASS** |
| Total Sessions in `storage_sessions.csv` | 1,800 | 1,800 | **PASS** |
| Session to Batch Cardinality | Exactly 1:1 | Exactly 1:1 | **PASS** |
| Training Batches (`dispatch_datetime < 2025-05-01`) | 900 | 900 | **PASS** |
| Held-Out Batches (`dispatch_datetime >= 2025-05-01`) | 900 | 900 | **PASS** |
| Cohort Overlap | 0 | 0 | **PASS** |
| Cohort Union | 1,800 | 1,800 | **PASS** |
| Training Membership Fingerprint (SHA256) | `ff68170549...` | `ff681705494a6818ff2642845736a7a4409db08fc9e4ba44b160181f9cc97646` | **PASS** |

---

## 7. Artifact ↔ VDR-06A parameter parity

The parameters in `backend/artifacts/baseline-crop-median-v1-p1-s2024.json` were compared directly against the accepted reference in `docs/data_recon/06a_baseline_evaluation_results.json` (`evaluation_results.p1_inter_season`):

| Parameter | Artifact Value | VDR-06A Reference | Absolute Difference ($\Delta$) | Status |
| :--- | :---: | :---: | :---: | :---: |
| `apples` | 6.4400% | 6.4400% | **0.0** | **PASS** |
| `apricots` | 17.5300% | 17.5300% | **0.0** | **PASS** |
| `pears` | 9.2600% | 9.2600% | **0.0** | **PASS** |
| `plums` | 11.7550% | 11.7550% | **0.0** | **PASS** |
| `raspberries` | 21.1350% | 21.1350% | **0.0** | **PASS** |
| `strawberries` | 16.0100% | 16.0100% | **0.0** | **PASS** |
| `table_grapes` | 14.7600% | 14.7600% | **0.0** | **PASS** |
| `tomatoes` | 15.5650% | 15.5650% | **0.0** | **PASS** |
| `global_median` | 11.0850% | 11.0850% | **0.0** | **PASS** |

- **Crop key sets identical**: `True`
- **Max crop median delta**: `0.0` ($\le 10^{-12}$)
- **Global median delta**: `0.0` ($\le 10^{-12}$)

---

## 8. Held-out API coverage

All 900 independently identified held-out batches were requested sequentially through `GET /api/v1/assessments/{batch_id}` using `TestClient(create_app())`:

- **Expected Count**: 900
- **Requested Count**: 900
- **HTTP 200 OK Count**: 900
- **Missing Predictions**: 0
- **Duplicate Predictions**: 0
- **Unexpected Predictions**: 0
- **Cache-Control `no-store` Count**: 900
- **Coverage Status**: **PASS** (100% complete coverage)

---

## 9. Per-batch score parity

Each API response score (`payload.risk.score`) was compared against the independent artifact-derived expected score:
- **Compared Batches**: 900
- **Tolerance**: $|\Delta| \le 10^{-12}$
- **Max Absolute Delta**: **0.0**
- **Mean Absolute Delta**: **0.0**
- **Mismatch Count**: **0**
- **Non-finite Values**: **0**
- **Unseen Crop Fallbacks**: **0** (all 8 crops present in held-out cohort were observed in training)
- **Parity Verdict**: **PASS**

---

## 10. P1 runtime metric parity

Retrospective evaluation was executed by joining the 900 API-derived predictions (`api_predicted_loss_fraction_pct = risk.score * 100`) with historical quality outcomes (`loss_fraction_pct`). The resulting continuous and ranking metrics match accepted VDR-06A evidence:

| Metric Group | Metric | API Runtime | VDR-06A Reference | Absolute Difference ($\Delta$) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Continuous** | MAE | 8.884177777777778 | 8.884177777777778 | **0.0** | **PASS** |
| | RMSE | 16.240119991346535 | 16.240119991346535 | **0.0** | **PASS** |
| | $R^2$ | 0.07365195166545269 | 0.07365195166545258 | **$1.11 \times 10^{-16}$** | **PASS** |
| | Spearman Correlation | 0.44969670620334207 | 0.44969670620334207 | **0.0** | **PASS** |
| **Ranking & Retrieval** | Spearman Correlation | 0.44969670620334207 | 0.44969670620334207 | **0.0** | **PASS** |
| | NDCG@10 | 0.2633852692946556 | 0.2633852692946556 | **0.0** | **PASS** |
| | NDCG@50 | 0.2796628426602165 | 0.2796628426602165 | **0.0** | **PASS** |
| | Precision@10 | 0.8000 | 0.8000 | **0.0** | **PASS** |
| | Precision@50 | 0.5800 | 0.5800 | **0.0** | **PASS** |
| | Recall@10 | 0.02666666666666667 | 0.02666666666666667 | **0.0** | **PASS** |
| | Recall@50 | 0.09666666666666666 | 0.09666666666666666 | **0.0** | **PASS** |
| | Tie Policy | Predicted loss DESC, `batch_id` ASC | — | Verified |

- **Metric Parity Verdict**: **PASS** across all 10 evaluated continuous and ranking metrics (all $\Delta \le 10^{-9}$).
- **Epistemic Note**: Observed held-out Precision@10 = 0.80 and NDCG@10 = 0.2633852692946556; P1 held-out $R^2 = 0.07365195166545258$. VDR-06B establishes implementation/runtime parity and does not establish operational utility or causal/explanatory attribution.

---

## 11. Training-cohort release rejection

All 900 training batches (`dispatch_datetime < 2025-05-01`) were requested through `GET /api/v1/assessments/{batch_id}`:
- **Requested Batches**: 900
- **HTTP 409 Conflict Count**: 900
- **Unexpected Status Count**: 0
- **Detail Exact Match**: `Batch is not eligible for this assessment release` (900/900 matches)
- **Cache-Control `no-store`**: 900/900 matches
- **Gate Verdict**: **PASS**

---

## 12. Unknown-batch behavior

- **Sentinel Identifier**: `VDR-06B-NOT-A-BATCH`
- **Absence Verification**: Verified absent from all 1,800 raw dataset batch IDs (`proved_absent = True`).
- **Endpoint Request**: `GET /api/v1/assessments/VDR-06B-NOT-A-BATCH`
- **HTTP Status**: `404 Not Found`
- **Detail Exact Match**: `Batch not found`
- **Cache-Control Header**: `no-store`
- **Verdict**: **PASS**

---

## 13. Unconfigured runtime behavior

Environment variables `SMART_HARVEST_DATA_DIR` and `SMART_HARVEST_BASELINE_ARTIFACT` were cleared before creating application instance:
- `GET /api/v1/health`: HTTP 200 OK, `status = "ok"`, `analytics = "not_configured"`.
- `GET /api/v1/assessments/{batch_id}`: HTTP 503 Service Unavailable, `detail = "Analytics runtime unavailable"`, `Cache-Control = "no-store"`.
- **Verdict**: **PASS**

---

## 14. Configured-unavailable behavior

`SMART_HARVEST_BASELINE_ARTIFACT` was configured to point to a guaranteed nonexistent path while `SMART_HARVEST_DATA_DIR` remained valid:
- Application remained alive without crashing.
- `GET /api/v1/health`: HTTP 200 OK, `status = "ok"`, `analytics = "unavailable"`.
- `GET /api/v1/assessments/{batch_id}`: HTTP 503 Service Unavailable, `detail = "Analytics runtime unavailable"`, `Cache-Control = "no-store"`.
- **Verdict**: **PASS**

---

## 15. GET-only API behavior

- Method rejection audit tested `POST /api/v1/assessments/{batch_id}` on a valid held-out batch.
- **HTTP Status**: `405 Method Not Allowed`
- **Observed Cache-Control**: `no-store`
- **Verdict**: **PASS**

---

## 16. Provenance and contract invariants

All 900 held-out responses satisfied 100% of schema and contract invariants (900/900 for every field):
- `batch_id`: exactly matches requested ID (900/900)
- `status`: `"assessed"` (900/900)
- `risk.score`: in bounds $[0, 1]$ (900/900)
- `risk.band`: `None` (900/900, uncalibrated)
- `deterioration_horizon`: `None` (900/900)
- `factors`: empty list `[]` (900/900)
- `recommendation`: `None` (900/900)
- `reliability`: `level = "unavailable"`, `confidence_score = None`, `reason_codes = []`, `missing_requirements = []` (900/900)
- `provenance.contract_version`: `"1.0.0"` (900/900)
- `provenance.engine_tier`: `"deterministic_baseline"` (900/900)
- `provenance.engine_version`: `"baseline-crop-median-v1-p1-s2024"` (900/900)
- `provenance.source_dataset_id`: `"training-agrifood-snapshot-v1"` (900/900)
- `provenance.simulation`: `True` (900/900)
- `provenance.notice`: `"SIMULATION / training challenge dataset / deterministic baseline / not production deployment"` (900/900)
- `provenance.generated_at`: parseable ISO 8601, timezone-aware UTC, execution-plausible (900/900)

---

## 17. Determinism / reproducibility

1. **Endpoint Request Determinism**:
   - Evaluated 9 unique sentinel batch IDs across 10 configured roles (8 distinct crop representatives plus first/last boundary batches, where `BAT-000901` serves as both `apples` representative and first held-out batch).
   - Executed 2 repeat requests per sentinel (18 total requests, all HTTP 200).
   - Removing only `generated_at`, all response payloads were 100% identical (0 mismatches across repeat requests).
2. **Audit Harness Reproducibility**:
   - Scratch Run 1 SHA256: `9128024b198e3492be988ed5b58d20b4f277063ef0959354b9fefbb9a8e60cb7`
   - Scratch Run 2 SHA256: `9128024b198e3492be988ed5b58d20b4f277063ef0959354b9fefbb9a8e60cb7`
   - Official Run SHA256: `9128024b198e3492be988ed5b58d20b4f277063ef0959354b9fefbb9a8e60cb7`
   - Byte-identical across all runs (`True`).

---

## 18. Findings

1. **Exact Parity Achieved**: The runtime release implementation faithfully serves the accepted deterministic baseline for all 900 held-out batches with zero score deviations ($\Delta = 0.0$) and exact P1 metric equivalence ($\Delta \le 1.11 \times 10^{-16}$).
2. **Fail-Closed Release Gates Enforced**: The application rigorously rejects all 900 training batches with HTTP 409, rejects unknown batches with HTTP 404, and gracefully handles unconfigured/unavailable analytics with HTTP 503 while preserving process liveness.
3. **Leakage & Scope Isolation Verified**: Request-time inference consumes only `batch_input.batch.crop_type` without exposure to post-dispatch transit realizations, arrival quality inspections, or historical outcome labels.

---

## 19. What this proves

OBSERVED RESULT:
For the pinned training-challenge snapshot and the concrete `baseline-crop-median-v1-p1-s2024` release, the dataset-backed single-batch FastAPI serving path returned complete held-out coverage and reproduced the accepted P1 deterministic-baseline scores/metrics within the declared parity tolerance.

---

## 20. What this does NOT prove

A PASS in VDR-06B does NOT establish:
- Real-world agricultural validity
- Production readiness
- Commercial readiness
- External dataset generalisation
- Future crop generalisation
- Future facility generalisation
- Causal prediction
- Calibrated probability
- Calibrated confidence
- Deterioration timing validity
- Recommendation efficacy
- Food-loss reduction
- Financial savings
- Scalability
- Concurrency capacity
- Network/deployment reliability
- Frontend correctness
- Multi-batch queue correctness
- Learned-model quality

---

## 21. Remaining UNKNOWNs

- Whether this baseline behavior transfers to external/non-simulation operational data.
- Calibration/reliability of any future predictive engine remains unestablished here.
- Selection of any learned engine or production serving architecture is outside VDR-06B and requires separate authorization.
- Performance and concurrency characteristics of multi-worker production deployments under heavy load.

---

## 22. Reproduction

To execute the independent runtime release parity audit and regenerate the results artifact:

```powershell
.\.venv\Scripts\python.exe scripts/vdr06b_runtime_release_parity.py `
  --data-dir sponsor_pack/data `
  --artifact backend/artifacts/baseline-crop-median-v1-p1-s2024.json `
  --vdr06a docs/data_recon/06a_baseline_evaluation_results.json `
  --output docs/data_recon/06b_runtime_release_parity_results.json
```

Safe scratch reproduction example:

```powershell
.\.venv\Scripts\python.exe scripts/vdr06b_runtime_release_parity.py `
  --data-dir sponsor_pack/data `
  --artifact backend/artifacts/baseline-crop-median-v1-p1-s2024.json `
  --vdr06a docs/data_recon/06a_baseline_evaluation_results.json `
  --output "$env:TEMP\vdr06b-scratch-results.json"
```

---

## 23. Final handoff evidence

- **Report Status**: Complete, verified against official JSON.
- **Runner Script**: `scripts/vdr06b_runtime_release_parity.py`
- **Report Markdown**: `docs/data_recon/06b_runtime_release_parity.md`
- **Results JSON**: `docs/data_recon/06b_runtime_release_parity_results.json`
- **Overall Verdict**: **PASS** across all audit gates.
