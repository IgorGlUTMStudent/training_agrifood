# Evaluation principles

The project currently makes no business-accuracy, agronomic-accuracy, loss-reduction, or model-performance claim.

## Sponsor-defined prediction boundary

- The prediction/assessment moment is dispatch: `T_assess = T_dispatch`, using the sponsor-defined dispatch semantics.
- Predictive features must be information genuinely available at or before that moment. Eligible candidates may include batch/agronomic metadata, storage history and telemetry up to dispatch, pre-dispatch inspection, and transport information that was planned or known at dispatch.
- Arrival-stage inspection cannot be required by the predictive path.
- Actual post-dispatch delay, transit incidents, realized transport outcomes, unavailable post-dispatch telemetry, final outcomes, and equivalent future observations must not influence a dispatch prediction.
- Public historical files may contain future or arrival-stage information for retrospective analysis. Public availability does not make it admissible at inference time, and hidden evaluation may withhold it entirely.
- Storage sessions connect batches to zones and therefore to zone telemetry. Accepted VDR-02 investigated shared-zone/shared-time structure and demonstrated that in standard randomized 80/20 train/test splits of batches, an average of 95.79% of test batches share an identical chamber microclimate cluster with training batches. Conversely, naive chronological splitting causes severe seasonal crop disappearance (summer crops drop to 0.0% in test). Both random batch splitting and naive chronological splitting have documented limitations, and shared-zone/shared-time dependence must be accounted for. However, a final evaluation split strategy is not yet selected, and the evaluation protocol still requires separate evidence (VDR-04) and a formal decision.

## Principles

- Implement and evaluate a deterministic baseline before introducing a complex model.
- Compare any learned model against that baseline on the same defensible split and metrics.
- Make no accuracy claim without usable, well-defined labels and known label provenance.
- Consider temporal leakage and group/entity leakage whenever the observed data structure makes them applicable.
- Prohibit false precision: unsupported scores, horizons, confidence values, and impact estimates must remain absent.
- Keep evaluation metrics dataset- and task-dependent; do not set arbitrary numerical acceptance thresholds.
- Evaluate graceful degradation and reliability communication, not only predictive output.
- Record dataset version, engine version, evaluation procedure, and known limitations with every result.

## Dataset-dependent work

Target choice, split design, metrics, error costs, subgroup evaluation, horizon evaluation, thresholds, numerical acceptance targets, and action-utility evaluation remain **UNKNOWN** until the dataset and operator workflow are understood. The dispatch boundary above is fixed even while those choices remain open.
