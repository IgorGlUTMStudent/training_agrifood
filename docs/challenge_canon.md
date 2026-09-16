# Challenge canon

## Status and scope

**FACT:** Smart Harvest: Reduce Post-Harvest Losses is a **SIMULATION / training challenge** for the SoS AgriFood team. It is not evidence of a real provider requirement or a production commitment.

**FACT:** The repository now contains the supplied training challenge materials under `sponsor_pack/`: the challenge brief, sponsor README, eight relational CSV tables, and `sponsor_pack/data/data_dictionary.xlsx`.

**FACT:** Those supplied materials document a relational source structure, declared field names and types, dispatch-time assessment semantics (`T_assess = T_dispatch`), historical outcome fields, and a public/hidden temporal restriction. This records what the training package supplies; it is not evidence about a real GigaHack provider or real commercial operations.

**FACT:** For predictive assessment, only information available at dispatch is eligible. Arrival inspection, actual post-dispatch delay or incidents, post-dispatch telemetry unavailable at assessment, final outcomes, and equivalent future observations are forbidden prediction inputs. Their presence in public historical files permits retrospective analysis, not inference-time use.

**UNKNOWN pending empirical reconnaissance:** actual data quality, completeness, distributions, observed type consistency, referential integrity, sampling gaps, label usefulness, evaluation design, model performance, validated recommendation effects, and agronomic thresholds. The existence of supplied schema and outcome columns does not establish any of those matters, and this document does not claim that Viktor's profiling has been completed.

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
