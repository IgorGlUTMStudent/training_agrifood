# Foundation demo runbook

This runbook demonstrates connectivity and contract behavior only. It does **not** demonstrate agricultural validity, business accuracy, risk prediction, or loss reduction.

## 1. Start the backend

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".\backend[test]"
python -m uvicorn app.main:app --app-dir backend --reload
```

Expected service origin: `http://localhost:8000`.

## 2. Verify the API

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
Invoke-RestMethod http://localhost:8000/api/v1/demo/assessment
```

Expected health fields are `status: ok`, `service: smart-harvest`, and `analytics: not_configured`. The demo assessment must be labeled `SIMULATION / synthetic fixture / not challenge data`, have `status: insufficient_data`, and omit risk, horizon, and recommendation values.

## 3. Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/api` to the backend. An explicit `VITE_API_BASE_URL` can override this for local integration.

## Expected states

- **Loading:** the shell shows `Connecting…` while both API calls are pending.
- **Success:** the shell shows `Connected`, health metadata, and the synthetic assessment.
- **Backend unavailable/error:** the shell shows `Unavailable`, preserves the error state, and offers `Try again`; it does not fabricate `status: ok`.
- **Insufficient data:** the shell explicitly withholds risk percentage and deterioration horizon and explains why.

## Reset

Reset is N/A for this stateless foundation. Use `Try again` or reload the page to fetch a fresh fixture response.
