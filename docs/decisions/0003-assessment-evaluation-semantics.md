# ADR 0003 — Assessment, Ranking and Evaluation Semantics

- **Status:** ACCEPTED HUMAN DECISION; Phase B canonical recording prepared for Project Brain review. Not yet committed or integrated.
- **Decision owner:** Vladimir — Integrator.
- **Date:** 2026-09-20.
- **Task:** VLD-02B; documentation only, no application implementation.
- **Evidence base HEAD:** `aa5d40bee8368342e7a6b540278c26416cc89457` (PR #20 integrated).

## Human decision provenance

**DECISION — authorization:** After reviewing the Phase A decision packet, Vladimir explicitly wrote: “Одобряю переход VLD-02B к Phase B.” D1, D2 and D5–D10 were “APPROVED as recommended.” D3 was approved with an override restricting a common ranked queue to one `engine_tier + engine_version` until cross-tier/version comparability is separately validated. D4 was approved with a wording override preserving optional/conditionally eligible logistics and allowing their use by a future learned engine only if that engine is separately accepted; VLD-02B neither selects nor requires such an engine. These overrides are normative below.

Vladimir retained all Phase A UNKNOWNs and authorized only this ADR plus synchronization of `challenge_canon.md`, `assumptions_unknowns.md`, `evaluation.md`, and `integration_contract.md`. Verification and STOP for Project Brain review are required; commit, push, PR creation and downstream implementation are not authorized by this task.

## Evidence base

Authority order: supplied sponsor materials → accepted SoS decisions → accepted challenge/data evidence → committed application contracts for implementation state → accepted research evidence → recommendations/inference.

- [Challenge brief](../../sponsor_pack/brief/Training%20Challenge%20%233%20%E2%80%94%20AgriFood.md) and [sponsor README](../../sponsor_pack/README.md): desired operator outcomes and fixed dispatch assessment boundary.
- [ADR 0002](0002-predictive-input-semantics.md): accepted input semantics, eligibility, missingness and temporal rules; unchanged.
- [VDR-01](../data_recon/01_dataset_inventory.md), [VDR-02](../data_recon/02_temporal_leakage.md), [VDR-03](../data_recon/03_target_horizon_feasibility.md): accepted inventory, chronology, leakage, outcome and onset evidence.
- [VDR-04A](../data_recon/04_dispatch_predictability.md) and [results JSON](../data_recon/04_dispatch_predictability_results.json): ACCEPTED / INTEGRATED evidence through [PR #20](https://github.com/Slave-of-Skynet/training_agrifood/pull/20). The report's historical draft heading is retained; evidence acceptance does not adopt its recommendations.
- APR-01 [context inventory](../product_recon/01_context_inventory.md), [research questions](../product_recon/02_research_questions.md), [source map](../product_recon/03_source_map.md), and [evidence map](../product_recon/04_evidence_map.md): accepted research evidence through PR #17, not automatically canon or validated action rules.
- [Python output contract](../../backend/app/domain/assessment.py), [TypeScript contract](../../frontend/src/api/contracts.ts), [data contract](../data_contract.md), [domain guard](../domain_rules.md), and [architecture](../architecture.md): existing schema and implementation boundaries; unchanged.

## Context — FACT / OBSERVED RESULT

- **FACT:** `T_assess = T_dispatch`. Arrival QC, actual transit realizations, observations after dispatch and historical outcomes are forbidden inference inputs. Outcomes are available only on the historical training/evaluation label side.
- **FACT:** `quality_status` follows observed loss intervals; `economic_loss_eur` is derived from loss fraction, weight and inferred crop price. `quality_score` is strongly associated with loss, but its exact generation rule is undocumented. Three discrete QC checkpoints provide no exact biological onset timestamp.
- **OBSERVED RESULT:** Continuous point-prediction lift is LIMITED / CONTEXT-SPECIFIC. P1 crop-median MAE is 8.8842 versus F3 HGB 8.9664 percentage points; R² is 0.0737 versus 0.2799. Superiority depends on the metric.
- **OBSERVED RESULT:** Ranking lift is demonstrated, strongest with planned logistics and protocol/model-dependent without them. F3 nonlinear NDCG@10 is 0.8831 in P1 and 0.8888 in P2; Precision@10 is 1.00 in both, but Recall@10 is only 0.0333 and 0.0158. P2 F1 linear NDCG@10 is 0.5977 versus crop-median 0.2533: ranking without logistics is not impossible.
- **OBSERVED RESULT:** The jointly tested planned-logistics family gives the strongest consistent incremental association among tested feature families. Individual contributions and causal effects were not independently established.
- **OBSERVED RESULT:** Tested telemetry aggregates show no stable material incremental lift in F1→F2. F3 includes context, telemetry and logistics; context plus logistics without telemetry was not separately tested.
- **FACT — implementation state:** At the evidence base, ingestion and analytics contain only initializer files, and the application returns a synthetic insufficient-data fixture. Benchmark code is evidence, not a production analytics engine.

## Accepted decisions D1–D10

### D1 — Primary task and target

**DECISION:** The primary operational task is batch prioritisation/ranking at dispatch. The primary offline supervised analytical target is `loss_fraction_pct`, representing historical percentage of harvest weight condemned/lost at destination. It is a training/evaluation label, never an inference input.

`quality_status` remains a derived historical/evaluation representation. The ≥5%, ≥15% and ≥35% probes are analytical/evaluation boundaries only. In particular, ≥15% is not a production high-risk, risk-band or operator-alert threshold. Neither monetary loss nor `quality_score` is selected as the primary target.

### D2 — Risk score and band

**DECISION:** `risk.score` is a bounded degradation/loss-severity score derived monotonically (non-decreasingly) from predicted loss:

```text
score = clip(predicted_loss_fraction_pct, 0, 100) / 100
risk.band = null
```

The deterministic baseline uses the same transformation on its fitted median estimate. Higher means greater predicted loss severity. The score is not a probability, calibrated confidence, guaranteed future loss or causal impact estimate. Risk bands remain null until separately validated policy exists; no arbitrary cutoffs are adopted.

### D3 — Ranking and comparability (human override)

**DECISION:** Rank assessed batches by `risk.score DESC`, then `batch_id ASC` for deterministic order stability. `batch_id` remains forbidden as a predictive feature. An `insufficient_data` result has no score and must not be interpreted as zero-risk.

A common ranked queue is permitted only for results with the same `engine_tier + engine_version`. Results from different tiers or versions must not automatically be merged into one ranking queue until a separate validation establishes cross-tier/version comparability. Until then, fallback/degraded-engine assessments must be explicitly separated or identified; identification does not itself authorize a mixed ranked queue.

Ranking is prioritisation, not exhaustive screening: small-K recall is low. Use “priority,” “higher predicted risk,” or “higher assessment score”; do not claim guaranteed highest loss, certain spoilage or a discard instruction.

### D4 — Planned logistics (human wording override)

**DECISION:** `planned_logistics` remains optional / conditionally eligible under ADR 0002, including its dispatch-time availability conditions.

**OBSERVED RESULT:** VDR-04A establishes that the planned-logistics feature family produced the strongest and most consistent incremental association among the tested feature families. This is neither an individual-feature attribution nor a causal finding.

**DECISION:** A future learned ranking engine may use this family if that engine is separately accepted. VLD-02B does not select or require a production learned model/engine. Missing planned logistics alone does not make ranking impossible. An accepted weaker engine/baseline may be a future fallback, but exact selection and routing remain for a subsequent implementation contract; provenance and D3 segregation apply.

### D5 — Evaluation protocol, baseline and metrics

**DECISION:** Primary evaluation is **P1 — Forward Inter-Season Holdout** (operational Season 2024 training, 900 batches; Season 2025 testing, 900 batches). Mandatory secondary robustness evaluation is **P2 — Chamber-Time Grouped OOF** (five folds, 157 chamber-time clusters, 1,800 batches). P2 is not a substitute for forward-season evidence. **P3 — random split with chamber overlap is a NON-DEFENSIBLE DIAGNOSTIC** and cannot support product-performance claims.

The evaluation/runtime deterministic baseline is the crop-conditioned **training** median `loss_fraction_pct`, with the global **training** median for an unseen crop. Outcomes are used only during fitting; inference uses `crop_type`. In evaluation, fit each baseline only on that split/fold's training partition. An unseen crop fallback does not establish generalisation quality and does not authorize treating a missing required crop field as valid.

Canonical ranking metrics are Spearman, NDCG@10, NDCG@50, Precision@10, Precision@50, Recall@10 and Recall@50. Precision/Recall use historical loss ≥15% as evaluation relevance only; benchmark NDCG uses continuous loss relevance. Retain MAE, RMSE, R² and Spearman as continuous-loss diagnostics. Compare candidate engines and the baseline on identical defensible partitions and metrics; no numerical pass/fail threshold is adopted.

### D6 — Deterioration horizon

**DECISION:** `deterioration_horizon = null` for all current analytical engines. Communicate “not estimable from supplied observations.” The nullable API field remains for forward compatibility. Neither exact countdowns nor coarse intervals are authorized by current evidence.

### D7 — Reliability and data sufficiency

**DECISION:** Until a separate validated reliability/calibration policy exists:

```text
reliability.level = unavailable
reliability.confidence_score = null
```

Factual limitations may be conveyed through `reason_codes` and `missing_requirements`. Do not invent confidence percentages or low/medium/high reliability thresholds.

**DECISION:** `assessed` means the selected engine can produce its accepted risk output from the inputs required by that engine version. `insufficient_data` means that engine cannot meet its declared minimum input requirements. An assessed result requires non-null risk; insufficient data requires both risk and horizon to be null. Ability to assess is distinct from calibrated reliability.

Optional telemetry-channel absence does not automatically imply insufficient data. Non-CA CO2/O2 nulls are legitimate structural missingness; ZONE-006 surface-temperature absence is legitimate observed missingness. The 204 truncated batches must not be rejected solely for telemetry truncation. No arbitrary staleness cutoff is adopted. Exact engine minimums remain for a later implementation contract and do not relax ADR 0002's canonical-input requirements or missingness rules.

### D8 — Factors and explanation

**DECISION:** An `AssessmentFactor` may describe factual data-quality/context conditions or a verified contribution to model output produced by an accepted explanation method. `increases_risk` / `decreases_risk` means contribution to the assessment, not a biological cause. A factual condition without verified directional contribution uses `effect = unknown`.

Until an explanation mechanism is implemented and verified, `factors` may remain `[]`. Do not fabricate factors to populate the UI or claim that changing a field will reduce actual loss. No explanation algorithm is selected.

### D9 — Recommendations and actions

**DECISION:** Current predictive production output uses `recommendation = null` until a separate domain/action evidence gate. Future informational human-review/process actions may be considered only with accepted traceable evidence, no causal-effectiveness claim, and `requires_human_review = true`; none is admitted here.

No intervention efficacy, prevented-loss estimate or financial-savings claim is authorized. Historical economic-loss reconstruction does not establish action benefit.

### D10 — Telemetry scope

**DECISION:** Keep telemetry in canonical-input semantics. Do not expand into complex waveform/sliding-window engineering without new evidence, and do not claim that telemetry materially improves production prediction. The final learned-model feature subset remains an implementation/evaluation question.

Weak F1→F2 lift does not authorize removing telemetry from a final learned model. A simplification proposal must directly compare logistics-enabled models with and without telemetry. The deterministic crop-median baseline does not require telemetry for scoring; this says nothing about the final learned subset and does not change the canonical schema.

## Rejected alternatives

**DECISION — not adopted in this gate:**

- Binary severe-loss classification or exact continuous point prediction as the primary product task; the former lacks accepted operational threshold meaning, and the latter has metric-dependent lift.
- Probability/confidence interpretation of the severity score, arbitrary risk bands, and unsupported confidence values.
- Automatic ranking across engine tiers/versions; another queue objective such as FIFO, FEFO or financial ordering without its own evidence and decision.
- Mandatory canonical logistics or selection/requirement of a production learned engine from the benchmark.
- P2 as primary evaluation in place of P1, global-median-only baseline, or P3 as defensible product-performance evidence.
- Fabricated deterioration intervals/countdowns, blanket rejection of legitimate missingness/truncation, causal factors, intervention prescriptions or savings estimates.
- Removal of learned-model telemetry based solely on F1→F2 results.

These rejections preserve future evidence-backed reconsideration; they do not rewrite the historical reports.

## Consequences and implementation implications

**DECISION:** Semantics conceptually unblock a bounded deterministic baseline implementation contract, bounded analytics-engine implementation planning, UX reconciliation and an evaluation-harness contract. This ADR implements none of them and does not authorize starting downstream work in VLD-02B.

IGR-03 retains ADR 0002's accepted input semantics but must respect actual IGR-02 integration state. No integrated raw ingestion implementation exists at this base. Engine minimums, fitted artifact/version management, missing-input behavior and fallback routing need subsequent bounded contracts. No backend/frontend, public schema, enum, bound, dependency, domain-rule register or architecture change is required by these decisions.

## UX implications

**DECISION:** Present score meaning as loss severity used for priority, not probability/confidence or certain future loss. Keep risk bands absent, horizon unavailable, confidence absent and recommendations absent under the current policy. Empty factors are valid. Distinguish unassessed batches from scored batches, and segregate/identify fallback assessments without combining different engine tiers/versions into a ranked queue. Queue membership and operational review capacity remain open.

## Evaluation implications

**DECISION:** Preserve training-only fitting and dispatch-safe inputs, report all accepted metrics and limitations, and keep P1 primary and P2 secondary. Do not turn benchmark results into promised runtime accuracy or model selection. Subsequent evaluation must distinguish raw benchmark predictions from clipped runtime scores: clipping can introduce ties. Benchmark Precision/Recall use deterministic ID tie-breaking, whereas NDCG is calculated directly from prediction arrays; metric implementation details must remain explicit rather than silently assumed identical to the operational queue. See [benchmark ranking implementation](../../scripts/vdr04a_predictability.py).

**UNKNOWN:** Operational queue evaluation, cross-tier/version comparability, exact engine treatment of truncated observations and numerical acceptance targets remain unresolved. VDR-04A's truncated-cohort comparison is confounded by crop/season composition and does not establish a safe freshness threshold or exclusion rule.

## Explicit non-decisions and open UNKNOWNs

The [global UNKNOWN register](../assumptions_unknowns.md) remains authoritative. All unresolved areas from the Phase A packet are retained:

1. Production learned model family, hyperparameters, final feature subset, and acceptance of any production learned engine.
2. Exact engine requirements, fallback routing, cross-tier/version comparability, feature transformations/windows, imputation/repair/exclusion policies and fitted artifact handling.
3. Confidence calibration, risk-band/alert thresholds, telemetry staleness cutoffs and broader reliability validation beyond the current unavailable state.
4. Exact biological deterioration onset, crop-specific event/agronomic thresholds and future interval-estimation feasibility.
5. Explanation algorithm, attribution reference/baseline semantics, validation criteria and operator comprehension.
6. Operator persona, authority, workflow, queue membership, review capacity and permitted action catalogue.
7. Intervention effects, costs, lead times, prevented loss, financial savings and action utility.
8. Broader label/business provenance: quality-score generation, historical status-threshold provenance, inferred-price validity and weak QC/outcome associations.
9. Generalisation to unseen crops/facilities, subgroup sufficiency and residual facility/zone dependence; future-data cardinalities and unseen-value handling.
10. Hosting, persistence, runtime resource needs, realtime workflow requirements and nominal-capacity-exceedance interpretation.

**DECISION — completion boundary:** Submit the documentation and verification evidence for Project Brain review, then STOP. An ACCEPTABLE review is not authorization to commit, push, merge, release, or execute downstream tasks.
