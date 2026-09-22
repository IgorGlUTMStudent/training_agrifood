# VLD-R6 — Post-RBS-01 State Reconciliation

## Status / base / provenance

- **Task-local ID:** `VLD-R6`
- **Role:** Integration / continuity reconciliation
- **Human owner:** Vladimir — Integrator
- **Repository:** `Slave-of-Skynet/training_agrifood`
- **Target branch:** `vladimir/vld-r6-post-rbs01-reconciliation`
- **Authoritative base commit:** `794eac36b2deb7f244aeccc4ee2326100996edac` (Merge PR #42 — Serve pinned baseline assessments)
- **RBS-01 implementation commit:** `59cd759a1ac098475e553a6852505904f61341a7`
- **Preceding reference base:** `e8e14e3da7921a1d87f7bfc6e474f639ef87aa53` (VLD-R5 / ADR 0005 acceptance)
- **Nature of task:** Documentation-only reconciliation following successful Human Integration of RBS-01 / PR #42. Introduces no code, schema, dependency, configuration, or product decisions.

## Scope

Reconcile repository documentation with the integrated RBS-01 baseline serving implementation. Specifically:
- Acknowledge that ADR 0005 decisions D1–D7 are now enforced in committed code.
- Correct stale documentation that previously described runtime baseline serving as future or unimplemented work.
- Maintain strict epistemic boundaries between implemented backend serving, existing frontend synthetic demo behavior, accepted architecture decisions, and deferred capabilities.
- Identify candidate next bounded implementation slices for Human Integrator decision.

## Current committed implementation

At `794eac36b2deb7f244aeccc4ee2326100996edac`, the repository implements and enforces:
1. **Offline baseline artifact generation:** `scripts/generate_baseline_artifact.py` performs a controlled fit on the Season-2024 training partition (`dispatch_datetime < 2025-05-01`, 900 batches) and writes a validated JSON artifact.
2. **Versioned runtime artifact:** `backend/artifacts/baseline-crop-median-v1-p1-s2024.json` carries format version `baseline-artifact.v1`, family `baseline-crop-median-v1`, engine version `baseline-crop-median-v1-p1-s2024`, dataset `training-agrifood-snapshot-v1`, Season-2024 training partition metadata, SHA256 hashes of all 8 source tables, training membership SHA256 fingerprint, crop medians, and global median.
3. **Runtime snapshot and artifact validation:** `backend/app/runtime/artifact.py` verifies the pinned 8-table raw snapshot against accepted SHA256 digests, validates structural diagnostics, verifies 1:1 session-batch relations, checks training membership against the artifact fingerprint, and reconstructs `CropMedianBaseline` without historical outcomes.
4. **FastAPI lifespan runtime context:** `backend/app/main.py` and `backend/app/runtime/context.py` initialize `AnalyticsRuntimeContext` on application startup via environment variables `SMART_HARVEST_DATA_DIR` and `SMART_HARVEST_BASELINE_ARTIFACT`, providing an explicit fail-closed dependency (`get_runtime`).
5. **Real single-batch HTTP assessment route:** `GET /api/v1/assessments/{batch_id}` in `backend/app/api/routes.py`:
   - Validates release eligibility: Season-2024 training batches receive HTTP 409 ("Batch is not eligible for this assessment release").
   - Validates existence: Unknown batch IDs receive HTTP 404 ("Batch not found").
   - Degraded / unconfigured transport: Returns HTTP 503 ("Analytics runtime unavailable") if runtime is unconfigured or failed validation.
   - Internal failure transport: Returns HTTP 500 on canonical mapping or unexpected internal errors.
   - Eligible held-out batches (`dispatch_datetime >= 2025-05-01`, 900 batches) receive HTTP 200 with dataset-backed `RiskAssessment` (`status = "assessed"`, `risk.score`, `simulation = true`, engine tier `deterministic_baseline`, engine version `baseline-crop-median-v1-p1-s2024`, dataset `training-agrifood-snapshot-v1`, and exact notice `"SIMULATION / training challenge dataset / deterministic baseline / not production deployment"`).
   - Enforces `Cache-Control: no-store` on all assessment responses.
6. **Tri-state health synchronization:** `HealthResponse` supports `analytics: "not_configured" | "ready" | "unavailable"`, synchronized across backend Pydantic models, frontend TypeScript contracts, and API tests. Top-level `status = "ok"` and HTTP 200 represent process liveness.
7. **Preserved synthetic demo:** `GET /api/v1/demo/assessment` remains available and unchanged (`status: insufficient_data`).

## Gaps closed by RBS-01

RBS-01 closed the following previously documented gaps:
- **Offline artifact generation:** Replaced manual/ad-hoc fitting with a reproducible script and validated schema.
- **Runtime snapshot verification:** Replaced blind CSV reading with SHA256 digest validation, structural diagnostics, and cohort fingerprinting.
- **Runtime lifecycle & provider:** Replaced unconfigured-only state with FastAPI lifespan loading and fail-closed dependency injection.
- **HTTP assessment serving:** Replaced absence of real route with `GET /api/v1/assessments/{batch_id}`.
- **Health state contract:** Replaced hardcoded `"not_configured"` with synchronized tri-state readiness across backend and frontend contracts.

## Remaining gaps / deferred work

The following work was **NOT** authorized or implemented by RBS-01 and remains deferred:
- **Frontend real assessment consumption:** The frontend still fetches `GET /api/v1/health` and `GET /api/v1/demo/assessment`. It does NOT consume `GET /api/v1/assessments/{batch_id}`.
- **Multi-batch collection / replay route:** No endpoint exists to query or list multiple assessments.
- **Ranked operator queue:** No queue ordering, review window, capacity bounds, or prioritization UI exists.
- **Facility filtering and pagination:** No facility query parameters, filtering, or pagination logic exists.
- **Learned model tier:** No ML model family (e.g. HistGradientBoosting) is selected or wired for serving.
- **Action recommendations:** `recommendation` remains `null`; no intervention catalogue or causal efficacy is validated.
- **Deterioration horizon:** `deterioration_horizon` remains `null`; continuous countdown is unsupported by data.
- **Production deployment:** `simulation = false` is forbidden; no cloud hosting or deployment is configured.
- **Challenge outcomes:** Outcome 1 (relative loss-severity score) is operational for individual eligible batches; Outcomes 2, 3, and 4 remain unclosed. No claim of food-loss reduction is demonstrated.
- **VLD-03:** The end-to-end verification gate has not started.

## Current end-to-end path

### Backend execution graph (IMPLEMENTED)

```text
SMART_HARVEST_DATA_DIR
+
SMART_HARVEST_BASELINE_ARTIFACT
        ↓
FastAPI lifespan
        ↓
pinned snapshot validation (8 tables SHA256 + diagnostics)
+
artifact validation (schema + cohort fingerprint)
        ↓
AnalyticsRuntimeContext
        ↓
GET /api/v1/assessments/{batch_id}
        ↓
release eligibility check (409 if training, 404 if unknown)
        ↓
IGR-03 build_batch_assessment_input()
        ↓
BatchAssessmentInput
        ↓
loaded CropMedianBaseline
        ↓
IGR-04B build_baseline_assessment()
        ↓
RiskAssessment (HTTP 200, Cache-Control: no-store)
```

### Browser / UI path (EXISTING — NOT INTEGRATED TO REAL ROUTE)

```text
HomePage
  ├── GET /api/v1/health          ──► BackendStatus (renders "not configured" or "ready")
  └── GET /api/v1/demo/assessment ──► AssessmentCard (renders synthetic insufficient_data fixture)
```

The browser UI path is strictly connected to the synthetic demo fixture. It does NOT invoke or display the dataset-backed assessment route.

## Stale-document reconciliation

The following files were updated to reconcile stale statements with committed code:
1. `docs/decisions/0005-runtime-baseline-serving.md`: Appended a non-breaking post-decision implementation status note recording fulfillment of ADR 0005 D1–D7 by RBS-01 (PR #42). Preserved historical decision provenance at base `e8e14e3da7921a1d87f7bfc6e474f639ef87aa53`.
2. `docs/architecture.md`: Updated layer boundaries to include `backend/app/runtime`, updated conceptual flow and runtime decision sections to describe single-batch baseline serving as implemented, and updated explicit non-goals to reflect that single-batch serving is complete while multi-batch/queue/frontend integration remain deferred.
3. `docs/integration_contract.md`: Updated purpose paragraph, contract inventory table (Provenance, API Endpoints, HealthResponse, Production Ingestion, Analytics Baseline), ownership entries for Vladimir and Igor, boundary matrix rows B2–B5, Section 8 current-state narrative, tables, and readiness gates, and Section 10 limitations.
4. `docs/assumptions_unknowns.md`: Added VLD-R6 reconciliation note, updated persistence needs row, updated health/CORS row, documented completion of the initial ADR 0005 D7 slice, and retained all canonical UNKNOWNs.
5. `docs/demo_runbook.md`: Restructured runbook into Mode A (unconfigured default) and Mode B (configured RBS-01 runtime), including example held-out batch `BAT-000901`, and explicitly recorded the frontend demo limitation.
6. `README.md`: Updated overview to describe both synthetic fixture and optional configured dataset-backed API, updated "What exists" and "What does not exist yet", documented unconfigured and configured execution modes, and added ADR 0005 to canonical documentation.

Historical reconnaissance documents (`docs/recon/VLD-R5-runtime-assessment-path-recon.md`, `docs/recon/PUX-08-data-ux-reconciliation.md`, `docs/product_recon/**`, `prscr_ux_demo_qa_report.md`) were deliberately preserved without modification.

## Candidate next bounded slices — HUMAN DECISION REQUIRED

VLD-R6 identifies three technically plausible next bounded implementation slices. No choice is authorized by this reconciliation; a Human Integrator decision is strictly required.

### Candidate A — Single-batch frontend integration
- **Intent:** Connect the existing React frontend shell to the implemented dataset-backed route `GET /api/v1/assessments/{batch_id}` for a single selected batch.
- **What it unlocks:** Visible end-to-end operator demonstration of real baseline assessment in the browser UI.
- **Prerequisites:** Frontend API client method for `/api/v1/assessments/{batch_id}`, UI input or selector control, and error handling for 404, 409, and 503.
- **Must NOT assume:** Multi-batch queue, operator ranking, facility filtering, pagination, or recommendation engine.

### Candidate B — Multi-batch / replay backend foundation
- **Intent:** Implement a backend collection or replay endpoint for held-out batches, establishing the data foundation needed before an operator queue.
- **What it unlocks:** Batch collection querying and replay capability for queue-level evaluation and presentation.
- **Prerequisites:** New Human decision and bounded contract (explicitly deferred by ADR 0005 D7), batch filtering criteria, pagination and windowing semantics.
- **Must NOT assume:** Production database, streaming pipeline, or learned model selection.

### Candidate C — VLD-03 preparation / end-to-end verification gate
- **Intent:** Conduct formal end-to-end verification across integrated backend and frontend components.
- **What it unlocks:** Formal verification sign-off before expanding feature scope.
- **Prerequisites:** Definition of VLD-03 scope. If VLD-03 requires UI demonstration of real dataset-backed assessments, Candidate A logically precedes it; if VLD-03 tests backend APIs and synthetic frontend separately, it could proceed immediately.
- **Must NOT assume:** VLD-03 can pass on frontend synthetic demo alone if user-facing dataset-backed assessment is part of the verification criteria.

```text
HUMAN DECISION REQUIRED — no next slice is authorized by VLD-R6 itself.
```

## Stop conditions

The reconciliation is complete under the following verified conditions:
- All edits are confined to the authorized documentation write scope.
- No backend, frontend, script, or sponsor pack code was modified.
- No baseline artifact was regenerated or refitted.
- No tests were modified.
- No ADR 0005 decision semantics were altered.
- Historical reconnaissance documents remain intact.
- STOP before commit, push, or pull request creation, awaiting Project Brain review.
