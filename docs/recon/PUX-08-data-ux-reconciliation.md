# PUX-08 — Evidence-Safe UX Reconciliation & Design Readiness Report

**Author:** Denis (`denis100strike`)
**Role:** Frontend / UX / Design specialist
**Repository:** `Slave-of-Skynet/training_agrifood`
**Base Revision:** `70ab2a3ce6f060f9b2b43fcb7fb4ecd284426fdd`
**Target File:** `docs/recon/PUX-08-data-ux-reconciliation.md`
**Status:** DRAFT FOR REVIEW

---

## 1. Executive Summary & Epistemic Boundaries

This document reconciles previous UX proposals (PUX-00 through PUX-07) against the accepted evidence base (VDR-01, VDR-02, VDR-03, ADR 0002, APR-01 steps 0–5, VLD-R3). The analytical deliverable VDR-04A remains pending and unavailable.

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

| UX Element | Original PUX Proposal | Current Implementation State | Evidence Support | Disposition | What Is Safe to Show Now | What Must NOT Be Shown | Blocking Evidence / Decision | Blocker Owner | Post-VDR-04A Relevance |
|---|---|---|---|---|---|---|---|---|---|
| **Batch Overview List** | Multi-batch table showing contextual fields and status | Implemented via static/fixture interfaces | `SUPPORTED` | `KEEP` | Neutral list, Batch IDs, crop type, dispatch metadata, facility/zone identifier | Implied risk triage ordering | None for neutral list structure | None | Baseline UI frame |
| **Risk-Ordered Priority Queue** | Triage queue sorted by risk score descending | Not implemented; static list order only | `UNKNOWN` | `BLOCKED` | Neutral list sorted by neutral attributes (dispatch time, batch ID) | Default sorting by risk score or severity band | Demonstration of valid ranking lift and ranking contract | Data Science / VLD-02B | Resolves whether risk triage queue is technically legitimate |
| **Risk Score (Numeric / Float)** | Decimal [0.0–1.0] displayed directly or as progress bar | Implemented as raw float in unreachable `assessed` branch | `SUPPORTED WITH LIMITATION` | `CHANGE` | Score display with explicit qualification of experimental status once validated | Raw uncalibrated probabilities, false precision, unverified percentages | Model calibration, evaluation metric, target definition | VDR-04A / VLD-02B | Establishes statistical validity and display format |
| **Risk Band (Low / Mod / High)** | Color-coded categorical tags (Green/Amber/Red) | Schema field exists; band thresholds undefined | `UNKNOWN` | `BLOCKED` | Neutral status badges or explicit "Pending Assessment" state | Hard-coded cut-offs, traffic-light color severity scales | Threshold policy definition (VLD-02B) | VLD-02B | Defines validated classification boundaries |
| **Deterioration Horizon** | "In 18 hours" continuous countdown, hover timestamps | Implemented as raw timestamp string in inactive branch | `NOT SUPPORTED` | `REMOVE` | Nullable/coarse inspection checkpoint window (if later confirmed) | Continuous countdowns, precise minute/hour arrival timestamps | Rejection of continuous time model (VDR-03) | Integrator / VDR-03 | Continuous countdown permanently forbidden |
| **Contributing Factors** | Environmental drivers (e.g. "Humidity caused +15% loss") | Structured container rendered if populated | `SUPPORTED WITH LIMITATION` | `CHANGE` | Factor presence / sensor association without directional or causal attribution | Causal phrasing ("caused", "resulted in"), synthetic factor weights | Explanatory feature relevance evidence | VDR-04A | Determines valid explanatory factors |
| **Recommendations / Actions** | Direct intervention buttons ("Sell now", "Reroute") | Single `Recommendation` container in schema | `UNKNOWN` | `BLOCKED` | Structured container marked "Human Review Recommended" if payload arrives | Prescribed business interventions, autonomous action dispatch | Operational action-effect validation catalog | APR / Product Lead | Verifies operational efficacy of recommended actions |
| **Reliability / Confidence Score** | Quantitative confidence metric (e.g. "94% reliable") | Fields exist in domain model; logic undefined | `SUPPORTED WITH LIMITATION` | `CHANGE` | Explicit indicators for missing requirements and unavailable status | Invented numerical confidence scores, arbitrary scoring formulas | Reliability policy and sufficiency rules | VLD-02B | Defines formal data sufficiency criteria |
| **Missing / Partial Data Handling** | Generic warning banner | `insufficient_data` state implemented in frontend card | `SUPPORTED` | `KEEP` | Explicit reason codes, list of missing required telemetry channels | Silent null suppression, fabricated zero defaults | None for explicit missing state UI | None | Core robust UX pattern |
| **Historical Outcomes vs Predictions** | Display historical loss alongside prediction | Not implemented in client UI | `NOT SUPPORTED` | `REMOVE` | Retrospective evaluation views clearly separated from operational triage | Historical transit losses displayed as if known prior to dispatch | Target leakage rules (ADR 0002) | Integrator | Prevents retrospective target leakage |
| **Financial / Economic Loss Claims** | Predicted EUR savings counter, prevented loss metrics | Not implemented | `NOT SUPPORTED` | `REMOVE` | Raw historical baseline economics strictly in offline evaluation views | Predicted monetary savings, ROI calculations, commercial claims | Absence of causal savings models (VDR-03) | Product Lead | Monetary savings claims strictly excluded |
| **Real-Time Streaming Alerts** | Push alerts, continuous reefer truck tracking | Batch API request model | `NOT SUPPORTED` | `REMOVE` | On-demand batch evaluation trigger, static update timestamps | Live streaming trackers, simulated live telemetry ticks | Batch architecture decision (ADR 0001) | Architecture | Confirms purely on-demand/batch evaluation |

---

## 3. Current Frontend Audit (`frontend/src/**`)

Review of committed client code:

1. **Connection & Status Management (`BackendStatus.tsx`):**
   - Renders live connectivity states: `Checking...`, `Connected`, `Unavailable`.
   - Contains manual retry button (`handleRetry`), handling backend communication failure gracefully.
2. **Synthetic Fixture / Provenance Indicator (`HomePage.tsx`):**
   - Flags synthetic demo status with `DEMO FIXTURE` / `NON-PRODUCTION ENVIRONMENT`.
   - Complies with simulation transparency requirements.
3. **Assessment Card (`AssessmentCard.tsx`):**
   - **Loading State:** Clean indicator with accessible role announcement.
   - **Insufficient Data State:** Handled explicitly; renders reason codes and missing input fields.
   - **Unreachable `assessed` Branch:** Displays `Risk score: {assessment.risk.score}` as a raw decimal and `Deterioration window starts: {assessment.horizon.window_start}`. This presentation branch contains raw floating numbers and premature timestamp fields that require transformation before production exposure.

---

## 4. Smallest Truthful Future UX Skeleton

The future layout structure must remain resilient against null fields and evolving analytics:

1. **Header & Provenance Banner:**
   - Displays evaluation mode, dataset provenance tag, and simulation disclaimer.
2. **Batch Context Block:**
   - Displays immutable metadata: `batch_id`, crop variety, facility identifier, dispatch timestamp.
3. **Data Quality & Sufficiency Gate:**
   - Evaluates input completeness. Halts at a neutral degraded state displaying explicit reason codes if inputs are missing.
4. **Assessment Slot (Conditional):**
   - Renders status badges. Numeric metrics remain hidden unless explicitly validated by VDR-04A.
5. **Contributing Evidence Slot:**
   - Displays associated telemetry observations without causal claims.
6. **Action Guidance Slot:**
   - Displays operator advisory placeholders flagged for human verification.

---

## 5. VDR-04A Decision-Slot Matrix

| UX Question | What VDR-04A May Resolve | What VDR-04A Cannot Resolve Alone | What VLD-02B Must Decide | Frontend Consequence |
|---|---|---|---|---|
| **Risk Ranking Viability** | Presence of non-random ranking lift on validation sets | Operational utility in real-world triage | Whether to enable priority triage queue as default view | Enables or suppresses priority ordering UI |
| **Risk Thresholds & Bands** | Score distribution and error boundaries | Business tolerance for false positives/negatives | Cut-off values for categorical risk bands | Dictates whether categorical badges are displayed |
| **Feature Signal Relevance** | Statistically significant feature families | Explanatory narrative framing | Approved list of explanatory factor labels | Defines visible contributing factor items |
| **Deterioration Coarseness** | Feasibility of discrete horizon classification | Continuous onset timing (already rejected) | Presentation format of discrete evaluation windows | Controls horizon card visibility |

---

## 6. Implementation Readiness Classification

- **READY AFTER CURRENT CONTRACTS:**
  - Backend connection & error fallback components
  - Simulation/provenance disclosure banners
  - Batch metadata identification cards
  - Missing-data state presentation and reason code chips
- **WAIT FOR VDR-04A:**
  - Risk score numeric precision and formatting
  - Telemetry contribution indicators
  - Ranking feasibility confirmation
- **WAIT FOR VLD-02B:**
  - Default sort order (risk triage vs chronological)
  - Risk band categorical thresholds and semantic styles
  - Sufficiency/reliability policy enforcement
- **NOT CURRENTLY JUSTIFIED / EXCLUDED:**
  - Continuous deterioration countdown timer
  - Real-time GPS/telemetry tracking feeds
  - Automated monetary savings calculations