# Foundation architecture

## Accepted decision

The application is a modular monolith with a React + TypeScript + Vite operator frontend and a Python + FastAPI + Pydantic backend. The two sides communicate through a typed, versioned HTTP application contract. This is a **DECISION**, not an architecture proposal.

A later deployment may package built SPA assets with the FastAPI service as one artifact. The foundation does not select or configure a hosting platform.

## Boundaries

- `frontend/src/api` — HTTP client and TypeScript representations of public responses.
- `frontend/src/components` and `frontend/src/pages` — operator presentation and connection states.
- `backend/app/api` — versioned HTTP boundary; no business logic.
- `backend/app/domain` — canonical `BatchAssessmentInput` and stable `RiskAssessment` output contracts.
- `backend/app/ingestion` — raw CSV ingestion, structural diagnostics, and raw-to-canonical mapping.
- `backend/app/analytics` — implemented deterministic crop-median baseline (IGR-04A), used by the internal IGR-04B assessment service; artifact loading and HTTP serving remain pending. No production learned engine is selected.
- `backend/app/explain` — future structured explanation boundary.
- `backend/app/recommend` — future structured action boundary.
- `backend/app/services` — application orchestration; contains both the synthetic fixture builder and the implemented deterministic baseline assessment application service (IGR-04B).

ADR 0005 selects a separate validated JSON application artifact for the initial deterministic baseline. Broader persistence remains undecided; no database, ORM, model registry service or migration framework is selected.

## Conceptual flow

```text
Raw/Input Dataset
       ↓
Ingestion + Validation
       ↓
Canonical Representation
       ↓
Feature / Analytics Layer
       ↓
Assessment Engine
       ↓
RiskAssessment
   ↙       ↓       ↘
horizon  factors  quality
       ↓
Explanation + Action Layer
       ↓
FastAPI typed HTTP contract
       ↓
React operator UI
```

Raw ingestion and structural diagnostics, canonical `BatchAssessmentInput`, the raw-to-canonical mapper (IGR-03), deterministic crop-median baseline (IGR-04A), and deterministic baseline assessment service (IGR-04B) are implemented internally. The runtime demo provides the typed `RiskAssessment` output contract, API transport, and a UI rendering a synthetic insufficient-data state. Runtime artifact loading and real assessment HTTP serving are not yet implemented.

## Analytics principles

- A deterministic baseline is mandatory before any complex model.
- A learned/ML tier is optional and dataset-dependent.
- Both tiers must preserve the public `RiskAssessment` semantics.
- `insufficient_data` retains ADR 0003 D7's engine-minimum meaning. ADR 0005's lookup, release-eligibility and service failures use HTTP errors, not fabricated insufficient-data assessments; no new minimum-input policy is introduced.
- Explanations are structured outputs, with version and provenance attached.
- An LLM is outside the risk, causal, numeric, and action-selection path. No LLM integration exists.

## Runtime decisions

- MVP processing is batch/on-demand.
- Streaming, WebSockets, event buses, queues, and distributed services are excluded.
- The backend and frontend remain logical modules of one deployable product.
- Initial baseline artifact serving is accepted under ADR 0005; broader persistence and production operating constraints remain undecided.

### Initial deterministic baseline serving — ADR 0005

**ACCEPTED DECISION — NOT YET IMPLEMENTED:** Vladimir accepted HG-R5 D1–D7 on 2026-09-22; [ADR 0005](decisions/0005-runtime-baseline-serving.md) is authoritative, not the recon recommendations as a whole.

```text
controlled offline baseline artifact
→ lifespan-loaded and validated pinned snapshot + artifact
→ complete runtime context / explicit provider
→ IGR-03 canonical mapper
→ IGR-04B baseline assessment service
→ GET /api/v1/assessments/{batch_id}
```

The initial fit uses the 900 Season-2024 batches with `dispatch_datetime < 2025-05-01`; initial assessment/demo eligibility is the 900 held-out Season-2025 batches with `dispatch_datetime >= 2025-05-01`. Serving is inference-only. No request-time/import-time fitting, automatic refitting, hidden artifact regeneration, background training or hot reload is introduced. VDR-06A evidence JSON is not runtime model state.

The initial concrete engine is `baseline-crop-median-v1-p1-s2024` (family `baseline-crop-median-v1`); `training-agrifood-snapshot-v1` identifies the pinned assessment-source snapshot, with fit/training lineage in the artifact. Dataset-backed responses use `simulation=true` and the exact notice `SIMULATION / training challenge dataset / deterministic baseline / not production deployment`. The synthetic fixture remains distinct and unchanged.

On analytics-resource failure, the application may remain running with health and synthetic demo reachable, while the real route is unavailable. Publish the context only after all required resources pass validation. Accepted target health states are `not_configured`, `ready`, `unavailable`; top-level `status="ok"` and HTTP 200 express application liveness. Current health code still only implements `not_configured`.

Accepted settings are `SMART_HARVEST_DATA_DIR` and `SMART_HARVEST_BASELINE_ARTIFACT`; defaults/path packaging remain implementation details. GET needs no change to `allow_methods=["GET"]`. The modular monolith is preserved; no database requirement, registry service, worker, message queue, microservice or background retraining is introduced. This is not production HA/scaling policy.

## Explicit non-goals for the foundation

Internal baseline assessment execution exists through IGR-04B. Runtime artifact generation/loading, lifespan/provider wiring and the accepted single-batch GET endpoint remain unimplemented and belong to the next bounded ADR 0005 slice, together with health reconciliation and focused verification. A multi-batch ranked/replay endpoint, facility filtering, pagination, frontend queue integration, production learned engine, validated recommendation engine, supported deterioration horizon, new confidence/minimum policy and deployment/VLD-03 remain deferred. General persistence, authentication, realtime processing, action-effect estimation and savings estimation remain unimplemented.
