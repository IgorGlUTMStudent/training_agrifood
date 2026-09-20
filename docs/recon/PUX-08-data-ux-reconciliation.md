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
| **Batch Overview List** | Multi-batch table showing contextual fields and status | No implemented multi-batch overview/triage list; no production batch-list API | `SUPPORTED` | `KEEP` | Neutral list, Batch IDs, crop type, dispatch metadata, facility/zone identifier | Implied risk triage ordering | None for neutral list structure |
| **Risk-Ordered Priority Queue** | Triage queue sorted by risk score descending | Not implemented | `SUPPORTED WITH LIMITATION` | `BLOCKED` | Neutral list sorted by neutral attributes (dispatch time, batch ID) | Default sorting by risk score or severity band | VLD-02B (Operational framing and planned-logistics policy) |
| **Risk Score (Numeric / Float)** | Decimal [0.0–1.0] displayed directly or as progress bar | Implemented as raw float in unreachable `assessed` branch | `SUPPORTED WITH LIMITATION` | `CHANGE` | Score display with explicit qualification of experimental status once validated | Raw uncalibrated probabilities, false precision, unverified percentages | VLD-02B (Model calibration and target definition) |
| **Risk Band (Low / Mod / High)** | Color-coded categorical tags (Green/Amber/Red) | Schema field exists; band thresholds undefined | `UNKNOWN` | `BLOCKED` | Neutral status badges or explicit "Pending Assessment" state | Hard-coded cut-offs, traffic-light color severity scales | VLD-02B (Threshold policy definition) |
| **Deterioration Horizon** | "In 18 hours" continuous countdown, hover timestamps | Implemented as `starts_at` in inactive branch | `NOT SUPPORTED` | `REMOVE` | Nullable state | Continuous countdowns, precise minute/hour arrival timestamps | VDR-03 (Exact continuous onset unsupported); coarse proxy is UNKNOWN/DECISION REQUIRED |
| **Contributing Factors** | Environmental drivers | Structured container rendered if populated | `SUPPORTED WITH LIMITATION` | `CHANGE` | Factor presence (e.g., data-quality factor) without directional/causal attribution | Causal phrasing, synthetic factor weights, telemetry as confirmed risk contributor | Predictive factor semantics remain gated |
| **Recommendations / Actions** | Direct intervention buttons ("Sell now", "Reroute") | Single `Recommendation` container in schema | `UNKNOWN` | `BLOCKED` | Render as unavailable/withheld rather than trusting arbitrary payload | Prescribed business interventions, autonomous action dispatch | Operational action-effect validation catalog |
| **Missing / Partial Data Handling** | Generic warning banner | `insufficient_data` state implemented in frontend card | `SUPPORTED` | `KEEP` | Generic degradation state | Silent null suppression, fabricated zero defaults | None for explicit missing state UI |
| **Financial / Economic Loss Claims** | Predicted EUR savings counter, prevented loss metrics | Not implemented | `NOT SUPPORTED` | `REMOVE` | Raw historical baseline economics strictly in offline evaluation views | Predicted monetary savings, ROI calculations, commercial claims (unsupported) | Absence of causal savings models |
| **Real-Time Streaming Alerts** | Push alerts, continuous reefer truck tracking | Batch API request model | `NOT SUPPORTED` | `REMOVE` | On-demand batch evaluation trigger, static update timestamps | Live streaming trackers, simulated live telemetry ticks | Batch architecture decision (ADR 0001) |
| **Charts & Visualizations** | Predictive trendlines | Not implemented | `NOT SUPPORTED` | `REMOVE` | Historical observation charts in evaluation | Future/forecast trendlines | No time-series prediction evidence |

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
- **CHANGE:** 
  - Risk score numeric display (requires qualification of experimental status once validated).
  - Contributing factors (preserve structured container; show presence without causal attribution).
- **REMOVE:** 
  - Real-time streaming/push/live-tracking alerts (outside MVP scope).
  - Continuous deterioration countdown timers (exact continuous onset unsupported).
  - Predicted financial/monetary savings and ROI claims (unsupported under current evidence).
  - Retrospective/historical outcomes presented alongside active predictions.
- **BLOCKED:** 
  - Risk-Ordered Priority Queue (pending VLD-02B on operational framing/planned-logistics policy).
  - Risk Band categories (pending VLD-02B on threshold policies).
  - Recommendations/Actions (withhold rendering until accepted action semantics exist).
- **NEW UX REQUIREMENTS:** 
  - Render recommendations as unavailable/withheld rather than trusting arbitrary payload content.
  - Ensure insufficient-data UI accommodates `reason_codes` if required by VLD-02B.
