# Smart Harvest foundation

Smart Harvest is a **SIMULATION / training challenge** prototype for post-harvest decision support. The repository contains a synthetic foundation demo AND an optional configured dataset-backed deterministic-baseline single-batch API.

## What exists

- FastAPI backend with:
  - `GET /api/v1/health`: tri-state analytics health reporting (`not_configured`, `ready`, `unavailable`).
  - `GET /api/v1/demo/assessment`: synthetic contract fixture marked `SIMULATION / synthetic fixture / not challenge data` (`status: insufficient_data`).
  - `GET /api/v1/assessments/{batch_id}`: dataset-backed deterministic-baseline single-batch assessment route (RBS-01 / PR #42) serving Season-2025 held-out batches with `Cache-Control: no-store`.
- Pydantic output contracts for assessment status, risk, deterioration horizon, factors, structured recommendations, reliability, and provenance.
- React + TypeScript + Vite operator shell with loading, available, and unavailable backend states. The frontend currently consumes `/api/v1/health` and `/api/v1/demo/assessment`.
- Raw dataset ingestion and physical structural diagnostics for the sponsor CSV tables ([`backend/app/ingestion/`](backend/app/ingestion/)).
- Typed canonical `BatchAssessmentInput` domain models ([`backend/app/domain/batch.py`](backend/app/domain/batch.py)) and deterministic raw-to-canonical mapper ([`backend/app/ingestion/canonical_mapper.py`](backend/app/ingestion/canonical_mapper.py)), enforcing dispatch-time cutoffs ($T_{assess} \equiv T_{dispatch}$), leakage-safe exclusion of future arrival/transit/outcome fields, preservation of structural missingness as `None`, and planned logistics mapping.
- Offline baseline artifact generator ([`scripts/generate_baseline_artifact.py`](scripts/generate_baseline_artifact.py)) and versioned JSON baseline artifact ([`backend/artifacts/baseline-crop-median-v1-p1-s2024.json`](backend/artifacts/baseline-crop-median-v1-p1-s2024.json)).
- FastAPI lifespan runtime validation of pinned snapshot and baseline artifact ([`backend/app/runtime/`](backend/app/runtime/)).
- Canonical architecture, data-contract, evaluation, domain-rule, and runbook documentation under [`docs/`](docs/).

## What does not exist yet

While raw ingestion, canonical input mapping, offline baseline fitting, and single-batch baseline serving are implemented, the repository does not have:
- Frontend consumption of the real assessment route (the browser UI currently fetches only `/api/v1/demo/assessment` and `/api/v1/health`);
- Ranked multi-batch queue endpoint or batch list API;
- Facility filtering or pagination;
- Action recommendation engine (`recommendation` remains `None`);
- Deterioration timing prediction (`deterioration_horizon` remains `None`);
- Production learned model (no machine learning model selected);
- External persistence layer (database/ORM);
- Authentication, realtime streaming, or production deployment.

## Prerequisites

- Python 3.11+
- Node.js 20.19+ or 22.12+ and npm

## Run the backend

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".\backend[test]"
```

### Unconfigured startup (default)

```powershell
python -m uvicorn app.main:app --app-dir backend --reload
```

- `GET /api/v1/health` returns `analytics: "not_configured"`.
- `GET /api/v1/demo/assessment` returns the synthetic fixture.
- `GET /api/v1/assessments/{batch_id}` returns HTTP 503 ("Analytics runtime unavailable").

### Configured runtime (dataset-backed baseline)

Configure the accepted environment variables before launching:

```powershell
$env:SMART_HARVEST_DATA_DIR = "sponsor_pack/data"
$env:SMART_HARVEST_BASELINE_ARTIFACT = "backend/artifacts/baseline-crop-median-v1-p1-s2024.json"
python -m uvicorn app.main:app --app-dir backend --reload
```

- `GET /api/v1/health` returns `analytics: "ready"`.
- `GET /api/v1/assessments/BAT-000901` returns HTTP 200 with dataset-backed baseline assessment (`status: assessed`, `risk.score: 0.0644`). Note: `BAT-000901` is a recorded Season-2025 training-challenge batch, not a production live batch.
- Season-2024 training batches return HTTP 409 (release ineligible).

## Run the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` requests to `http://localhost:8000` in development. To use another API origin, copy `.env.example` to `.env` and set `VITE_API_BASE_URL`.

The current frontend operator shell fetches `GET /api/v1/health` and `GET /api/v1/demo/assessment` (synthetic fixture); it does not yet consume the real assessment route.

The backend's allowed frontend origins can be configured with the `SMART_HARVEST_CORS_ORIGINS` environment variable (comma-separated; default: `http://localhost:5173`).

## Checks

Before running checks, complete the dependency setup above: create and activate `.venv`, install the backend with `python -m pip install -e ".\backend[test]"`, and run `npm install` in `frontend`. The editable backend installation is required for pytest to import `app`.

The preferred full local repository verification gate for the Windows-first team is, from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify.ps1
```

It runs the backend pytest suite using the project `.venv`, then the frontend production build. It does not install dependencies. CI performs clean dependency installation separately before running its checks.

For targeted or manual checks, with `.venv` activated, start from the repository root:

```powershell
python -m pytest backend/tests
cd frontend
npm run build
```

The backend tests validate all endpoints (health, demo fixture, and dataset-backed baseline route) and enforce domain contract invariants. The frontend build runs TypeScript checking before bundling.

See [`scripts/README.md`](scripts/README.md) for script lifecycle and evidence reproduction rules.

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
- [`docs/decisions/0005-runtime-baseline-serving.md`](docs/decisions/0005-runtime-baseline-serving.md) — runtime baseline serving decision (ADR 0005).
- [`docs/data_recon/01_dataset_inventory.md`](docs/data_recon/01_dataset_inventory.md) — accepted dataset inventory and integrity profile (VDR-01).
- [`docs/data_recon/02_temporal_leakage.md`](docs/data_recon/02_temporal_leakage.md) — accepted temporal semantics and leakage audit (VDR-02).
- [`docs/data_recon/03_target_horizon_feasibility.md`](docs/data_recon/03_target_horizon_feasibility.md) — accepted target and deterioration-horizon feasibility evidence (VDR-03).
- [`docs/data_recon/04_dispatch_predictability.md`](docs/data_recon/04_dispatch_predictability.md) — accepted dispatch predictability benchmark evidence (VDR-04A).
- [`docs/product_recon/`](docs/product_recon/) — product and domain research evidence (APR-01; research notes, not automatically challenge canon).

The sponsor pack supplies an inspectable raw schema. Observed integrity of the supplied snapshot has been profiled in accepted, integrated [VDR-01](docs/data_recon/01_dataset_inventory.md), temporal/leakage semantics have been audited in accepted, integrated [VDR-02](docs/data_recon/02_temporal_leakage.md), and target & deterioration-horizon feasibility has been profiled in accepted, integrated [VDR-03](docs/data_recon/03_target_horizon_feasibility.md). Canonical predictive-input semantics and the `BatchAssessmentInput` definition were accepted under [ADR 0002](docs/decisions/0002-predictive-input-semantics.md) (VLD-02A), and canonical mapping is implemented in application code (IGR-03). Assessment, ranking, baseline, and evaluation semantics were accepted under [ADR 0003](docs/decisions/0003-assessment-evaluation-semantics.md). Single-batch baseline serving was accepted under [ADR 0005](docs/decisions/0005-runtime-baseline-serving.md) and implemented in code (RBS-01 / PR #42). Ranked queue endpoints, frontend consumption of the real assessment route, recommendations, and learned models remain separately unbuilt.
