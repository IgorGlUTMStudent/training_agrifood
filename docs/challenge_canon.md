# Challenge canon

## Status and scope

**FACT:** Smart Harvest: Reduce Post-Harvest Losses is a **SIMULATION / training challenge** for the SoS AgriFood team. It is not evidence of a real provider requirement or a production commitment.

**FACT:** The repository now contains the supplied training challenge materials under `sponsor_pack/`: the challenge brief, sponsor README, eight relational CSV tables, and `sponsor_pack/data/data_dictionary.xlsx`.

**FACT:** Those supplied materials document a relational source structure, declared field names and types, dispatch-time assessment semantics (`T_assess = T_dispatch`), historical outcome fields, and a public/hidden temporal restriction. This records what the training package supplies; it is not evidence about a real GigaHack provider or real commercial operations.

**FACT:** For predictive assessment, only information available at dispatch is eligible. Arrival inspection, actual post-dispatch delay or incidents, post-dispatch telemetry unavailable at assessment, final outcomes, and equivalent future observations are forbidden prediction inputs. Their presence in public historical files permits retrospective analysis, not inference-time use.

**FACT — accepted snapshot evidence:** [VDR-01](data_recon/01_dataset_inventory.md), accepted and integrated through [PR #7](https://github.com/Slave-of-Skynet/training_agrifood/pull/7), empirically inspected the supplied snapshot. It established observed schemas/types, row counts and file sizes, PK/FK integrity, observed relationships/cardinalities, sampling/coverage characteristics, missingness and selected data-quality anomalies, and crop/cultivar and historical outcome coverage. These findings update the earlier pre-profiling state; they do not guarantee the same structure or quality in future data.

**UNKNOWN / decisions still required:** detailed assessment-time eligibility pending accepted VDR-02 evidence; production validation and canonical predictive mapping; target choice and label fitness; feature windows and missing-data treatment; split/evaluation protocol; baseline/model performance; deterioration semantics; validated action effects; agronomic thresholds; and business/loss-reduction claims. Historical outcome relationships do not establish deterministic prediction from dispatch-time inputs.

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
