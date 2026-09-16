# Application output contract

**Supplied raw schema:** inspectable in the sponsor CSV headers and `sponsor_pack/data/data_dictionary.xlsx`.

**Accepted production/canonical input model:** not yet defined. The supplied raw schema does not by itself establish validation behavior, observed integrity, canonical mapping, or a production `BatchInput`.

This document specifies the current public output semantics only. It deliberately defines no production `BatchInput` and does not promote raw sponsor fields into an accepted application contract.

## Assessment status

- `assessed` — sufficient evidence exists for an assessment; a risk estimate is required.
- `insufficient_data` — required validated evidence is unavailable; risk and deterioration horizon must both be absent.

The Pydantic model enforces these invariants. Consumers must not derive or display fake values for absent fields.

## `RiskAssessment`

| Field | Shape | Semantics |
| --- | --- | --- |
| `batch_id` | string | Identifier in the assessment context; not a declaration of raw-data field names |
| `status` | assessment status | Whether an assessment could be made |
| `risk` | `RiskEstimate` object or null | The enclosing object may be null. When present, `score` is required and numeric in `[0,1]`; `band` is optional. The score is not necessarily a calibrated probability. An `assessed` result requires this object. |
| `deterioration_horizon` | `DeteriorationHorizon` object or null | The enclosing object may be null. When present, `starts_at` is required and `ends_at` is optional. It must remain null when a horizon is unsupported. |
| `factors` | list of structured factors | Evidence-linked contributors or data-quality blockers |
| `recommendation` | structured object or null | Machine-readable action, priority, rationale codes, and review flag |
| `reliability` | object | Reliability level, optional confidence score, reason codes, and missing requirements |
| `provenance` | object | Contract/engine versions, tier, timestamp, dataset reference, and simulation labeling |

## Structured factor

A factor has a stable `code`, a category, an effect (`increases_risk`, `decreases_risk`, or `unknown`), a human-readable summary, and optional evidence references. A factor is not a causal claim unless its provenance and validation justify that claim.

## Structured recommendation

A recommendation uses an `action_code`, label, priority, rationale codes, and `requires_human_review`. It is not free-form LLM output. The foundation fixture returns no recommendation because validated action evidence is unavailable.

## Reliability and confidence

Reliability is explicit even when unavailable. A numeric `confidence_score` is optional and must not be populated without a defined, validated interpretation. `reason_codes` and `missing_requirements` explain degradation without inventing precision.

## Provenance and implementation tiers

`engine_tier` permits `fixture`, `deterministic_baseline`, or `learned_model`, allowing a future implementation to change tier without changing the public assessment meaning. Contract version, engine version, generation timestamp, optional source-dataset identifier, and a simulation flag preserve traceability.

The current endpoint returns `contract_version: 1.0.0`, an engine tier of `fixture`, and the notice `SIMULATION / synthetic fixture / not challenge data`.
