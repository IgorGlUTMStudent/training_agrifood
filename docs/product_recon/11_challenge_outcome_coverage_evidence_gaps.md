STATUS:
PRODUCT / CHALLENGE COVERAGE AUDIT
EVIDENCE & GAP ANALYSIS
NOT A NEW ADR
NOT CANON BY ITSELF
NOT IMPLEMENTATION
NOT FINAL PITCH APPROVAL

# APR-04A — Challenge Outcome Coverage & Evidence Gaps

## 1. Task identity and inspected base

- **Task ID:** `APR-04A`
- **Role:** Product Owner / Product Reconciliation & Epistemic Audit
- **Author:** Alisa (Product Owner) / Vladimir (Integration support)
- **Authoritative Inspected Base:** `main @ fc71c67356704c2b33d0c4c5c28afc09c4007560` (clean working tree)
- **Preceding Reference:** APR-03A ([`10_mvp_demo_narrative_claim_freeze.md`](10_mvp_demo_narrative_claim_freeze.md)), VLD-R6 ([`VLD-R6-post-rbs01-reconciliation.md`](../recon/VLD-R6-post-rbs01-reconciliation.md)), RBS-01 ([PR #42](../recon/VLD-R6-post-rbs01-reconciliation.md#L10) / commit `59cd759`).
- **Nature of Document:** Product Reconciliation & Evidence Gap Audit (awaiting review and human integration; NOT CANON BY ITSELF). Reconciles challenge outcomes (O1–O4), evaluation criteria (E1–E6), committed implementation state, and product flow at base `fc71c67`.
- **Governing Invariants:**
  1. Reflects exclusively the committed code and accepted decisions at base `fc71c67356704c2b33d0c4c5c28afc09c4007560`.
  2. Does **NOT** assume unmerged concurrent tasks are complete (specifically PUX-11A single-batch frontend, VDR-06B runtime release audit, IGR-05A multi-batch recon, IGR-05B multi-batch implementation, future queue UI).
  3. Introduces no code, schema, config, or dependency modifications.

---

## 2. Executive summary

At base `main @ fc71c67356704c2b33d0c4c5c28afc09c4007560`, the technical reality of the repository is defined by the successful integration of RBS-01 (PR #42) and VLD-R6 (PR #43):

1. **Backend Dataset Serving is Live for Single Batches:** The backend actively serves real, dataset-backed baseline assessments for Season-2025 held-out batches via [`GET /api/v1/assessments/{batch_id}`](../../backend/app/api/routes.py#L36-L61). It enforces release eligibility (HTTP 409 for training batches, HTTP 404 for unknown batches) and fail-closed dependency injection (HTTP 503 if unconfigured).
2. **The Frontend Does NOT Consume the Real Assessment Route:** The browser client ([`frontend/src/api/client.ts`](../../frontend/src/api/client.ts)) only calls `getHealth()` and `getDemoAssessment()`. The UI ([`HomePage.tsx`](../../frontend/src/pages/HomePage.tsx#L25-L39)) renders exclusively the synthetic demo fixture (`BAT-DEMO-0001`, `insufficient_data`). Real dataset scores are not visible in the browser.
3. **No Multi-Batch Route or Operator Queue Exists:** The backend has no collection query, replay feed, facility filtering, or pagination ([ADR 0005 §D7](../decisions/0005-runtime-baseline-serving.md#L201-L203)). The frontend has no multi-item triage table or queue sorting.
4. **Outcome Status is Strictly Bounded:**
   - **O1 (Which batches are most at risk?):** `PARTIAL` — single-batch score is implemented; cross-batch triage workflow is not implemented.
   - **O2 (When deterioration is likely to occur):** `UNSUPPORTED BY DATA` — continuous biological onset curves cannot be derived from single-point pre-dispatch inspections; the application returns `deterioration_horizon = null` with a truthful disclaimer.
   - **O3 (What factors contribute to the risk?):** `PARTIAL` — formula transparency is rendered; feature attribution is unsupported (`factors = []`).
   - **O4 (What action should be prioritised?):** `UNSUPPORTED BY DATA` — challenge data contain zero interventional records; `recommendation = null` is strictly enforced.
5. **Epistemic Discipline:** APR-03A's obsolete statement that a real assessment endpoint is not implemented is superseded. However, single-batch scoring must never be exaggerated into an implemented operator triage queue, and truthful disclaimers must never be claimed as outcome fulfillment.

---

## 3. Authority and sources

Assertions in this document strictly adhere to the project's 5-level authority hierarchy:

- **Level 1 — Supplied Challenge Materials:**
  - `S1`: [`Training Challenge #3 — AgriFood.md`](../../sponsor_pack/brief/Training%20Challenge%20%233%20%E2%80%94%20AgriFood.md): Four desired outcomes and evaluation criteria E1–E6.
  - `S2`: [`sponsor_pack/README.md`](../../sponsor_pack/README.md): Target `loss_fraction_pct` and fixed assessment clock $T_{\text{assess}} \equiv T_{\text{dispatch}}$.
- **Level 2 — Accepted Architectural & Product Decisions:**
  - `S3`: [`ADR 0001`](../decisions/0001-foundation-architecture.md): Foundation architecture and layer boundaries.
  - `S4`: [`ADR 0002`](../decisions/0002-predictive-input-semantics.md): Canonical input semantics and temporal leakage boundary.
  - `S5`: [`ADR 0003`](../decisions/0003-assessment-evaluation-semantics.md): Risk score clip formula, baseline engine, and evaluation protocol.
  - `S6`: [`ADR 0004`](../decisions/0004-mvp-product-scope.md): MVP product scope, persona, replay queue policy, explanation rules (APR2-D1–D6).
  - `S7`: [`ADR 0005`](../decisions/0005-runtime-baseline-serving.md): Runtime baseline serving and release verification (D1–D7).
- **Level 3 — Accepted / Committed Technical Evidence & Reconciliation:**
  - `S8`: [`challenge_canon.md`](../challenge_canon.md): Canonical repository framing and historical evidence register.
  - `S9`: [`VLD-R6`](../recon/VLD-R6-post-rbs01-reconciliation.md): Post-RBS-01 state reconciliation.
  - `S10`: Data reconnaissance reports [`VDR-01`](../data_recon/01_dataset_inventory.md), [`VDR-02`](../data_recon/02_temporal_leakage.md), [`VDR-03`](../data_recon/03_target_horizon_feasibility.md), [`VDR-04A`](../data_recon/04_dispatch_predictability.md), [`VDR-06A`](../data_recon/06a_baseline_evaluation.md).
- **Level 4 — Committed Application Code:**
  - `S11`: Backend services and runtime: [`raw_reader.py`](../../backend/app/ingestion/raw_reader.py), [`canonical_mapper.py`](../../backend/app/ingestion/canonical_mapper.py), [`crop_median_baseline.py`](../../backend/app/analytics/crop_median_baseline.py), [`baseline_assessment.py`](../../backend/app/services/baseline_assessment.py), [`artifact.py`](../../backend/app/runtime/artifact.py), [`context.py`](../../backend/app/runtime/context.py), [`routes.py`](../../backend/app/api/routes.py).
  - `S12`: Frontend client and UI: [`client.ts`](../../frontend/src/api/client.ts), [`HomePage.tsx`](../../frontend/src/pages/HomePage.tsx), [`AssessmentCard.tsx`](../../frontend/src/components/AssessmentCard.tsx).
  - `S13`: Offline generation script & artifact: [`generate_baseline_artifact.py`](../../scripts/generate_baseline_artifact.py), [`baseline-crop-median-v1-p1-s2024.json`](../../backend/artifacts/baseline-crop-median-v1-p1-s2024.json).
- **Level 5 — Non-Canonical Research & Exploratory Notes:**
  - `S14`: Subordinate research: [`docs/product_recon/**`](../product_recon), [`docs/recon/PUX-08-data-ux-reconciliation.md`](../recon/PUX-08-data-ux-reconciliation.md).

---

## 4. Status taxonomy & epistemic discipline

### 4.1 Evaluation States
- **`IMPLEMENTED`**: Capability is written, tested, and actively functioning in committed code at `main @ fc71c67`.
- **`EVIDENCED`**: Empirical data analysis or benchmark results have been computed, documented, and formally accepted in committed reports.
- **`PARTIAL`**: A bounded sub-slice is implemented or evidenced, but does not satisfy the complete challenge requirement or user-facing path.
- **`UNSUPPORTED`**: Capability cannot be derived from the available dataset or code without unverified leaps.
- **`UNKNOWN`**: Crucial real-world or domain information is fundamentally absent from challenge materials.
- **`TARGET / INTENDED`**: Planned future capability defined in proposals, not yet implemented or verified.

### 4.2 Epistemic Statement Classification
To eliminate ambiguity, statements in this audit are explicitly tagged:
- **FACT:** Directly verifiable in committed code or accepted project records.
- **DECISION:** Formally adopted in an accepted ADR (0001–0005).
- **OBSERVED RESULT:** Empirically verified metric or audit outcome in committed reports.
- **INFERENCE:** Methodological deduction logically derived from facts and decisions.
- **RECOMMENDATION:** Bounded proposal for next engineering steps.
- **UNKNOWN:** Explicitly identified absence of empirical or operational knowledge.

---

## 5. Current committed capability snapshot

Reconciliation of all 20 specified capabilities against committed code at base `fc71c67`:

| # | Capability | Current State | Code / Document Source | Technical Summary & Boundary |
|---|---|---|---|---|
| 1 | **Raw ingestion** | `IMPLEMENTED` | [`raw_reader.py`](../../backend/app/ingestion/raw_reader.py#L38-L100), [`structural_manifest.py`](../../backend/app/ingestion/structural_manifest.py#L1-L108) | FACT: SHA256 snapshot hashing and column validation for all 8 challenge CSVs. |
| 2 | **Canonical `BatchAssessmentInput`** | `IMPLEMENTED` | [`canonical_mapper.py`](../../backend/app/ingestion/canonical_mapper.py#L141-L245), [`batch.py`](../../backend/app/domain/batch.py#L129-L141) | FACT: Full mapping into typed domain models enforcing $T_{\text{assess}} \equiv T_{\text{dispatch}}$. |
| 3 | **Deterministic baseline** | `IMPLEMENTED` | [`crop_median_baseline.py`](../../backend/app/analytics/crop_median_baseline.py#L1-L76) | DECISION (ADR 0003 D5): Predicts historical crop median loss fraction; global fallback. |
| 4 | **Baseline assessment service** | `IMPLEMENTED` | [`baseline_assessment.py`](../../backend/app/services/baseline_assessment.py#L26-L72) | FACT: Orchestrates `BatchAssessmentInput` $\to$ schema-compliant `RiskAssessment`. |
| 5 | **Offline baseline artifact** | `IMPLEMENTED` | [`generate_baseline_artifact.py`](../../scripts/generate_baseline_artifact.py#L1-L157), [`baseline-crop-median-v1-p1-s2024.json`](../../backend/artifacts/baseline-crop-median-v1-p1-s2024.json) | FACT: Script fits Season-2024 partition (900 batches) and writes signed JSON. |
| 6 | **Runtime artifact validation** | `IMPLEMENTED` | [`artifact.py`](../../backend/app/runtime/artifact.py#L77-L141), [`context.py`](../../backend/app/runtime/context.py#L36-L50) | FACT: Verifies snapshot table hashes, partition membership SHA256, and crop coverage on startup. |
| 7 | **Single-batch real HTTP API** | `IMPLEMENTED` | [`routes.py:L36-L61`](../../backend/app/api/routes.py#L36-L61) | FACT: `GET /api/v1/assessments/{batch_id}` serves baseline; 409 training, 404 unknown, 503 unconfigured. |
| 8 | **Health state** | `IMPLEMENTED` | [`routes.py:L20-L26`](../../backend/app/api/routes.py#L20-L26), [`context.py:L31-L34`](../../backend/app/runtime/context.py#L31-L34), [`contracts.ts:L3-L7`](../../frontend/src/api/contracts.ts#L3-L7) | FACT: Synchronized tri-state health: `"not_configured" \| "ready" \| "unavailable"`. |
| 9 | **Synthetic fixture** | `IMPLEMENTED` | [`demo_assessment.py`](../../backend/app/services/demo_assessment.py#L1-L47), [`routes.py:L29-L34`](../../backend/app/api/routes.py#L29-L34) | FACT: Returns synthetic fixture `BAT-DEMO-0001` (`insufficient_data`). |
| 10 | **Frontend real-route consumption** | `NOT IMPLEMENTED` | [`client.ts:L18-L24`](../../frontend/src/api/client.ts#L18-L24), [`HomePage.tsx:L25-L39`](../../frontend/src/pages/HomePage.tsx#L25-L39) | FACT: Frontend calls only `getHealth()` and `getDemoAssessment()`; real route uncalled. |
| 11 | **Multi-batch route** | `NOT IMPLEMENTED` | [`routes.py`](../../backend/app/api/routes.py), [ADR 0005 §D7](../decisions/0005-runtime-baseline-serving.md#L201-L203) | DECISION (ADR 0005 D7): Multi-batch collection route explicitly deferred. |
| 12 | **Ranked queue** | `NOT IMPLEMENTED` | [`HomePage.tsx`](../../frontend/src/pages/HomePage.tsx), [ADR 0004 §APR2-D2](../decisions/0004-mvp-product-scope.md#L73-L84) | FACT: No multi-item triage table or sorting by `risk.score DESC, batch_id ASC` in UI. |
| 13 | **Replay controls** | `NOT IMPLEMENTED` | [`HomePage.tsx`](../../frontend/src/pages/HomePage.tsx) | FACT: No time-window sliders or historical dispatch replay parameters exist. |
| 14 | **Facility filtering** | `NOT IMPLEMENTED` | [`routes.py`](../../backend/app/api/routes.py), [`HomePage.tsx`](../../frontend/src/pages/HomePage.tsx) | FACT: No query parameters or UI controls filter assessments by `facility_id`. |
| 15 | **Pagination** | `NOT IMPLEMENTED` | [`routes.py`](../../backend/app/api/routes.py) | FACT: No cursor, limit/offset, or windowed batch pagination implemented. |
| 16 | **Batch Context presentation** | `PARTIAL` | [`batch.py:L29-L42`](../../backend/app/domain/batch.py#L29-L42), [`AssessmentCard.tsx`](../../frontend/src/components/AssessmentCard.tsx#L82-L98) | FACT: Domain models contain context; UI displays formula description, not intake metadata. |
| 17 | **Recommendation engine** | `NOT IMPLEMENTED` | [`baseline_assessment.py:L55`](../../backend/app/services/baseline_assessment.py#L55), [ADR 0004 §APR2-D5](../decisions/0004-mvp-product-scope.md#L140-L153) | DECISION (ADR 0003/0004): Output fixed to `recommendation=null`. UI renders truthful disclaimer. |
| 18 | **Deterioration model** | `NOT IMPLEMENTED` | [`baseline_assessment.py:L53`](../../backend/app/services/baseline_assessment.py#L53), [ADR 0003 §D8](../decisions/0003-assessment-evaluation-semantics.md#L141-L150) | DECISION (ADR 0003 D8): Output fixed to `deterioration_horizon=null`. Continuous countdown unevidenced. |
| 19 | **Learned engine** | `NOT IMPLEMENTED` | [ADR 0004 §5.1](../decisions/0004-mvp-product-scope.md#L184), [ADR 0005 §D4](../decisions/0005-runtime-baseline-serving.md#L170-L175) | FACT: No ML model family is selected, trained, or wired to runtime serving. |
| 20 | **Production deployment** | `NOT IMPLEMENTED` | [ADR 0005 §D6](../decisions/0005-runtime-baseline-serving.md#L190-L198), [`routes.py:L55-L56`](../../backend/app/api/routes.py#L55-L56) | FACT: Responses enforce `simulation=True`. No cloud hosting or production CI/CD exists. |

---

## 6. Current backend vs browser path

The committed code features two completely decoupled execution paths:

### 6.1 Browser / UI Path (Current User Experience)
```text
Browser User
    │
    ▼
HomePage.tsx (Mount / Retry)
    │
    ├── getHealth() ─────────────► GET /api/v1/health
    │                                    │
    │                                    ▼
    │                               FastAPI returns HealthResponse
    │                               (status="ok", analytics="not_configured"|"ready"|"unavailable")
    │                                    │
    │                                    ▼
    │                               BackendStatus.tsx renders status pill
    │
    └── getDemoAssessment() ─────► GET /api/v1/demo/assessment
                                         │
                                         ▼
                                    build_demo_assessment()
                                         │
                                         ▼
                                    Returns synthetic fixture:
                                    - batch_id: "BAT-DEMO-0001"
                                    - status: "insufficient_data"
                                    - risk: null
                                    - reason_codes: ["MISSING_PRE_DISPATCH_INSPECTION", ...]
                                    - provenance: engine_tier="fixture", simulation=true
                                         │
                                         ▼
                                    AssessmentCard.tsx renders synthetic card
```
- **FACT:** The browser UI path **never** invokes `GET /api/v1/assessments/{batch_id}`.
- **INFERENCE:** A user viewing the current web interface sees only the synthetic demo fixture; real dataset-backed scores are completely invisible in the browser.

### 6.2 Backend Serving Path (Dataset-Backed Baseline)
```text
External HTTP Client (cURL / Automated Tests / Direct API call)
    │
    ▼
GET /api/v1/assessments/{batch_id}  (routes.py)
    │
    ├── Runtime Context Check (Depends(get_runtime))
    │     └── If state.analytics != "ready" ──► Return HTTP 503 ("Analytics runtime unavailable")
    │
    ├── Release Eligibility Gate
    │     ├── batch_id in runtime.training_ids (Season 2024: 900 batches)
    │     │     └── Return HTTP 409 ("Batch is not eligible for this assessment release")
    │     └── batch_id not in runtime.held_out_ids (Season 2025: 900 batches)
    │           └── Return HTTP 404 ("Batch not found")
    │
    ├── Canonical Ingestion Mapping (canonical_mapper.py)
    │     └── build_batch_assessment_input(runtime.snapshot, batch_id)
    │           └── Enforces T_assess == T_dispatch temporal boundary
    │
    ├── Baseline Scoring Engine (baseline_assessment.py & crop_median_baseline.py)
    │     └── predict_risk_score(runtime.baseline, batch_input)
    │           └── risk.score = clip(predicted_loss_fraction_pct, 0, 100) / 100
    │     └── build_baseline_assessment(...)
    │           └── status: "assessed"
    │           └── risk: RiskEstimate(score=score, band=None)
    │           └── deterioration_horizon: None
    │           └── factors: []
    │           └── recommendation: None
    │           └── reliability: UNAVAILABLE
    │           └── provenance: engine_tier="deterministic_baseline", simulation=true
    │
    ▼
HTTP 200 Response with Cache-Control: no-store
```
- **FACT:** Real single-batch baseline assessment is fully functional over HTTP, with strict release gating and provenance tracking.

---

## 7. Challenge Outcome O1 — "Which batches are most at risk?"

- **FACT:** RBS-01 implemented [`GET /api/v1/assessments/{batch_id}`](../../backend/app/api/routes.py#L36-L61) returning dataset-backed scores for Season-2025 batches.
- **DECISION (ADR 0003 D1–D3):** The primary task is dispatch-time review prioritisation. Risk score is defined as continuous relative loss severity: $\text{risk.score} = \text{clip}(\text{predicted\_loss\_fraction\_pct}, 0, 100) / 100$. Ranking is strictly $\text{risk.score DESC, batch\_id ASC}$ within identical $\text{engine\_tier} + \text{engine\_version}$.
- **OBSERVED RESULT (VDR-06A):** The crop-median baseline achieves NDCG@10 of 0.7067 and MAE of 8.53 on held-out Season-2025 data.
- **FACT:** The backend does **not** contain a multi-batch query endpoint, replay route, or filtering API ([ADR 0005 §D7](../decisions/0005-runtime-baseline-serving.md#L201-L203)). The frontend does **not** contain a triage queue table.
- **INFERENCE:** Scoring individual batches does not satisfy the operational requirement to show "which batches are most at risk" across a facility; this requires multi-batch ranking and queue presentation.
- **UNKNOWN:** Real operator review capacity per shift, live queue membership duration, and facility-specific triage quotas.
- **EPISTEMIC STATUS:** `PARTIAL`.

---

## 8. Challenge Outcome O2 — "When deterioration is likely to occur"

- **OBSERVED RESULT (VDR-03):** Challenge data record produce quality at two isolated moments: harvest and pre-dispatch. Pre-dispatch inspection occurs on average 2.0 hours prior to dispatch. Zero continuous or longitudinal inspection records exist during storage.
- **INFERENCE:** Continuous biological deterioration curves, survival probabilities, and onset timestamps cannot be mathematically or biologically derived from single-point observations.
- **DECISION (ADR 0003 D8):** `deterioration_horizon` is fixed to `null` across all production contracts. Continuous countdown timers and shelf-life heuristics are strictly forbidden.
- **FACT:** Baseline service outputs `deterioration_horizon = None` ([`baseline_assessment.py:L53`](../../backend/app/services/baseline_assessment.py#L53)), and UI displays *"Deterioration timing: Not estimable from supplied observations"* ([`AssessmentCard.tsx:L101-L103`](../../frontend/src/components/AssessmentCard.tsx#L101-L103)).
- **INFERENCE:** Honest refusal to fabricate an unevidenced countdown timer is methodologically sound, but it does **not** fulfill Outcome 2.
- **EPISTEMIC STATUS:** `UNSUPPORTED BY DATA` (handled via truthful unavailable state).

---

## 9. Challenge Outcome O3 — "What factors contribute to the risk?"

- **DECISION (ADR 0004 APR2-D4):** Cleanly separates three conceptual areas:
  1. *How this score is computed:* Transparent description of the deterministic crop-median formula.
  2. *Batch Context:* Observable pre-dispatch intake metadata (crop, variety, harvest date, planned logistics, target zone environment) displayed with mandatory caption: *"Context only; contribution to this score has not been established."*
  3. *Model attribution (deferred):* Quantitative feature attributions (e.g. SHAP) are unsupported for the baseline.
- **FACT:** Baseline service outputs `factors = []` ([`baseline_assessment.py:L54`](../../backend/app/services/baseline_assessment.py#L54)).
- **FACT:** The UI renders the formula description ([`AssessmentCard.tsx:L82-L98`](../../frontend/src/components/AssessmentCard.tsx#L82-L98)), but does not yet render the non-causal Batch Context panel.
- **INFERENCE:** The system provides algorithmic explainability (how the baseline calculates scores), but zero causal or feature attribution for individual batch risk.
- **UNKNOWN:** Mathematical feature attribution methods (e.g. TreeSHAP) and operator comprehension testing for a future learned engine.
- **EPISTEMIC STATUS:** `PARTIAL` (algorithmic transparency exists; factor attribution unsupported).

---

## 10. Challenge Outcome O4 — "What action should be prioritised?"

- **OBSERVED RESULT (APR-01 / VDR-01):** The challenge dataset is purely observational. It contains no interventional trial logs, no A/B testing of warehouse actions, no record of post-dispatch treatment efficacy, and no action cost metadata.
- **INFERENCE:** Prescribing an operational action (e.g. "re-cool produce", "divert shipment", "reject batch") requires counterfactual causal evidence demonstrating that the action reduces loss. Such evidence does not exist in the dataset.
- **DECISION (ADR 0003 D9 / ADR 0004 APR2-D5):** `recommendation` is fixed to `null` across all production contracts. Fabricating rule-based heuristics is strictly forbidden.
- **FACT:** Baseline service outputs `recommendation = None` ([`baseline_assessment.py:L55`](../../backend/app/services/baseline_assessment.py#L55)). UI renders the accepted disclaimer: *"Action recommendations are unavailable. Current evidence does not validate intervention effectiveness. Smart Harvest prioritizes batches for review but does not prescribe an operational action."* ([`AssessmentCard.tsx:L115-L119`](../../frontend/src/components/AssessmentCard.tsx#L115-L119)).
- **DECISION:** Prioritising batches for human review attention is **not** equivalent to prescribing operational interventions.
- **UNKNOWN:** Warehouse SOP action catalogues, operator authority to halt shipments, and intervention cost structures.
- **EPISTEMIC STATUS:** `UNSUPPORTED BY DATA` (handled via truthful unavailable state).

---

## 11. Four-outcome coverage matrix

| Outcome | Brief Requirement | Accepted Framing | Evidence Status | Implementation Status | Evidence Source | Implemented Path | Limitations | Safe Demo / Pitch Claim | Unsupported Claim Leap | Candidate Next Implementation | What Would Close The Gap |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **O1** | "Which batches are most at risk?" | Dispatch-time relative risk prioritisation within identical engine tier/version. | `EVIDENCED` (Baseline NDCG@10=0.7067) | `PARTIAL` (Single-batch serving only) | [VDR-06A](../data_recon/06a_baseline_evaluation.md), [ADR 0003 D1-D3](../decisions/0003-assessment-evaluation-semantics.md#L45-L68) | [`routes.py:L36-L61`](../../backend/app/api/routes.py#L36-L61), [`baseline_assessment.py`](../../backend/app/services/baseline_assessment.py) | No multi-batch API, no operator queue UI, frontend calls only demo fixture. | "We compute a dataset-backed relative loss severity score for eligible batches; scores order batches by review priority." | "We provide an operational triage queue showing which batches are currently at risk." | Single-batch frontend integration (PUX-11A); Multi-batch backend route (IGR-05A/B). | Multi-batch replay route and UI queue table sorting by `risk.score DESC, batch_id ASC`. |
| **O2** | "When deterioration is likely to occur" | Explicitly unavailable; continuous biological countdown unsupported. | `EVIDENCED` (Negative proof in VDR-03) | `PARTIAL` (Enforces truthful null output) | [VDR-03](../data_recon/03_target_horizon_feasibility.md#L1-L50), [ADR 0003 D8](../decisions/0003-assessment-evaluation-semantics.md#L141-L150) | [`baseline_assessment.py:L53`](../../backend/app/services/baseline_assessment.py#L53), [`AssessmentCard.tsx:L101-L103`](../../frontend/src/components/AssessmentCard.tsx#L101-L103) | Single-point pre-dispatch inspections cannot establish biological onset timing. | "Deterioration timing is explicitly not estimable from the supplied single-point inspection data." | "Our system predicts shelf-life, remaining storage days, or deterioration countdown." | None (unclosable within challenge dataset). | Longitudinal multi-point inspection datasets tracking biological decay curves over time. |
| **O3** | "What factors contribute to the risk" | Algorithmic transparency for baseline + factual batch context display. | `EVIDENCED` (Crop medians computed in VDR-06A) | `PARTIAL` (Score explanation text in UI; context fields missing) | [ADR 0003 D5](../decisions/0003-assessment-evaluation-semantics.md#L88-L105), [ADR 0004 APR2-D4](../decisions/0004-mvp-product-scope.md#L115-L131) | [`AssessmentCard.tsx:L82-L98`](../../frontend/src/components/AssessmentCard.tsx#L82-L98) | Baseline has `factors=[]`. UI shows formula description but not intake metadata. | "We provide full algorithmic transparency on how baseline scores are derived from historical crop medians." | "The system identifies environmental or handling factors that caused this batch's risk score." | Add non-causal Batch Context panel in UI (ADR 0004 APR2-D4). | Validated feature attribution (e.g. SHAP) on an approved learned ML model tier. |
| **O4** | "What action should be prioritised" | Honest unavailable output; ranking attention != prescribing actions. | `EVIDENCED` (Negative proof in APR-01) | `PARTIAL` (Enforces truthful null output) | [ADR 0003 D9](../decisions/0003-assessment-evaluation-semantics.md#L152-L161), [ADR 0004 APR2-D5](../decisions/0004-mvp-product-scope.md#L138-L153) | [`baseline_assessment.py:L55`](../../backend/app/services/baseline_assessment.py#L55), [`AssessmentCard.tsx:L105-L121`](../../frontend/src/components/AssessmentCard.tsx#L105-L121) | Observational data contain zero counterfactual intervention trials or action logs. | "Action recommendations are unavailable because available data do not validate intervention efficacy." | "Smart Harvest recommends immediate dispatch, re-cooling, or quality re-inspection." | None (unclosable within challenge dataset). | Interventional logging, controlled trials, or warehouse SOP action catalogues. |

---

## 12. Evaluation-criteria matrix

| Criterion | What the Brief Asks | Current Supporting Evidence | Current Implementation Support | Current Limitation | Safe Demo / Pitch Evidence | Unsupported Leap | Potential Next Evidence |
|---|---|---|---|---|---|---|---|
| **E1: Usefulness** | Agricultural & business value; operational decision support. | Designed usefulness for dispatch-side storage operator triage ([ADR 0004 §APR2-D1](../decisions/0004-mvp-product-scope.md#L53-L59)). | Advisory decision support UI and single-batch scoring API. | Operator authority, warehouse SOPs, review capacity, and business ROI are UNKNOWN. | "Designed to help dispatch operators focus limited review attention on high-risk batches." | "Proven to reduce operational costs or automate warehouse dispatch decisions." | Warehouse workflow interviews; operator review capacity studies. |
| **E2: Accuracy & Reliability** | Sound methodology, model validation, reliable predictions. | Baseline evaluated on Season-2025: MAE=8.53, NDCG@10=0.7067 ([VDR-06A](../data_recon/06a_baseline_evaluation.md)). | In-memory artifact validation, cohort fingerprinting, fail-closed runtime provider. | VDR-06B runtime release audit uncommitted; baseline is uncalibrated relative index. | "Deterministic baseline achieves NDCG@10 of 0.71 and MAE of 8.53 on held-out 2025 data." | "High-accuracy machine learning model guaranteeing low operational error." | Commit VDR-06B runtime parity audit across all 900 Season-2025 batches. |
| **E3: Usability & Explainability** | Intuitive interface, transparent reasoning, clear risk factors. | Transparent baseline formula explanation ([ADR 0004 §APR2-D4](../decisions/0004-mvp-product-scope.md#L116-L125)). | UI renders formula text, simulation notice, and unavailable disclaimers. | No operator queue; UI displays only demo fixture; factor attribution unsupported. | "Interface provides complete transparency on how scores are computed and explicitly states limitations." | "Interactive operator dashboard providing feature-level explanations of risk drivers." | Connect UI to real single-batch route; add non-causal Batch Context panel. |
| **E4: Loss Reduction** | Measurable or plausible reduction in post-harvest food loss. | Theoretical mechanism: prioritizing inspection enables timely dispatch review. | No loss-reduction logic or impact measurement in code. | Zero empirical evidence of prevented loss, salvaged volume, or economic ROI. | "Prioritisation provides a mechanism to focus inspection, which could mitigate spoilage if paired with effective SOPs." | "Smart Harvest reduces food waste by X% or saves €Y per season." | Operational pilot data; simulation of loss reduction under assumed intervention SOPs. |
| **E5: Scalability** | Handling data scale, robust architecture, operational readiness. | Bounded ingestion schemas, pinned artifact validation, stateless FastAPI architecture. | Stateless backend runtime, type-safe Pydantic contracts, in-memory artifact caching. | No database, no streaming ingestion, no async worker queues, no container deployment. | "Lightweight, stateless architecture with reproducible artifact validation and fail-closed runtime checks." | "Enterprise-ready scalable platform handling real-time IoT telemetry across enterprise cold chains." | Containerization (Dockerfile); load benchmarking across multi-batch collections. |
| **E6: Innovation** | Novel approach, methodological rigor, creative problem-solving. | Strict epistemic boundaries, leakage-proof temporal mapping, signed reproducible artifacts. | Deterministic baseline serving, fail-closed runtime, explicit unavailable status lifecycle. | No novel deep learning model or autonomous decision agents. | "Innovative through epistemic discipline: mathematically honest boundaries, zero data leakage, and transparent provenance." | "State-of-the-art AI breakthrough solving post-harvest supply chain loss." | Comparative evaluation of candidate learned models with SHAP explainability. |

---

## 13. Gap register

Account of all 11 project gaps identified across outcomes and evaluation criteria:

| Gap ID | Related Outcome / Criterion | Current State | Gap Type | Evidence / Source | What Would Close It | What Would NOT Close It | Dependency | Likely Owner / Workstream | Priority | Human Decision Required? |
|---|---|---|---|---|---|---|---|---|---|---|
| **GAP-01** | O1, E3 | Browser calls only synthetic fixture; dataset route unconsumed | `IMPLEMENTATION GAP` | [`client.ts`](../../frontend/src/api/client.ts#L22-L24), [`HomePage.tsx`](../../frontend/src/pages/HomePage.tsx#L27) | Implement frontend API client method for `GET /api/v1/assessments/{batch_id}` and add batch selector/input in UI with error handling. | Regenerating baseline artifacts, editing backend models, or claiming demo parity without UI code. | RBS-01 (done) | Frontend / PRSCR | `HIGH` | **YES** (Candidate-slice execution requires a separate Human Integrator gate/contract; APR-04A itself grants no implementation authority) |
| **GAP-02** | O1, E1, E5 | No batch collection or replay API route exists | `IMPLEMENTATION GAP` | [`routes.py`](../../backend/app/api/routes.py), [ADR 0005 §D7](../decisions/0005-runtime-baseline-serving.md#L201-L203) | Specify and implement bounded multi-batch query/replay endpoint for held-out partition batches. | Front-end looping over single-batch endpoint, client-side pagination, or synthetic mocks. | ADR 0005 D7 scope boundary | Backend / Igor | `HIGH` | **YES** (Contract & filtering scope) |
| **GAP-03** | O1, E1, E3 | No ranked triage queue or sorting UI in frontend | `IMPLEMENTATION GAP` | [`HomePage.tsx`](../../frontend/src/pages/HomePage.tsx), [ADR 0004 §APR2-D2](../decisions/0004-mvp-product-scope.md#L80-L84) | Implement multi-item table sorting by `risk.score DESC, batch_id ASC` within identical engine tier/version. | Re-sorting single cards, hardcoding static HTML tables, or combining scores across versions. | GAP-02 (Multi-batch route) | Frontend / PRSCR | `MEDIUM` | **NO** (Governed by ADR 0004 APR2-D2) |
| **GAP-04** | O2, E2 | Deterioration horizon output is fixed to `null` | `DOMAIN EVIDENCE GAP` | [`baseline_assessment.py:L53`](../../backend/app/services/baseline_assessment.py#L53), [VDR-03](../data_recon/03_target_horizon_feasibility.md#L1-L50) | Longitudinal inspection measurements across storage stay to observe actual biological onset curves. | Synthesizing fake countdown timers, linear shelf-life heuristics, or subtracting transit hours. | Challenge dataset limitations | Data / Domain | `DEFER` | **NO** (Unclosable with challenge data) |
| **GAP-05** | O3, E3 | Explanations lack model attribution; factor list is empty | `IMPLEMENTATION GAP` / `EVIDENCE GAP` | [`baseline_assessment.py:L54`](../../backend/app/services/baseline_assessment.py#L54), [ADR 0004 §APR2-D4](../decisions/0004-mvp-product-scope.md#L116-L131) | 1. Implement Batch Context UI display (intake metadata). 2. For future learned model: compute validated SHAP attributions. | Fabricating causal factor weights for crop-median baseline, or claiming correlation equals causation. | Learned model selection (for attribution) | Backend & Frontend | `MEDIUM` (for Context UI); `DEFER` (for XAI) | **NO** (Context UI authorized; XAI deferred) |
| **GAP-06** | O4, E1, E4 | Action recommendations are fixed to `null` | `DOMAIN EVIDENCE GAP` | [`baseline_assessment.py:L55`](../../backend/app/services/baseline_assessment.py#L55), [ADR 0004 §APR2-D5](../decisions/0004-mvp-product-scope.md#L140-L153) | Interventional logging, controlled trials, or warehouse SOP records establishing counterfactual treatment efficacy. | Rule-based if-then heuristics ("re-cool batch"), fake action buttons, or assuming ranking equals action. | Real-world operational evidence | Domain / Sponsor | `DEFER` | **NO** (Unclosable with challenge data) |
| **GAP-07** | E2, E5 | Runtime baseline parity audit VDR-06B uncommitted | `VERIFICATION GAP` / `EVIDENCE GAP` | [VLD-R6 §5](../recon/VLD-R6-post-rbs01-reconciliation.md#L53), [`test_runtime_baseline.py`](../../backend/tests/test_runtime_baseline.py) | Execute and commit full offline-vs-runtime parity audit on all 900 held-out batches (VDR-06B). | Asserting parity based on unit tests alone, or sampling a single batch. | RBS-01 (done) | Data / Viktor | `HIGH` | **NO** (Technical verification task) |
| **GAP-08** | E1, E4 | No measured food loss reduction or financial ROI | `EXTERNAL VALIDATION GAP` | [ADR 0004 §APR2-D5](../decisions/0004-mvp-product-scope.md#L154-L157) | Live A/B testing or historical shadow pilot comparing standard dispatch against prioritised review. | Multiplying risk score by crop price, inventing €/tonne savings formulas, or claiming theoretical gains. | Warehouse deployment | External / Operations | `DEFER` | **NO** (Requires external pilot) |
| **GAP-09** | E5 | Production cloud deployment and containerization missing | `IMPLEMENTATION GAP` | [ADR 0005 §D6](../decisions/0005-runtime-baseline-serving.md#L190-L198) | Dockerfile, CI/CD deployment pipeline, and production infrastructure definition. | Claiming local development server or simulation mode constitutes production deployment. | Product scope gate | DevOps / Vladimir | `LOW` | **YES** (Infrastructure scope approval) |
| **GAP-10** | E1, E3 | Batch Context intake metadata not displayed in UI | `IMPLEMENTATION GAP` | [`AssessmentCard.tsx:L82-L98`](../../frontend/src/components/AssessmentCard.tsx#L82-L98), [ADR 0004 §APR2-D4](../decisions/0004-mvp-product-scope.md#L126-L129) | Add non-causal "Batch Context" section to `AssessmentCard.tsx` rendering crop, variety, harvest date, and planned logistics. | Attributing risk score to context fields or omitting required non-causal disclaimer. | GAP-01 (Frontend real route) | Frontend / PRSCR | `MEDIUM` | **NO** (Explicitly authorized by APR2-D4) |
| **GAP-11** | E2, E6 | Learned model engine tier not implemented/served | `IMPLEMENTATION GAP` / `PRODUCT DECISION GAP` | [ADR 0004 §5.1](../decisions/0004-mvp-product-scope.md#L184), [ADR 0005 §D4](../decisions/0005-runtime-baseline-serving.md#L170-L175) | Formally select model (e.g. HistGradientBoosting), fit artifact, add `learned_model` runtime provider and tests. | Serving uncalibrated experimental notebook models without runtime verification. | Model selection decision | Data & Backend | `LOW` / `DEFER` | **YES** (Human decision on ML tier) |

---

## 14. What can still move through implementation

The following backlog items can be completed by engineering without new domain evidence:

1. **Single-Batch Frontend Integration (PUX-11A / Candidate A):** Connect `HomePage.tsx` to `GET /api/v1/assessments/{batch_id}` via client method; provide batch selector input and error states for HTTP 404, 409, and 503.
2. **Batch Context UI Display (ADR 0004 APR2-D4):** Add intake metadata display in `AssessmentCard.tsx` with non-causal disclaimer captions.
3. **Multi-Batch Backend Foundation (Candidate B / future IGR-05A/B):** Bounded collection and replay route for Season-2025 held-out batches with deterministic ordering.
4. **Operator Triage Queue UI:** Interactive table sorting multiple batches by $\text{risk.score DESC, batch\_id ASC}$ within identical engine version.
5. **Bounded Filtering & Pagination Controls:** API parameters and UI components for `facility_id` filtering and window pagination.
6. **Learned Model Engineering Pipeline (if authorized):** Serialization and runtime provider for an approved HistGradientBoosting artifact.

---

## 15. What can still move through evidence / verification

The following items can be resolved through internal computation and formal auditing on existing data:

1. **VDR-06B Runtime Baseline Parity Audit:** Automated full-cohort verification proving that HTTP serving outputs bit-exact predictions against the offline evaluation on all 900 Season-2025 batches.
2. **Cross-Tier Benchmark Evaluation:** Rigorous empirical ranking comparison (NDCG@10, MAE, Spearman $\rho$) between baseline and candidate ML models.
3. **VLD-03 End-to-End Verification Gate:** Multi-component automated test suite validating the complete path from CSV snapshot to browser DOM.
4. **Feature Missingness & Telemetry Stability Audits:** Empirical resilience testing across storage facilities and sensor blackout intervals.

---

## 16. What requires new domain evidence

The following areas **cannot** be solved by writing code or analyzing the current dataset; they are fundamentally unclosable without new empirical domain data:

1. **Continuous Biological Deterioration Onset & Countdown (Outcome 2):** Requires longitudinal produce quality inspections during storage stay.
2. **Actionable Intervention Recommendations (Outcome 4):** Requires interventional logging, controlled trials, or warehouse SOP action catalogues.
3. **Causal Risk Factor Attribution (Outcome 3):** Requires controlled agronomic experiments to establish physical cause-and-effect beyond correlation.
4. **Measured Food Loss Reduction & Financial ROI (Criterion E4):** Requires an operational warehouse shadow pilot measuring waste reduction under formal SOPs.
5. **Real Operator Authority & Legal SOP Mandates:** Requires official job descriptions, CMR transport signing rules, and warehouse management protocols.

---

## 17. APR-03A → APR-04A claim delta

Audit of claim transitions between APR-03A (pre-RBS-01) and APR-04A (post-RBS-01 & VLD-R6 at base `fc71c67`):

| Capability / Dimension | APR-03A Stated Claim | APR-04A Audited Reality | Evidence / Source of Delta | Impact on Project Claims |
|---|---|---|---|---|
| **Real Assessment HTTP API** | `NOT IMPLEMENTED` (*"No real assessment endpoint exists; only demo fixture"*) | **`IMPLEMENTED`** (Single-batch dataset-backed route) | [`routes.py:L36-L61`](../../backend/app/api/routes.py#L36-L61) ([PR #42](../recon/VLD-R6-post-rbs01-reconciliation.md#L10)) | **MAJOR UPGRADE:** Backend now actively serves dataset-backed scores for Season-2025 held-out batches with release gating (409/404/503). |
| **Baseline Artifact Lifecycle** | `NOT IMPLEMENTED` (*"Manual/ad-hoc fitting; no versioned artifact in tree"*) | **`IMPLEMENTED`** (Controlled fit script & signed JSON artifact) | [`generate_baseline_artifact.py`](../../scripts/generate_baseline_artifact.py), [`baseline-crop-median-v1-p1-s2024.json`](../../backend/artifacts/baseline-crop-median-v1-p1-s2024.json) | **MAJOR UPGRADE:** Artifact carries schema version, 8-table SHA256 hashes, training cohort SHA256 fingerprint, and fitted medians. |
| **Runtime Validation & Context** | `NOT IMPLEMENTED` (*"No startup validation; blind file reading"*) | **`IMPLEMENTED`** (FastAPI lifespan context loader) | [`artifact.py`](../../backend/app/runtime/artifact.py), [`context.py`](../../backend/app/runtime/context.py) | **MAJOR UPGRADE:** Application enforces strict startup validation: snapshot table integrity, cohort fingerprinting, and fail-closed DI (`get_runtime`). |
| **Health State Synchronization** | `PARTIAL` (*"Hardcoded analytics: 'not_configured' across all paths"*) | **`IMPLEMENTED`** (Synchronized tri-state health model) | [`routes.py:L20-L26`](../../backend/app/api/routes.py#L20-L26), [`contracts.ts:L3-L7`](../../frontend/src/api/contracts.ts#L3-L7) | **UPGRADE:** Tri-state `analytics: "not_configured" \| "ready" \| "unavailable"` is fully typed and verified across backend and frontend contracts. |
| **Frontend Real-Route Integration** | `NOT IMPLEMENTED` | **`NOT IMPLEMENTED`** (Unchanged) | [`client.ts:L18-L24`](../../frontend/src/api/client.ts#L18-L24), [`HomePage.tsx:L25-L39`](../../frontend/src/pages/HomePage.tsx#L25-L39) | **STABLE BOUNDARY:** Frontend still calls only `getDemoAssessment()` and renders the synthetic fixture. Real route is unconsumed in UI. |
| **Multi-Batch / Queue Capability** | `NOT IMPLEMENTED` | **`NOT IMPLEMENTED`** (Unchanged) | [`routes.py`](../../backend/app/api/routes.py), [ADR 0005 §D7](../decisions/0005-runtime-baseline-serving.md#L201-L203) | **STABLE BOUNDARY:** Multi-batch route, replay feed, triage queue UI, and filtering remain deferred. Single-batch scoring does not equal triage workflow. |
| **Outcome 1 Epistemic Status** | `PARTIAL` (Analytics code exists, no serving) | **`PARTIAL`** (Single-batch serving exists; triage queue missing) | [ADR 0005 §D1](../decisions/0005-runtime-baseline-serving.md#L144-L151) | **CLARIFIED STATUS:** Single-batch scoring is dataset-backed, but the primary task ("which batches are most at risk?") requires multi-batch ranking. |
| **Outcomes 2, 3, 4 Epistemic Status** | `UNSUPPORTED` / `PARTIAL` | **`UNSUPPORTED` / `PARTIAL`** (Strictly Preserved) | [`baseline_assessment.py`](../../backend/app/services/baseline_assessment.py#L53-L55) | **STABLE BOUNDARY:** O2 (`deterioration_horizon=null`), O3 (algorithmic transparency only; no feature attribution), O4 (`recommendation=null`). Truthful disclaimers are preserved. |

---

## 18. Demo-safe outcome wording

Factual rules for presentation and pitch assembly (preparation for later VLD-05):

### Outcome 1
- **MAY SHOW:** Backend API returning dataset-backed `RiskAssessment` for eligible held-out batch (`BAT-000901`); release gating (409 on training, 404 on unknown); fail-closed 503; VDR-06A benchmark results.
- **MAY SAY:** *"Smart Harvest computes a transparent relative loss-severity score for individual batches at dispatch, derived from historical training medians by crop. Scores prioritise operator review attention: `risk.score DESC, batch_id ASC`."*
- **MUST NOT SAY:** *"The frontend displays an operational triage queue of all at-risk batches."* / *"The score is a calibrated probability."* / *"We classify batches into green/yellow/red risk bands."*

### Outcome 2
- **MAY SHOW:** Schema field `deterioration_horizon: null`; UI disclaimer *"Deterioration timing: Not estimable from supplied observations"*; VDR-03 single-point data proof.
- **MAY SAY:** *"Deterioration timing is explicitly not estimable from supplied data because observations occur at a single fixed moment before dispatch. The system honestly communicates this limitation."*
- **MUST NOT SAY:** *"Smart Harvest predicts remaining shelf-life days or deterioration countdowns."* / *"Planned transit hours represent the deterioration horizon."*

### Outcome 3
- **MAY SHOW:** Formula explanation panel in UI; empty factors list `factors: []`; ingestion code mapping observable pre-dispatch batch, storage, and telemetry context.
- **MAY SAY:** *"For the baseline, we provide algorithmic transparency on how median scores are computed from training history. Observable context fields are pre-dispatch intake facts, not causal explanations."*
- **MUST NOT SAY:** *"The system identifies chamber humidity or temperature as the cause of this batch's risk score."* / *"We have implemented full XAI or SHAP feature attributions."*

### Outcome 4
- **MAY SHOW:** Schema field `recommendation: null`; UI panel rendering accepted disclaimer *"Action recommendations are unavailable. Current evidence does not validate intervention effectiveness."*
- **MAY SAY:** *"Action recommendations are unavailable because available challenge data contain zero counterfactual intervention trials. Smart Harvest prioritises batches for review, but does not prescribe physical interventions."*
- **MUST NOT SAY:** *"Smart Harvest recommends re-cooling, re-routing, or discarding high-risk batches."* / *"Prioritising review attention is equivalent to prescribing operational actions."* / *"Using this tool saves €X or reduces food loss by Y%."*

---

## 19. Priority recommendations

- **HIGH PRIORITY:**
  - **RECOMMENDATION (GAP-01 — Single-batch frontend integration):** Connect UI to `GET /api/v1/assessments/{batch_id}`. Closes the immediate disconnect between live backend capability and user experience.
  - **RECOMMENDATION (GAP-07 — VDR-06B runtime parity audit):** Complete and commit full 900-batch parity verification.
  - **RECOMMENDATION (GAP-02 — Multi-batch backend foundation):** Specify bounded collection/replay endpoint to support cross-batch ranking.
- **MEDIUM PRIORITY:**
  - **RECOMMENDATION (GAP-10 — Batch Context UI display):** Expose observable intake facts in UI per ADR 0004 APR2-D4.
  - **RECOMMENDATION (GAP-03 — Ranked queue UI):** Implement multi-item triage table once GAP-02 provides the data feed.
- **LOW PRIORITY:**
  - **RECOMMENDATION (GAP-09 — Production cloud deployment):** Containerization and deployment definitions.
  - **RECOMMENDATION (GAP-11 — Learned engine tier):** ML model pipeline (HistGradientBoosting), if authorized by Human Gate.
- **DEFER:**
  - **RECOMMENDATION (GAP-04 Deterioration horizon, GAP-06 Action recommendations, GAP-08 Measured loss reduction / ROI):** Strictly defer. These require fundamentally new domain evidence; writing speculative code violates project canon.

---

## 20. Human decisions required

The following bounded decisions strictly require Human Integrator authorization:

1. **Selection of Next Implementation Slice (VLD-R6 §11):**
   - *Candidate A:* Single-batch frontend integration (PRSCR).
   - *Candidate B:* Multi-batch / replay backend foundation (Igor).
   - *Candidate C:* VLD-03 preparation / end-to-end verification gate (Vladimir).
2. **Multi-Batch Contract Scope (GAP-02):** Explicitly deferred by ADR 0005 D7; requires decision on filtering parameters, sorting constraints, and replay window bounds.
3. **Learned Engine Selection & Activation (GAP-11):** Human decision on whether to train and serve a candidate ML model family (e.g. HistGradientBoosting) or freeze at the deterministic baseline.

---

## 21. Questions for possible official clarification

> [!NOTE]
> None of these questions have been submitted or answered. No external contact has been initiated.

- **`QUESTION FOR POSSIBLE OFFICIAL CLARIFICATION 1` — Partial Support of Four Outcomes:**
  *"Does the challenge evaluation criteria expect working algorithmic implementations for all four stated outcomes (O1–O4), or is an explicit, mathematically sound, and honest 'unavailable / not estimable' status recognized as valid technical rigor when the supplied dataset lacks longitudinal inspection or intervention records?"*
  - *Impact:* Clarifies whether the team must maintain strict null outputs or consider rule-based domain heuristics for O2/O4.

- **`QUESTION FOR POSSIBLE OFFICIAL CLARIFICATION 2` — Nature of Action Recommendations (Outcome 4):**
  *"Is the prioritised action recommendation expected to be empirically derived from the provided dataset, or is it permissible/desirable to incorporate external agronomic cold-storage literature (e.g. FAO post-harvest guidelines, standard cold-chain SOPs) as deterministic expert rules?"*
  - *Impact:* Determines whether an external rule-based recommendation catalogue is acceptable or violates empirical boundaries.

- **`QUESTION FOR POSSIBLE OFFICIAL CLARIFICATION 3` — Implemented Capability vs. Unavailable-State Honesty:**
  *"In scoring criterion E3 (Usability & Explainability) and E2 (Accuracy & Reliability), how do judges weigh a narrower, fully validated, and leakage-proof baseline with explicit unavailable states against a broader predictive prototype that estimates all four outcomes with uncalibrated heuristics?"*
  - *Impact:* Governs whether to prioritize a candidate learned model (HGB) or solidify baseline UI integration and replay.

- **`QUESTION FOR POSSIBLE OFFICIAL CLARIFICATION 4` — Single-Batch vs. Multi-Batch Operational Scope:**
  *"Is the primary operational demonstration expected to be an interactive multi-batch dispatch queue (triage table), or is deep single-batch inspection at dispatch considered sufficient proof of concept for the MVP?"*
  - *Impact:* Directly dictates whether next implementation priority must be Candidate A (single-batch UI) or Candidate B (multi-batch replay route and queue).

---

## 22. Explicit forbidden claims

To preserve epistemic integrity, the following claims are strictly forbidden across all documentation, code comments, and demo narratives:

1. **Forbidden:** Claiming that `risk.score` is a calibrated probability or a percentage likelihood of spoilage.
2. **Forbidden:** Grouping batches into green/yellow/red traffic light risk bands (`risk.band` is fixed to `null`).
3. **Forbidden:** Claiming that Smart Harvest predicts biological deterioration countdowns or remaining shelf-life days.
4. **Forbidden:** Prescribing physical warehouse actions ("pre-cool", "re-route", "discard") or claiming Outcome 4 is fulfilled.
5. **Forbidden:** Claiming empirical food loss reductions (e.g. "saves 15% of produce") or financial ROI (€ / $).
6. **Forbidden:** Claiming that the current browser UI displays a live, dataset-backed operator triage queue.
7. **Forbidden:** Attributing causal blame to batch context fields (e.g. "high chamber humidity caused this risk score").
8. **Forbidden:** Merging baseline scores and future learned-model scores into a common ranking without empirical calibration.

---

## 23. Remaining UNKNOWNs

The twelve canonical UNKNOWNs established in ADR 0004 §5 remain open and unresolved:

1. **Production learned model selection:** Model family, hyperparameters, and formal acceptance criteria.
2. **Final feature subset:** Inclusion or exclusion of specific telemetry aggregates in a future learned model.
3. **Cross-tier / cross-version comparability:** Validation of score equivalence across different engine tiers.
4. **Engine minimum input requirements:** Exact criteria defining `insufficient_data` for future learned engines.
5. **Calibrated reliability & confidence:** Statistical probability calibration and numerical confidence scoring.
6. **Operational risk bands:** Categorical thresholds (`risk.band`), traffic-light tags, or operator alert triggers.
7. **Biological deterioration onset & timing:** Exact biological onset timestamps or deterioration intervals.
8. **Explainability & model attribution (XAI):** Algorithm selection (SHAP) and operator comprehension testing.
9. **Operator authority & warehouse SOP:** Formal role titles, hold/release authority, and CMR document signing.
10. **Triage queue membership & capacity:** Exact duration of dispatch replay windows and shift review quotas.
11. **Action catalogue & intervention efficacy:** Counterfactual treatment effects, action costs, and lead times.
12. **Telemetry audit & diagnostic utility:** Use of sensor streams for equipment-health monitoring or fault diagnostics.

---

## 24. Verification

- **Working Tree Integrity:** Verified via `git status` at `main @ fc71c67356704c2b33d0c4c5c28afc09c4007560`.
- **Write Scope Adherence:** Only `docs/product_recon/11_challenge_outcome_coverage_evidence_gaps.md` was created. Zero code, schema, config, or existing documentation files were altered.
- **Reference Integrity:** All cited files, line ranges, and ADR decisions exist and conform to repository state.

---

## 25. Final handoff

Task **APR-04A** is complete.

- **Deliverable:** `docs/product_recon/11_challenge_outcome_coverage_evidence_gaps.md`.
- **Intended Consumers:**
  - **Vladimir (Integrator):** Candidate slice selection (A, B, or C), demo script assembly, and subsequent VLD-05 audit.
  - **Denis / PRSCR (Frontend):** UI implementation boundaries (GAP-01 single-batch integration, GAP-10 batch context display, GAP-03 queue UI).
  - **Igor (Backend):** Multi-batch replay foundation contract design (GAP-02).
  - **Viktor (Data):** Runtime baseline release audit execution (GAP-07 / VDR-06B).
- **Execution State:** Stopped for Project Brain and Human Integrator review. No further write actions authorized.

---

## Human decisions required after APR-04A

The following decisions genuinely require Vladimir (Human Integrator). They define the remaining implementation priorities, narrative boundaries, and external interactions. No decision here creates a new ADR automatically; formal adoption requires a separate Human Gate.

### Decision ID: `DEC-APR04-01`
- **Question:** Which remaining implementation slice receives immediate priority for next engineering work?
- **Current Evidence:** Backend serves single-batch baseline via `GET /api/v1/assessments/{batch_id}` ([`routes.py:L36-L61`](../../backend/app/api/routes.py#L36-L61)). Frontend currently calls only the synthetic fixture ([`HomePage.tsx:L25-L39`](../../frontend/src/pages/HomePage.tsx#L25-L39)). Multi-batch route is unbuilt ([ADR 0005 §D7](../decisions/0005-runtime-baseline-serving.md#L201-L203)).
- **What Is Already Fixed:** Baseline algorithm, artifact lifecycle, single-batch HTTP contract, and release gating (ADR 0005 D1–D7).
- **Option A:** Candidate A (Single-batch frontend integration — connect `HomePage.tsx` to `GET /api/v1/assessments/{batch_id}` and add batch selector in UI).
- **Option B:** Candidate B (Multi-batch / replay backend foundation — implement collection endpoint for Season-2025 held-out batches).
- **Option C:** Candidate C (VLD-03 preparation / formal end-to-end verification gate across existing components).
- **Alisa Recommendation:** Option A (Candidate A). Directly closes GAP-01, making the live dataset-backed backend visible in the browser and resolving the severe disconnect where users see only `insufficient_data`.
- **Consequence:** If Option A is selected through the Human Integrator gate, a bounded frontend implementation contract may be authorized. APR-04A itself does not authorize implementation. Candidate B and Candidate C remain queued.
- **Vladimir Decision:** PENDING

---

### Decision ID: `DEC-APR04-02`
- **Question:** What product and demo posture should be maintained for unsupported outcomes O2 (deterioration timing) and O4 (action recommendations)?
- **Current Evidence:** VDR-03 proves single-point pre-dispatch inspections cannot establish continuous biological decay curves. Challenge data contain zero interventional trial records or action logs. ADR 0003 (D8, D9) and ADR 0004 (APR2-D5) enforce `deterioration_horizon = null` and `recommendation = null`.
- **What Is Already Fixed:** Production schemas, API serializer, and UI disclaimers enforce `null` with explicit limitation notices.
- **Option A:** Strictly disclose O2 and O4 as "not estimable / unavailable due to dataset constraints" and pitch this explicit refusal to fabricate data as core engineering rigor and epistemic honesty.
- **Option B:** Authorize a research spike into external agronomic cold-storage guidelines (e.g. FAO literature) to explore rule-based advisory actions for O4 only.
- **Alisa Recommendation:** Option A. Preserves absolute canon integrity and avoids introducing uncalibrated rule-based heuristics that cannot be validated against the competition dataset.
- **Consequence:** Freezes O2 and O4 as truthful unavailable states for the final demo; no engineering resources spent attempting to invent countdowns or action catalogues.
- **Vladimir Decision:** PENDING

---

### Decision ID: `DEC-APR04-03`
- **Question:** Which claims and analytics capabilities are admitted into the final MVP demo (preparation for VLD-05)?
- **Current Evidence:** Deterministic crop-median baseline is fully verified and served at runtime (NDCG@10=0.7067, MAE=8.53 in VDR-06A). Candidate learned models (HistGradientBoosting) were benchmarked in VDR-04A/B but are not wired to runtime serving.
- **What Is Already Fixed:** Baseline runtime serving, simulation flag (`simulation=True`), and simulation notice copy (ADR 0005 D5, D6).
- **Option A:** Freeze runtime demo strictly at the deterministic baseline tier (`baseline-crop-median-v1-p1-s2024`); present learned model benchmarks strictly as offline feasibility evidence in slides/appendix.
- **Option B:** Authorize full runtime implementation of a `learned_model` engine tier (HistGradientBoosting) alongside the baseline before demo freeze.
- **Alisa Recommendation:** Option A. Minimizes integration risk and avoids cross-tier ranking comparability issues, while presenting a verified, leakage-free working prototype.
- **Consequence:** Runtime serving remains baseline-only. Team focuses remaining time on UI polish, replay controls, and end-to-end verification.
- **Vladimir Decision:** PENDING

---

### Decision ID: `DEC-APR04-04`
- **Question:** Should the team seek official mentor / challenge-owner clarification on evaluation criteria weighting between outcome coverage and methodological honesty?
- **Current Evidence:** The challenge brief asks for four outcomes (O1–O4) and lists evaluation criteria E1–E6, but provides no formal guidance on how judges score explicit "not estimable" disclosures versus heuristic models.
- **What Is Already Fixed:** Four concrete questions formulated in APR-04A §21 (`QUESTION FOR POSSIBLE OFFICIAL CLARIFICATION 1–4`).
- **Option A:** Submit Clarification Questions 1 and 2 if an official Q&A window is opened before final submission.
- **Option B:** Seek no external clarification; proceed entirely self-contained under current accepted SoS canon and decisions.
- **Alisa Recommendation:** Option A, provided an official public channel exists and does not leak proprietary architectural strategy.
- **Consequence:** If answered, reduces uncertainty on whether rule-based actions are acceptable. If unanswered, Option B remains default.
- **Vladimir Decision:** PENDING

