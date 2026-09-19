# Smart Harvest foundation

Smart Harvest is a **SIMULATION / training challenge** prototype for post-harvest decision support. This repository currently proves a small architectural trunk: a React operator shell calls a FastAPI backend, which returns a typed health response and a synthetic `insufficient_data` assessment.

## What exists

- FastAPI application with `GET /api/v1/health` and `GET /api/v1/demo/assessment`.
- Pydantic output contracts for assessment status, risk, deterioration horizon, factors, structured recommendations, reliability, and provenance.
- React + TypeScript + Vite shell with loading, available, and unavailable backend states.
- A deliberately neutral synthetic fixture marked `SIMULATION / synthetic fixture / not challenge data`.
- Canonical architecture, data-contract, evaluation, domain-rule, and runbook documentation under [`docs/`](docs/).

## What does not exist yet

There is no challenge-dataset ingestion, production input schema, risk formula, validated agronomic rule set, ML model, persistence layer, authentication, realtime processing, or deployment integration. Those choices remain intentionally unresolved until dataset and domain reconnaissance.

## Prerequisites

- Python 3.11+
- Node.js 20.19+ or 22.12+ and npm

## Run the backend

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".\backend[test]"
python -m uvicorn app.main:app --app-dir backend --reload
```

The API is available at `http://localhost:8000`. Verify it with:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
Invoke-RestMethod http://localhost:8000/api/v1/demo/assessment
```

## Run the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` requests to `http://localhost:8000` in development. To use another API origin, copy `.env.example` to `.env` and set `VITE_API_BASE_URL`.

## Checks

```powershell
python -m pytest backend/tests
cd frontend
npm run build
```

The backend tests validate both endpoints and enforce that an `insufficient_data` assessment has no fabricated risk or deterioration horizon. The frontend build runs TypeScript checking before bundling.

## Canonical documentation

- [`docs/challenge_canon.md`](docs/challenge_canon.md) — challenge facts, outcomes, evaluation criteria, and unknowns.
- [`docs/architecture.md`](docs/architecture.md) — accepted system shape and boundaries.
- [`docs/assumptions_unknowns.md`](docs/assumptions_unknowns.md) — unresolved dataset and environment questions.
- [`docs/data_contract.md`](docs/data_contract.md) — current output/application contract.
- [`docs/evaluation.md`](docs/evaluation.md) — evaluation principles without unsupported targets.
- [`docs/domain_rules.md`](docs/domain_rules.md) — guardrails for future agronomic rules.
- [`docs/demo_runbook.md`](docs/demo_runbook.md) — foundation demo procedure.
- [`docs/team_roles.md`](docs/team_roles.md) — current SoS challenge-specific ownership.
- [`docs/workstreams/`](docs/workstreams/) — SoS challenge-specific operating guides for the five team workstreams.
- [`docs/decisions/0001-foundation-architecture.md`](docs/decisions/0001-foundation-architecture.md) — foundation ADR.

The sponsor pack supplies an inspectable raw schema. Observed integrity of the supplied snapshot has been profiled in accepted, integrated [VDR-01](docs/data_recon/01_dataset_inventory.md). Canonical predictive mapping and an accepted production `BatchAssessmentInput` remain pending accepted temporal/leakage evidence and integration decisions; observed snapshot integrity does not establish production input semantics.
