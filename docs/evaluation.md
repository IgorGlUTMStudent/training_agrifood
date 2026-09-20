# Evaluation principles

**History:** This document previously left target, baseline and split policy open pending reconnaissance. VDR-04A is now ACCEPTED / INTEGRATED through [PR #20](https://github.com/Slave-of-Skynet/training_agrifood/pull/20). Vladimir approved [ADR 0003](decisions/0003-assessment-evaluation-semantics.md) on 2026-09-20, with D3/D4 overrides. The accepted semantics below do not implement an evaluation harness or select a production learned engine.

The project makes no production accuracy, agronomic validity, loss-reduction or financial-savings promise. Accepted benchmark observations are bounded to their dataset, features and protocols.

## Sponsor-defined prediction boundary

- The prediction/assessment moment is dispatch: `T_assess = T_dispatch`, using the sponsor-defined dispatch semantics.
- Predictive features must be information genuinely available at or before that moment. Eligible candidates may include batch/agronomic metadata, storage history and telemetry up to dispatch, pre-dispatch inspection, and transport information that was planned or known at dispatch.
- Arrival-stage inspection cannot be required by the predictive path.
- Actual post-dispatch delay, transit incidents, realized transport outcomes, unavailable post-dispatch telemetry, final outcomes, and equivalent future observations must not influence a dispatch prediction.
- Public historical files may contain future or arrival-stage information for retrospective analysis. Public availability does not make it admissible at inference time, and hidden evaluation may withhold it entirely.
- Storage sessions connect batches to zones and therefore to zone telemetry. Accepted VDR-02 investigated shared-zone/shared-time structure and demonstrated that in standard randomized 80/20 train/test splits of batches, an average of 95.79% of test batches share an identical chamber microclimate cluster with training batches. Conversely, naive chronological splitting causes severe seasonal crop disappearance (summer crops drop to 0.0% in test). Both random batch splitting and naive chronological splitting have documented limitations, and shared-zone/shared-time dependence must be accounted for. VDR-04A has now tested the candidate protocols; ADR 0003 adopts P1 as primary and P2 as mandatory robustness. Residual facility/zone dependence and external generalisation remain unresolved.

## Principles

- Implement and evaluate a deterministic baseline before introducing a complex model.
- Compare any learned model against that baseline on the same defensible split and metrics.
- Make no accuracy claim without usable, well-defined labels and known label provenance.
- Consider temporal leakage and group/entity leakage whenever the observed data structure makes them applicable.
- Prohibit false precision: unsupported scores, horizons, confidence values, and impact estimates must remain absent.
- Keep evaluation metrics dataset- and task-dependent; do not set arbitrary numerical acceptance thresholds.
- Evaluate graceful degradation and reliability communication, not only predictive output.
- Record dataset version, engine version, evaluation procedure, and known limitations with every result.

## Accepted policy — DECISION, ADR 0003 D1–D5

- **Task/target:** Dispatch-time batch prioritisation; `loss_fraction_pct` is the offline supervised label, never an inference input. Historical `quality_status` is a derived evaluation representation.
- **Primary — P1 Forward Inter-Season Holdout:** Train on operational Season 2024 (900 batches, dispatches 2024-05-25 through 2025-04-11); test on Season 2025 (900 batches, dispatches 2025-05-25 through 2026-04-03). These are operational seasons, not calendar-year partitions. The observed hiatus is 43.97 days, with zero cross-season chamber overlaps.
- **Mandatory secondary robustness — P2 Chamber-Time Grouped OOF:** Five folds, with each of the 157 chamber-time connected clusters confined to one validation fold; aggregate held-out predictions over 1,800 batches. P2 checks grouped generalisation and does not replace prospective P1 evaluation or prove independence from every site effect.
- **P3 random split:** NON-DEFENSIBLE DIAGNOSTIC only. Its 94.44% test-batch chamber-cluster overlap with training precludes its use for product-performance claims. The performance difference from P1 also involves season shift; it does not isolate the causal effect of chamber overlap.
- **Deterministic evaluation/runtime baseline:** Crop-conditioned training median `loss_fraction_pct`, with global training median fallback for an unseen crop. Fit medians exclusively on the relevant split/fold's training labels; inference uses `crop_type`, not historical outcomes. Missing required crop input is not automatically equivalent to an unseen crop. A baseline is required before a complex model; no production learned model/engine is selected or required by VLD-02B.
- **Score:** `clip(predicted_loss_fraction_pct, 0, 100) / 100`, including the baseline median estimate. This bounded severity score is not probability or confidence; `risk.band = null`.
- **Operational ranking:** `risk.score DESC`, then `batch_id ASC`. IDs are excluded from predictive features. A common ranked queue may contain only one `engine_tier + engine_version`; different tiers/versions require separate comparability validation before mixing. Fallback/degraded assessments must be separated or identified without automatically creating a mixed ranking. Unassessed results have no score, not a zero-risk score.

### Canonical reporting set — DECISION

| Purpose | Metrics | Interpretation |
| --- | --- | --- |
| Ranking | Spearman; NDCG@10; NDCG@50; Precision@10; Precision@50; Recall@10; Recall@50 | Report ordering quality and both retrieval precision and coverage; small-K priority is not exhaustive screening |
| Continuous-loss diagnostics | MAE; RMSE; R²; Spearman | MAE/RMSE in loss percentage points; point-estimate superiority is metric-dependent |

Precision/Recall use historical `loss_fraction_pct >= 15%` as evaluation relevance only. NDCG in the accepted benchmark uses continuous loss relevance. The ≥5%, ≥15% and ≥35% probes are not production risk-band or alert thresholds. Compare candidate engines against the crop-median baseline on the same partitions and metrics. No arbitrary numerical pass/fail target is adopted.

### Evidence interpretation and implementation limits

**OBSERVED RESULT:** [VDR-04A](data_recon/04_dispatch_predictability.md) and its [JSON](data_recon/04_dispatch_predictability_results.json) show limited/context-specific point-prediction lift and meaningful ranking lift, strongest with the jointly tested planned-logistics family. Non-logistics ranking is protocol/model-dependent, not impossible. Individual logistics contributions and causal effects are unestablished. Under ADR 0003 D4, logistics remain optional/conditionally eligible and may support a future learned engine only if it is separately accepted.

**DECISION:** Retain canonical telemetry and require a direct logistics-enabled with/without-telemetry comparison before claiming safe learned-model removal. F1→F2 did not show stable material marginal lift, but context plus logistics without telemetry was not tested.

**FACT:** Benchmark ranking metrics were calculated on prediction arrays. Its Precision/Recall ranking explicitly resolves ties by batch ID; NDCG is calculated directly by `ndcg_score`, separately from that order. Subsequent harness documentation must preserve the actual metric definitions and distinguish raw benchmark predictions from clipped runtime scores, which can introduce ties. Do not silently treat historical metrics as validation of a mixed-engine operational queue.

**DECISION:** Preserve D6–D9: null horizon, unavailable reliability with null confidence, engine-specific sufficiency, factual/verified non-causal factors (empty allowed), and null recommendations. Optional channel missingness and the 204 truncated histories are not automatic rejection grounds. VDR-04A evaluated all 900 P1 test batches and reported truncation subgroups; the subgroup difference is confounded by crop/season composition, not validation of a staleness cutoff. Exact engine missing-input behavior remains for later contracts.

## Remaining UNKNOWNs

Numerical acceptance targets, operational queue membership/capacity, cross-tier/version comparability, error costs, external crop/facility generalisation, residual site dependence, exact engine minimums and missingness treatment, feature windows/subset, model family/hyperparameters, probability/confidence calibration, operational bands/alerts, agronomic/onset thresholds and action utility remain unresolved. Runtime null/unavailable policies resolve current representation, not biological timing or intervention efficacy. The full retained register is [assumptions_unknowns.md](assumptions_unknowns.md).
