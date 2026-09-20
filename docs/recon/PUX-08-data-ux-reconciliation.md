# PUX-08 — Evidence-Safe UX Reconciliation & Design Readiness Report

**Author:** Denis (`denis100strike`)
**Role:** Frontend / UX / Design specialist
**Repository:** `Slave-of-Skynet/training_agrifood`
**Base Revision:** `70ab2a3ce6f060f9b2b43fcb7fb4ecd284426fdd`
**Inspected Latest Main Revision:** `aa5d40bee8368342e7a6b540278c26416cc89457`
**Target File:** `docs/recon/PUX-08-data-ux-reconciliation.md`
**Status:** DRAFT FOR REVIEW (Targeted Fix-Up)

---

## 1. Executive Summary & Epistemic Boundaries

This document reconciles previous UX proposals (PUX-00 through PUX-07) against the accepted evidence base (VDR-01, VDR-02, VDR-03, VDR-04A, ADR 0002, APR-01 steps 0–5, VLD-R3). 

### Epistemic Classifications Applied:
- **FACT:** Directly verifiable from committed repository code, dataset distributions, or accepted challenge canon.
- **DECISION:** Formally recorded architectural and product rulings (ADR 0001, ADR 0002, VLD-02A).
- **OBSERVED IMPLEMENTATION:** The actual behavior and structure present in current codebase files (`frontend/src/**`, `backend/app/**`).
- **INFERENCE:** Analytical conclusions logically grounded in validated evidence.
- **RECOMMENDATION:** Proposed UI/UX structures and information hierarchy designed to remain resilient across prospective model outcomes.
- **UNKNOWN:** Semantics, policies, or performance thresholds that have not been established or verified.
- **SIMULATION:** Synthetic demo fixtures or mock states that do not represent evaluated production data.

---

## 2. Master Reconciliation Matrix

All data-dependent UX concepts proposed across PUX-00–07 are evaluated on two orthogonal axes:
- **Axis A (Evidence Support):** `SUPPORTED`, `SUPPORTED WITH LIMITATION`, `NOT SUPPORTED`, `UNKNOWN`.
- **Axis B (UX Disposition):** `KEEP`, `CHANGE`, `REMOVE`, `BLOCKED`.

| UX Element | Original PUX Proposal | Current Implementation State | Evidence Support | Disposition | What Is Safe to Show Now | What Must NOT Be Shown | Blocking Evidence / Decision |
|---|---|---|---|---|---|---|---|
| **Batch Overview List** | Multi-batch table showing contextual fields | No implemented multi-batch overview/triage list | `SUPPORTED` | `KEEP` | Neutral list, Batch IDs, crop type, dispatch metadata | Implied risk triage ordering | None for neutral list structure |
| **Risk-Ordered Priority Queue** | Triage queue sorted by risk score | Not implemented | `SUPPORTED WITH LIMITATION` | `BLOCKED` | Neutral list sorted by neutral attributes | Default sorting by risk score | VLD-02B |
| **Risk Score (Numeric / Float)** | Decimal [0.0–1.0] displayed directly | Implemented as raw float in unreachable `assessed` branch | `SUPPORTED WITH LIMITATION` | `CHANGE` | Score display with explicit experimental qualification | Raw probabilities, false precision | VLD-02B |
| **Risk Band (Low / Mod / High)** | Color-coded categorical tags | Schema field exists; thresholds undefined | `UNKNOWN` | `BLOCKED` | Neutral status badges | Hard-coded cut-offs, traffic-light severity | VLD-02B |
| **Confidence Score (Numeric)** | Percentage UI (e.g., "94% reliable") | `Reliability.level` exists; `confidence_score` optional | `UNKNOWN` | `BLOCKED` | Existing coarse `Reliability.level` structure | Numeric confidence UI, raw percentages | Accepted validated interpretation |
| **Deterioration Horizon** | Continuous countdown, hover timestamps | Implemented as `starts_at` in inactive branch | `NOT SUPPORTED` | `REMOVE` | Nullable state | Continuous countdowns, exact minute/hour timestamps | VDR-03 |
| **Contributing Factors** | Environmental drivers | Structured container rendered if populated | `SUPPORTED WITH LIMITATION` | `CHANGE` | Factor presence without directional/causal attribution | Causal phrasing, synthetic factor weights | Predictive factor semantics gated |
| **Recommendations / Actions** | Direct intervention buttons | Single `Recommendation` container in schema | `UNKNOWN` | `BLOCKED` | Render as unavailable/withheld | Prescribed business interventions | Operational action-effect validation |
| **Missing / Partial Data** | Generic warning banner | `insufficient_data` state implemented | `SUPPORTED` | `KEEP` | Generic degradation state | Silent null suppression | None for explicit missing state UI |
| **Historical Comparison** | Final outcomes shown alongside active data | Not implemented | `SUPPORTED WITH LIMITATION` | `REMOVE` | Retrospective/evaluation views only | Available to or explanatory for dispatch-time assessment | Temporal/Lineage Invariants |
| **Financial / Economic Loss** | Predicted EUR savings counter | Not implemented | `NOT SUPPORTED` | `REMOVE` | Offline evaluation baseline economics | Predicted monetary savings, ROI | Absence of causal savings models |
| **Real-Time Streaming Alerts** | Push alerts, live tracking | On-demand health request + single synthetic assessment. No production batch-list or streaming/push infrastructure. | `NOT SUPPORTED` | `REMOVE` | On-demand batch evaluation trigger | Live streaming trackers, simulated live telemetry ticks | Batch architecture decision (ADR 0001) |
| **Charts: Pre-dispatch Telemetry** | Historical observation charts | Not implemented | `SUPPORTED WITH LIMITATION` | `KEEP` | Bounded to T_dispatch, strict session->zone->sensor lineage | Causal or agronomic thresholds | None for strict lineage |
| **Charts: Predictive Forecasts** | Predictive trendlines | Not implemented | `NOT SUPPORTED` | `REMOVE` | None | Deterioration trendlines, future trajectories, safe-corridors | Pending evidence/decisions |

---

## 3. Current Frontend Audit (`frontend/src/**`)

Review of exact current committed client code:

1. **Connection & Status Management (`HomePage.tsx` & `BackendStatus.tsx`):**
   - `HomePage.tsx` orchestrates the loading, unavailable, and retry states.
   - `BackendStatus.tsx` renders the available/connected state ONLY.
2. **Synthetic Fixture / Provenance Indicator (`AssessmentCard.tsx`):**
   - Rendered by `AssessmentCard` from `assessment.provenance.notice`.
   - Current fixture notice text: `SIMULATION / synthetic fixture / not challenge data`.
   - `AssessmentCard` itself does NOT own the loading state.
3. **Assessment Card Branches (`AssessmentCard.tsx`):**
   - **Insufficient Data State:** Handled explicitly, but currently does NOT display `reliability.reason_codes` or `missing_requirements` (though these fields exist in the contract/backend fixture).
   - **Unreachable `assessed` Branch:** Actual assessed fields accessed are `assessment.risk?.score` and `assessment.deterioration_horizon?.starts_at`.

---

## 4. VDR-04A Status and Consequences

The analytical deliverable VDR-04A has been integrated and demonstrates the following:
- **Dispatch-time ranking:** `MEANINGFUL LIFT DEMONSTRATED`. It is the strongest and most consistent ranking, specifically with planned-logistics features.
- **Non-logistics ranking:** Remains protocol/model-dependent.
- **Planned logistics:** Provide the strongest tested incremental predictive association.
- **Telemetry aggregates:** Did NOT demonstrate material incremental lift under the tested construction. (Note: This does not infer telemetry should be removed from canonical input).
- **Continuous point prediction:** Has `LIMITED / CONTEXT-SPECIFIC LIFT`.
- VDR-04A did **NOT** select a production target, production model, production thresholds, UX policy, or establish discrete deterioration-horizon feasibility.

---

## 5. Temporal & Data-Lineage Invariants

The proposed predictive UX must strictly adhere to the following invariants:
- **Assessment Timing:** Operates strictly at `T_assess = T_dispatch`.
- **Evidentiary Boundaries:** Does NOT use arrival QC, actual post-dispatch delay/incidents, realized transit telemetry, or final outcomes as prediction/explanation evidence.
- **Logistics Distinction:** Strictly distinguishes planned logistics (known at dispatch) from realized transport outcomes.
- **Telemetry Association:** When storage telemetry is referenced, it preserves the lineage: `batches <- storage_sessions -> storage_zones -> sensor_readings`. It never implies a direct `batch -> sensor` relationship.

---

## 6. Explicit Final Reconciliation Synthesis

- **KEEP:** 
  - Missing/partial data handling and degradation states.
  - Neutral batch context metadata blocks.
  - Provenance/simulation disclosure banners.
  - Ordinary in-app status/warning/degraded-state alerts.
  - Observed pre-dispatch telemetry charts (strictly bounded to information available by T_dispatch, using accepted storage-session → zone → sensor lineage, without implying causal/agronomic thresholds).
- **CHANGE:** 
  - Risk score numeric display (requires qualification of experimental status once validated).
  - Contributing factors (preserve structured container; show presence without causal attribution).
- **REMOVE:** 
  - Predictive/forecast deterioration trendlines, future trajectories, or safe-corridor charts.
  - Real-time streaming/push/live-tracking alerts.
  - Continuous deterioration countdown timers.
  - Predicted financial/monetary savings and ROI claims.
  - Historical/final outcomes used as information available to, or explanatory evidence for, the dispatch-time assessment.
- **BLOCKED:** 
  - Numeric confidence scores (e.g., "94% reliable") pending accepted validated interpretation (explicitly distinguished from established `Reliability.level`).
  - Risk-Ordered Priority Queue (pending VLD-02B).
  - Risk Band categories (pending VLD-02B).
  - Recommendations/Actions (withhold rendering until accepted action semantics exist).
- **NEW UX REQUIREMENTS:** 
  - Render recommendations as unavailable/withheld rather than trusting arbitrary payload content.
  - The future insufficient-data UI must be capable of exposing/explaining populated `reason_codes` and `missing_requirements` truthfully, while exact user-facing wording/policy may remain a later UX/integration decision.
