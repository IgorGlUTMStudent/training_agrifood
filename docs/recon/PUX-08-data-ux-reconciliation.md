# PUX-08 — Evidence-Safe UX Reconciliation & Design Readiness Report

**Author:** Denis (`denis100strike`)
**Role:** Frontend / UX / Design specialist
**Repository:** `Slave-of-Skynet/training_agrifood`
**Base Revision:** `70ab2a3ce6f060f9b2b43fcb7fb4ecd284426fdd`
**Inspected Latest Main Revision:** `98e0df1db0b2987301b6f7523fd45520d67dffa0` (reconciled post-IGR-03 / APR-02F integration; historical PR #22 inspected `204c3ac37fb2098bfe6c0908a66c54065cda23ae`)
**Target File:** `docs/recon/PUX-08-data-ux-reconciliation.md`
**Status:** DRAFT FOR REVIEW (Reconciled After Repository Advance; Post-Human-Gate Note Added 2026-09-21)

> **Post-Human-Gate Note (2026-09-21):**
> Decisions APR2-D1 through APR2-D6 were accepted by Human Integrator Vladimir through [ADR 0004](../decisions/0004-mvp-product-scope.md).
> Where ADR 0004 directly establishes a product/UX boundary, that decision is authoritative over earlier tentative PUX-08 proposals.
> All other PUX-08 layouts, workflow proposals, indicators, interaction patterns and recommendations remain research/design recommendations unless separately accepted.

---

## 1. Executive Summary & Epistemic Boundaries

This report reconciles earlier UX proposals (PUX-00 through PUX-07) against the established evidence and decision canon across the repository:
- **Normative Decisions:** ADR 0001 (batch architecture), ADR 0002 (predictive input semantics, temporal boundaries, missingness), ADR 0003 / VLD-02B (assessment, ranking, and evaluation semantics), ADR 0004 (MVP product scope & human decision reconciliation).
- **Data & Evaluation Evidence:** VDR-01 (dataset inventory), VDR-02 (temporal leakage), VDR-03 (target/horizon feasibility), VDR-04A (dispatch predictability benchmark), VDR-04B (telemetry marginal-value ablation under planned logistics).
- **Product Research & Decisions:** APR-01 Steps 0–8 (user decision model, proposed product workflow, adversarial review) and APR-02 packets. APR2-D1–D6 were formally accepted by Human Integrator Vladimir on 2026-09-21 in [ADR 0004](../decisions/0004-mvp-product-scope.md) as authoritative MVP product scope; the surrounding APR-02 source documents remain mixed research/specification artifacts.
- **Implementation State:** Ingestion diagnostics (IGR-02), canonical BatchAssessmentInput mapping (IGR-03), frontend status/assessment components, and PR CI foundation (VLD-CI-01).

The historical task starting base remains recorded as `70ab2a3ce6f060f9b2b43fcb7fb4ecd284426fdd`. The repository has advanced to `98e0df1db0b2987301b6f7523fd45520d67dffa0` on `origin/main` (incorporating PR #28 IGR-03 and PR #29 APR-02F). This reconciliation updates all UX requirements to be truthful to accepted decisions while strictly isolating unratified proposals and unknown operational parameters.

### Epistemic Classifications Applied:
- **FACT:** Directly verifiable from committed repository code, dataset distributions, or accepted challenge canon.
- **DECISION:** Formally recorded architectural and product rulings (ADR 0001, ADR 0002, ADR 0003 / VLD-02B).
- **OBSERVED IMPLEMENTATION:** The actual behavior and structure present in current codebase files (`frontend/src/**`, `backend/app/**`).
- **INFERENCE:** Analytical conclusions logically grounded in validated evidence.
- **RECOMMENDATION:** Proposed UI/UX structures, product workflows, or candidate personas that remain subject to formal decision gates.
- **UNKNOWN:** Semantics, operational policies, quotas, or performance thresholds that have not been established or verified.
- **SIMULATION:** Synthetic demo fixtures or mock states that do not represent evaluated production data.

---

## 2. Master Reconciliation Matrix

All data-dependent UX concepts proposed across PUX-00–07 are evaluated on two orthogonal axes:
- **Axis A (Evidence Support):** `SUPPORTED`, `SUPPORTED WITH LIMITATION`, `NOT SUPPORTED`, `UNKNOWN`.
- **Axis B (UX Disposition):** `KEEP`, `CHANGE`, `REMOVE`, `BLOCKED`.

| UX Element | Original PUX Proposal | Current Implementation State | Evidence Support | Disposition | What Is Safe to Show Now | What Must NOT Be Shown | Blocking Evidence / Decision | Blocker Owner | Post-VDR-04A/04B Relevance |
|---|---|---|---|---|---|---|---|---|---|
| **Batch Overview List (Neutral)** | Multi-batch table showing contextual fields and status | Not implemented; current frontend contains only a single synthetic AssessmentCard fixture and no production multi-batch API | `SUPPORTED` | `KEEP` | Neutral list, Batch IDs, crop type, dispatch metadata, facility/zone identifier | Implied risk triage ordering or sorting by unassessed severity | None for neutral list structure | None | Baseline UI frame |
| **Ranking / Ordering Semantics** | Deterministic sorting rule for assessed batches | Implemented in evaluation benchmark scripts; not in production API | `SUPPORTED` | `KEEP` | Descending `risk.score` sort with deterministic `batch_id ASC` tie-breaker strictly within same `engine_tier + engine_version` | Merging different engine tiers/versions into a single ranked queue; treating unassessed/insufficient_data as zero-risk | Formal comparability validation across tiers/versions (ADR 0003 D3) | Data Science / Integrator | Accepted ranking semantics (ADR 0003 D3) |
| **Concrete Operator Triage Queue Workflow** | Default operator queue with review quotas (e.g. K=10, K=50) for specific persona | Not implemented; static single-card UI | `UNKNOWN` / `RECOMMENDATION` | `BLOCKED` | Neutral list sorted by chronological dispatch or batch ID; explicit notice that ranking is prioritisation, not exhaustive screening | Default triage queue mode, K=10/50 treated as operator quotas, unvalidated persona-specific authority | Team/Integrator decision on persona, operator authority, review capacity, and fallback routing | Product Lead / Integrator | APR-01 Steps 6–8 candidate workflow |
| **Risk Score (Severity / Numeric)** | Decimal [0.0–1.0] displayed directly or as progress bar | Implemented as raw float in unreachable `assessed` branch of `AssessmentCard.tsx` | `SUPPORTED` | `CHANGE` | Score presented strictly as predicted loss/degradation severity used for prioritisation (`clip(pct, 0, 100) / 100`) | Interpreting score as probability, calibrated confidence, certainty of spoilage, or causal impact; false decimal precision | None on semantics (ADR 0003 D2 accepted); visual precision and production model scoring pending | UX / Frontend | Establishes bounded loss-severity semantics |
| **Risk Band (Low / Mod / High)** | Color-coded categorical tags (Green/Amber/Red) | Schema field exists (`risk.band` in `contracts.ts`), currently null | `NOT SUPPORTED` / `POLICY DECIDED` | `BLOCKED` | Neutral status badges, explicit "Pending Assessment" or omitting band container | Hard-coded cut-offs, traffic-light color severity scales, inferred ≥15% high-risk band | Gated by future risk band and threshold policy validation (ADR 0003 D2 sets `risk.band = null`) | Integrator / Product | Prevents arbitrary alert thresholds |
| **Deterioration Horizon** | "In 18 hours" continuous countdown, hover timestamps | Implemented as `starts_at` in unreachable branch of `AssessmentCard.tsx` | `NOT SUPPORTED` | `REMOVE` | Nullable state communicating "Not estimable from supplied observations" (field preserved for forward compatibility) | Continuous countdowns, arrival timestamps, coarse deterioration windows/intervals | Rejection of continuous time model and interval estimation from supplied observations (VDR-03, ADR 0003 D6) | Integrator / VDR-03 | Continuous countdowns and coarse deterioration intervals are unsupported and not authorized under current accepted evidence and ADR 0003 policy |
| **Reliability State & Numerical Confidence** | Quantitative confidence metric (e.g. "94% reliable") | Fields exist in domain model; demo returns `level: "unavailable"`, `confidence_score: null` | `SUPPORTED WITH LIMITATION` | `CHANGE` | Factual display of `level: unavailable` along with explicit `reason_codes` and `missing_requirements` when populated | Invented numerical confidence scores (e.g. "94%"), arbitrary low/medium/high reliability thresholds | Calibrated reliability policy and sufficiency criteria validation (ADR 0003 D7) | Integrator / Data Science | Separates assessment capability from calibrated confidence |
| **Contributing Factors / Explanations** | Environmental drivers (e.g. "Humidity caused +15% loss") | Structured container rendered if populated (`AssessmentCard.tsx`) | `SUPPORTED WITH LIMITATION` | `CHANGE` | Factor presence for factual data-quality/context condition, or verified model contribution from accepted method; `effect = unknown` or `factors = []` | Causal phrasing ("caused", "resulted in"), synthetic factor weights, feature-family associations presented as individual causal factor cards | Explanation mechanism selection and attribution baseline validation (ADR 0003 D8) | Data Science / Integrator | Directs factors to verified model attribution, not biological causality |
| **Recommendations / Actions** | Direct intervention buttons ("Sell now", "Reroute", "Pre-cool") | `Recommendation` container in schema; demo returns null | `NOT SUPPORTED` / `POLICY DECIDED` | `BLOCKED` | Rendering recommendation as unavailable/withheld (`recommendation = null`) | Prescribed business interventions, autonomous action dispatch, financial savings claims, prevented loss claims | Domain action-effect validation catalog and operator authority definition (ADR 0003 D9) | Product Lead / Integrator | Candidate action classes 1–5 remain research, not product output |
| **Missing / Partial Data Handling** | Generic warning banner | `insufficient_data` state implemented in `AssessmentCard.tsx` | `SUPPORTED` | `KEEP` | Explicit degradation state explaining that required inputs are missing, displaying populated `reason_codes` and `missing_requirements` | Silent null suppression, fabricated zero defaults, automatically treating missing telemetry as insufficient data | None for UI display capability; exact engine minimums remain implementation decisions (ADR 0003 D7) | Implementation / Integrator | Core robust UX pattern |
| **Historical Outcomes vs Predictions** | Display historical loss alongside prediction | Not implemented in client UI | `NOT SUPPORTED` | `REMOVE` | Retrospective evaluation / benchmark / analytics review views strictly segregated from operational triage | Historical transit losses or final outcomes displayed as if known prior to dispatch (`T_assess = T_dispatch`) | Temporal and lineage invariants; target leakage rules (ADR 0002, ADR 0003 D1) | Integrator | Prevents retrospective target leakage |
| **Financial / Economic Loss Claims** | Predicted EUR savings counter, prevented loss metrics | Not implemented | `NOT SUPPORTED` | `REMOVE` | Raw historical baseline economics strictly in offline evaluation views | Predicted monetary savings, ROI calculations, commercial savings claims | Absence of causal savings models and intervention benefit evidence (VDR-03, ADR 0003 D9) | Product Lead | Monetary savings claims strictly excluded |
| **Real-Time Streaming Alerts & Tracking** | Push alerts, continuous reefer truck tracking | ADR 0001 accepts batch/on-demand MVP architecture. Current implementation provides health checking and a single synthetic demo assessment only; no production batch-assessment, inventory, push, or streaming infrastructure exists. | `NOT SUPPORTED` | `REMOVE` | Static update timestamps only (on-demand request lifecycle once batch evaluation API exists) | Live streaming trackers, simulated live telemetry ticks, GPS transit tracking | Batch architecture decision (ADR 0001) | Architecture | Confirms purely on-demand/batch evaluation |
| **Charts: Pre-dispatch Telemetry** | Historical observation charts | Not implemented | `SUPPORTED WITH LIMITATION` | `KEEP` | Strictly observational charts bounded to `T_dispatch`, preserving lineage `batch -> storage_session -> storage_zone -> sensor_readings` | Telemetry presented as driving the score; unsupported safe/unsafe thresholds; future trajectories; causal explanations | None for optional observed context; marginal value remains unproven under tested configurations (VDR-04B, ADR 0003 D10) | Data Science / Product | Optional observed context, not core explanatory surface |
| **Charts: Predictive Forecasts** | Predictive trendlines, deterioration trajectories | Not implemented | `NOT SUPPORTED` | `REMOVE` | None | Deterioration trendlines, future quality trajectories, safe-corridor bands | Rejection of continuous time model and interval estimation (VDR-03, ADR 0003 D6) | Integrator | Predictive future trajectories are unsupported and not authorized under current accepted evidence and ADR 0003 policy |

---

## 3. Current Frontend & Backend Implementation Audit

Review of committed repository code as of latest `origin/main` (`204c3ac37fb2098bfe6c0908a66c54065cda23ae`):

### 3.1 Frontend Implementation State (`frontend/src/**`)
1. **Connection & Status Management (`HomePage.tsx` & `BackendStatus.tsx`):**
   - `HomePage.tsx` orchestrates connection lifecycle: `loading` (spinner with accessible announcement), `available`, and `unavailable` (with manual retry trigger `retry()`).
   - `BackendStatus.tsx` renders the connected/available state with service and analytics status chips.
2. **Synthetic Fixture / Provenance Indicator (`AssessmentCard.tsx`):**
   - Renders notice from `assessment.provenance.notice`: `SIMULATION / synthetic fixture / not challenge data`.
   - Correctly establishes simulation transparency.
3. **Assessment Card Branches (`AssessmentCard.tsx`):**
   - **Insufficient Data State:** Explicitly handled; displays fallback message. Currently does *not* render `reliability.reason_codes` or `missing_requirements`, although both fields are defined in the TypeScript contract (`frontend/src/api/contracts.ts`) and backend schema.
   - **Unreachable `assessed` Branch:** Displays `Risk score: {assessment.risk?.score}` as an unformatted raw number and `Deterioration window starts: {assessment.deterioration_horizon?.starts_at}`. This branch reflects outdated assumptions (continuous timestamps) that must be transformed before exposure.
4. **Missing Production Frontend Surfaces:**
   - No multi-batch list or batch inventory view exists.
   - No ranked triage queue or interactive triage workflow exists.
   - No telemetry visualization charts exist.

### 3.2 Backend Implementation State (`backend/app/**`)
1. **Raw Ingestion & Structural Diagnostics [IGR-02] (`backend/app/ingestion/**`):**
   - Pure raw CSV reading (`raw_reader.py`), physical schema specification (`structural_manifest.py`), and dataset integrity verification (`diagnostics.py`) are **IMPLEMENTED**.
   - Handles raw reading of all 8 sponsor CSV files and detects missing files, duplicate keys, broken foreign keys, and structural nulls.
2. **Canonical Mapping & Analytics Pipeline:**
   - **Canonical `BatchAssessmentInput` mapping [IGR-03]:** **IMPLEMENTED** (`backend/app/domain/batch.py`, `backend/app/ingestion/canonical_mapper.py`). Implements deterministic raw-to-canonical conversion, temporal leakage boundary enforcement ($T_{entry} \le t \le T_{dispatch}$), preservation of structural missingness as `None`, planned logistics mapping, and fail-closed cardinality validation.
   - **Analytics & Assessment Runtime:** Feature engineering, ML model scoring, runtime crop-median engine, production ranking endpoint, and product batch inventory API are **NOT YET IMPLEMENTED**.
   - `demo_assessment.py` continues to return a synthetic `insufficient_data` fixture.

---

## 4. Reconciliation of Accepted ADR 0003 Semantics

ADR 0003 (VLD-02B) is a committed normative architectural decision. PUX-08 reconciles its rulings (D1–D10) as accepted canon:

### 4.1 Primary Task and Target (D1)
- **Primary Operational Task:** Batch prioritisation/ranking at dispatch.
- **Primary Offline Analytical Target:** `loss_fraction_pct` (historical percentage of harvest weight lost at destination). Strictly a training/evaluation label, never an inference input.
- **Implication for UX:** The system is designed to order batches by predicted severity, not to provide definitive binary pass/fail verdicts or continuous loss guarantees.

### 4.2 Risk Score Semantics (D2)
- **Accepted Formula:**
  $$\text{score} = \frac{\text{clip}(\text{predicted\_loss\_fraction\_pct}, 0, 100)}{100}$$
- **Accepted Meaning:** Bounded degradation/loss severity score used for prioritisation. Higher score indicates greater predicted loss severity.
- **Negative Epistemic Boundaries:** The score is **NOT** a probability of loss, **NOT** calibrated confidence, **NOT** certainty of spoilage, and **NOT** a causal impact estimate.
- **Obsolete Wording Removed:** Statements framing the score meaning as "pending VLD-02B" or "experimental" are removed. Semantics are accepted; production scoring implementation is pending.

### 4.3 Ranking Semantics vs Comparability (D3)
- **Ranking Rule:** Assessed batches are ordered by `risk.score DESC`, then `batch_id ASC` for deterministic tie-breaking.
- **Tier & Version Isolation:** A common ranked queue is permitted **ONLY** within the same `engine_tier + engine_version`. Results from different tiers or versions must **NOT** be merged into a single ranked list until cross-tier comparability is formally validated.
- **Insufficient Data Handling:** `insufficient_data` results have no risk score and must **NOT** be treated as zero risk or sorted alongside scored batches.
- **Prioritisation vs Screening:** Ranking is prioritisation, not exhaustive screening. Small-$k$ recall is low; UI must use terms like "priority" or "higher predicted severity", never "guaranteed highest loss" or "discard instruction".

### 4.4 Risk Band Policy (D2)
- Current accepted policy mandates: `risk.band = null`.
- Low / Moderate / High categorical bands, traffic-light color scales, and inferred thresholds (e.g. ≥15% high risk) are strictly absent. Future band policy remains separately gated.

### 4.5 Deterioration Horizon Policy (D6)
- Current accepted policy mandates: `deterioration_horizon = null` for all analytical engines.
- Permitted user-facing communication: `"Not estimable from supplied observations"`.
- Neither continuous countdowns nor discrete coarse intervals are authorized. The nullable contract field is preserved solely for forward compatibility.

### 4.6 Reliability and Data Sufficiency (D7)
- Current accepted runtime policy:
  ```text
  reliability.level = "unavailable"
  reliability.confidence_score = null
  ```
- Factual data limitations may be communicated through `reason_codes` and `missing_requirements`. Invented numerical confidence percentages (e.g. "94% reliable") are prohibited.
- `assessed` vs `insufficient_data`: `assessed` indicates the engine satisfied its declared input minimums; `insufficient_data` indicates minimums were not met. Ability to assess is distinct from calibrated confidence.
- Legitimate missingness (non-CA atmospheric readings, ZONE-006 surface temperature, 204 telemetry-truncated batches) must not be treated as automatic grounds for `insufficient_data`.

### 4.7 Factors and Explanations (D8)
- Factors represent factual data-quality/context conditions or verified contributions from an accepted explanation method.
- `increases_risk` / `decreases_risk` signifies mathematical contribution to the assessment, **NOT** biological causation. Without verified directional contribution, `effect = unknown`.
- Empty factor output (`factors = []`) is fully valid until a formal explanation mechanism is integrated.

### 4.8 Recommendations and Actions (D9)
- Current accepted policy mandates: `recommendation = null`.
- No intervention efficacy, prevented loss, or financial savings claims are authorized.

### 4.9 Telemetry Scope (D10)
- Telemetry remains in canonical input semantics. However, weak incremental predictive lift means telemetry is not proven to provide material production benefit under tested representations.

---

## 5. Separation of Ranking Semantics from Concrete Operator Triage Workflow

A critical epistemic distinction exists between mathematical ranking semantics and operational workflow:

```
+-------------------------------------------------------------+
| DECISION (ADR 0003 D3)                                      |
| - Ranking order: risk.score DESC, batch_id ASC             |
| - Isolation: single engine_tier + engine_version            |
| - Unassessed: segregated, never zero-risk                  |
+-------------------------------------------------------------+
                              |
                              v  (Operational Translation)
+-------------------------------------------------------------+
| RECOMMENDATION / UNKNOWN (APR-01 Steps 6–8)                 |
| - Candidate Persona: Dispatch Supervisor / Ramp Inspector   |
| - Operator Authority: D1–D4 decision framework              |
| - Queue Review Capacity: K=10 or K=50 evaluation metrics    |
|   are NOT operator quotas                                   |
| - Fallback Routing: unassessed batch routing unresolved     |
+-------------------------------------------------------------+
```

### 5.1 Accepted Ranking Semantics (DECISION)
Mathematical ordering within an evaluation or single-engine context is established: `risk.score DESC`, `batch_id ASC`.

### 5.2 Concrete Operator Triage Queue (RECOMMENDATION / UNKNOWN)
APR-01 Steps 6–8 provide a thorough research synthesis for operator workflow, but explicitly preserve the following as non-canonical:
- **Target Persona:** `Dispatch Supervisor / Ramp Quality Inspector` is a strong research candidate, but the final persona remains an open team decision.
- **Review Capacity & Quotas:** Benchmark metrics K=10 and K=50 are analytical probes, **NOT** operator throughput quotas. The number of batches an operator can inspect before transport dispatch is contract-dependent and unknown.
- **Operational Authority:** The candidate D1–D4 decisions (Release/Hold, Pre-cooling, Transport Verification, Route Alignment) and candidate action classes 1–5 are research options, not accepted software-dispatched recommendations.
- **Fallback Queue Routing:** Routing for `insufficient_data` batches (e.g. secondary inspection, manual hold) is not defined by repository decisions.

**UX Constraint:** Future UI layouts must remain functional and truthfully presented regardless of whether the final operator is a ramp inspector, cold-store technologist, or facility manager.

---

## 6. Empirical Evidence Reconciliation: VDR-03, VDR-04A & VDR-04B

### 6.1 VDR-03 (Target & Horizon Feasibility)
- **VDR-03 Horizon Feasibility:** Exact biological deterioration onset and continuous/coarse deterioration horizon are unsupported by the supplied checkpoint observations.

### 6.2 VDR-04A (Dispatch Predictability Benchmark)
- **Primary Operational Task:** Dispatch-time prediction/ranking feasibility and continuous-loss benchmark evidence; ranking lift is demonstrated and strongest when planned logistics are present. Non-logistics ranking remains protocol/model-dependent.
- **Continuous Point Prediction:** Demonstrates limited, context-specific lift over crop-median baseline.
- **Planned Logistics:** Feature family providing the strongest consistent incremental predictive association.

### 6.3 VDR-04B (Telemetry Marginal Value Ablation)
VDR-04B directly evaluated the marginal value of pre-dispatch storage telemetry under planned logistics ($C+L \to C+T+L$):
- **Observed Result:** Under tested aggregate telemetry representations and fixed model configurations, adding telemetry to context and logistics did **NOT** produce stable marginal lift:
  - In Protocol P2 (Chamber-Time Grouped OOF), $C+T+L$ degraded relative to $C+L$ across all 5 folds for $R^2$ and Spearman correlation, and in 4 of 5 folds for MAE and NDCG@10.
  - In Protocol P1 (Forward Inter-Season), adding telemetry showed small positive deltas on selected ranking metrics, but slightly degraded continuous-loss metrics.
- **Negative Epistemic Boundaries:** This finding does **NOT** prove that telemetry is biologically irrelevant or that telemetry should be removed from canonical inputs (ADR 0003 D10 retains telemetry).
- **UX Implication:** Pre-dispatch telemetry charts are an **optional observed context** surface. They must **NOT** be presented as the primary explanatory driver of risk scores or as proven determinants of loss.

---

## 7. Temporal & Data-Lineage Invariants

The predictive UX must strictly adhere to core invariant boundaries:
- **Prediction Moment:** $T_{\text{assess}} \equiv T_{\text{dispatch}} = \text{storage\_sessions.dispatch\_datetime}$.
- **Strict Negative Boundary:** No arrival inspections (`arrival_*`), post-dispatch transit realizations (`actual_departure`, `actual_delay_minutes`, `cold_chain_incident`), or historical outcomes (`quality_status`, `loss_fraction_pct`, `economic_loss_eur`) may ever enter inference, explanation, or dispatch-time views.
- **Logistics Boundary:** Pre-dispatch planned logistics (`destination_market`, `vehicle_type`, `planned_duration_hours`) are distinct from realized transit execution.
- **Telemetry Lineage:** Telemetry must preserve relational lineage:
  `batch -> storage_session -> storage_zone -> sensor_readings`.
  Direct sensor-to-batch associations without zone context are prohibited.

---

## 8. Smallest Truthful Future UX Skeleton

The future single-batch and multi-batch UI must be structured to remain truthful across all evidence gates:

```
+-----------------------------------------------------------------------------+
| 1. PROVENANCE & SIMULATION DISCLOSURE BANNER                                |
|    [Notice: Simulation / Deterministic Baseline / Learned Model Version]    |
+-----------------------------------------------------------------------------+
| 2. BATCH CONTEXT METADATA                                                   |
|    Batch ID | Crop Type | Variety | Harvest Date | Facility / Zone | Dispatch|
+-----------------------------------------------------------------------------+
| 3. DATA SUFFICIENCY & DEGRADATION GATE                                      |
|    [If insufficient_data: Reason Codes Chips | Missing Requirements List]   |
+-----------------------------------------------------------------------------+
| 4. ASSESSMENT CARD (Conditional: rendered if status === "assessed")        |
|    - Severity Score: clip(predicted_loss, 0, 100) / 100 [Priority Indicator] |
|    - Score Qualification: "Predicted loss severity for prioritisation"      |
|    - Risk Band: [OMITTED / NULL — no traffic lights or cutoffs]             |
|    - Horizon: "Not estimable from supplied observations"                    |
|    - Reliability State: Unavailable (no synthetic percentages)              |
+-----------------------------------------------------------------------------+
| 5. CONTEXTUAL TELEMETRY OBSERVATIONS (Optional Context)                     |
|    - Pre-dispatch observed telemetry series (T_entry to T_dispatch)         |
|    - Factual readings only; no causal claims, no simulated trajectories     |
+-----------------------------------------------------------------------------+
| 6. EXPLANATORY FACTORS (Conditional: rendered if factors.length > 0)        |
|    - Verified model contribution or data condition                          |
|    - Directional effect: increases_risk / decreases_risk / unknown          |
+-----------------------------------------------------------------------------+
| 7. RECOMMENDATION STATUS                                                    |
|    - Status: "No validated recommendation available"                        |
|    - Current payload: recommendation = null                                 |
+-----------------------------------------------------------------------------+
```

*Recommendation Payload & Review Policy Separation:* Under current ADR 0003 D9 policy, `recommendation = null`, meaning no current recommendation payload or advisory object exists from which a `requires_human_review` field could be rendered. Any future admitted recommendation/action must require human review under ADR 0003 D9.

---

## 9. Implementation Readiness Classification

### 9.1 Ready After Current Contracts
- Backend connectivity and retry flow components (`HomePage.tsx`, `BackendStatus.tsx`).
- Simulation / provenance disclosure banners (`AssessmentCard.tsx`).
- Batch metadata display cards.
- Insufficient-data presentation with `reason_codes` and `missing_requirements` chips.
- Observational pre-dispatch telemetry charts (strictly bounded to $T_{\text{dispatch}}$ with zone lineage).

### 9.2 Wait for Production Analytics & Model Acceptance
- Numeric precision formatting and score display for production engine.
- Production batch inventory and multi-batch API endpoints.
- Feature explanation containers linked to an accepted explanation method.

### 9.3 Wait for Future Decision Gates (VLD / Product Decisions)
- Default queue sort order (operational triage queue vs neutral chronological sorting).
- Risk band categorical thresholds and styling (ADR 0003 D2 policy is currently null).
- Calibrated reliability scoring policy (ADR 0003 D7 policy is currently unavailable/null).
- Cross-tier and cross-version queue comparability validation.

### 9.4 Open Team / Product UNKNOWNs
- Final operator persona and operational decision authority.
- Operational review capacity and triage queue membership rules.
- Permitted action catalogue and fallback routing for degraded batches.

### 9.5 Excluded / Unsupported Under Current MVP Policy
- Continuous deterioration countdown timers and coarse deterioration intervals.
- Real-time GPS and in-transit streaming telemetry feeds.
- Automated monetary loss prevention or ROI calculations.
- Display of historical arrival outcomes at dispatch time.

---

## 10. Explicit Final Reconciliation Synthesis

- **KEEP:**
  - Neutral batch context metadata display (crop, harvest, facility, dispatch time).
  - Explicit missing/partial data handling and degradation states.
  - Provenance and simulation disclosure banners.
  - Deterministic ranking rule (`risk.score DESC, batch_id ASC`) for assessed batches within identical engine versions.
  - Observational pre-dispatch telemetry charts (as optional context, strictly bounded to $T_{\text{dispatch}}$, preserving zone lineage, without causal framing).
- **CHANGE:**
  - Risk score presentation: redefine from uncalibrated float to loss/degradation severity score used strictly for prioritisation; qualify that it does not represent probability or guaranteed loss.
  - AssessmentCard `assessed` branch: eliminate raw decimal precision and premature timestamp fields.
  - Contributing factors: restrict strictly to verified model attribution from accepted explanation methods or factual data conditions; default to `effect = unknown` or `factors = []`.
  - Reliability display: expose factual `reason_codes` and `missing_requirements` alongside `level: unavailable`; prohibit invented numerical confidence percentages.
- **REMOVE:**
  - Continuous deterioration countdown timers and discrete deterioration horizon intervals.
  - Predictive forecast trendlines, deterioration trajectories, and safe-corridor bands.
  - Real-time streaming trackers and in-transit telemetry feeds.
  - Financial savings counters, ROI metrics, and commercial loss claims.
  - Historical arrival outcomes displayed as dispatch-time information.
- **BLOCKED:**
  - Operational Triage Queue as default interface mode (pending team decision on persona, authority, and review capacity).
  - Risk band categorical tags (Low / Moderate / High) and color-coded alert thresholds (blocked by ADR 0003 D2 null policy).
  - Numerical confidence scores (e.g. "94% reliable") (blocked by ADR 0003 D7 unavailable policy).
  - Action recommendations (blocked by ADR 0003 D9 null policy).
  - Unified multi-batch ranking across different engine tiers or versions (blocked by ADR 0003 D3).
- **NEW UX REQUIREMENTS:**
  - The future UI must render `recommendation = null` as explicit absence of validated recommendations rather than fabricating advisory notices.
  - The insufficient-data state must be enhanced to display populated `reason_codes` and `missing_requirements` chips.
  - The UI must visually segregate batches evaluated by different engine tiers or versions to prevent invalid cross-tier ranking comparisons.
