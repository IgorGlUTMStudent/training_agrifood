# Foundation architecture

## Accepted decision

The application is a modular monolith with a React + TypeScript + Vite operator frontend and a Python + FastAPI + Pydantic backend. The two sides communicate through a typed, versioned HTTP application contract. This is a **DECISION**, not an architecture proposal.

A later deployment may package built SPA assets with the FastAPI service as one artifact. The foundation does not select or configure a hosting platform.

## Boundaries

- `frontend/src/api` — HTTP client and TypeScript representations of public responses.
- `frontend/src/components` and `frontend/src/pages` — operator presentation and connection states.
- `backend/app/api` — versioned HTTP boundary; no business logic.
- `backend/app/domain` — stable assessment output semantics.
- `backend/app/ingestion` — future validation/canonicalization boundary; intentionally empty.
- `backend/app/analytics` — future deterministic baseline and optional learned tier; intentionally empty.
- `backend/app/explain` — future structured explanation boundary.
- `backend/app/recommend` — future structured action boundary.
- `backend/app/services` — application orchestration; currently only a synthetic fixture builder.

Persistence must later sit behind an application boundary. No storage technology, ORM, or migration framework is selected.

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

Only the last three foundation links exist today: typed output contract, API transport, and a UI rendering a synthetic insufficient-data state.

## Analytics principles

- A deterministic baseline is mandatory before any complex model.
- A learned/ML tier is optional and dataset-dependent.
- Both tiers must preserve the public `RiskAssessment` semantics.
- Missing or unusable evidence must degrade explicitly to `insufficient_data`.
- Explanations are structured outputs, with version and provenance attached.
- An LLM is outside the risk, causal, numeric, and action-selection path. No LLM integration exists.

## Runtime decisions

- MVP processing is batch/on-demand.
- Streaming, WebSockets, event buses, queues, and distributed services are excluded.
- The backend and frontend remain logical modules of one deployable product.
- Persistence is intentionally undecided until dataset probe and operating constraints are known.

## Explicit non-goals for the foundation

Dataset ingestion, production `BatchInput`, feature engineering, risk formulas, crop rules, ML, persistence, authentication, realtime processing, action-effect estimation, savings estimation, and deployment-platform integration are not implemented.
