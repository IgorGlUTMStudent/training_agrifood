# PUX Workstream Report — UX, Demo + QA

**Role:** prscr — UX, Demo + QA
**Repository:** https://github.com/Slave-of-Skynet/training_agrifood
**Branch:** `prscr/ux-demo-qa`
**Base SHA:** `20021656028392a420561c6dc2a0f5434835081f`
**Status:** Reconnaissance Analysis Complete (PUX-00 … PUX-07) — NOT CANON. Application implementation blocked pending accepted contracts.
**Governing Workflow:** [`docs/workstreams/prscr-ux-demo-qa.md`](docs/workstreams/prscr-ux-demo-qa.md)
**Date:** 2026-09-18

---

## 1. READ FILES (Repository Reconnaissance Audit)

The following repository files were directly inspected to establish the baseline and evidentiary claims in this report:

### Canonical Documentation & Governance
1. [`README.md`](README.md) — Foundation scope, prerequisites, run instructions, and non-goals.
2. [`docs/challenge_canon.md`](docs/challenge_canon.md) — Challenge simulation status, 4 required operator outcomes, evaluation criteria, and canon classification rules.
3. [`docs/team_roles.md`](docs/team_roles.md) — Team roster, primary ownership boundaries, and task routing.
4. [`docs/assumptions_unknowns.md`](docs/assumptions_unknowns.md) — Unresolved dataset, agronomic, modeling, and architectural questions.
5. [`docs/data_contract.md`](docs/data_contract.md) — Output contract semantics, `RiskAssessment` invariants, and provenance fields.
6. [`docs/demo_runbook.md`](docs/demo_runbook.md) — Foundation demo procedure and user-visible connection states.
7. [`docs/architecture.md`](docs/architecture.md) — Modular monolith boundaries, batch/on-demand processing constraint, and analytics principles.
8. [`docs/evaluation.md`](docs/evaluation.md) — Sponsor prediction boundary ($T_{assess} = T_{dispatch}$) and leakage avoidance principles.
9. [`docs/domain_rules.md`](docs/domain_rules.md) — Guardrails against unvalidated agronomic rules and candidate review register.
10. [`docs/decisions/0001-foundation-architecture.md`](docs/decisions/0001-foundation-architecture.md) — Accepted ADR for React + FastAPI foundation.
11. [`docs/integration_contract.md`](docs/integration_contract.md) — Cross-workstream dependencies, STOP conditions, and draft contract boundaries.

### Reconnaissance & Evidence Reports
12. [`docs/data_recon/01_dataset_inventory.md`](docs/data_recon/01_dataset_inventory.md) — Physical schema, relational integrity, row counts, and telemetry truncation defect.
13. [`docs/recon/IGR-01-technical-recon.md`](docs/recon/IGR-01-technical-recon.md) — Backend technical reconnaissance and integration readiness.

### Sponsor Materials (Simulation / Training Pack)
14. [`sponsor_pack/README.md`](sponsor_pack/README.md) — Dataset description, relational topology, coordinate units, and temporal semantics.
15. [`sponsor_pack/brief/Training Challenge #3 — AgriFood.md`](sponsor_pack/brief/Training%20Challenge%20%233%20%E2%80%94%20AgriFood.md) — Problem statement and operator objectives.
16. [`sponsor_pack/data/data_dictionary.xlsx`](sponsor_pack/data/data_dictionary.xlsx) — Declared column types and nullability rules.
17. CSV headers for all 8 tables in `sponsor_pack/data/` (`facilities.csv`, `storage_zones.csv`, `batches.csv`, `storage_sessions.csv`, `sensor_readings.csv`, `quality_checks.csv`, `shipments.csv`, `historical_quality_outcomes.csv`).

### Frontend Codebase
18. [`frontend/package.json`](frontend/package.json) — Dependencies (React 18.3, TypeScript 5.7, Vite 8.3).
19. [`frontend/src/main.tsx`](frontend/src/main.tsx) — Entry point rendering `HomePage`.
20. [`frontend/src/styles.css`](frontend/src/styles.css) — Layout styling and visual tokens.
21. [`frontend/src/pages/HomePage.tsx`](frontend/src/pages/HomePage.tsx) — Connection state machine (`loading`, `available`, `unavailable`), retry handler, and layout.
22. [`frontend/src/components/BackendStatus.tsx`](frontend/src/components/BackendStatus.tsx) — Service connection status and analytics indicator.
23. [`frontend/src/components/AssessmentCard.tsx`](frontend/src/components/AssessmentCard.tsx) — Synthetic assessment card rendering `insufficient_data` state, factors, and reliability.
24. [`frontend/src/api/client.ts`](frontend/src/api/client.ts) — HTTP client fetching `/api/v1/health` and `/api/v1/demo/assessment`.
25. [`frontend/src/api/contracts.ts`](frontend/src/api/contracts.ts) — TypeScript interfaces matching backend contracts.

### Backend Codebase & Tests
26. [`backend/app/main.py`](backend/app/main.py) — FastAPI app definition and CORS setup.
27. [`backend/app/api/routes.py`](backend/app/api/routes.py) — Routes for `/api/v1/health` and `/api/v1/demo/assessment`.
28. [`backend/app/domain/assessment.py`](backend/app/domain/assessment.py) — Pydantic models and validation invariants for `RiskAssessment`.
29. [`backend/app/services/demo_assessment.py`](backend/app/services/demo_assessment.py) — Static synthetic fixture builder.
30. [`backend/tests/test_api.py`](backend/tests/test_api.py) — Endpoint status tests.
31. [`backend/tests/test_contract.py`](backend/tests/test_contract.py) — Pydantic invariant tests (forbidding risk/horizon when `insufficient_data`).

---

## 2. Current Committed Product State (PUX-00)

* **[SIMULATION / FACT] Simulation Context:** Smart Harvest is a simulated training challenge prototype for post-harvest decision support, not an active commercial deployment ([`docs/challenge_canon.md`](docs/challenge_canon.md#L3-L6)).
* **[FACT] Architecture & Foundation:** The committed repository implements a minimal vertical architectural trunk consisting of a React + TypeScript + Vite frontend and a Python + FastAPI + Pydantic backend ([`docs/architecture.md`](docs/architecture.md#L3-L7), [`docs/decisions/0001-foundation-architecture.md`](docs/decisions/0001-foundation-architecture.md#L10-L15)).
* **[FACT] Implemented Endpoints:** Exactly two HTTP `GET` endpoints exist in the application ([`backend/app/api/routes.py`](backend/app/api/routes.py#L11-L24)):
  * `GET /api/v1/health`: Returns service health metadata (`status: "ok"`, `service: "smart-harvest"`, `analytics: "not_configured"`).
  * `GET /api/v1/demo/assessment`: Returns a static synthetic fixture marked with `notice: "SIMULATION / synthetic fixture / not challenge data"` and `status: "insufficient_data"` ([`backend/app/services/demo_assessment.py`](backend/app/services/demo_assessment.py#L16-L49)).
* **[FACT] User-Visible States:** The frontend currently renders three live connection states and handles one hypothetical state ([`frontend/src/pages/HomePage.tsx`](frontend/src/pages/HomePage.tsx#L8-L12,L52-L80)):
  1. `loading`: Animated spinner with `Connecting…` text.
  2. `available`: Displays `BackendStatus` ("Connected", "Analytics: not configured") and `AssessmentCard` ("Insufficient data", no risk score, no horizon, reliability: unavailable).
  3. `unavailable`: Displays error panel ("Unavailable — Failed to reach API") with an interactive `Try again` button.
  4. `assessed` (coded in component, but not returned by current fixture): displays score and deterioration window ([`frontend/src/components/AssessmentCard.tsx`](frontend/src/components/AssessmentCard.tsx#L25-L32)).
* **[FACT] Missing Application Layers:** No implemented batch-inventory API/UI or multi-batch operator workflow exists; no production dataset ingestion pipeline, risk formulas, ML models, database persistence, or agronomic rules are implemented ([`README.md`](README.md#L13-L16), [`docs/architecture.md`](docs/architecture.md#L65-L68)).
* **[SIMULATION / FACT] Sponsor Data Scale vs. Coverage:** The sponsor pack describes coverage as "2024–2025 Agricultural Harvest & Storage Seasons" ([`sponsor_pack/README.md`](sponsor_pack/README.md#L4)). However, direct measurement shows that storage sessions extend into 2026 (storage entry spans 2024-05-20 to dispatch on 2026-04-03) across 1,800 batches, 10 facilities, and 25 storage zones ([`docs/data_recon/01_dataset_inventory.md`](docs/data_recon/01_dataset_inventory.md#L8-L15)).
* **[SIMULATION / FACT] Telemetry Truncation Defect:** Environmental sensor readings terminate abruptly on `2025-12-31 23:30:00`. Consequently, 204 batches (11.33% of all batches) that remain in cold storage into 2026 have zero telemetry for up to 92.5 days prior to their dispatch date ([`docs/data_recon/01_dataset_inventory.md`](docs/data_recon/01_dataset_inventory.md#L18-L20)).
* **[FACT] Known Output Contract & Invariants:** Pydantic and TypeScript contracts enforce that if `status == "insufficient_data"`, `risk` and `deterioration_horizon` **must** both be `null`. An `assessed` status strictly requires a non-null `risk` object with `score` in $[0.0, 1.0]$ ([`backend/app/domain/assessment.py`](backend/app/domain/assessment.py#L120-L129), [`docs/data_contract.md`](docs/data_contract.md#L9-L15)).
* **[FACT] Prediction Temporal Boundary:** Assessment occurs at dispatch ($T_{assess} = T_{dispatch}$). Inadmissible retrospective information (in-transit telemetry, actual delays, transit incidents, destination arrival inspection, and final commercial outcome) is **strictly forbidden** as predictive input or explanation evidence ([`sponsor_pack/README.md`](sponsor_pack/README.md#L40-L51), [`docs/challenge_canon.md`](docs/challenge_canon.md#L11), [`docs/evaluation.md`](docs/evaluation.md#L7-L12)).

---

## 3. UX Facts, Decisions, and Unknowns (PUX-01)

### A. Facts
1. **[FACT] Four Core Operator Outcomes:** The product must help an operator understand: (1) which batches are most at risk, (2) when product quality may begin to deteriorate, (3) what factors contribute to the risk, and (4) what action should be prioritized ([`sponsor_pack/brief/Training Challenge #3 — AgriFood.md`](sponsor_pack/brief/Training%20Challenge%20%233%20%E2%80%94%20AgriFood.md#L15-L20)).
2. **[FACT] Eligible Dispatch-Time Information:** Metadata, pre-dispatch quality checks, cold-storage telemetry up to $T_{dispatch}$, and planned transport logistics ([`sponsor_pack/README.md`](sponsor_pack/README.md#L44), [`docs/evaluation.md`](docs/evaluation.md#L8)).
3. **[FACT] No Validated Agronomic Rules:** Zero approved temperature thresholds, humidity safety limits, or intervention effect tables exist in the repository ([`docs/domain_rules.md`](docs/domain_rules.md#L5-L8)).

### B. Existing Team Decisions
1. **[DECISION] Architecture:** Modular monolith (React + TypeScript + Vite frontend; Python + FastAPI + Pydantic backend) ([`docs/decisions/0001-foundation-architecture.md`](docs/decisions/0001-foundation-architecture.md#L10-L15)).
2. **[DECISION] Batch/On-Demand Processing:** Real-time sensor streaming, WebSockets, and background queues are excluded from MVP ([`docs/architecture.md`](docs/architecture.md#L60-L62)).
3. **[DECISION] Baseline First:** Deterministic baseline is mandatory before any ML model ([`docs/architecture.md`](docs/architecture.md#L50-L53)).
4. **[DECISION] LLM Excluded from Numeric & Decision Path:** LLMs cannot generate scores, factors, dates, or actions ([`docs/architecture.md`](docs/architecture.md#L56)).
5. **[DECISION] Structured, Typed Explanations & Recommendations:** Factors and actions require stable codes, human-readable summaries, and explicit review flags (`requires_human_review: true`) ([`docs/data_contract.md`](docs/data_contract.md#L29-L36)).
6. **[DECISION] Explicit Degradation:** Unusable or missing data must degrade to `insufficient_data` or explicit reliability levels rather than fabricating precision ([`docs/data_contract.md`](docs/data_contract.md#L37-L40)).

### C. Things the UI Must NOT Claim Yet
1. **[MUST NOT CLAIM] Agronomic Thresholds:** Must NOT hardcode safety limits (e.g. "Safe temperature is 0–4°C") without validated domain evidence.
2. **[MUST NOT CLAIM] Retrospective Data as Prediction Evidence:** Must NOT show arrival inspection, actual transit delay, or final financial loss as explanatory reasons for a dispatch-time prediction.
3. **[MUST NOT CLAIM] Specific Unvalidated Actions:** Must NOT prescribe actions (e.g. "Reroute to local market to save €1,200") without an accepted action catalog.
4. **[MUST NOT CLAIM] False Precision:** Must NOT display spurious decimal percentages or fake countdown clocks during `insufficient_data` states.
5. **[MUST NOT CLAIM] Food Loss Reduction:** Must NOT claim the solution "reduces food loss by X%" without hold-out evaluation evidence.
6. **[MUST NOT CLAIM] Real-time Streaming:** Must NOT display blinking live radar indicators implying active telemetry streaming.

---

## 4. Complete Research Question Appendix (PUX-02)

Every question required to establish the operational interface is recorded below. Note: Questions where the provisional wireframe can proceed using semantic placeholders are classified as blocking `BEFORE IMPLEMENTATION` rather than `BEFORE WIREFRAME`.

### Group 1: Operator / User Workflow
* **Q1.1:** Who is the primary operator interacting with Smart Harvest at $T_{dispatch}$, and what is their immediate job duty?
  * *Why UX needs it:* Determines layout density, vocabulary, and primary call to action.
  * *Owner:* PRODUCT (Alisa) | *Blocking Stage:* BEFORE WIREFRAME | *Status:* UNKNOWN
* **Q1.2:** What operational trigger brings the operator to this screen?
  * *Why UX needs it:* Dictates whether the interface acts as a mandatory dispatch gate or an ambient exception monitor.
  * *Owner:* PRODUCT (Alisa) | *Blocking Stage:* BEFORE WIREFRAME | *Status:* UNKNOWN
* **Q1.3:** Does the system record operator confirmation / log overrides, or is it purely read-only advisory?
  * *Why UX needs it:* Determines whether interactive action buttons require stateful audit persistence.
  * *Owner:* PRODUCT / TECHNICAL (Alisa / Igor) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN

### Group 2: Batch Prioritization
* **Q2.1:** By what explicit metric or rule should batches be ranked on the overview screen?
  * *Why UX needs it:* Defines default table sorting logic.
  * *Owner:* DATA / PRODUCT (Viktor / Alisa) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN
* **Q2.2:** Should batch prioritization emphasize financial loss (EUR) or physical quality degradation?
  * *Why UX needs it:* Dictates column visual prominence in master table.
  * *Owner:* PRODUCT / DATA (Alisa / Viktor) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN
* **Q2.3:** Is prioritization scoped per facility/chamber or across all 10 facilities simultaneously?
  * *Why UX needs it:* Governs facility filter bar component structure.
  * *Owner:* PRODUCT (Alisa) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN

### Group 3: Risk Communication
* **Q3.1:** What exact visual and numerical format should be used to display `RiskEstimate.score`?
  * *Why UX needs it:* Determines whether to render a percentage, decimal, or categorical badge.
  * *Owner:* PRODUCT / UX (Alisa / prscr) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN (PROVISIONAL RECOMMENDATION: RiskBand chip + score)
* **Q3.2:** What are the validated numerical cut-offs for `RiskBand` (`low`, `moderate`, `high`)?
  * *Why UX needs it:* Required to assign semantic color tokens without arbitrary frontend guessing.
  * *Owner:* DATA / DOMAIN RESEARCH (Viktor) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN
* **Q3.3:** How should uncertainty or low confidence be visually communicated alongside the score?
  * *Why UX needs it:* Prevents operator over-reliance when telemetry is sparse.
  * *Owner:* UX / DATA (prscr / Viktor) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* PARTIAL (Supported by `Reliability` model)

### Group 4: Deterioration Timing Communication
* **Q4.1:** What does `DeteriorationHorizon.starts_at` semantically represent?
  * *Why UX needs it:* Informs timeline labeling (e.g. "Quality degradation expected by [Date]").
  * *Owner:* DATA / PRODUCT (Viktor / Alisa) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN
* **Q4.2:** Can the analytics engine calculate a deterioration horizon for all crop types, or will it frequently be `null`?
  * *Why UX needs it:* If `null` for certain crops, the layout must handle missing horizon cleanly.
  * *Owner:* DATA (Viktor) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN
* **Q4.3:** Should deterioration timing display as a relative countdown ("in 18 hours") or absolute timestamp (`YYYY-MM-DD HH:mm`)?
  * *Why UX needs it:* Determines formatting logic and layout width.
  * *Owner:* UX / PRODUCT (prscr / Alisa) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN (PROVISIONAL RECOMMENDATION: Relative countdown with absolute hover tooltip)

### Group 5: Explainability / Contributing Factors
* **Q5.1:** What specific categories and codes of factors will the analytics engine generate in `AssessmentFactor`?
  * *Why UX needs it:* Dictates factor chip styling and badge grouping.
  * *Owner:* DATA (Viktor) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN
* **Q5.2:** How should evidence references (`evidence_references`) be linked to visual evidence in UI?
  * *Why UX needs it:* Determines whether clicking a factor highlights an excursion on a chart.
  * *Owner:* UX / TECHNICAL (prscr / Igor) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN
* **Q5.3:** How many contributing factors will typically be returned per assessed batch?
  * *Why UX needs it:* Affects vertical height and card layout dimensions.
  * *Owner:* DATA (Viktor) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN

### Group 6: Recommended Actions
* **Q6.1:** What is the discrete catalog of operational actions (`action_code` and `label`) that can be recommended?
  * *Why UX needs it:* Needed to design action callouts and buttons.
  * *Owner:* PRODUCT / DOMAIN RESEARCH (Alisa) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN
* **Q6.2:** What does `requires_human_review: true` require the operator to see or do in the UI?
  * *Why UX needs it:* Determines whether a confirmation dialog or warning notice is rendered.
  * *Owner:* PRODUCT / UX (Alisa / prscr) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* PARTIAL (Contract defaults to `true`)
* **Q6.3:** Can the system calculate expected financial savings (EUR) if the recommended action is executed?
  * *Why UX needs it:* Avoids showing unsubstantiated monetary claims.
  * *Owner:* DATA / PRODUCT (Viktor / Alisa) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN

### Group 7: Inventory / Batch Navigation
* **Q7.1:** What query filters are necessary for the operator on the inventory screen?
  * *Why UX needs it:* Dictates filter bar controls.
  * *Owner:* PRODUCT / UX (Alisa / prscr) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN
* **Q7.2:** How many batches will an operator see in an active session?
  * *Why UX needs it:* Determines whether client-side filtering suffices or server-side pagination is required.
  * *Owner:* PRODUCT / TECHNICAL (Alisa / Igor) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN
* **Q7.3:** Should batch navigation use a Master-Detail split layout or separate URL routing?
  * *Why UX needs it:* Foundational frontend routing structure.
  * *Owner:* UX (prscr) | *Blocking Stage:* BEFORE WIREFRAME | *Status:* PROVISIONAL RECOMMENDATION: Master-Detail single view

### Group 8: Loading / Missing-Data / Insufficient-Data Behaviour
* **Q8.1:** How should batches with truncated telemetry (204 batches in 2026) appear in the inventory list?
  * *Why UX needs it:* Determines whether they are flagged with a warning chip or omitted from triage.
  * *Owner:* PRODUCT / DATA (Alisa / Viktor) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN
* **Q8.2:** When assessment returns `insufficient_data`, what exact user-facing explanation should display?
  * *Why UX needs it:* Must translate `reason_codes` and `missing_requirements` into plain language.
  * *Owner:* UX / DATA (prscr / Viktor) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* PARTIAL (Supported in contract)
* **Q8.3:** Should the UI provide skeleton loaders or inline spinners during API fetches?
  * *Why UX needs it:* Prevents layout shifts during demo transitions.
  * *Owner:* UX (prscr) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* PROVISIONAL RECOMMENDATION: Skeletons

### Group 9: Error and Degraded States
* **Q9.1:** How should the UI respond if the backend returns HTTP 500 on batch list vs single batch?
  * *Why UX needs it:* Determines full-page error boundary vs inline panel alert.
  * *Owner:* UX / TECHNICAL (prscr / Igor) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* PARTIAL (Full page error implemented in foundation)
* **Q9.2:** If telemetry exists but pre-dispatch physical inspection is missing, does it degrade to `insufficient_data` or `reliability: low`?
  * *Why UX needs it:* Dictates visual card state.
  * *Owner:* DATA / INTEGRATOR (Viktor / Vladimir) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN

### Group 10: Demo Comprehension
* **Q10.1:** What specific batch ID and facility will anchor the live pitch demo?
  * *Why UX needs it:* Identifies the showcase record for testing.
  * *Owner:* PRODUCT / UX (Alisa / prscr) | *Blocking Stage:* BEFORE DEMO | *Status:* UNKNOWN
* **Q10.2:** Can an evaluator understand the product value within 5 seconds of looking at the screen?
  * *Why UX needs it:* Dictates prominent headline metric placement.
  * *Owner:* UX / PRODUCT (prscr / Alisa) | *Blocking Stage:* BEFORE WIREFRAME | *Status:* PROVISIONAL RECOMMENDATION: Top aggregate summary bar
* **Q10.3:** How should the presenter toggle between an actionable high-risk batch and an insufficient-data batch?
  * *Why UX needs it:* Eliminates manual searching during a 3-minute pitch.
  * *Owner:* UX (prscr) | *Blocking Stage:* BEFORE DEMO | *Status:* PROVISIONAL RECOMMENDATION: 1-click simulation demo switcher

### Group 11: Accessibility and Visual Hierarchy
* **Q11.1:** Are color-blind safe palettes (accessible alternatives) required for risk bands?
  * *Why UX needs it:* Color cannot be the sole conveyor of risk (WCAG AA).
  * *Owner:* UX (prscr) | *Blocking Stage:* BEFORE WIREFRAME | *Status:* PROVISIONAL RECOMMENDATION: Always pair color with text badge and icon
* **Q11.2:** What typography and row density hierarchy best supports 1080p scanning?
  * *Why UX needs it:* Informs CSS design tokens.
  * *Owner:* UX (prscr) | *Blocking Stage:* BEFORE IMPLEMENTATION | *Status:* UNKNOWN

### Group 12: Mobile / Laptop Constraints
* **Q12.1:** What screen resolution will be used during the presentation?
  * *Why UX needs it:* Prevents horizontal scrolling or cut-off cards.
  * *Owner:* PRODUCT / UX (Alisa / prscr) | *Blocking Stage:* BEFORE DEMO | *Status:* UNKNOWN (Targeting 1920×1080 and 1440×900)
* **Q12.2:** Is a dedicated mobile viewport required for evaluation, or is laptop/desktop sufficient?
  * *Why UX needs it:* Governs responsive design investment.
  * *Owner:* PRODUCT (Alisa) | *Blocking Stage:* BEFORE WIREFRAME | *Status:* UNKNOWN (PROVISIONAL RECOMMENDATION: Desktop-first, responsive single-column collapse)

### Group 13: Trust and Avoiding False Precision
* **Q13.1:** How do we guarantee the UI never renders fabricated numbers when inputs are missing?
  * *Why UX needs it:* Core contract integrity requirement.
  * *Owner:* UX / TECHNICAL (prscr / Igor) | *Blocking Stage:* NOW | *Status:* KNOWN / ENFORCED (Enforced by Pydantic validator & tests)
* **Q13.2:** How should provenance, engine version, and simulation notices be placed?
  * *Why UX needs it:* Required for challenge honesty without obstructing operations.
  * *Owner:* UX (prscr) | *Blocking Stage:* BEFORE WIREFRAME | *Status:* PROVISIONAL RECOMMENDATION: Subtle footer strip

### Group 14: QA and Failure Scenarios
* **Q14.1:** What automated end-to-end test coverage is required before demo freeze?
  * *Why UX needs it:* Protects against presentation-day regressions.
  * *Owner:* TECHNICAL / UX (Igor / prscr) | *Blocking Stage:* BEFORE DEMO | *Status:* UNKNOWN
* **Q14.2:** How does the UI handle an empty batch list (0 batches pending)?
  * *Why UX needs it:* Requires dedicated empty-state messaging.
  * *Owner:* UX (prscr) | *Blocking Stage:* BEFORE WIREFRAME | *Status:* PROVISIONAL RECOMMENDATION: "No batches scheduled" placeholder

---

## 5. External UX Pattern Research (PUX-03)

*Note: This research investigates operational dashboard interaction patterns. It does NOT adopt foreign business logic or infer agricultural thresholds.*

### Source 1: Samsara Connected Operations Platform
* **SOURCE:** Samsara Reefer & Cold Chain Monitoring.
* **LINK:** [samsara.com/products/temperature-environmental-monitoring](https://www.samsara.com/products/temperature-environmental-monitoring)
* **WHAT THE PRODUCT DOES:** Real-time temperature, humidity, and reefer diagnostic monitoring across transport compartments.
* **OBSERVED UX PATTERN:**
  * *[OBSERVED PRACTICE]* Excursion duration banners (e.g. "Excursion: 2h 15m above setpoint").
  * *[OBSERVED PRACTICE]* Telemetry charts with shaded safe corridor; excursions spike outside the shaded band.
  * *[OBSERVED PRACTICE]* Direct two-way remote setpoint control.
* **WHY IT MAY BE RELEVANT:**
  * *[RECOMMENDATION]* Shaded corridor visual on telemetry charts explains *why* an `AssessmentFactor` was triggered without mental calculation.
* **LIMITATIONS:** Samsara is an active IoT fleet telematics tool with 2-way machine control, whereas Smart Harvest is a pre-dispatch decision-support tool.

### Source 2: Sensitech SensiWatch Platform
* **SOURCE:** Sensitech SensiWatch (ColdWatch / TempTale logistics quality platform).
* **LINK:** [sensitech.com/en/products/software/sensiwatch-platform](https://www.sensitech.com/en/products/software/sensiwatch-platform)
* **WHAT THE PRODUCT DOES:** Tracks perishable food and pharma shipments, validating cold-chain compliance for custody transfer decisions.
* **OBSERVED UX PATTERN:**
  * *[OBSERVED PRACTICE]* Status chip for decision gate: "Released", "Under Review", "Quarantine Required".
  * *[OBSERVED PRACTICE]* Cumulative exposure metrics: Mean Kinetic Temperature (MKT) and Time Out of Refrigeration (TOR).
* **WHY IT MAY BE RELEVANT:**
  * *[RECOMMENDATION]* Operators need an unambiguous triage status at $T_{dispatch}$ ("Cleared" vs "High Risk / Review Prioritized").
  * *[RECOMMENDATION]* Cumulative exposure summaries (degree-hours) are more digestible than raw sensor tables.
* **LIMITATIONS:** Focuses heavily on retrospective regulatory audit trails and post-transit quarantine, whereas Smart Harvest guides proactive choices before departure.

### Source 3: Controlant Cold Chain as a Service (ChaaS)
* **SOURCE:** Controlant Real-time Visibility & Exception Management.
* **LINK:** [controlant.com/platform/insights](https://www.controlant.com/platform/insights)
* **WHAT THE PRODUCT DOES:** Real-time supply chain monitoring and automated incident escalation for perishables and pharma.
* **OBSERVED UX PATTERN:**
  * *[OBSERVED PRACTICE]* Exception-only triage queue sorted strictly by severity (Critical > Warning > Resolved).
  * *[OBSERVED PRACTICE]* Dedicated contributing-factor / evidence callout box: "Root Cause: Ambient exposure at loading dock".
* **WHY IT MAY BE RELEVANT:**
  * *[RECOMMENDATION]* An "At-Risk Queue" prioritizes batches requiring immediate intervention at the top.
  * *[RECOMMENDATION]* Structured factor cards in `AssessmentFactor` map directly to Controlant's evidence callout pattern.
* **LIMITATIONS:** Tailored for 24/7 pharma control towers; agricultural packhouses operate with leaner dock staff and tighter turnarounds.

### Source 4: Afresh Technologies Fresh Operating System
* **SOURCE:** Afresh Store and Supply Chain Fresh Produce Management.
* **LINK:** [afresh.com/platform](https://www.afresh.com/platform)
* **WHAT THE PRODUCT DOES:** AI-powered replenishment and inventory optimization built for fresh produce with short shelf lives.
* **OBSERVED UX PATTERN:**
  * *[OBSERVED PRACTICE]* Items sorted by remaining commercial freshness window.
  * *[OBSERVED PRACTICE]* Prescriptive next best action with quantities (e.g. "Discount 30% — 15 crates").
  * *[OBSERVED PRACTICE]* Operator override with reason capture.
* **WHY IT MAY BE RELEVANT:**
  * *[RECOMMENDATION]* Supports the 4th challenge objective ("What action should be prioritized?"). The UI should pair risk scores directly with a concrete recommendation block.
* **LIMITATIONS:** Focused on retail store replenishment, whereas Smart Harvest focuses on cold storage chambers and transport dispatch.

### Source 5: FourKites Supply Chain Visibility & Temperature Tracking
* **SOURCE:** FourKites Cold Chain Control Tower.
* **LINK:** [fourkites.com/platform/temperature-tracking](https://www.fourkites.com/platform/temperature-tracking)
* **WHAT THE PRODUCT DOES:** Predictive freight tracking, transit delay tracking, and temperature excursion alerts.
* **OBSERVED UX PATTERN:**
  * *[OBSERVED PRACTICE]* Correlation of route progress against temperature deviation duration.
  * *[OBSERVED PRACTICE]* Explicit data completeness indicators ("Last Ping: 12m ago", "Degraded Telemetry" badge).
* **WHY IT MAY BE RELEVANT:**
  * *[RECOMMENDATION]* For batches with truncated telemetry (2026 gap), an explicit data completeness badge directly supports our `Reliability.level` and `missing_requirements` contracts.
* **LIMITATIONS:** High emphasis on GPS geospatial maps, which is unnecessary noise for dockside dispatch.

### Candidate Patterns / Recommendations (Not Approved Decisions)
1. *[RECOMMENDATION]* Urgency-first master table (exception triage).
2. *[RECOMMENDATION]* Master-Detail split view on desktop.
3. *[RECOMMENDATION]* Semantic risk badges: dual visual cues (color + text + icon) for WCAG AA compliance.
4. *[RECOMMENDATION]* Structured contributing-factor / evidence callout linked to evidence codes.
5. *[RECOMMENDATION]* Prescriptive action card with human-review banner (`requires_human_review: true`).
6. *[RECOMMENDATION]* Data quality / reliability strip reflecting `ReliabilityLevel`.
7. *[RECOMMENDATION]* Relative countdown with absolute timestamp tooltip.
8. *[RECOMMENDATION / SIMULATION]* Stateless demo scenario switcher for presentation reliability.

### Patterns to Avoid
* Full GIS map as primary screen (consumes space without assisting dockside decision).
* Raw telemetry dumps in default operational view (overwhelms operator).
* Blinking "live" indicators (contradicts batch/on-demand architecture).
* False-precision radial gauges (misleading when confidence is uncalibrated).
* Intrusive blocking modals for warnings (slows dispatch throughput).

---

## 6. Provisional Operator Workflow (PUX-04)

*Status: PROVISIONAL UX RECOMMENDATION: Master-Detail Single Screen — NOT AN ACCEPTED ARCHITECTURAL DECISION.*

```text
PROVISIONAL LAYOUT:
[Left Panel: Batch Triage Queue]  -->  [Right Panel: Assessment, Factors & Action Detail]
```

### Primary Flow Steps

#### Step 1: Scan Pending Dispatch Batches (Overview / Triage)
* **USER QUESTION:** *"Which batches currently scheduled for dispatch are most at risk of spoilage or commercial loss?"*
* **SCREEN / STATE:** `[PROVISIONAL] Batch Triage Overview (Master Panel)`
* **INFORMATION REQUIRED:** Batch ID, crop type, scheduled dispatch timestamp, `RiskBand`, urgency ranking. (*Available at $T_{dispatch}$*).
* **USER ACTION:** Operator scans triage queue and clicks on the highest-priority batch flagged as `high` risk.
* **EXPECTED RESULT:** Selected batch is highlighted; right panel loads assessment and contributing factors for this batch.
* **DATA DEPENDENCY:** `PROPOSED / NOT AN ACCEPTED API CONTRACT: GET /api/v1/batches`.
* **CURRENTLY SUPPORTED:** **NO** (Only single synthetic assessment at `GET /api/v1/demo/assessment` exists).

#### Step 2: Understand Risk Severity & Deterioration Horizon
* **USER QUESTION:** *"How severe is the risk for this selected batch, and when is product quality expected to degrade?"*
* **SCREEN / STATE:** `[PROVISIONAL] Batch Detail — Risk & Timing Section (Detail Panel)`
* **INFORMATION REQUIRED:** `batch_id`, `RiskEstimate.score`, `RiskBand`, `DeteriorationHorizon.starts_at`, `Reliability.level`. (*Available at $T_{dispatch}$*).
* **USER ACTION:** Operator reviews risk level and deterioration window against planned transport duration.
* **EXPECTED RESULT:** Operator sees whether produce will survive planned transit.
* **DATA DEPENDENCY:** `RiskAssessment.risk` and `RiskAssessment.deterioration_horizon` contracts.
* **CURRENTLY SUPPORTED:** **PARTIAL** (Contract models exist, but foundation fixture returns `null` because `status == "insufficient_data"`).

#### Step 3: Inspect Contributing Environmental / Storage Factors
* **USER QUESTION:** *"What specific storage or handling conditions contributed to this batch's risk?"*
* **SCREEN / STATE:** `[PROVISIONAL] Batch Detail — Contributing Factors Section (Detail Panel)`
* **INFORMATION REQUIRED:** Array of `AssessmentFactor` (`category`, `effect`, `summary`, `evidence_references`). (*Available at $T_{dispatch}$*).
* **USER ACTION:** Operator reads structured factor summaries (e.g. cumulative degree-hours, condensation).
* **EXPECTED RESULT:** Operator understands contributing conditions without requiring raw sensor analysis.
* **DATA DEPENDENCY:** Analytics engine factor generation; `AssessmentFactor` populated with evidence codes.
* **CURRENTLY SUPPORTED:** **PARTIAL** (Component renders in `AssessmentCard.tsx`, but displays single placeholder factor).

#### Step 4: Evaluate & Acknowledge Recommended Operational Action
* **USER QUESTION:** *"What action should be prioritized right now at the dock to reduce potential loss?"*
* **SCREEN / STATE:** `[PROVISIONAL] Batch Detail — Action Recommendation Section (Detail Panel)`
* **INFORMATION REQUIRED:** `Recommendation.action_code`, `label`, `priority`, `rationale_codes`, `requires_human_review`.
* **USER ACTION:** Operator reviews recommendation and clicks `[PROVISIONAL] "Acknowledge & Apply Intervention"`.
* **EXPECTED RESULT:** Batch status updates to indicate an acknowledged intervention.
* **DATA DEPENDENCY:** Action recommendation engine; agreed action catalog.
* **CURRENTLY SUPPORTED:** **NO** (Contract model exists, but fixture returns `null`; no action buttons exist in UI).

### Failure and Alternative Flows

#### Flow F1: Initial Loading State
* **USER QUESTION:** *"Is the system loading my data?"*
* **SCREEN / STATE:** `ConnectionState: "loading"`
* **INFORMATION REQUIRED:** API response pending.
* **USER ACTION:** Wait for initial fetch.
* **EXPECTED RESULT:** UI displays animated spinner with accessible `aria-live="polite"` text: `Connecting…`.
* **DATA DEPENDENCY:** `/api/v1/health` and `/api/v1/demo/assessment`.
* **CURRENTLY SUPPORTED:** **YES** ([`frontend/src/pages/HomePage.tsx:L52-L60`](frontend/src/pages/HomePage.tsx#L52-L60)).

#### Flow F2: Backend Unavailable / Network Disruption
* **USER QUESTION:** *"Why is data missing, and can I reconnect?"*
* **SCREEN / STATE:** `ConnectionState: "unavailable"`
* **INFORMATION REQUIRED:** HTTP failure or connection rejection error message.
* **USER ACTION:** Operator clicks `Try again` button.
* **EXPECTED RESULT:** Explicit error panel: *"The application could not reach the Smart Harvest API: [Error message]"*. Re-triggers fetch without page reload.
* **DATA DEPENDENCY:** Backend reachability.
* **CURRENTLY SUPPORTED:** **YES** ([`frontend/src/pages/HomePage.tsx:L62-L73`](frontend/src/pages/HomePage.tsx#L62-L73)).

#### Flow F3: Insufficient Data for Batch Assessment
* **USER QUESTION:** *"Why is there no risk percentage or expiration date for this batch?"*
* **SCREEN / STATE:** `AssessmentStatus: "insufficient_data"`
* **INFORMATION REQUIRED:** `Reliability.reason_codes`, `missing_requirements`.
* **USER ACTION:** Operator reads missing requirements; recommendation withheld; human review required.
* **EXPECTED RESULT:** Risk score and deterioration horizon are strictly omitted (`null`). Dedicated panel explains that validated challenge inputs are unavailable.
* **DATA DEPENDENCY:** `RiskAssessment` invariant enforcement.
* **CURRENTLY SUPPORTED:** **YES** ([`frontend/src/components/AssessmentCard.tsx:L17-L24`](frontend/src/components/AssessmentCard.tsx#L17-L24)).

#### Flow F4: Partially Missing Batch Data (e.g. Truncated 2026 Telemetry)
* **USER QUESTION:** *"Can I trust this assessment if recent sensor logs are missing?"*
* **SCREEN / STATE:** `[PROVISIONAL] Degraded Assessment State`
* **INFORMATION REQUIRED:** `Reliability.level: "low"`, reason code indicating missing telemetry window.
* **USER ACTION:** Operator views degraded reliability notice.
* **EXPECTED RESULT:** Risk score displayed alongside prominent warning: *"Assessment based on incomplete storage telemetry."*
* **DATA DEPENDENCY:** `PROPOSED / NOT AN ACCEPTED API CONTRACT`: analytics engine calculation of degraded reliability.
* **CURRENTLY SUPPORTED:** **NO**.

#### Flow F5: Analytics Not Configured
* **USER QUESTION:** *"Is the predictive engine active?"*
* **SCREEN / STATE:** Baseline Foundation State
* **INFORMATION REQUIRED:** `HealthResponse.analytics: "not_configured"`.
* **USER ACTION:** View status badge.
* **EXPECTED RESULT:** Status panel displays `Analytics: not configured`.
* **DATA DEPENDENCY:** `GET /api/v1/health`.
* **CURRENTLY SUPPORTED:** **YES** ([`frontend/src/components/BackendStatus.tsx:L22`](frontend/src/components/BackendStatus.tsx#L22)).

#### Flow F6: No High-Risk Batches Detected
* **USER QUESTION:** *"Are there any exceptions requiring attention today?"*
* **SCREEN / STATE:** `[PROVISIONAL] All Batches Cleared State`
* **INFORMATION REQUIRED:** All active batches have `RiskBand: "low"`.
* **USER ACTION:** Scan empty exception queue.
* **EXPECTED RESULT:** Master panel displays: *"All pending batches cleared under standard transit protocols. No high-risk exceptions detected."*
* **DATA DEPENDENCY:** `PROPOSED / NOT AN ACCEPTED API CONTRACT: GET /api/v1/batches`.
* **CURRENTLY SUPPORTED:** **NO**.

#### Flow F7: Unexpected API Failure on Single Batch Selection
* **USER QUESTION:** *"Why did this batch fail to open, and can I still inspect other batches?"*
* **SCREEN / STATE:** `[PROVISIONAL] Inline Batch Error State`
* **INFORMATION REQUIRED:** HTTP 500 error on single-batch request.
* **USER ACTION:** Click inline `Retry` button on detail card or select another batch.
* **EXPECTED RESULT:** Master list remains interactive; right panel shows inline error card without crashing application.
* **DATA DEPENDENCY:** `PROPOSED / NOT AN ACCEPTED API CONTRACT: GET /api/v1/batches/{id}/assessment`.
* **CURRENTLY SUPPORTED:** **NO** (Only global page error currently exists).

---

## 7. Provisional Wireframe Specification (PUX-05)

*Status: PROVISIONAL SPECIFICATION ONLY — NO CODE IMPLEMENTATION.*
*Uses semantic placeholders (`[RISK INDICATOR]`, `[DETERIORATION HORIZON]`, `[CONTRIBUTING FACTORS]`, `[PRIORITIZED ACTION]`) to avoid fabricating unvalidated values.*

```text
+-------------------------------------------------------------------------------------------------------------+
|  SMART HARVEST  | Facility: [FACILITY SELECTOR] | Analytics: [ENGINE TIER]    [DEMO QUICK SWITCHER: A | B]  |
+-------------------------------------------------------------------------------------------------------------+
|  OPERATIONAL SUMMARY: [TOTAL BATCHES] Pending | [HIGH RISK COUNT] Action Needed | [CLEARED COUNT] Cleared   |
+------------------------------------------------------+------------------------------------------------------+
|  SECTION 1: BATCH TRIAGE QUEUE (MASTER)              |  SECTION 2: BATCH DETAIL & ACTION (DETAIL)           |
|                                                      |                                                      |
|  [Filter: Crop Type v] [Sort: Urgency v]             |  BATCH: [BATCH_ID] | Crop: [CROP] | Variety: [VARIETY]|
|  +-------------------------------------------------+ |  Scheduled Dispatch: [PLANNED DISPATCH DATETIME]     |
|  | [RISK BAND]  [BATCH_ID]  [CROP]  [DESTINATION]  | |  +-------------------------------------------------+ |
|  | > High Risk   BATCH-042   Apple   București     | |  | SECTION 2A: RISK SEVERITY & TIMING              | |
|  |   Moderate    BATCH-019   Plum    Chișinău      | |  | [RISK INDICATOR]           [DETERIORATION HORIZON| |
|  |   Low         BATCH-008   Grape   Iași          | |  | Reliability: [RELIABILITY LEVEL]                | |
|  |   Incomplete  BATCH-104   Apple   Brașov        | |  +-------------------------------------------------+ |
|  +-------------------------------------------------+ |  | SECTION 2B: CONTRIBUTING FACTORS (WHY AT RISK)  | |
|  | [PAGINATION / BATCH COUNT SUMMARY]              | |  | [CONTRIBUTING FACTORS LIST]                         | |
|                                                      |  | - [FACTOR 1: SUMMARY + EVIDENCE CODE]            | |
|                                                      |  | - [FACTOR 2: SUMMARY + EVIDENCE CODE]            | |
|                                                      |  +-------------------------------------------------+ |
|                                                      |  | SECTION 2C: PRIORITIZED ACTION (WHAT TO DO)       | |
|                                                      |  | [PRIORITIZED ACTION CALLOUT]                     | |
|                                                      |  | Priority: [PRIORITY] | Review: [HUMAN SIGN-OFF]   | |
|                                                      |  | [BUTTON: ACKNOWLEDGE & APPLY INTERVENTION]        | |
|                                                      |  +-------------------------------------------------+ |
|                                                      |  | Provenance: [ENGINE VERSION] | [SIMULATION BANNER]|
+------------------------------------------------------+------------------------------------------------------+
```

### Detailed Section Specifications

#### 1. Global Navigation & Summary Bar
* **PURPOSE:** Anchor operational context, provide aggregate triage numbers, and display system health.
* **PRIMARY USER QUESTION:** *"Is the system connected, and how many batches require intervention today?"*
* **INFORMATION HIERARCHY:** (1) Product identity (`Smart Harvest`), (2) Aggregate counters (`[TOTAL BATCHES]`, `[HIGH RISK COUNT]`), (3) Backend status chip (`Connected` / `Unavailable`).
* **PRIMARY ACTION:** Facility selector or Demo Quick Switcher (`Scenario A: Actionable High Risk` vs `Scenario B: Insufficient Data`).
* **SECONDARY INFORMATION:** Engine tier (`fixture` / `deterministic_baseline`), contract version.
* **DATA REQUIRED:** `HealthResponse`, aggregate count of batches by `RiskBand`.
* **EMPTY STATE:** Counter displays `0 Batches Pending`.
* **LOADING STATE:** Pulsing skeleton bars across counters.
* **ERROR STATE:** Red status chip: `Backend Unavailable — Reconnecting…`.
* **INSUFFICIENT-DATA STATE:** Counter displays: `[COUNT] Unassessed / Incomplete`.
* **UNCERTAINTY / EXPLAINABILITY:** Simulation notice displayed in header (`SIMULATION / training challenge`).
* **MOBILE CONSIDERATIONS:** Collapses into sticky top bar; counters stack vertically.
* **DEMO IMPORTANCE:** **CRITICAL** (Establishes 5-second situational awareness).

#### 2. Section A: Batch Triage Queue (Master Panel)
* **PURPOSE:** List all pending dispatch batches sorted strictly by urgency/risk.
* **PRIMARY USER QUESTION:** *"Which batch must I inspect first before clearing dispatch?"*
* **INFORMATION HIERARCHY:** (1) Severity badge (`[RISK BAND]`), (2) Batch ID (`[BATCH_ID]`), (3) Crop type (`[CROP]`), (4) Planned destination and dispatch time.
* **PRIMARY ACTION:** Click row to select and load batch detail.
* **SECONDARY INFORMATION:** Variety, storage chamber ID.
* **DATA REQUIRED:** `PROPOSED / NOT AN ACCEPTED API CONTRACT: GET /api/v1/batches`.
* **EMPTY STATE:** Panel displays: *"No batches currently scheduled for dispatch. [Refresh]"*.
* **LOADING STATE:** 5 skeleton table rows with pulsing placeholders.
* **ERROR STATE:** Inline alert: *"Failed to load batch list. [Retry]"*.
* **INSUFFICIENT-DATA STATE:** Batches with missing pre-dispatch data show an `[INCOMPLETE DATA]` chip and are placed in a review section.
* **UNCERTAINTY / EXPLAINABILITY:** Clear separation between assessed risk tiers and unassessed batches.
* **MOBILE CONSIDERATIONS:** Full-width view; selecting a batch transitions to detail view with back button.
* **DEMO IMPORTANCE:** **CRITICAL** (Answers: *"Which batches are most at risk?"*).

#### 3. Section B: Risk Severity & Deterioration Horizon (Detail Panel — Top)
* **PURPOSE:** Communicate the degree of risk and the expected timeframe before quality degrades.
* **PRIMARY USER QUESTION:** *"How severe is the risk, and when will deterioration begin relative to transit duration?"*
* **INFORMATION HIERARCHY:** (1) `[RISK INDICATOR]`, (2) `[DETERIORATION HORIZON]`, (3) Planned transit comparison, (4) `Reliability.level`.
* **PRIMARY ACTION:** None (informational decision card).
* **SECONDARY INFORMATION:** Confidence score, reason codes if degraded.
* **DATA REQUIRED:** `RiskAssessment.risk`, `RiskAssessment.deterioration_horizon`, `RiskAssessment.reliability`.
* **EMPTY STATE:** Prompts: *"Select a batch from the triage list to view assessment."*
* **LOADING STATE:** Card skeleton with shimmering boxes for risk meter and timeline.
* **ERROR STATE:** Inline alert: *"Failed to calculate risk assessment for this batch. [Retry]"*.
* **INSUFFICIENT-DATA STATE:** Displays neutral notice: *"Insufficient Data for Quantitative Assessment"*. Numeric score and horizon are strictly omitted (`null`). Missing requirements listed.
* **UNCERTAINTY / EXPLAINABILITY:** Explicit display of `Reliability.level`.
* **MOBILE CONSIDERATIONS:** Stacks directly above contributing factors.
* **DEMO IMPORTANCE:** **CRITICAL** (Answers: *"When may quality begin to deteriorate?"*).

#### 4. Section C: Contributing Factors & Causal Evidence (Detail Panel — Middle)
* **PURPOSE:** Explain the physical and environmental storage factors contributing to the risk score.
* **PRIMARY USER QUESTION:** *"What storage or handling factors contributed to this risk alert?"*
* **INFORMATION HIERARCHY:** (1) Category badge (`Environmental`, `Storage`), (2) Impact direction (`[INCREASES RISK]`), (3) Plain language summary: `[FACTOR SUMMARY]`, (4) Evidence reference code: `[EVIDENCE CODE]`.
* **PRIMARY ACTION:** Expand/collapse evidence log snippet.
* **SECONDARY INFORMATION:** Chamber ID, sensor probe references.
* **DATA REQUIRED:** `RiskAssessment.factors` array.
* **EMPTY STATE:** When risk is low: *"No environmental or storage anomalies detected. Parameters remained within target range."*
* **LOADING STATE:** 2–3 shimmering placeholder factor cards.
* **ERROR STATE:** Inline alert: *"Factor explanations unavailable for this batch."*
* **INSUFFICIENT-DATA STATE:** Displays data quality blockers: category `data_quality`, effect `unknown`, explaining what telemetry was missing.
* **UNCERTAINTY / EXPLAINABILITY:** Every factor states whether it increases or decreases risk. Retrospective post-dispatch data is strictly excluded.
* **MOBILE CONSIDERATIONS:** Stacked list of expandable cards.
* **DEMO IMPORTANCE:** **CRITICAL** (Answers: *"What factors contribute to the risk?"*).

#### 5. Section D: Prioritized Action & Intervention (Detail Panel — Bottom)
* **PURPOSE:** Surface the single most effective operational action to mitigate loss before departure.
* **PRIMARY USER QUESTION:** *"What action should I prioritize right now at the dock to avoid loss?"*
* **INFORMATION HIERARCHY:** (1) `[PRIORITIZED ACTION]` headline with action verb, (2) Priority badge (`High`), (3) Rationale bullets, (4) Human review notice (`requires_human_review: true`), (5) Action button: `[BUTTON: ACKNOWLEDGE & APPLY INTERVENTION]`.
* **PRIMARY ACTION:** `[BUTTON: ACKNOWLEDGE & APPLY INTERVENTION]`.
* **SECONDARY INFORMATION:** Operational notes, vehicle assignment link.
* **DATA REQUIRED:** `RiskAssessment.recommendation`.
* **EMPTY STATE:** When risk is low: *"Standard Dispatch Cleared — Proceed with planned carrier and route."*
* **LOADING STATE:** Shimmering action callout box.
* **ERROR STATE:** Inline alert: *"Recommendation engine failed to generate an action."*
* **INSUFFICIENT-DATA STATE:** Recommendation withheld; missing requirements exposed; human review required before clearing dispatch.
* **UNCERTAINTY / EXPLAINABILITY:** Clear disclaimer that recommendations require human operator validation.
* **MOBILE CONSIDERATIONS:** Fixed bottom sticky action bar with action button.
* **DEMO IMPORTANCE:** **CRITICAL** (Answers: *"What action should be prioritized?"*).

### Synthesis & Proposals
* **Minimum Viable Screen Set:** One screen (Master-Detail View).
* **Information Hierarchy:** (1) Urgency Triage (Left) -> (2) Impact & Deadline (Top Right) -> (3) Contributing Factors (Middle Right) -> (4) Prioritized Action (Bottom Right) -> (5) Provenance (Footer).
* **First 5 Seconds Comprehension:** Top summary bar instantly conveys total pending batches and count of high-risk exceptions.
* **After Opening a Batch:** Operator understands why it is at risk, the deterioration deadline vs transit time, and the prioritized intervention.
* **Cut List If Time Becomes Limited:** Remove multi-facility dropdown, remove interactive telemetry charts, remove secondary text search. **Keep:** Master-Detail split view, 4 core outputs, `insufficient_data` and failure handling.

---

## 8. Demo Story (PUX-06)

### A. Currently Demonstrable (Today's Repository State)
* **Live Functional Capabilities:**
  1. Frontend boots and displays `BackendStatus: Connected` and `Service: smart-harvest` ([`frontend/src/components/BackendStatus.tsx`](frontend/src/components/BackendStatus.tsx#L14-L24)).
  2. Frontend renders `AssessmentCard` for `synthetic-batch-001` with `status: "insufficient_data"`, displaying `notice: "SIMULATION / synthetic fixture / not challenge data"` and withholding risk percentages and deterioration dates ([`frontend/src/components/AssessmentCard.tsx`](frontend/src/components/AssessmentCard.tsx#L12-L24)).
  3. Killing backend triggers error panel (`Unavailable`) with working `Try again` recovery button ([`frontend/src/pages/HomePage.tsx`](frontend/src/pages/HomePage.tsx#L62-L73)).
* **Explicit Foundation Boundary:** The current foundation does **not** possess a high-risk batch, valid deterioration horizon, validated contributing factors, or validated operational recommendations.

### B. Target Demo (After Analytics Integration)
The target demo communicates this causal narrative:
```text
COLD-STORAGE TELEMETRY + HARVEST METADATA
  --> RISK DETECTED AT T_dispatch
  --> PRIORITIZED BATCH SURFACED AT TOP OF QUEUE
  --> CONTRIBUTING FACTORS EXPLAINED (STORAGE ANOMALIES)
  --> DETERIORATION HORIZON COMPARED TO PLANNED TRANSIT
  --> OPERATIONAL INTERVENTION PRIORITIZED (HUMAN SIGN-OFF)
  --> LOSS PREVENTED BEFORE DEPARTURE
```

### Core Demo Flow (3 Minutes)
* **0:00–0:30 (Situational Awareness):** Presenter opens dashboard on a 1080p screen. Points to top summary bar: *35 Batches Scheduled for Dispatch Today — 2 Batches Flagged High Risk*. Explains that Smart Harvest moves decision-making to $T_{dispatch}$ before the truck departs.
* **0:30–1:15 (Triage & Batch Selection):** Presenter clicks the top high-risk batch in the triage queue. Right detail panel smoothly populates.
* **1:15–1:50 (Timing & Explainability):** Presenter points to `[DETERIORATION HORIZON]`: expected quality decline begins before planned transit completes. Points to `[CONTRIBUTING FACTORS]`: chamber experienced cumulative degree-hours above setpoint and surface condensation events.
* **1:50–2:30 (Prioritized Intervention):** Presenter highlights `[PRIORITIZED ACTION]`: upgrade vehicle to Reefer or reroute to local market. Points to `Requires Human Review` badge and clicks `Acknowledge Intervention`.
* **2:30–3:00 (Wrap-Up):** Presenter summarizes the value proposition: transforming telemetry into proactive dockside intervention.

### Failure-Safe Demo Flow (Resilience Showcase)
* Used if backend returns `insufficient_data` or to intentionally demonstrate trustworthiness:
* Presenter uses the **Demo Scenario Switcher** (*note: explicitly described as a potential SIMULATION control, never as sponsor-data analytical evidence*) to select an incomplete batch (e.g. 2026 batch with truncated telemetry).
* Presenter highlights that the system **refuses to guess**: numeric scores and horizons are omitted; recommendation is withheld; missing requirements are exposed; human review is required.
* *Narrative:* Demonstrates that knowing when not to trust an automated estimate is essential for industrial safety.

### Presenter Must NOT Claim
* "Reduces food loss by X%" without hold-out evaluation evidence.
* "Predicts exact fruit firmness on arrival."
* "Monitors trucks live in transit."
* "Saved €X on this batch."

---

## 9. UX / Exploratory QA Plan (PUX-07)

### Test Execution Separation
* **TEST PLAN:** Defined test cases designed to verify user-visible functionality.
* **TESTS ACTUALLY EXECUTED:** Only tests marked with explicit command runs and recorded evidence in Section 11 were executed for this report.

### A. Current Foundation Test Plan (Executable Against Present Codebase)

#### TC-F01: Initial Loading Transition
* **PRECONDITION:** Backend and frontend dev servers are running.
* **ACTION:** Open `http://localhost:5173` or hard refresh (`Ctrl+F5`).
* **EXPECTED USER-VISIBLE RESULT:** Panel briefly displays animated spinner with text `Backend status: Connecting…` (`aria-live="polite"`). Transitions cleanly to `Connected` grid once endpoints resolve.
* **WHAT MUST NOT HAPPEN:** Blank white flash, jumping layout, or permanent stuck spinner.
* **EVIDENCE NEEDED:** Visual inspection of loading panel before component mount.

#### TC-F02: Slow Backend Response (Throttled Network)
* **PRECONDITION:** Network throttled to "Slow 3G" in browser DevTools.
* **ACTION:** Reload `http://localhost:5173`.
* **EXPECTED USER-VISIBLE RESULT:** `Connecting…` state remains steady without flickering or premature timeout. Updates cleanly when responses arrive.
* **WHAT MUST NOT HAPPEN:** Premature error state before 10s; unstyled HTML elements.
* **EVIDENCE NEEDED:** Network tab showing pending requests while UI maintains loading state.

#### TC-F03: Backend Unavailable / Hard Network Disruption
* **PRECONDITION:** FastAPI backend process stopped.
* **ACTION:** Open `http://localhost:5173` or click `Try again`.
* **EXPECTED USER-VISIBLE RESULT:** Error card renders: `Backend status: Unavailable`, displaying message: `The application could not reach the Smart Harvest API: Failed to fetch`. `Try again` button is visible.
* **WHAT MUST NOT HAPPEN:** App crash, white screen, false "Connected" status, or fabricated assessment.
* **EVIDENCE NEEDED:** Screenshot of error card with active `Try again` button.

#### TC-F04: Error Recovery via Retry
* **PRECONDITION:** UI displays `Backend status: Unavailable`.
* **ACTION:** Start backend, wait 2s, click `Try again`.
* **EXPECTED USER-VISIBLE RESULT:** Switches briefly to `Connecting…` and then renders `Connected` status and synthetic assessment card.
* **WHAT MUST NOT HAPPEN:** Button remains disabled or requires browser page reload.
* **EVIDENCE NEEDED:** Screen capture of recovery via `Try again`.

#### TC-F05: Rapid Click / Re-fetch Spam
* **PRECONDITION:** UI is open.
* **ACTION:** Click `Try again` 10 times in 2 seconds.
* **EXPECTED USER-VISIBLE RESULT:** `AbortController` in `HomePage.tsx` cancels pending promises cleanly. UI settles without race conditions.
* **WHAT MUST NOT HAPPEN:** Duplicate component renders, memory leaks, uncaught abort exceptions in console.
* **EVIDENCE NEEDED:** Browser console showing zero uncaught rejection errors.

#### TC-F06: Insufficient-Data Contract Verification
* **PRECONDITION:** Backend returns synthetic fixture (`status: "insufficient_data"`).
* **ACTION:** Inspect `AssessmentCard` component in browser.
* **EXPECTED USER-VISIBLE RESULT:** Renders `Insufficient data` block; explains that validated challenge inputs are unavailable; displays factor summary; displays `Reliability: unavailable`.
* **WHAT MUST NOT HAPPEN:** Numeric score (e.g. `0%`, `NaN`), risk gauge, or deterioration date rendered in DOM.
* **EVIDENCE NEEDED:** DOM inspection verifying `.assessment-values` is absent and `.insufficient-state` is present.

#### TC-F07: Absence of Optional Information
* **PRECONDITION:** Contract models have optional fields (`ends_at`, `band`, `confidence_score`, `source_dataset_id`) set to `null`.
* **ACTION:** Inspect current synthetic assessment where optional fields are `null`.
* **EXPECTED USER-VISIBLE RESULT:** Renders cleanly without broken image icons, missing text placeholders like `"null"`, or awkward whitespace gaps.
* **WHAT MUST NOT HAPPEN:** Literal text `"null"` or `"undefined"` visible in UI.
* **EVIDENCE NEEDED:** Visual screenshot of card showing clean typographic formatting.

#### TC-F08: Long Copy / Word-Wrapping Stress Test
* **PRECONDITION:** Factor summary or provenance notice contains lengthy unbroken text.
* **ACTION:** Inspect rendered text inside `.fixture-banner` and `.factor-list`.
* **EXPECTED USER-VISIBLE RESULT:** Text wraps naturally within panel borders; no root horizontal scrollbar appears.
* **WHAT MUST NOT HAPPEN:** Text clipping or extending outside container cards.
* **EVIDENCE NEEDED:** Screenshot showing word wrapping inside `.assessment-panel`.

#### TC-F09: Responsive Viewport Collapse (Mobile / Narrow Window)
* **PRECONDITION:** Viewport resized to 375px × 667px (mobile) and 768px × 1024px (tablet).
* **ACTION:** Navigate visible cards.
* **EXPECTED USER-VISIBLE RESULT:** Layout collapses to single column (`.content-grid` switches from multi-column to single-column flex/grid). Text and buttons remain legible without horizontal scrolling.
* **WHAT MUST NOT HAPPEN:** Horizontal page scrollbar or overlapping elements.
* **EVIDENCE NEEDED:** DevTools responsive screenshot at 375px width.

#### TC-F10: Keyboard Navigation & Focus Ring
* **PRECONDITION:** UI is loaded in error state (`Unavailable`) or available state.
* **ACTION:** Press `Tab` key repeatedly.
* **EXPECTED USER-VISIBLE RESULT:** Focus visibly lands on `Try again` button with clear focus outline (`outline: 2px solid`). Pressing `Enter` or `Space` activates the button.
* **WHAT MUST NOT HAPPEN:** Invisible focus ring or keyboard trap.
* **EVIDENCE NEEDED:** Screenshot showing visible focus outline on active button.

---

### B. Future Analytics UI Tests (`[FUTURE CONTRACT REQUIRED]`)
* **TC-A01 `[FUTURE CONTRACT REQUIRED]`:** Multi-batch inventory loading & empty state (verifying 0 batches displays empty state and 35 batches sorts by urgency).
* **TC-A02 `[FUTURE CONTRACT REQUIRED]`:** Full "Assessed" state display (verifying `status: "assessed"` displays risk badge and deterioration horizon).
* **TC-A03 `[FUTURE CONTRACT REQUIRED]`:** Operational recommendation presentation (verifying recommendation callout renders priority and human-review notice).
* **TC-A04 `[FUTURE CONTRACT REQUIRED]`:** Truncated telemetry degradation (verifying 204 batches stored into 2026 render `Reliability.level: "low"` with telemetry gap warning).
* **TC-A05 `[FUTURE CONTRACT REQUIRED]`:** Colour-independent risk discrimination (verifying risk bands are identifiable by text badge and distinct icon shape under color-blind simulation).
* **TC-A06 `[FUTURE CONTRACT REQUIRED]`:** Jargon-free operator comprehension (verifying factor summaries use plain language rather than raw database column names).

---

### Risk Audit
* **Demo-Critical Risks:** API freeze during live pitch; master-detail selection lag (>150ms); failure of demo scenario switcher.
* **Regression Risks:** Breaking Pydantic invariant in frontend TypeScript types (accidentally permitting score when insufficient); Vite proxy failure in production bundle.
* **Accessibility Risks:** Relying exclusively on color (red/green) for risk bands without text and icon cues; missing `aria-live` announcements on dynamic state changes.
* **False-Precision Risks:** Rendering spurious decimals (e.g. `84.72%`) or precise second-by-second countdown clocks for biological decay.
* **Misleading-UI Risks:** Retrospective leakage in UI (displaying arrival inspection or final losses as dispatch evidence); fake pulsing lights simulating streaming.

---

### Smoke Checks

#### CURRENT FOUNDATION SMOKE CHECK (Executable Today)
1. **Backend Service Health:** Run `Invoke-RestMethod http://localhost:8000/api/v1/health` -> verify `status: "ok"`, `service: "smart-harvest"`.
2. **Synthetic Assessment Contract:** Run `Invoke-RestMethod http://localhost:8000/api/v1/demo/assessment` -> verify `status: "insufficient_data"`, `risk: null`, `deterioration_horizon: null`.
3. **Clean Browser Mount:** Open `http://localhost:5173` in Incognito -> verify "Connecting…" spinner transitions to "Connected" badge.
4. **Insufficient Data Presentation:** Verify `AssessmentCard` displays `Insufficient data` notice, factor summary, and `Reliability: unavailable`.
5. **Backend Error Resilience:** Stop backend process -> click `Try again` -> verify UI transitions to `Unavailable` error card with active retry button.

#### TARGET DEMO SMOKE CHECK (`[FUTURE CONTRACT REQUIRED]`)
1. **Batch Triage Display:** Verify top high-risk batch displays at top of triage list.
2. **Master-Detail Selection:** Click batch -> verify detail panel populates within 150ms.
3. **Core Outputs Check:** Verify risk indicator, deterioration horizon vs transit time, contributing factors, and prioritized action callout are visible simultaneously.
4. **Demo Switcher Check:** Toggle Demo Switcher to "Insufficient Data Scenario" -> verify quantitative numbers hide and missing data notice displays.
5. **Resolution Check:** Set browser zoom to 100% on 1920×1080 display -> verify zero horizontal scrollbar.

---

## 10. Workstream Blockers & Dependencies

### BLOCKED BY DATA (Viktor)
* Specific batch ranking metric formula (Risk Score vs Loss in EUR).
* Factor dictionary (codes, categories, and human-readable summaries).
* Mathematical definition and calculation of `DeteriorationHorizon.starts_at`.
* Reliability degradation rules for truncated telemetry (204 batches in 2026).

### BLOCKED BY PRODUCT (Alisa)
* Final approval of operator persona and dockside operational context.
* Validated operational action catalog (`action_code` and plain-language action labels).
* Selection of the primary anchor batch ID for live demo presentation.
* Confirmation of mobile viewport requirement.

### BLOCKED BY TECH (Igor / Vladimir)
* Specification and integration of `PROPOSED / NOT AN ACCEPTED API CONTRACT: GET /api/v1/batches`.
* Specification and integration of `PROPOSED / NOT AN ACCEPTED API CONTRACT: GET /api/v1/batches/{id}/assessment`.
* Backend transition milestone from `engine_tier: "fixture"` to `deterministic_baseline`.

---

## 11. What Was NOT Done (By Design)

* No application source code was modified (`frontend/` and `backend/` untouched).
* No configuration, dependencies, package files, or lockfiles were modified.
* No API contracts or schemas were altered.
* No canonical project documents or sponsor pack files were modified.
* No agricultural rules or threshold numbers were invented.
* No merge, rebase, or force push actions were performed.

---

## 12. EVIDENCE / HANDOFF

* **Base Commit SHA:** `20021656028392a420561c6dc2a0f5434835081f`
* **HEAD Commit SHA:** `8ce2da45f8c687468d566d444dd3d16e019769b5` (prior to this fix commit)
* **Branch:** `prscr/ux-demo-qa` (tracking `origin/prscr/ux-demo-qa`)
* **Changed Files:** `prscr_ux_demo_qa_report.md` (only file modified)

### Actual Commands & Checks Executed

1. **Working Tree & Branch Verification:**
   ```powershell
   git branch --show-current
   # Output: prscr/ux-demo-qa

   git status --short
   # Output: M prscr_ux_demo_qa_report.md (only target file modified)
   ```

2. **Commit History Check:**
   ```powershell
   git log --oneline -5
   # Output:
   # 8ce2da4 docs: add PUX workstream report (PUX-00 through PUX-07)
   # bb66c6c docs: add PUX workstream report (PUX-00 through PUX-07)
   # 2002165 Merge pull request #8 from IgorGlUTMStudent/igor/igr-01-technical-recon
   # a0ad812 Merge pull request #7 from Slave-of-Skynet/victor-vdr-01-dataset-recon
   # 2f1ee84 IGR-01: Add technical reconnaissance report
   ```

3. **Whitespace & Git Diff Check:**
   ```powershell
   git diff --check
   # Output: [Clean — zero whitespace errors, zero trailing space]
   ```

4. **Name-Only Diff Against Base:**
   ```powershell
   git diff --name-only 20021656028392a420561c6dc2a0f5434835081f...HEAD
   # Output:
   # prscr_ux_demo_qa_report.md
   ```

### Unexecuted Checks
* Live browser execution of foundation test cases (TC-F01 through TC-F10) was not executed in this headless fix pass (local dev servers were not running).
* Future analytics test cases (TC-A01 through TC-A06) were not executed because backend endpoints and analytics engines do not yet exist (`FUTURE CONTRACT REQUIRED`).

### Boundary Invariants
* **Shared contract changes:** **NO**
* **Dependency changes:** **NO**
* **Config changes:** **NO**
* **Application code changes:** **NO**
