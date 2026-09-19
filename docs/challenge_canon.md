# Challenge canon

## Status and scope

**FACT:** Smart Harvest: Reduce Post-Harvest Losses is a **SIMULATION / training challenge** for the SoS AgriFood team. It is not evidence of a real provider requirement or a production commitment.

**FACT:** The repository now contains the supplied training challenge materials under `sponsor_pack/`: the challenge brief, sponsor README, eight relational CSV tables, and `sponsor_pack/data/data_dictionary.xlsx`.

**FACT:** Those supplied materials document a relational source structure, declared field names and types, dispatch-time assessment semantics (`T_assess = T_dispatch`), historical outcome fields, and a public/hidden temporal restriction. This records what the training package supplies; it is not evidence about a real GigaHack provider or real commercial operations.

**FACT:** For predictive assessment, only information available at dispatch is eligible. Arrival inspection, actual post-dispatch delay or incidents, post-dispatch telemetry unavailable at assessment, final outcomes, and equivalent future observations are forbidden prediction inputs. Their presence in public historical files permits retrospective analysis, not inference-time use.

**FACT — accepted snapshot inventory evidence:** [VDR-01](data_recon/01_dataset_inventory.md), accepted and integrated through [PR #7](https://github.com/Slave-of-Skynet/training_agrifood/pull/7), empirically inspected the supplied snapshot. It established observed schemas/types, row counts and file sizes, PK/FK integrity, observed relationships/cardinalities, sampling/coverage characteristics, missingness and selected data-quality anomalies, and crop/cultivar and historical outcome coverage. These findings update the earlier pre-profiling state; they do not guarantee the same structure or quality in future data.

**FACT — accepted snapshot temporal/leakage evidence:** [VDR-02](data_recon/02_temporal_leakage.md), accepted and integrated through [PR #14](https://github.com/Slave-of-Skynet/training_agrifood/pull/14), audited temporal chronology, assessment boundaries, and leakage risks. Across all 1,800 batches, observed physical events follow an ordered physical actual-event sequence with 0 sequence violations: $T_{harvest} < T_{harvest\_qc} < T_{entry} < T_{pre\_dispatch\_qc} < T_{dispatch} \le T_{actual\_departure} < T_{actual\_arrival} = T_{arrival\_qc}$. The prediction cutoff boundary is $T_{assess} \equiv T_{dispatch} = \text{storage_sessions.dispatch_datetime}$. Pre-dispatch features (intake descriptors, storage session context, zone/facility specifications, harvest and pre-dispatch quality checks) are physically available prior to release, while post-dispatch fields (arrival QC, actual departure/arrival/delay, in-transit telemetry and incidents, destination outcomes) represent severe future/target leakage and are strictly forbidden prediction inputs. Telemetry logging terminates globally on 2025-12-31 23:30:00, leaving 204 batches (11.33%, primarily apples and pears) dispatched in 2026 with pre-dispatch telemetry gaps of 0.56 to 92.54 days, while non-truncated batches exhibit maximum staleness of 29.4 minutes at dispatch. 1,734 of 1,800 batches (96.33%) concurrently share storage chambers, forming 157 disjoint chamber-time clusters; in standard randomized 80/20 train/test splits, an average of 95.79% of test batches share an identical chamber microclimate cluster with training batches, while naive chronological 70/30 splitting causes complete disappearance of summer crops from the test partition.

**DECISION — accepted predictive-input semantics (ADR 0002 / VLD-02A):** [ADR 0002](decisions/0002-predictive-input-semantics.md), accepted under VLD-02A through [PR #16](https://github.com/Slave-of-Skynet/training_agrifood/pull/16), established canonical predictive-input semantics for dispatch-time assessment ($T_{assess} \equiv T_{dispatch}$). It defined canonical entity boundaries, authoritative identity sources, a 73-field eligibility taxonomy, strict exclusion of arrival/in-transit/outcome leakage, bounding of telemetry to storage stay ($T_{entry} \le t \le T_{dispatch}$), explicit missingness / zero-fabrication rules, and the canonical `BatchAssessmentInput` specification. It does not establish production code implementation, feature-engineering windows, target, metric, evaluation split, runtime deterioration-horizon policy, risk formula, baseline/model, reliability policy, or action effects.

**FACT — accepted target and deterioration-horizon feasibility evidence (VDR-03):** [VDR-03](data_recon/03_target_horizon_feasibility.md), accepted and integrated through [PR #18](https://github.com/Slave-of-Skynet/training_agrifood/pull/18), profiled candidate outcomes and deterioration timing. Four complete historical candidate outcome fields exist for all 1,800 batches in `historical_quality_outcomes.csv`: `quality_status`, `loss_fraction_pct`, `quality_score`, and `economic_loss_eur`. `quality_status` is reproduced by observed `loss_fraction_pct` intervals ($[0,5)\%$, $[5,15)\%$, $[15,35)\%$, $[35,100]\%$) with zero mismatches in the supplied snapshot. `economic_loss_eur` is deterministically reproduced from loss fraction $\times$ harvest weight $\times$ inferred crop unit price. `quality_score` is strongly correlated ($r = -0.9727$) with `loss_fraction_pct`, but its exact generation rule remains undocumented. Quality inspections occur at exactly three discrete checkpoints per batch (`harvest`, `pre_dispatch`, `arrival`); no intermediate quality inspections exist during storage or transit. No exact deterioration-onset timestamp is observed.

**INFERENCE / evidence conclusion:** Exact continuous deterioration timing is not supportable from the current observations.

**UNKNOWN / decisions still required:** production implementation of canonical mapping; feature transformations and aggregation windows; minimum required telemetry sufficiency, staleness policy, and missing-data treatment; primary production target, task framing, and target interpretation; final evaluation protocol and selected split; baseline selection and model comparison/justification; runtime deterioration-horizon representation and policy; reliability policy; agronomic rules; validated action effects; and business/loss-reduction claims. Historical outcome relationships do not establish deterministic prediction from dispatch-time inputs, and VDR-03 explicitly did not select a production target or runtime deterioration-horizon policy.

## Required operator outcomes

The intended product should help an operator understand:

1. which batches are most at risk;
2. when quality may begin to deteriorate;
3. which factors contribute to the risk;
4. which action should be prioritized to reduce losses.

These are desired challenge outcomes, not proof that the present foundation computes them. The current synthetic response reports `insufficient_data`.

## Evaluation criteria

- Agricultural and business usefulness.
- Accuracy and reliability.
- Usability and explainability.
- Potential reduction of food loss.
- Scalability.
- Innovation.

Metrics, targets, thresholds, and claims remain **UNKNOWN** until dataset and domain reconnaissance provides evidence.

## Canon rule

Every future claim must be classified:

- **FACT** — directly supported by supplied challenge material or validated evidence.
- **DECISION** — an explicit engineering/product choice with recorded rationale.
- **UNKNOWN** — unresolved and not safe to treat as fact.

Assumptions used for experiments must remain visibly labeled and must not silently enter production semantics.
