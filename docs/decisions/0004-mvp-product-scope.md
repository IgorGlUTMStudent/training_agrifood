# ADR 0004 — MVP Product Scope and UX Boundaries

- **Status:** ACCEPTED HUMAN DECISION
- **Decision owner:** Vladimir — Integrator
- **Date:** 2026-09-21
- **Decision source:** APR-02F Human Gate (APR2-D1–D6)
- **Evidence/reference base HEAD:** `fb5d3a888474250a89d4eb1e06928ca9cd94f813`

---

## 1. Human decision provenance

On 2026-09-21, Vladimir (Human Integrator) reviewed the reconciled APR-02F product decision package (`docs/product_recon/08_mvp_scope_decision_packet.md` and `docs/product_recon/09_product_acceptance_traceability.md`) at repository base `fb5d3a888474250a89d4eb1e06928ca9cd94f813` and explicitly accepted all six amended decision proposals:

- **APR2-D1:** Primary MVP design persona
- **APR2-D2:** Dataset-backed replay/view queue policy
- **APR2-D3:** Operator treatment and UI presentation of `insufficient_data` state
- **APR2-D4:** Minimum truthful explainability baseline for crop-median engine
- **APR2-D5:** Honest handling and representation of recommendations (Outcome 4)
- **APR2-D6:** Telemetry evidence and MVP narrative boundary (VDR-04B product implication)

**Provenance invariants:**
1. Acceptance was decided explicitly by the Human Integrator (Vladimir). Acceptance was NOT decided by an AI agent and was NOT inferred from a merge commit.
2. This Human Gate accepts **APR2-D1–D6 only**, in their exact bounded and amended formulations recorded below.
3. This decision does NOT promote the APR-02F source documents wholesale to canonical truth: research notes, candidate wireframes, exploratory workflow steps, historical implementation snapshots, and unapproved recommendations in `08_mvp_scope_decision_packet.md`, `09_product_acceptance_traceability.md`, and `docs/recon/PUX-08-data-ux-reconciliation.md` remain non-canonical research/specification artifacts. ADR 0004 is the single authoritative decision record of the Human Gate.

---

## 2. Evidence and authority hierarchy

The authority order governing this decision record conforms to project canon:
1. **Challenge materials:** Challenge brief and sponsor `README.md` defining the four operational outcomes and the fixed dispatch assessment moment ($T_{\text{assess}} \equiv T_{\text{dispatch}}$).
2. **Accepted architectural and semantic decisions:** ADR 0001 (foundation architecture), ADR 0002 (predictive input semantics and temporal leakage boundary), and ADR 0003 (assessment, ranking, and evaluation semantics).
3. **Accepted data and feasibility evidence:** VDR-01 (dataset inventory), VDR-02 (temporal leakage audit), VDR-03 (target and horizon feasibility), and VDR-04A (dispatch predictability benchmark).
4. **Committed application contracts:** `backend/app/domain/batch.py`, `backend/app/domain/assessment.py`, `backend/app/ingestion/canonical_mapper.py`, `frontend/src/api/contracts.ts` (authoritative for current runtime/code reality).
5. **Accepted research evidence:** APR-01 Steps 0–7 (product reconnaissance and adversarial review).
6. **Committed research / evidence input (draft):** VDR-04B (telemetry ablation under planned logistics, committed as `DRAFT FOR REVIEW — EVIDENCE ONLY`; informs the accepted product narrative boundary in APR2-D6, but is not accepted wholesale as canon).
7. **Accepted product decisions:** APR2-D1–D6 (authoritative for MVP product scope via this ADR; source documents 08 and 09 remain mixed research/specification artifacts).
8. **Proposals and recommendations:** PUX-08 (reconciled UX draft, not canon).

---

## 3. Context

Following the formal adoption of ADR 0003 (assessment ranking, deterministic crop-median baseline, null horizon, null recommendations, and evaluation protocol) and the integration of IGR-03 (deterministic raw-to-canonical `BatchAssessmentInput` mapper enforcing temporal boundaries), the repository required authoritative boundaries for MVP product scope and UX presentation.

The APR-02F synthesis formulated six bounded decision proposals (APR2-D1 through APR2-D6) addressing the four core challenge outcomes. The Human Integrator reviewed these proposals, confirmed they preserve all epistemic boundaries and UNKNOWN registers, and formally accepted them as recorded herein.

---

## 4. Accepted decisions (APR2-D1–D6)

### APR2-D1 — Primary MVP design persona

**DECISION:**
- The primary MVP design persona for Smart Harvest is the **dispatch-side storage operator**.
- The label `Dispatch Supervisor` is permitted strictly as an internal Slave-of-Skynet (SoS) design persona label. It is **NOT** a sponsor-specified job title, **NOT** a verified Moldovan cold-storage warehouse role, and **NOT** an assertion of real operational authority.
- Smart Harvest is designed as advisory Decision Support for a user reviewing batches at dispatch; it does not define or alter the human operator's formal employment responsibilities.

**RETAINED UNKNOWN:**
- Real operator authority remains an open UNKNOWN. The system does not know or assume who possesses authority for:
  - Hold/release decisions;
  - Outbound shipment cancellation;
  - Carrier or vehicle replacement;
  - Mandatory quality control (QC) escalation;
  - CMR or transport document signing;
  - Physical warehouse inspection procedures or formal Standard Operating Procedures (SOPs).

---

### APR2-D2 — Dataset-backed replay/view queue

**DECISION:**
- For the dataset-backed MVP and demonstration, the operational triage view selects canonical recorded assessment events via a **configurable replay/view window**.
- The single authoritative assessment clock remains strictly:
  $$\text{assessment\_timestamp} \equiv \text{storage\_sessions.dispatch\_datetime}$$
  as established in ADR 0002. No secondary, competing, or live clock is introduced.
- `facility_id` serves strictly as a **UI and context filter**. It does not partition the underlying dataset into separate operational jurisdictions.
- `planned_dispatch_datetime` may be displayed strictly as **planning and schedule context** (conditionally eligible under ADR 0002). It does **NOT** replace, alter, or offset the canonical assessment clock.
- Batch ordering within the replay queue remains governed strictly by ADR 0003 (D1, D3):
  $$\text{risk.score DESC, batch\_id ASC}$$
  strictly within a single, identical `engine_tier + engine_version`. Deterministic tie-breaking by `batch_id ASC` ensures display stability; it does not indicate any difference in predicted risk between tied batches.
- Assessments produced by different engine tiers or different engine versions must not be merged into a common ranked queue until cross-tier/version comparability is empirically validated.

**RETAINED UNKNOWN / REJECTED OVER-INTERPRETATIONS:**
- Exact replay-window duration, actual operator review capacity (number of batches reviewed per shift), live queue membership rules, and real warehouse workflows remain strictly UNKNOWN.
- The fixed review quota $K=10$ is **REJECTED** as an operational constraint.
- The 2-hour offset between `pre_dispatch` quality check and `dispatch_datetime` observed in the training data is an empirical dataset pattern, **NOT** a verified warehouse operating window or SOP rule.
- Unvalidated Warehouse Management System (WMS) readiness states are **REJECTED** from the product model.

---

### APR2-D3 — `insufficient_data` presentation

**DECISION:**
- Batches with status `insufficient_data` must be presented in a **separate, neutral "Not assessed / Incomplete data" section or state**, visually and structurally distinct from scored batches.
- Under ADR 0003 (D3, D7), an `insufficient_data` assessment carries:
  $$\text{risk} = \text{null}$$
  $$\text{deterioration\_horizon} = \text{null}$$
  and is strictly excluded from numeric ranking.
- Data limitations and missing requirements must be communicated factually through available factual `reason_codes` and `missing_requirements`. No standardized vocabulary, reason-code catalogue, engine minimum rules, or fallback policies are established here; those remain UNKNOWN and subject to future implementation decisions.
- An unassessed batch does **NOT** indicate low risk, high risk, a safe batch, or a defective batch.

**Accepted UI notice copy:**
> "No predictive score is available for this batch because required inputs were not satisfied. This does not mean low or high risk. Smart Harvest does not determine the operational disposition of this batch."

**RETAINED UNKNOWN / REJECTED OVER-INTERPRETATIONS:**
- Real operational disposition of unassessed batches, fallback routing, mandatory QC inspection, and physical release/hold behavior remain strictly UNKNOWN.
- It is strictly **FORBIDDEN** to invent automatic routing of `insufficient_data` batches to manual QC, laboratory inspection, or automatic dispatch blocking.
- It is strictly **FORBIDDEN** to fabricate numeric scores (e.g. `score = 0.0`) or treat unassessed batches as zero-risk.

---

### APR2-D4 — Minimum truthful explainability baseline

**DECISION:**
- For the deterministic crop-median baseline (`baseline-crop-median-v1` under ADR 0003 D5), the model factors list is strictly empty:
  $$\text{factors} = [\,]$$
- Product presentation must cleanly separate three distinct conceptual areas:
  1. **How this score is computed:** Transparent description of the deterministic baseline algorithm:
     - The score is derived from the historical median `loss_fraction_pct` for the batch's crop type in the training partition;
     - For an unseen crop type, the score falls back to the global training-partition median;
     - The continuous score is clipped to $[0, 100]$ and divided by 100:
       $$\text{risk.score} = \frac{\text{clip}(\text{predicted\_loss\_fraction\_pct}, 0, 100)}{100}$$
     - The score is strictly an uncalibrated relative loss severity index, not a probability or confidence percentage.
  2. **Batch Context:** Display of factual, observable pre-dispatch inputs (e.g. crop type, variety, storage duration, planned logistics, target chamber temperature/humidity). This section must be explicitly captioned:
     > "Context only; contribution to this score has not been established."
  3. **Model attribution (deferred):** Quantitative feature contribution is not supported for the baseline engine.
- Batch context fields must **NOT** be labeled as "causes", "drivers", "contributing risk factors", or "model contributions" to the baseline score.
- Directional factor effects (`increases_risk` / `decreases_risk`) remain strictly forbidden until an explanation method is formally validated on an approved learned engine.

**RETAINED UNKNOWN / DEFERRED:**
- Model attribution algorithms (e.g. SHAP, TreeSHAP, integrated gradients), attribution reference/baseline semantics, mathematical explanation validation, and operator comprehension testing remain strictly DEFERRED and UNKNOWN.
- Outcome 3 ("What factors contribute to the risk?") is only **PARTIALLY SUPPORTED** through baseline algorithmic transparency and factual context display; individual feature attribution to the predicted score remains **UNSUPPORTED**.

---

### APR2-D5 — Honest handling of recommendations (Outcome 4)

**DECISION:**
- Production assessment output maintains:
  $$\text{recommendation} = \text{null}$$
  reaffirming ADR 0003 (D9).
- The product interface must present a neutral, factual notice explaining that operational recommendations are unavailable because available data do not validate intervention effectiveness.

**Accepted UI notice copy:**
> "Action recommendations are unavailable. Current evidence does not validate intervention effectiveness. Smart Harvest prioritizes batches for review but does not prescribe an operational action."

**CRITICAL EPISTEMIC INVARIANT:**
- **Outcome 4 ("What action should be prioritised?") is NOT SUPPORTED BY CURRENT EVIDENCE.**
- Returning `recommendation = null` or rendering an unavailable notice does **NOT** satisfy, fulfill, or implement Outcome 4.
- Prioritising or ranking batches by predicted loss severity is **NOT** equivalent to recommending an operational intervention.

**RETAINED UNKNOWN / REJECTED OVER-INTERPRETATIONS:**
- Action catalogue, intervention efficacy, physical action costs, operational lead times, user decision authority, formal warehouse SOPs, prevented loss amounts, and financial savings remain strictly UNKNOWN.
- It is strictly **FORBIDDEN** to prescribe physical actions (e.g. "pre-cool", "reroute", "re-inspect", "discard"), to implement autonomous action execution, to set `requires_human_review = false`, or to display monetary savings claims (€ / $ / %).

---

### APR2-D6 — Telemetry evidence and MVP narrative boundary

**DECISION:**
- Storage telemetry remains a **canonical input** to the system per ADR 0002 and ADR 0003 (D10). Ingestion mapping (IGR-03) continues to parse, type, and preserve telemetry observations and structural missingness.
- Research report VDR-04B informs the bounded product narrative regarding tested feature representations.
- **Accepted narrative boundary:** Context + Planned Logistics (C+L) is recognized strictly as a **candidate feature-family simplification for a future learned-engine decision**.
- C+L is **NOT**:
  - The current MVP analytics architecture;
  - The selected production model;
  - An approved learned engine;
  - The final feature subset;
  - Proof that telemetry is useless or redundant across agricultural operations.
- The approved analytical direction for current MVP development remains the deterministic crop-median baseline (ADR 0003 D5).

**RETAINED UNKNOWN / EPISTEMIC BOUNDARIES:**
- The potential utility of telemetry for real-time monitoring, cold-chain compliance auditing, equipment fault/health detection, and sensor-based diagnostics remains UNKNOWN and unvalidated by VDR-04B. None of these hypotheses is promoted to canon or claimed as implemented capability.
- **VDR-04B research status & boundary:** VDR-04B remains committed research evidence with the formal status `DRAFT FOR REVIEW — EVIDENCE ONLY`. Human Gate APR2-D6 accepts strictly the product narrative boundary regarding tested feature sets; it does **NOT** constitute wholesale acceptance of VDR-04B, does not adopt all VDR-04B claims as canon, and does not alter canonical schemas.

---

## 5. Explicit retained UNKNOWN and DEFERRED register

In accordance with `docs/assumptions_unknowns.md` and ADR 0003, the following twelve areas remain strictly **UNKNOWN** or **DEFERRED**; this Human Gate does not resolve or close them:

1. **Production learned model selection:** Model family (e.g. HistGradientBoosting, Ridge, LightGBM), hyperparameters, calibration, and formal acceptance criteria.
2. **Final feature subset:** Inclusion or exclusion of specific telemetry aggregates, chamber interactions, or agronomic indices in a future learned model.
3. **Cross-tier / cross-version comparability:** Validation of score equivalence across different engine tiers (baseline vs learned) or version bumps.
4. **Engine minimum input requirements:** Exact criteria defining `insufficient_data` for future learned engines, and fallback routing policies between engines.
5. **Calibrated reliability & confidence:** Statistical probability calibration, prediction intervals, and numerical confidence scoring (currently fixed at `level = unavailable`, `confidence_score = null`).
6. **Operational risk bands:** Categorical thresholds (`risk.band`), traffic-light tags, or operator alert triggers (currently fixed at `risk.band = null`).
7. **Biological deterioration onset & timing:** Exact biological onset timestamps, continuous countdown timers, or coarse deterioration intervals (currently fixed at `deterioration_horizon = null`).
8. **Explainability & model attribution (XAI):** Algorithm selection (e.g. SHAP), reference/baseline value definitions, attribution stability, and operator comprehension validation.
9. **Operator authority & warehouse SOP:** Formal role titles, hold/release authority, CMR document signing, transport cancellation authority, and official inspection workflows.
10. **Triage queue membership & capacity:** Exact duration of dispatch replay windows, number of batches reviewed per shift, pagination limits, and live streaming queue mechanics.
11. **Action catalogue & intervention efficacy:** Inventory of available physical actions, counterfactual treatment effects, implementation costs, operational lead times, and financial savings.
12. **Telemetry audit & diagnostic utility:** Use of sensor streams for equipment-health monitoring, anomaly detection, or facility condition auditing.

---

## 6. Rejected over-interpretations

The following interpretations were explicitly reviewed and **REJECTED** by the Human Integrator:

- **Wholesale promotion of APR-02F prose:** Committing or accepting APR2-D1–D6 does not transform the surrounding research discussions, wireframes, or historical text of `08_mvp_scope_decision_packet.md` into binding canon.
- **Wholesale promotion of PUX-08:** Design proposals, screen mockups, badge designs, and workflow recommendations in `docs/recon/PUX-08-data-ux-reconciliation.md` remain design recommendations, not mandatory specifications.
- **Universalization of VDR-04B:** VDR-04B empirical benchmark findings under specific models (Ridge/HGB) do not constitute universal truths about post-harvest telemetry, nor do they authorize deleting telemetry fields from canonical schemas.
- **Invented operator authority:** Describing the design persona as a dispatch-side storage operator does not authorize assuming the user can cancel shipments, re-cool produce, or sign transport waivers.
- **Invented operator capacity:** Benchmarks evaluating top-10 metrics (NDCG@10, Precision@10) do not establish an operational quota of 10 batches per shift ($K=10$).
- **Fulfillment of Outcome 4:** Neither a null recommendation nor an ordered triage queue satisfies the challenge requirement for prioritised action recommendations.
- **Causal attribution of baseline context:** Displaying observed chamber temperatures or planned transit hours alongside a crop-median score does not imply those factors caused or influenced the baseline score.
- **Premature implementation claims:** Accepting product decisions does not mean that analytics scoring, triage queues, or interactive UI components are implemented in application code.

---

## 7. Downstream consequences

### What is conceptually unblocked:
1. **Frontend triage queue design:** Development of an interactive batch table adhering to `risk.score DESC, batch_id ASC` for a single engine tier/version, with clear simulation/provenance indicators.
2. **Insufficient-data UI presentation:** Implementation of an isolated "Not assessed / Incomplete data" panel displaying available factual `reason_codes` and `missing_requirements`.
3. **Baseline explainability UI:** Implementation of the transparent score calculation description alongside a clearly demarcated "Batch Context (non-causal)" panel.
4. **Recommendation panel:** Implementation of the honest, neutral notice communicating that action recommendations are currently unavailable.
5. **Product & pitch narratives:** Alignment of demo runbooks and pitch scripts with the accepted epistemic boundaries (severity score, unbanded, null horizon, null recommendation, C+L as future learned candidate only).

### What is NOT authorized or implemented by this ADR:
1. This ADR does **NOT** write, modify, or merge application code in `backend/` or `frontend/`.
2. This ADR does **NOT** select, approve, or deploy any learned machine learning model.
3. This ADR does **NOT** introduce categorical risk bands, confidence percentages, or countdown timers.
4. This ADR does **NOT** establish a prescriptive action catalogue or claim financial loss reductions.
5. All downstream technical changes require their own bounded implementation contracts and testing.

---

## 8. Completion boundary

This document completes the canonical reconciliation of the APR-02F Human Gate (VLD-APR-HG1R).

Submitting this document alongside its synchronized cross-document updates is the sole deliverable of this task. Upon completion of verification, execution must **STOP FOR PROJECT BRAIN REVIEW**. Commit, push, PR creation, and downstream code execution are not authorized.
