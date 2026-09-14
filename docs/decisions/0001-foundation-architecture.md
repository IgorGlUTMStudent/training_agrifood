# ADR 0001: Foundation architecture

- Status: Accepted
- Date: 2026-09-15

## Context

The training challenge needs a minimal, inspectable product trunk before the real dataset schema, domain rules, hosting constraints, or model feasibility are known. The foundation must demonstrate a typed frontend/backend relationship without prematurely selecting analytics or persistence.

## Decision

- Use React + TypeScript + Vite for the operator frontend.
- Use Python + FastAPI + Pydantic for the application/backend/analytics runtime.
- Structure the product as a modular monolith with typed HTTP boundaries.
- Prefer one deployable artifact later, while leaving deployment integration outside this step.
- Require a deterministic baseline before any complex model.
- Treat ML as optional and dataset-dependent.
- Use batch/on-demand processing for the MVP.
- Do not introduce distributed infrastructure.
- Leave persistence intentionally undecided.
- Keep any future LLM outside the critical path: it cannot create numbers, causes, risks, or actions.

## Consequences

The team can develop UI and Python analytics independently against stable output semantics. `insufficient_data`, reliability, and provenance are first-class. The team must conduct dataset/domain reconnaissance before implementing production inputs, analytics, rules, model selection, or storage.

## Alternatives considered

### Python-only server-rendered UI or Streamlit

This would reduce language/tooling count, but offers a less explicit operator-application boundary and less control over a product-style frontend. It remains suitable for disposable analysis prototypes, not the accepted product trunk.

### TypeScript full-stack

This would unify the language, but Python is the accepted analytics runtime and avoids forcing future analysis work across a language boundary.

### Distributed architecture

Separate services, queues, or event infrastructure add operational and contract complexity without demonstrated MVP requirements. The modular monolith preserves internal boundaries and can be revisited only if evidence establishes a need.
