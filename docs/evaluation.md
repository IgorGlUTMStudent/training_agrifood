# Evaluation principles

The project currently makes no business-accuracy, agronomic-accuracy, loss-reduction, or model-performance claim.

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

Target definition, splits, metrics, error costs, subgroup evaluation, horizon evaluation, and action-utility evaluation remain **UNKNOWN** until the dataset and operator workflow are understood.
