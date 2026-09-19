# Application data contract

**Accepted production/canonical input model:** defined under [ADR 0002](decisions/0002-predictive-input-semantics.md) as `BatchAssessmentInput`.

The normative raw→canonical mapping for all 73 supplied fields is defined by [ADR 0002](decisions/0002-predictive-input-semantics.md), Field Mapping Matrix.

This document specifies both the canonical predictive input contract (`BatchAssessmentInput`) and the public assessment output contract (`RiskAssessment`).

## Canonical Predictive Input Contract (`BatchAssessmentInput`)

### Assessment Cutoff and Invariant
- **Assessment Moment:** Strictly $T_{assess} \equiv T_{dispatch} = \text{storage_sessions.dispatch_datetime}$.
- **Assessment Clock:** Single source of truth `assessment_context.assessment_timestamp`.
- **Temporal Sequence Invariant:** $T_{harvest} < T_{harvest\_qc} < T_{entry} < T_{pre\_dispatch\_qc} < T_{dispatch}$.

### Field Eligibility Taxonomy
All 73 raw CSV table-field pairs are classified into exact roles:
- **`PREDICTIVE_ELIGIBLE` (25 fields):** Observable and fixed at or before $T_{dispatch}$; authorized candidate features.
- **`STAGE_CONDITIONAL` (4 fields):** `quality_checks.check_datetime`, `firmness_kg_cm2`, `sugar_brix`, `defect_pct`. Eligible strictly for `stage in ('harvest', 'pre_dispatch')`; forbidden for `stage == 'arrival'`.
- **`CONDITIONALLY_ELIGIBLE` (16 fields):** Available before dispatch but conditional on operational booking immutability (`planned_logistics.*`, `planned_dispatch_datetime`) or chamber physics (gas sensors in CA rooms, surface temp in ZONE-006, equipment states).
- **`CONTEXT_ONLY` (10 fields):** Identifiers and metadata retained for identity, provenance, and UI display; strictly prohibited from model features.
- **`LABEL_OR_EVALUATION_ONLY` (4 fields):** Historical outcome fields (`historical_quality_outcomes.*`); strictly forbidden from inference input.
- **`FORBIDDEN_FUTURE` (5 fields):** Post-dispatch transit realizations (`shipments` actual departure/arrival/delay/incidents/telemetry); strictly forbidden from inference input.
- **`RAW_ONLY / NOT NEEDED IN CANONICAL INPUT` (9 fields):** Surrogate keys and duplicate join FKs verified during ingestion and not duplicated in canonical domain entities.

### Telemetry Boundary
Joined via `zone_id` and bounded strictly by `storage_sessions.entry_datetime <= timestamp <= storage_sessions.dispatch_datetime`. Stored as raw typed eligible readings. Feature engineering, aggregation, and imputation are deferred to analytics tasks.


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
