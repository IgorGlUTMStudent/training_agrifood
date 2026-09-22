STATUS:
PRODUCT NARRATIVE / CLAIM BOUNDARY
DERIVED FROM ACCEPTED DECISIONS
NOT A NEW ADR
NOT FINAL RUNTIME VERIFICATION

# APR-03A — MVP Demo Narrative & Claim Boundary Freeze

- Inspected committed base: `d2767685f7be82dfcdf5b30958e142dfbcf6d386`.
- Temporary executor: Vladimir — Integrator, acting as temporary APR-03A executor.
- Original Product Owner: Alisa.
- Reason: temporary Product Owner unavailability during training timebox.
- Permanent ownership change: NO. Self-approval: NO. Execution != acceptance.
- Runtime claims must be reverified before VLD-05.

This is a derived narrative artifact awaiting Project Brain review and subsequent Human integration, not a final pitch or a new decision gate. It serves Alisa's product narrative ownership after return, Denis's UI wording, Vladimir's demo/pitch assembly, and VLD-05's final claim audit.

## 1. Authority and source traceability

Use supplied training challenge materials → accepted SoS ADRs/decisions → challenge canon → accepted/committed evidence with its exact status → committed application code for implementation state → APR research notes. Code proves implementation state, not challenge requirements. Merge != automatic promotion of research to canon. APR2-D1–D6 are not reopened.

Source keys below resolve to repository paths; section references in the tables narrow the authority used.

| Key | Source path and authority |
| --- | --- |
| S1 | `sponsor_pack/README.md`, §3: supplied dispatch-time boundary; `sponsor_pack/brief/Training Challenge #3 — AgriFood.md`: four desired outcomes. |
| S2 | `docs/decisions/0002-predictive-input-semantics.md`: accepted input, assessment clock, leakage and missingness semantics. |
| S3 | `docs/decisions/0003-assessment-evaluation-semantics.md`, D1–D10: accepted score, ordering, baseline, evaluation and unavailable-output policy. |
| S4 | `docs/decisions/0004-mvp-product-scope.md`, APR2-D1–D6: accepted persona, replay/view scope, copy, explanation and telemetry boundaries. |
| S5 | `docs/challenge_canon.md`: training simulation context and accepted evidence history. |
| S6 | `docs/data_recon/03_target_horizon_feasibility.md`, executive summary; `docs/data_recon/04_dispatch_predictability.md`: accepted feasibility evidence, with acceptance recorded in S3/S5; historical draft headings do not select an engine. |
| S7 | `docs/data_recon/06a_baseline_evaluation.md`, §§1–2, 5–6, 8, 10; `docs/data_recon/06a_baseline_evaluation_results.json`, `metadata`, `reference_parity`, `application_parity`: committed parity evidence with status qualifier. |
| S8 | `backend/app/ingestion/raw_reader.py`; `backend/app/ingestion/canonical_mapper.py`, `build_batch_assessment_input`; `backend/app/domain/batch.py`: committed ingestion and canonical input. |
| S9 | `backend/app/analytics/crop_median_baseline.py`: committed fitting and prediction functions. |
| S10 | `backend/app/services/baseline_assessment.py`, `build_baseline_assessment`: committed application service. |
| S11 | `backend/app/main.py`; `backend/app/api/routes.py`; `backend/app/services/demo_assessment.py`: public API wiring and synthetic fixture. |
| S12 | `frontend/src/api/client.ts`; `frontend/src/pages/HomePage.tsx`; `frontend/src/components/AssessmentCard.tsx`: committed public UI path. |
| S13 | `docs/data_recon/04b_telemetry_ablation.md`, “Telemetry marginal value with logistics”: DRAFT FOR REVIEW — EVIDENCE ONLY; S4 D6 accepts the bounded narrative, not the entire report. |
| S14 | `docs/product_recon/04_evidence_map.md`; `docs/product_recon/07_adversarial_review.md`; `docs/product_recon/08_mvp_scope_decision_packet.md`; `docs/product_recon/09_product_acceptance_traceability.md`: research/mixed source packets, subordinate to S2–S4. |
| S15 | `docs/demo_runbook.md`; `docs/integration_contract.md`, §§1.2, 8–9; `docs/assumptions_unknowns.md`; `README.md`: process, UNKNOWNs and historical implementation summaries. |

**Reconciliation:** S14's older unresolved-persona wording is superseded by S4 D1. The older adversarial review's partial action-support language does not establish Outcome 4 support; S4 D5 is authoritative. Planned duration is logistics context, never a deterioration estimate. Statements in README, integration contract and older APR snapshots that baseline execution is absent are an **older implementation snapshot — not authoritative for current code state**. The runbook still describes the fixture path; its “risk percentage” wording must not be reused as score semantics. These sources remain unchanged.

## 2. Product narrative

**PRIMARY VERSION:** Smart Harvest is a dispatch-time decision-support prototype designed to help a storage operator focus limited review attention on comparable assessed batches using a transparent predicted-loss severity score.

**30-second explanation:** Around dispatch, a storage operator may have many batches to review and limited attention. Smart Harvest is designed to prioritise comparable assessments using a transparent score from zero to one that represents predicted loss severity, not probability. The baseline uses historical training medians by crop. It does not estimate deterioration timing or prescribe actions. Today, the assessment service exists internally; the public demo still shows a synthetic fixture, not a ranked batch queue.

The primary user is the **dispatch-side storage operator**, a SoS design persona (S4 D1), not a verified employment title or grant of operational authority. The limited-attention problem is product framing, not a measured warehouse SOP. Operator count, shift capacity, a fixed K=10 quota and actual workflow remain UNKNOWN.

Bounded value: designed to support prioritisation and review, transparency, traceability, consistent assessment presentation and explicit unavailable states. Descriptive innovation wording may combine dispatch-time decision support, traceable data boundaries, transparent deterministic scoring and explicit provenance; it does not establish novelty or market leadership.

**Smart Harvest is being developed in a training challenge simulation.** The supplied sponsor dataset is not evidence of a real commercial deployment. A future dataset-backed assessment would still need the training-context disclosure; it must also be distinguished from the current synthetic fixture (S5, S11).

## 3. Four-outcome matrix

| Outcome | Current evidence/support | Honest narrative |
| --- | --- | --- |
| 1. Which batches are most at risk? | SUPPORTED AS RELATIVE PRIORITISATION in accepted semantics (S3 D1–D3). Score-producing application service IMPLEMENTED (S10); ranked end-user queue NOT YET IMPLEMENTED (S11–S12). | Comparable assessed batches can be ordered by predicted loss severity: `risk.score DESC, batch_id ASC`, only within identical `engine_tier + engine_version`. This is a supported ordering rule, not a currently available queue or exhaustive detection. |
| 2. When may quality begin to deteriorate? | NOT SUPPORTED BY CURRENT EVIDENCE (S6; S3 D6). | Deterioration timing is not estimable from supplied observations; `deterioration_horizon = null`. |
| 3. What factors contribute to the risk? | PARTIALLY SUPPORTED (S4 D4). Baseline `factors = []` (S10); explanatory target surfaces are not yet implemented (S12). | Explain the transparent score mechanism and factual Batch Context when available; individual feature attribution and causal drivers are unsupported. |
| 4. What action should be prioritised? | NOT SUPPORTED BY CURRENT EVIDENCE (S4 D5). | Action recommendations are unavailable because current evidence does not validate intervention effectiveness; `recommendation = null` (S10). Ranking or an unavailable notice does not satisfy this outcome. |

**Invariant:** prioritising a batch for review != prescribing an operational action.

## 4. Score, evidence and unavailable-state boundaries

The deterministic baseline uses the historical training median `loss_fraction_pct` for the batch's crop. For a crop unseen during fitting, it uses the global training median. Outcomes belong only to fitting/evaluation; inference reads `batch_input.batch.crop_type`. The accepted transformation is `risk.score = clip(predicted_loss_fraction_pct, 0, 100) / 100` (S3 D2/D5; S9).

`risk.score` is an uncalibrated relative loss-severity score in [0, 1], not probability, confidence, chance of spoilage, accuracy or a guarantee. `risk.band = null`: no Low/Medium/High, Green/Yellow/Red or validated alert policy. Equal crop medians can produce tied scores; `batch_id ASC` stabilises display and does not establish a severity difference. No mixed-tier/version ranking is authorized (S3 D2–D3).

Accepted replay semantics select recorded assessments through a configurable replay/view window on `assessment_timestamp = storage_sessions.dispatch_datetime`. `facility_id` is a UI/context filter; `planned_dispatch_datetime` is planning context, not a replacement clock. Window duration, live membership and review capacity remain UNKNOWN. This does not claim implemented controls (S2; S4 D2).

For `insufficient_data`, use **Not assessed / Incomplete data**; there is no predictive score, and the case is excluded from numeric ranking. Accepted copy (S4 D3):

> No predictive score is available for this batch because required inputs were not satisfied. This does not mean low or high risk. Smart Harvest does not determine the operational disposition of this batch.

Do not infer safety, rejection or mandatory QC. Report available factual reasons without inventing a reason-code catalogue, minimum-input rules or routing. Optional sensor absence or truncated telemetry alone does not authorize rejection. IGR-04B takes a validated canonical input and fitted baseline; it is not a general missing-input/fallback orchestration service (S3 D7; S10).

**Reliability disclaimer:** `reliability.level = unavailable`, `confidence_score = null`; no calibrated uncertainty or model-confidence claim is supported (S3 D7; S10). Explicit provenance identifies the assessment; it does not establish model quality.

**OBSERVED RESULT — VDR-06A:** the committed report records reproduction of the accepted historical VDR-04A crop-median baseline metrics using the IGR-04A application implementation under accepted P1/P2 protocols. Preserve its exact status: **EVIDENCE / IMPLEMENTATION PARITY AUDIT; NOT CANON BY ITSELF; DRAFT FOR REVIEW — PARITY VERIFIED (PASS)**. Its evaluated base is `6447d0884ec5a64bc2112f9c72d00e42cba3cd01`; this document inspects the evidence committed at `d2767685f7be82dfcdf5b30958e142dfbcf6d386`. P1 is forward inter-season holdout; P2 is chamber-time grouped OOF. This is crop-only baseline parity through canonical inputs, not an evaluation of the later IGR-04B service, HTTP integration, business effectiveness or commercial readiness (S7).

VDR-04A learned models are offline feasibility benchmarks, not a selected production engine, runtime model or current MVP engine. The accepted analytical direction remains the deterministic crop-median baseline (S3 D5; S4 D6). No benchmark metric is used as a headline here. Any later numerical metric needs the exact protocol, model family, feature family, offline label and explicit “NOT runtime performance” qualification. P3 remains a non-defensible diagnostic (S3 D5).

**Telemetry:** telemetry remains canonical input. Tested aggregate telemetry representations did not show stable marginal improvement over planned-logistics-enabled features under the tested configurations. C+L is only a candidate simplification for a FUTURE learned-engine decision, not current architecture (S13 with its draft status; accepted narrative boundary S4 D6). No general telemetry-utility conclusion follows.

## 5. Current implementation snapshot

**CURRENT AT APR-03A BASE — verified against committed base: `d2767685f7be82dfcdf5b30958e142dfbcf6d386`.** Verification here means read-only committed-source inspection, not fresh runtime execution, screenshot validation or rerunning evaluation. All implementation rows require **REVERIFY BEFORE FINAL DEMO / VLD-05 = YES**.

| Capability | State at base | Direct evidence / limit |
| --- | --- | --- |
| Canonical ingestion | IMPLEMENTED | S8: raw reading and `build_batch_assessment_input`; supplied-snapshot boundary, not generalized production-data handling. |
| IGR-04A crop-median baseline | IMPLEMENTED | S9: fitting, crop lookup, global fallback and score transformation. |
| IGR-04B assessment service | IMPLEMENTED | S10: fitted baseline + canonical input → `build_baseline_assessment()` → `RiskAssessment`. |
| VDR-06A parity evidence | COMMITTED EVIDENCE / PARITY PASS | S7, with the full status qualifier in §4; no fresh evaluation run in APR-03A. |
| Production baseline fitting/artifact lifecycle | NOT IMPLEMENTED | S9 has an explicit fitting function; S10 requires its fitted result. S11 contains no production fit/load/serve wiring. |
| Real assessment HTTP endpoint | NOT IMPLEMENTED | S11 only wires health and synthetic demo routes. |
| Multi-batch ranked queue | NOT IMPLEMENTED | S11–S12: no multi-batch endpoint or queue UI. |
| Replay/facility API | NOT IMPLEMENTED | S11–S12: no replay-window/facility endpoints or controls. |
| Action recommendation engine | NOT IMPLEMENTED | `backend/app/recommend/__init__.py` is a future boundary; S10 preserves null. |
| Deterioration model | NOT IMPLEMENTED | Application analytics contains only S9; S10/S11 preserve null horizon. |
| Selected learned production engine | NOT IMPLEMENTED | S3/S4 select none; application analytics contains S9 only. |
| Current public demo | SYNTHETIC FIXTURE | S11–S12: `GET /api/v1/health`, `GET /api/v1/demo/assessment`; single-assessment shell, `insufficient_data`. |

IGR-04B's output is `status = assessed`, deterministic `risk.score`, `risk.band = null`, `deterioration_horizon = null`, `factors = []`, `recommendation = null`, with empty `reason_codes` and `missing_requirements`. Reliability remains unavailable as stated in §4. Provenance fixes `engine_tier = deterministic_baseline` and `contract_version = 1.0.0`; `engine_version`, `generated_at`, `source_dataset_id`, `simulation` and `notice` are caller supplied. Do not invent a deployed engine version (S10).

**APPLICATION SERVICE IMPLEMENTED != END-TO-END PRODUCT PATH IMPLEMENTED.** The latter is false at this base. The public fixture uses `engine_tier = fixture`, `engine_version = foundation-fixture-v1`, `simulation = true`, null risk/horizon/recommendation, and a factual data-quality factor with unknown effect. Its nonempty fixture factors are not baseline attribution; the baseline service keeps `factors = []`. The fixture's “Validated challenge dataset schema” missing-requirement text is synthetic copy, not evidence that canonical ingestion is absent (S10–S12).

IGR-04B and VDR-06A are committed and inspected; no future results are assumed. PUX-10A is not part of the inspected implementation: no pending/local Denis work is treated as completed. The public card contains a scored rendering branch, but the public fixture never exercises it; that branch alone does not establish a scored end-user flow (S12).

## 6. Demo story beats and presenter narrative

This is the intended MVP sequence. “IMPLEMENTED AT CURRENT BASE” below means source-inspected behavior of the stated fixture scope only; all live behavior still needs demo verification. Target rows are explanatory narrative, not screens to pretend are currently available. Sources: S4 D2–D5 for intent; S11–S12 for current UI.

| Beat | WHAT USER SEES | WHAT PRESENTER MAY SAY | WHAT PRESENTER MUST NOT SAY | IMPLEMENTATION STATUS |
| --- | --- | --- | --- | --- |
| 1. Operator opens Smart Harvest. | Current shell: connecting, available or unavailable/retry states. | “This training prototype currently demonstrates API connectivity and a synthetic assessment.” | “A deployed operational warehouse dashboard is running.” | IMPLEMENTED AT CURRENT BASE — shell only. |
| 2. Available assessments are presented. | Target: available recorded assessments; currently only one synthetic card. | “The intended MVP presents dispatch assessments; today's public path shows one fixture.” | “These are evaluated customer batches.” | TARGET MVP — IMPLEMENTATION NOT YET VERIFIED. |
| 3. Comparable scored batches can be prioritised. | Target: scored cases ordered within one engine tier/version. | “The accepted order is score descending, then batch ID ascending for ties.” | “The current UI already ranks batches” or “all risky batches are detected.” | TARGET MVP — IMPLEMENTATION NOT YET VERIFIED. |
| 4. A batch assessment is inspected. | Target: selectable assessment detail; currently only a static synthetic card. | “A future detail view would show the selected assessment and provenance.” | “This fixture is the baseline assessment service output.” | TARGET MVP — IMPLEMENTATION NOT YET VERIFIED. |
| 5. Score calculation is explained. | Target: “How this score is computed” plus distinct “Batch Context.” | “The baseline uses crop training median loss, with global training median fallback.” | “Displayed context fields caused or contributed to this score.” | TARGET MVP — IMPLEMENTATION NOT YET VERIFIED. |
| 6. Unsupported deterioration/actions remain unavailable. | Current fixture card: “Not estimable from supplied observations”; “No validated recommendation available.” | “Timing and intervention recommendations are unsupported; these notices disclose the gaps.” | “Showing these notices solves Outcomes 2 and 4.” | IMPLEMENTED AT CURRENT BASE — fixture notices only; exact ADR copy remains target guidance. |
| 7. Incomplete-data cases remain separate from scored cases. | Target: neutral unassessed section; current card only has an insufficient-data state. | “No score is available; unassessed cases must be excluded from numeric ranking.” | “The product routes these cases to a required physical procedure.” | TARGET MVP — IMPLEMENTATION NOT YET VERIFIED; separate multi-batch presentation is absent. |

## 7. Claim registry

“Demo-safe?” permits only the wording and scope in the row, not final pitch approval. Source keys resolve to exact paths in §1. “No (decision)” means no runtime dependency for describing the accepted rule; §10 still checks that it remains applicable. Implementation claims are always snapshot-qualified and require reverification.

| Claim ID | Claim | Classification | Source | Demo-safe? | Reverification needed? | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| C01 | Assessment occurs at dispatch; only eligible information at/before that moment enters inference. | SAFE — ACCEPTED DECISION | S1 §3; S2 §§1–3 | Yes, semantic rule | No (decision) | Historical outcomes are fitting/evaluation labels only. |
| C02 | Dispatch-side storage operator is the MVP design persona. | SAFE — ACCEPTED DECISION | S4 D1 | Yes, design label | No (decision) | Real authority remains UNKNOWN. |
| C03 | Severity score is bounded [0,1] with null bands. | SAFE — ACCEPTED DECISION | S3 D2; S4 D4 | Yes, semantic rule | No (decision) | Meaning and exclusions in §4. |
| C04 | Same-engine order is `risk.score DESC, batch_id ASC`. | SAFE — ACCEPTED DECISION | S3 D3; S4 D2 | Yes, rule only | No (decision) | No mixed tier/version queue; ties do not imply differences. |
| C05 | Horizon is unavailable; baseline factors empty; recommendation null. | SAFE — ACCEPTED DECISION | S3 D6/D9; S4 D4/D5 | Yes, policy | No (decision) | Outcome 3 partial; Outcomes 2/4 unsupported. |
| C06 | Unassessed means no score; exclude from numeric ranking. | SAFE — ACCEPTED DECISION | S3 D3/D7; S4 D3 | Yes, with accepted copy | No (decision) | No fabricated score or disposition. |
| C07 | Telemetry remains canonical; C+L is only a future candidate. | SAFE — ACCEPTED DECISION | S2; S3 D10; S4 D6 | Yes, bounded | No (decision) | No learned-engine selection. |
| C08 | Replay window uses dispatch clock; facility is context filter. | SAFE — ACCEPTED DECISION | S4 D2 | Yes, intended semantics | No (decision) | Exact duration and capacity unresolved. |
| C09 | Supplied observations do not establish exact deterioration onset. | SAFE — ACCEPTED EVIDENCE | S6 VDR-03; S3 D6 | Yes, supplied-data limit | Yes, latest evidence | Not a new agricultural finding. |
| C10 | VDR-04A learned models provide offline feasibility evidence only. | SAFE — ACCEPTED EVIDENCE | S6 VDR-04A; S3 evidence base/D5 | Yes, offline qualifier | Yes, latest evidence | No numerical metric copied. |
| C11 | VDR-06A reports P1/P2 baseline parity PASS. | SAFE — COMMITTED EVIDENCE WITH STATUS QUALIFIER | S7 §§8/10 and JSON `reference_parity` | Yes, full §4 qualifier | Yes | Evaluated earlier base; no service/API validation. |
| C12 | Tested telemetry aggregates showed no stable marginal lift with logistics. | SAFE — COMMITTED EVIDENCE WITH STATUS QUALIFIER | S13; S4 D6 | Yes, tested configurations only | Yes | DRAFT FOR REVIEW — EVIDENCE ONLY. |
| C13 | Canonical ingestion and crop-median fitting/scoring exist. | SAFE — VERIFIED IMPLEMENTATION AT BASE | S8; S9 | Yes, base-qualified | YES | Source inspection, not a fresh runtime test. |
| C14 | IGR-04B constructs scored assessments with explicit provenance. | SAFE — VERIFIED IMPLEMENTATION AT BASE | S10 | Yes, internal service only | YES | Fitted baseline required; §5 output limits. |
| C15 | Public HTTP path exposes health and a synthetic fixture. | SAFE — VERIFIED IMPLEMENTATION AT BASE | S11; S12 | Yes, synthetic qualifier | YES | No real assessment HTTP endpoint or ranked queue. |
| C16 | Current shell renders one synthetic card and unavailable notices. | SAFE — VERIFIED IMPLEMENTATION AT BASE | S12 | Yes, source-inspected scope | YES | No target dashboard completion claim. |
| C17 | Final demo can show ranked assessments, detail, explanation and replay controls. | CONDITIONAL — REVERIFY BEFORE DEMO | S4 intent; S11–S12 current absence | No, until implemented and verified | YES | §6 target beats; no prediction of delivery. |
| C18 | Biological timing or effective intervention can be produced now. | UNSUPPORTED | S3 D6/D9; S4 D5; S10 | No | New evidence/decision required | Null outputs do not fulfill the outcomes. |
| C19 | Operator authority, actual SOP, shift capacity and window duration are known. | UNKNOWN | S4 D1–D3; S15 UNKNOWN register | No | Evidence/decision required | Do not invent. |
| C20 | Current UI is an end-to-end baseline assessment product. | FORBIDDEN | S10–S12 | No | Implementation and verification required | Service capability is not public integration. |
| C21 | Forbidden business, quality, intervention and adoption assertions in §8. | FORBIDDEN | S3 D2/D6–D10; S4 D1/D4–D6; S5 | No | Separate evidence/decision required | Apply F01–F08 to every presenter surface. |

## 8. Forbidden claims and what we deliberately do not invent

These are **FORBIDDEN claim examples**, not product assertions or actions:

| ID | FORBIDDEN wording / interpretation | Boundary source |
| --- | --- | --- |
| F01 | Guaranteed food-loss reduction; proven to reduce losses; measured financial savings; ROI; labour reduction; throughput improvement. | S3 D9; S4 D5: no measured business effectiveness. |
| F02 | Production accuracy guarantee; 100% accuracy; confidence percentage; calibrated confidence; “0.82 = 82% probability”; real-world accuracy validated by parity. | S3 D2/D7; S7 §10: score meaning and parity limits. |
| F03 | Real-time spoilage prediction or prevention; exact time-to-spoilage; shelf-life countdown; hours remaining; days remaining. | S3 D6; S6: onset unsupported. |
| F04 | Validated physical recommendations; autonomous decisions; pre-cool, reroute, hold shipment, release shipment, inspect, discard, change carrier, expedite, send to QC or reject batch as system instructions. | S3 D9; S4 D1/D5: no admitted action catalogue or authority. |
| F05 | Causal feature attribution; Batch Context as score drivers; validated risk bands; traffic-light classifications; an unassessed batch means low risk, high risk or safe. | S3 D2/D8; S4 D3/D4. |
| F06 | Real Moldova warehouse deployment; real customer adoption; real operator SOP; a sponsor-defined job title or verified operator powers. | S4 D1; S5: simulation and persona limits. |
| F07 | AI model / advanced ML / validated production AI describing the current baseline; HGB/Ridge as current runtime; first in Moldova; world-first; industry-leading; state of the art. | S3 D5; S4 D6; S5: no selected learned engine or novelty evidence. |
| F08 | Telemetry is useless; remove telemetry; telemetry improves production prediction; telemetry enables equipment monitoring or detects refrigeration failures; C+L is selected architecture; PUX-10A complete. | S3 D10; S4 D6; S11–S13: unsupported utility, selection and completion. |

**Evidence discipline:** no deterioration countdown, risk bands, calibrated confidence, causal attribution, action recommendation, financial savings claim or fabricated score for `insufficient_data`. These are limitations, not functionality or marketing differentiation. Missing assessment must never be represented as zero risk.

## 9. UI wording handoff

Copy guidance only, not a new layout specification or a claim that these surfaces are already implemented. Existing ADR semantics govern placement/separation. Reverify actual screens before use.

| UI surface | Preferred wording | Semantic boundary | Source |
| --- | --- | --- | --- |
| Risk score label | Predicted loss severity score (0–1) | No percentage interpretation or bands; score only when assessed. | S3 D2; S4 D4 |
| Insufficient-data title | Not assessed / Incomplete data | No predictive score; excluded from numeric ranking. | S4 D3 |
| Insufficient-data message | No predictive score is available for this batch because required inputs were not satisfied. This does not mean low or high risk. Smart Harvest does not determine the operational disposition of this batch. | Exact accepted copy; no routing instruction. | S4 D3 |
| Deterioration unavailable | Not estimable from supplied observations | No date, interval or countdown. | S3 D6 |
| Recommendation unavailable | Action recommendations are unavailable. Current evidence does not validate intervention effectiveness. Smart Harvest prioritizes batches for review but does not prescribe an operational action. | Exact accepted target copy; prioritisation is intended scope, not proof of a current queue. For today's fixture, presenter explicitly states the §5 limitation. | S4 D5 |
| How this score is computed | The deterministic baseline uses the historical training median loss for this crop, or the global training median for an unseen crop. The estimate is clipped to [0,100] and divided by 100. | Algorithm description only; no individual feature attribution. | S3 D5; S4 D4; S9 |
| Batch Context disclaimer | Context only; contribution to this score has not been established. | Context fields are not causes or score contributions. | S4 D4 |
| Simulation notice | SIMULATION / synthetic fixture / not challenge data | Exact current fixture notice; never describe this output as an evaluated batch or baseline result. | S11 |

## 10. Final pitch refresh checklist — RUN BEFORE VLD-05

- [ ] Record latest main SHA and the exact commit actually demonstrated; reconcile changes since the APR-03A base.
- [ ] Inspect current API endpoints and verify their actual responses; distinguish service-only capability from HTTP integration.
- [ ] Inspect current frontend surfaces and PUX implementation state; verify target beats individually.
- [ ] Record actual engine tier/version, contract version and provenance; confirm same-engine comparability and tie handling.
- [ ] Verify runtime assessment path and baseline artifact/fitting lifecycle, including training/inference separation.
- [ ] Verify whether a ranked queue exists; check unassessed exclusion and separation without invented membership or capacity.
- [ ] Verify replay/facility controls against accepted dispatch clock and context-filter semantics.
- [ ] Review latest VDR evidence, its evaluated commit, protocol and epistemic status; do not silently upgrade parity to operational validity.
- [ ] Trace simulation versus non-simulation paths and dataset provenance; keep training data distinct from the synthetic fixture and commercial deployment.
- [ ] Capture actual screenshots from the demonstrated build; verify score meaning, context disclaimer, unavailable notices and simulation labeling.
- [ ] Record exact executed tests, commands, exit codes and outputs; source inspection alone is not a runtime pass.
- [ ] Check `docs/demo_runbook.md` accuracy against the demonstrated path, including score wording.
- [ ] Check `README.md` implementation-state accuracy; reconcile stale summaries through separately authorized work.
- [ ] Re-audit every slide, spoken claim and UI string against this registry and latest accepted decisions/evidence.

APR-03A prepares a bounded claim/narrative source. VLD-05 performs the final evidence and consistency audit. APR-03A does NOT approve the final pitch.

## 11. Takeover and completion boundary

APR-03A was executed by Vladimir as a temporary takeover during Alisa's unavailability. This execution does not change Product Owner assignment or permanently transfer the Product workstream. Alisa retains product ownership; Vladimir remains Integrator/final human gate. Execution != acceptance, including when the executor and Integrator are the same person.

No new product decision is introduced. Retained UNKNOWNs are not resolved here. Any proposal requiring a new persona, threshold, recommendation, queue-membership rule, action, model policy or business KPI must be recorded as **NEW DECISION REQUIRED — NOT RESOLVED IN APR-03A** and taken to the appropriate decision process; a material dependency stops synthesis.

Only this new document is in APR-03A write scope. No source document, application file or evidence artifact is changed. No fresh application tests, runtime demo or evaluation rerun are claimed by this narrative.

**STOP FOR PROJECT BRAIN REVIEW**

No commit, push, PR creation or merge before review and subsequent Human integration gate.
