# Foundation demo runbook

This runbook demonstrates connectivity and contract behavior only. It does **not** demonstrate agricultural validity, business accuracy, risk prediction, or loss reduction.

## 1. Start the backend

Prerequisites from repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".\backend[test]"
```

Expected service origin: `http://localhost:8000`.

### Mode A — No analytics runtime configuration (default)

Start without setting analytics environment variables:

```powershell
python -m uvicorn app.main:app --app-dir backend --reload
```

Verify the API:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
Invoke-RestMethod http://localhost:8000/api/v1/demo/assessment
```

Expected behavior:
- `health.analytics = "not_configured"` (`status: ok`, `service: smart-harvest`).
- `demo/assessment` returns the synthetic fixture (`status: insufficient_data`, `simulation: true`, notice `"SIMULATION / synthetic fixture / not challenge data"`, omitting risk, horizon, and recommendation).
- Real assessment route `GET /api/v1/assessments/{batch_id}` returns HTTP 503 ("Analytics runtime unavailable") with `Cache-Control: no-store`.

### Mode B — Configured RBS-01 backend

Configure runtime settings in PowerShell before launching:

```powershell
$env:SMART_HARVEST_DATA_DIR = "sponsor_pack/data"
$env:SMART_HARVEST_BASELINE_ARTIFACT = "backend/artifacts/baseline-crop-median-v1-p1-s2024.json"
python -m uvicorn app.main:app --app-dir backend --reload
```

Verify the API:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
Invoke-RestMethod http://localhost:8000/api/v1/assessments/BAT-000901
```

Expected behavior:
- `health.analytics = "ready"` (`status: ok`, `service: smart-harvest`).
- `BAT-000901` is a recorded Season-2025 held-out training-challenge batch (not a production live batch).
- `GET /api/v1/assessments/BAT-000901` returns HTTP 200 with `status: assessed`, `risk.score: 0.0644`, `simulation: true`, and notice `"SIMULATION / training challenge dataset / deterministic baseline / not production deployment"`.
- Requests for Season-2024 training-partition batches (e.g. `BAT-000001`) return HTTP 409 ("Batch is not eligible for this assessment release").
- Requests for unknown batch IDs return HTTP 404 ("Batch not found").
- All assessment responses include `Cache-Control: no-store`.

## 2. Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/api` to the backend. An explicit `VITE_API_BASE_URL` can override this for local integration.

> [!NOTE]
> **Frontend Limitation:** The current frontend operator shell fetches `GET /api/v1/health` and `GET /api/v1/demo/assessment` (synthetic fixture). It does **NOT** yet consume `GET /api/v1/assessments/{batch_id}`.

## Expected UI states

- **Loading:** the shell shows `Connecting…` while initial API calls are pending.
- **Success:** the shell shows `Connected`, health metadata (`Analytics: not configured` or `ready`), and the assessment card.
- **Backend unavailable/error:** the shell shows `Unavailable`, preserves the error state, and offers `Try again`; it does not fabricate `status: ok`.
- **Insufficient data:** the shell explicitly withholds risk percentage and deterioration horizon and explains why.

## Reset

Reset is N/A for this stateless foundation. Use `Try again` or reload the page to fetch a fresh response.
