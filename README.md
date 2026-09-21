# Smart Harvest foundation

Smart Harvest is a **SIMULATION / training challenge** prototype for post-harvest decision support. This repository currently proves a small architectural trunk: a React operator shell calls a FastAPI backend, which returns a typed health response and a synthetic `insufficient_data` assessment.

## What exists

- FastAPI application with `GET /api/v1/health` and `GET /api/v1/demo/assessment`.
- Pydantic output contracts for assessment status, risk, deterioration horizon, factors, structured recommendations, reliability, and provenance.
- React + TypeScript + Vite shell with loading, available, and unavailable backend states.
- A deliberately neutral synthetic fixture marked `SIMULATION / synthetic fixture / not challenge data`.
- Raw dataset ingestion and physical structural diagnostics for the sponsor CSV tables ([`backend/app/ingestion/`](backend/app/ingestion/)).
- Typed canonical `BatchAssessmentInput` domain models ([`backend/app/domain/batch.py`](backend/app/domain/batch.py)) and deterministic raw-to-canonical mapper ([`backend/app/ingestion/canonical_mapper.py`](backend/app/ingestion/canonical_mapper.py)), enforcing dispatch-time cutoffs ($T_{assess} \equiv T_{dispatch}$), leakage-safe exclusion of future arrival/transit/outcome fields, preservation of structural missingness as `None`, and planned logistics mapping.
- Canonical architecture, data-contract, evaluation, domain-rule, and runbook documentation under [`docs/`](docs/).

## What does not exist yet

While raw ingestion and canonical predictive-input mapping are now implemented, there is still no production analytics scoring runtime, runtime crop-median engine integration, production batch assessment endpoint, ranked multi-batch queue endpoint, recommendation engine, production learned model, persistence layer, authentication, realtime processing, or deployment integration. The demo endpoint continues to return a synthetic `insufficient_data` fixture. Those choices remain intentionally unresolved until subsequent evidence and decision gates.

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
- [`docs/integration_contract.md`](docs/integration_contract.md) — workstream dependency map, integration boundaries, and STOP conditions.
- [`docs/assumptions_unknowns.md`](docs/assumptions_unknowns.md) — unresolved dataset and environment questions.
- [`docs/data_contract.md`](docs/data_contract.md) — current output/application contract.
- [`docs/evaluation.md`](docs/evaluation.md) — evaluation principles without unsupported targets.
- [`docs/domain_rules.md`](docs/domain_rules.md) — guardrails for future agronomic rules.
- [`docs/demo_runbook.md`](docs/demo_runbook.md) — foundation demo procedure.
- [`docs/team_roles.md`](docs/team_roles.md) — current SoS challenge-specific ownership.
- [`docs/workstreams/`](docs/workstreams/) — SoS challenge-specific operating guides for the five team workstreams.
- [`docs/decisions/0001-foundation-architecture.md`](docs/decisions/0001-foundation-architecture.md) — foundation ADR.
- [`docs/decisions/0002-predictive-input-semantics.md`](docs/decisions/0002-predictive-input-semantics.md) — canonical predictive input semantics decision (ADR 0002).
- [`docs/decisions/0003-assessment-evaluation-semantics.md`](docs/decisions/0003-assessment-evaluation-semantics.md) — assessment, ranking, and evaluation semantics decision (ADR 0003).
- [`docs/data_recon/01_dataset_inventory.md`](docs/data_recon/01_dataset_inventory.md) — accepted dataset inventory and integrity profile (VDR-01).
- [`docs/data_recon/02_temporal_leakage.md`](docs/data_recon/02_temporal_leakage.md) — accepted temporal semantics and leakage audit (VDR-02).
- [`docs/data_recon/03_target_horizon_feasibility.md`](docs/data_recon/03_target_horizon_feasibility.md) — accepted target and deterioration-horizon feasibility evidence (VDR-03).
- [`docs/data_recon/04_dispatch_predictability.md`](docs/data_recon/04_dispatch_predictability.md) — accepted dispatch predictability benchmark evidence (VDR-04A).
- [`docs/product_recon/`](docs/product_recon/) — product and domain research evidence (APR-01; research notes, not automatically challenge canon).

The sponsor pack supplies an inspectable raw schema. Observed integrity of the supplied snapshot has been profiled in accepted, integrated [VDR-01](docs/data_recon/01_dataset_inventory.md), temporal/leakage semantics have been audited in accepted, integrated [VDR-02](docs/data_recon/02_temporal_leakage.md), and target & deterioration-horizon feasibility has been profiled in accepted, integrated [VDR-03](docs/data_recon/03_target_horizon_feasibility.md). Canonical predictive-input semantics and the `BatchAssessmentInput` definition were accepted under [ADR 0002](docs/decisions/0002-predictive-input-semantics.md) (VLD-02A), and canonical mapping is implemented in application code (IGR-03). Assessment, ranking, baseline, and evaluation semantics were accepted under [ADR 0003](docs/decisions/0003-assessment-evaluation-semantics.md). Production analytics scoring, runtime crop-median engine execution, ranked queue endpoints, recommendations, and learned models remain separately unbuilt.
