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
- `backend/app/runtime` — artifact schema validation, pinned snapshot validation, and FastAPI lifespan runtime context provider.
- `backend/app/analytics` — implemented deterministic crop-median baseline (IGR-04A), evaluated by the internal IGR-04B assessment service; runtime baseline artifact loading and single-batch HTTP serving are implemented (RBS-01). No production learned engine is selected.
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

Raw ingestion and structural diagnostics, canonical `BatchAssessmentInput`, the raw-to-canonical mapper (IGR-03), deterministic crop-median baseline (IGR-04A), deterministic baseline assessment service (IGR-04B), and runtime baseline serving via `GET /api/v1/assessments/{batch_id}` with lifespan artifact/snapshot validation (RBS-01) are implemented in backend code. The operator UI currently fetches health and the synthetic `/api/v1/demo/assessment` endpoint; frontend integration of the real assessment route is not yet implemented. Multi-batch/replay queue, learned models, deterioration prediction, and action recommendations remain unimplemented.

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

**IMPLEMENTED / ENFORCED IN CODE (RBS-01 / PR #42):** Vladimir accepted HG-R5 D1–D7 on 2026-09-22; [ADR 0005](decisions/0005-runtime-baseline-serving.md) is authoritative, not the recon recommendations as a whole. RBS-01 implemented and verified this slice in code.

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

On analytics-resource failure, the application may remain running with health and synthetic demo reachable, while the real route is unavailable (HTTP 503). Publish the context only after all required resources pass validation. Accepted and implemented health states are `not_configured`, `ready`, and `unavailable`; top-level `status="ok"` and HTTP 200 express application liveness.

Accepted settings are `SMART_HARVEST_DATA_DIR` and `SMART_HARVEST_BASELINE_ARTIFACT`; defaults/path packaging remain implementation details. GET needs no change to `allow_methods=["GET"]`. The modular monolith is preserved; no database requirement, registry service, worker, message queue, microservice or background retraining is introduced. This is not production HA/scaling policy.

## Explicit non-goals for the foundation

Single-batch deterministic baseline serving via `GET /api/v1/assessments/{batch_id}`, offline artifact generation/validation, lifespan runtime loading, and health synchronization are implemented in backend code (RBS-01).

A multi-batch ranked/replay endpoint, facility filtering, pagination, frontend real-assessment consumption, frontend operator queue, production learned engine, validated recommendation engine, supported deterioration horizon, new confidence/minimum policy, and deployment/VLD-03 remain deferred. General persistence, authentication, realtime processing, action-effect estimation, and savings estimation remain unimplemented.
