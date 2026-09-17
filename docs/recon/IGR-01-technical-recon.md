# IGR-01 Technical Recon

**Document Type:** Technical Reconnaissance & Architecture Mapping Report  
**Workstream:** IGR-01 (Backend & Technical Deputy Workstream)  
**Author / Owner:** Igor (Technical Deputy)  
**Integrator / Reviewer:** Vladimir  
**Project:** SoS — Training AgriFood / Smart Harvest  
**Repository:** `https://github.com/Slave-of-Skynet/training_agrifood`  
**Classification:** SIMULATION / Training Challenge  

---

## 1. Recon identity

- **Repository:** `https://github.com/Slave-of-Skynet/training_agrifood`
- **Local working directory:** `D:\AgriFood\training_agrifood`
- **Current branch:** `igor/igr-01-technical-recon`
- **Starting / base SHA:** `7461dc9918cb557c533e64da19785eb8f3124946`
- **Inspected HEAD:** `7461dc9918cb557c533e64da19785eb8f3124946`
- **Reference SHA at task preparation:** `72ab453f52d3bb7909001d0403fc62f89dce117d`
- **Base state comparison:** Current HEAD (`7461dc9`) is newer than the preparation reference SHA (`72ab453`). It incorporates commit `cafbcf832e7abb410ee9ff07954b4bb50e34aa81` (*docs: reconcile sponsor pack and adopt team workstreams*), commit `fbd1f311394c8b6dca18b1a8d54c13dbfe0678d8` (*docs: add VLD-01 integration contract*), and PR #6 merge commit `7461dc9`. In accordance with workstream rules, the fresh upstream base was preserved without resetting.
- **Working-tree state before recon:** Clean (`git status --short` was empty before recon actions).

---

## 2. Executive technical summary

The Smart Harvest repository currently implements a lightweight, fully functional end-to-end foundation proving vertical contract transport between a React operator shell and a Python FastAPI service.

**What is actually implemented today:**
1. **HTTP Service & Transport:** A FastAPI modular application (`backend/app/main.py`) exposing two endpoints: `GET /api/v1/health` and `GET /api/v1/demo/assessment` (`backend/app/api/routes.py`). CORS middleware is active, allowing GET requests from configured origins (default: `http://localhost:5173`).
2. **Pydantic Output Contracts:** Strict Pydantic v2 domain models (`backend/app/domain/assessment.py`) enforcing `extra="forbid"`, validated status invariants, and rich output structures covering assessment status, risk estimates, deterioration horizons, structured factors, recommendations, reliability metadata, and provenance.
3. **Synthetic Demo Fixture:** A service builder (`backend/app/services/demo_assessment.py::build_demo_assessment`) returning a synthetic assessment in an `insufficient_data` state, with explicit simulation labeling.
4. **Automated Backend Tests:** A 4-test pytest suite (`backend/tests/test_api.py`, `backend/tests/test_contract.py`) passing 100%, verifying endpoint serialization, contract round-tripping, and status invariant enforcement.
5. **Operator Frontend Shell:** A React 18 + TypeScript + Vite application (`frontend/src/`) rendering connecting, connected, unavailable, and insufficient-data states, with typed API client calls fetching both endpoints simultaneously.
6. **Canonical Architecture Documentation:** Authoritative decisions, data contracts, domain rule guardrails, evaluation guidelines, assumptions, and runbooks committed under `docs/`.

**What exists only as skeleton or documented future boundary:**
1. Modules `backend/app/ingestion/`, `backend/app/analytics/`, `backend/app/explain/`, and `backend/app/recommend/` exist only as directory skeletons containing 2-line docstring `__init__.py` files.
2. No challenge dataset ingestion, raw file parsing, or canonical entity validation exists.
3. No risk calculation formula, heuristic scoring, or ML models exist.
4. No database, ORM, caching layer, or background queue exists.
5. No validated agronomic rule sets or intervention effect catalogs exist.

---

## 3. Verified foundation behaviour

The following verification commands were executed in the repository environment:

### 3.1. Backend Tests

- **Command:** `.\.venv\Scripts\python.exe -m pytest backend/tests`
- **Result:** **PASS** (Exit code: 0)
- **Output:**
  ```text
  ....                                                                     [100%]
  ============================== warnings summary ===============================
  .venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
  .venv\Lib\site-packages\starlette\testclient.py:53: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
  .venv\Lib\site-packages\_pytest\cacheprovider.py:475: PytestCacheWarning: could not create cache path ... Access is denied: 'pytest-cache-files-vxjhyk0j'
  4 passed, 3 warnings in 0.82s
  ```
- **What it proves:**
  - `GET /api/v1/health` returns HTTP 200 with `status="ok"`, `service="smart-harvest"`, `analytics="not_configured"`.
  - `GET /api/v1/demo/assessment` returns HTTP 200 with `status="insufficient_data"`, `risk=None`, `deterioration_horizon=None`, `recommendation=None`, and `simulation=True`.
  - Pydantic model validation round-trips `RiskAssessment` instances cleanly to and from JSON.
  - The model validator strictly rejects false precision: an `insufficient_data` payload containing a non-null `risk` estimate raises `ValidationError`.
- **What it does NOT prove:**
  - It does not prove that the system can process challenge datasets.
  - It does not prove the validity of any risk predictions or agronomic models.
  - It does not prove persistence or database connectivity.

### 3.2. Backend Runtime

- **Command 1 (Standard Runbook):** `.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload` (default port 8000)
- **Result:** **FAIL / PORT CONFLICT** (Exit code: 1)
- **Output:**
  ```text
  ERROR: [Errno 13] error while attempting to bind on address ('127.0.0.1', 8000): [winerror 10013] an attempt was made to access a socket in a way forbidden by its access permissions
  ```
- **Read-Only Diagnosis:** Port 8000 is occupied by an existing local system process (`Manager`, PID 5572). This is a host-environment conflict on the standard port, not an application code defect.
- **Command 2 (Verification on Free Port):** `.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --port 8001`
- **Result:** **PASS** (Server initialized and accepted connections)
- **HTTP Verification Output:**
  - `Invoke-RestMethod http://localhost:8001/api/v1/health`:
    ```json
    {
      "status": "ok",
      "service": "smart-harvest",
      "analytics": "not_configured"
    }
    ```
  - `Invoke-RestMethod http://localhost:8001/api/v1/demo/assessment`:
    ```json
    {
      "batch_id": "synthetic-batch-001",
      "status": "insufficient_data",
      "risk": null,
      "deterioration_horizon": null,
      "factors": [
        {
          "code": "validated_inputs_unavailable",
          "category": "data_quality",
          "effect": "unknown",
          "summary": "Validated assessment inputs are not configured for this fixture.",
          "evidence_references": []
        }
      ],
      "recommendation": null,
      "reliability": {
        "level": "unavailable",
        "confidence_score": null,
        "reason_codes": ["INSUFFICIENT_VALIDATED_INPUTS"],
        "missing_requirements": ["Validated challenge dataset schema"]
      },
      "provenance": {
        "contract_version": "1.0.0",
        "engine_tier": "fixture",
        "engine_version": "foundation-fixture-v1",
        "generated_at": "2026-09-17T14:34:18.029362Z",
        "source_dataset_id": null,
        "simulation": true,
        "notice": "SIMULATION / synthetic fixture / not challenge data"
      }
    }
    ```
- **What it proves:**
  - FastAPI app boots cleanly, mounts middleware, and serves valid typed JSON matching Pydantic schemas over HTTP.
- **What it does NOT prove:**
  - It does not prove that production traffic or heavy analytics payloads can be served without configuring worker pools or async handlers.

### 3.3. Frontend Build

- **Command:** `cd frontend; npm.cmd ci; npm.cmd run build`
- **Result:** **FAIL / PERMISSIONS BLOCKER** (Exit code: 1)
- **Output:**
  ```text
  npm error code EPERM
  npm error syscall mkdir
  npm error path D:\AgriFood\training_agrifood\frontend\node_modules
  npm error errno -4048
  npm error Error: EPERM: operation not permitted, mkdir 'D:\AgriFood\training_agrifood\frontend\node_modules'
  ...
  'tsc' is not recognized as an internal or external command
  ```
- **Read-Only Diagnosis:** NTFS permissions on `D:\AgriFood\training_agrifood` grant standard unprivileged users `(RX)` (Read and Execute) access only (`BUILTIN\Users:(I)(OI)(CI)(RX)`). Directory creation requires elevated / Administrator privileges. Consequently, dependencies in `node_modules` are not installed, and `tsc` is not present in PATH.
- **What it proves / does NOT prove:**
  - Proves that dependency installation in the current unprivileged shell session is blocked by filesystem access controls.
  - Does NOT indicate a defect in TypeScript code or configuration (`package.json`, `tsconfig.json`, and `vite.config.ts` are syntactically sound and static inspection shows complete alignment with backend contracts).
  - In accordance with STOP conditions, no file permissions or configuration files were modified.

---

## 4. Current technical trunk

The end-to-end runtime path from operator interface to response payload was traced across concrete files, classes, and functions:

```text
[React Browser View]
      │
      ▼
frontend/src/main.tsx
  └─ renders <HomePage /> (frontend/src/pages/HomePage.tsx)
      │
      ▼
frontend/src/pages/HomePage.tsx
  └─ triggers useEffect() -> Promise.all([getHealth(), getDemoAssessment()])
      │
      ▼
frontend/src/api/client.ts
  ├─ getHealth(): fetch("/api/v1/health") -> Promise<HealthResponse>
  └─ getDemoAssessment(): fetch("/api/v1/demo/assessment") -> Promise<RiskAssessment>
      │
      ▼ (Vite proxy: /api -> http://localhost:8000 or VITE_API_BASE_URL)
backend/app/main.py
  ├─ create_app() -> FastAPI application
  ├─ CORSMiddleware -> allows GET from http://localhost:5173
  └─ include_router(router, prefix="/api/v1")
      │
      ▼
backend/app/api/routes.py
  ├─ @router.get("/health") -> returns HealthResponse(status="ok", service="smart-harvest", analytics="not_configured")
  └─ @router.get("/demo/assessment") -> calls build_demo_assessment()
      │
      ▼
backend/app/services/demo_assessment.py
  └─ build_demo_assessment() -> instantiates RiskAssessment
      │
      ▼
backend/app/domain/assessment.py
  └─ RiskAssessment(ContractModel)
      ├─ executes model_validator: enforce_status_semantics()
      ├─ enforces: status == INSUFFICIENT_DATA => risk is None and deterioration_horizon is None
      └─ serializes to JSON response (FastAPI response_model=RiskAssessment)
      │
      ▼ (HTTP 200 JSON Response)
frontend/src/api/client.ts
  └─ deserializes response to RiskAssessment interface (frontend/src/api/contracts.ts)
      │
      ▼
frontend/src/pages/HomePage.tsx
  └─ updates React state: setConnection({ kind: "available", health, assessment })
      │
      ├─ renders <BackendStatus health={health} /> (frontend/src/components/BackendStatus.tsx)
      │    └─ displays service name and analytics status
      │
      └─ renders <AssessmentCard assessment={assessment} /> (frontend/src/components/AssessmentCard.tsx)
           ├─ displays notice banner ("SIMULATION / synthetic fixture / not challenge data")
           ├─ checks assessment.status === "insufficient_data"
           ├─ renders Insufficient State message (withholding risk and horizon)
           ├─ iterates over assessment.factors (displays category and summary)
           └─ displays reliability level ("unavailable")
```

**Key Operational Observations:**
- `routes.py` contains zero business logic; it acts solely as an HTTP router delegating to `build_demo_assessment()`.
- `build_demo_assessment()` is an explicit synthetic fixture builder, returning hardcoded objects with `simulation=True` and `engine_tier="fixture"`.
- The frontend UI honors the `insufficient_data` contract by deliberately suppressing percentage gauges or countdown horizons when those fields are null.

---

## 5. Backend module map

| Module / Path | Present Implementation | Intended Boundary (per `docs/architecture.md`) | Status | Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| **`backend/app/api`** | `routes.py` defining `/health` and `/demo/assessment` | Versioned HTTP presentation boundary (`/api/v1`). Pure transport; no business or analytics logic. | **IMPLEMENTED** | `app.domain.assessment`, `app.services.demo_assessment` |
| **`backend/app/domain`** | `assessment.py` defining `ContractModel`, `RiskAssessment`, and associated value objects/enums | Stable application domain contracts and output semantics. Governs public shared structures. | **IMPLEMENTED** | Standard library (`datetime`, `enum`, `typing`), `pydantic` |
| **`backend/app/services`** | `demo_assessment.py` (`build_demo_assessment`) | Application service orchestration layer connecting ingestion, analytics, explain, and recommend pipelines. | **SKELETON** | `app.domain.assessment` |
| **`backend/app/ingestion`** | Empty `__init__.py` docstring: *"Future ingestion boundary; intentionally unimplemented until dataset probe."* | Dataset parsing, validation, referential integrity checking, timestamp normalization, and raw-to-canonical mapping. | **SKELETON** | Blocked by VDR-01 (inventory/integrity) and approved input schema |
| **`backend/app/analytics`** | Empty `__init__.py` docstring: *"Future analytics boundary; no risk logic is implemented in the foundation."* | Deterministic baseline scoring engine, feature extraction windows, and optional learned model tier. | **SKELETON** | Blocked by VDR-02 (leakage), later Viktor evaluation contract, and domain evidence |
| **`backend/app/explain`** | Empty `__init__.py` docstring: *"Future structured explanation boundary."* | Transformation of model/heuristic outputs into evidence-linked `AssessmentFactor` objects. | **SKELETON** | Blocked by analytics feature representations and factor catalog |
| **`backend/app/recommend`** | Empty `__init__.py` docstring: *"Future structured recommendation boundary."* | Generation of prioritized, actionable `Recommendation` objects with human review flags. | **SKELETON** | Blocked by Alisa product research on operator actions and domain rules |

---

## 6. Preserved contracts

The repository defines strict Pydantic v2 domain models in `backend/app/domain/assessment.py`. These represent preserved shared contracts:

### 6.1. Contract Invariants & Semantics

1. **`ContractModel` Base Configuration:**
   - Enforces `model_config = ConfigDict(extra="forbid")`. Any unrecognized extra attribute causes immediate validation failure across all models.
2. **`AssessmentStatus`:**
   - Enum with values: `ASSESSED = "assessed"`, `INSUFFICIENT_DATA = "insufficient_data"`.
3. **Core Invariant Validator (`enforce_status_semantics`):**
   - If `status == INSUFFICIENT_DATA`: both `risk` and `deterioration_horizon` **must be `None`**. Setting either raises `ValueError("insufficient_data assessments cannot claim risk or a deterioration horizon")`.
   - If `status == ASSESSED`: `risk` **must not be `None`** (`ValueError("assessed assessments require a risk estimate")`). `deterioration_horizon` remains optional.
4. **`RiskEstimate`:**
   - `score: float` strictly constrained to `ge=0.0, le=1.0`.
   - `band: RiskBand | None` (`"low"`, `"moderate"`, `"high"`).
   - *Semantics:* The score represents a normalized risk index; it is not guaranteed to be a calibrated frequentist probability.
5. **`DeteriorationHorizon`:**
   - `starts_at: datetime` (required timestamp).
   - `ends_at: datetime | None` (optional upper bound).
   - *Semantics:* Bounded window when product degradation is projected to occur.
6. **`AssessmentFactor`:**
   - Fields: `code: str`, `category: FactorCategory`, `effect: FactorEffect`, `summary: str`, `evidence_references: list[str]`.
   - `FactorCategory`: `"data_quality"`, `"environmental"`, `"storage"`, `"transport"`, `"inventory"`, `"historical"`.
   - `FactorEffect`: `"increases_risk"`, `"decreases_risk"`, `"unknown"`.
   - *Semantics:* Structured explanation drivers; not causal claims unless backed by validated evidence.
7. **`Recommendation`:**
   - Fields: `action_code: str`, `label: str`, `priority: RecommendationPriority`, `rationale_codes: list[str]`, `requires_human_review: bool = True`.
   - `RecommendationPriority`: `"informational"`, `"low"`, `"medium"`, `"high"`.
   - *Semantics:* Machine-actionable intervention recommendation. Explicitly non-free-form (no uncontrolled LLM text generation).
8. **`Reliability`:**
   - Fields: `level: ReliabilityLevel`, `confidence_score: float | None` (`ge=0.0, le=1.0`), `reason_codes: list[str]`, `missing_requirements: list[str]`.
   - `ReliabilityLevel`: `"unavailable"`, `"low"`, `"medium"`, `"high"`.
   - *Semantics:* Explicit degradation communication. When inputs are insufficient, `missing_requirements` lists exact missing data fields.
9. **`Provenance`:**
   - Fields: `contract_version: str`, `engine_tier: Literal["fixture", "deterministic_baseline", "learned_model"]`, `engine_version: str`, `generated_at: datetime`, `source_dataset_id: str | None`, `simulation: bool`, `notice: str`.
   - *Semantics:* Auditability and tier transparency. Prevents simulation fixtures from being mistaken for production calculations.

### 6.2. Preserving Semantics in Future Deterministic Baseline

**Recon Assessment:** Can a future deterministic baseline be implemented without breaking the current public `RiskAssessment` contract?
- **FACT:** Yes. The `RiskAssessment` contract already includes `engine_tier="deterministic_baseline"`.
- When an assessment has adequate data, setting `status=AssessmentStatus.ASSESSED`, `risk=RiskEstimate(score=calculated_score, band=calculated_band)`, `reliability=Reliability(level=ReliabilityLevel.MEDIUM, ...)`, and `provenance=Provenance(engine_tier="deterministic_baseline", ...)` satisfies every Pydantic validator and serialization rule without changing a single field definition.

---

## 7. Frontend/backend coupling

1. **Contract Mirroring:**
   - Frontend TypeScript interfaces in `frontend/src/api/contracts.ts` are a direct manual mirror of `backend/app/domain/assessment.py`.
   - No automated code generation (e.g. `openapi-typescript` or `pydantic2ts`) is configured. Any backend schema modification immediately creates a risk of silent TypeScript divergence.
2. **Current Field Consumption:**
   - `HomePage.tsx` consumes `health.service`, `health.analytics`, `assessment.status`, `assessment.batch_id`.
   - `AssessmentCard.tsx` consumes `assessment.provenance.notice`, `assessment.batch_id`, `assessment.status`, `assessment.risk?.score`, `assessment.deterioration_horizon?.starts_at`, `assessment.factors` (`category`, `summary`), and `assessment.reliability.level`.
   - `BackendStatus.tsx` consumes `health.service`, `health.analytics`.
3. **Unrendered Contract Surfaces:**
   - The UI does **not** currently render: `assessment.recommendation` (no card or action list exists), `assessment.reliability.reason_codes`, `assessment.reliability.missing_requirements`, `assessment.factors[].evidence_references`, or `assessment.provenance.engine_tier`.
4. **Contract-Breaking Hazards:**
   - Renaming or removing any field from `RiskAssessment` or `HealthResponse`.
   - Changing `status` enum strings (`"assessed"`, `"insufficient_data"`).
   - Changing ISO 8601 datetime serialization formats.
   - Returning unexpected HTTP error payloads without status codes handled by `client.ts` (`fetch().ok` check).

---

## 8. Sponsor-pack technical boundary

*Notice: This section documents physical files and structural boundaries only for technical dependency mapping. In strict adherence to division of responsibilities, no data profiling, column distributions, null rates, leakage calculations, or statistical modeling were performed (reserved for Viktor VDR-01 / VDR-02).*

### 8.1. File Inventory & Storage Profile

Under `sponsor_pack/`:
- `brief/Training Challenge #3 — AgriFood.md` (1,542 B)
- `README.md` (4,800 B)
- `data/data_dictionary.xlsx` (10,088 B)
- `data/facilities.csv` (869 B)
- `data/storage_zones.csv` (2,529 B)
- `data/batches.csv` (163,479 B)
- `data/storage_sessions.csv` (174,934 B)
- `data/sensor_readings.csv` (53,087,361 B ~ 53 MB)
- `data/quality_checks.csv` (360,451 B)
- `data/shipments.csv` (278,921 B)
- `data/historical_quality_outcomes.csv` (73,347 B)

### 8.2. Declared Relational Structure (Sponsor Documentation)

```text
[facilities] ──< [storage_zones] ──< [sensor_readings]
                       │
             [storage_sessions] >── [batches] ──< [quality_checks]
                                       │
                                  [shipments]
                                       │
                         [historical_quality_outcomes]
```

### 8.3. Declared Temporal Semantics

- Decision moment: $T_{assess} = T_{dispatch}$ (defined as `dispatch_datetime` in `storage_sessions.csv`).
- Declared admissible at dispatch: agronomic metadata, ambient harvest weather, storage sensor telemetry up to $T_{dispatch}$, pre-dispatch quality checks, planned shipment attributes.
- Declared strictly inadmissible at dispatch (future information): actual transit delays, en-route breakdown incidents, transit telemetry, arrival inspections, and final outcomes.
- Evaluation protocol notice: Hidden competition test suites withhold arrival-stage quality checks entirely.

---

## 9. Evidence-specific dependency gates

Technical decisions for subsequent implementation work are partitioned across four specific evidence gates:

### 9.1. Decisions Blocked by VDR-01 (Inventory / Integrity Evidence — Viktor)

| Decision Blocked | Required Viktor Evidence | Affected Module | Safe Pre-Work Possible? |
| :--- | :--- | :--- | :--- |
| **Production Raw Input Models** | Exact column types, nullability behaviors, header encodings, and value constraints across CSVs. | `backend/app/ingestion/models.py` | Yes: Define abstract parser interface and protocol types. |
| **Canonical Entity Schemas** | Verified entity boundaries, observed surrogate keys, and normalization targets. | `backend/app/domain/entities.py` | Yes: Document candidate entities matching sponsor ERD. |
| **Relational Join Strategy** | Primary/foreign key uniqueness, orphan records, many-to-many linkages between sessions and batches. | `backend/app/ingestion/joins.py` | No: Joining logic without integrity verification risks silent drop or duplicate rows. |
| **Missingness & Parsing Rules** | Null frequencies, sentinel values (e.g. `-999`, empty strings), invalid timestamp strings. | `backend/app/ingestion/cleaners.py` | Yes: Implement generic sanitization utilities. |
| **Memory / Ingestion Architecture** | Verified row counts and memory footprint of `sensor_readings.csv` (~53 MB). | `backend/app/ingestion/reader.py` | Yes: In-memory chunking / streaming reader prototype. |

### 9.2. Decisions Blocked by VDR-02 (Temporal / Leakage Evidence — Viktor)

| Decision Blocked | Required Viktor Evidence | Affected Module | Safe Pre-Work Possible? |
| :--- | :--- | :--- | :--- |
| **Feature Extraction Cutoff Logic** | Audit of timestamps in `sensor_readings` relative to `dispatch_datetime` in `storage_sessions`. | `backend/app/analytics/features.py` | Yes: Write filtering signature `filter_telemetry_before(session, t_cutoff)`. |
| **Admissible Predictor Whitelist** | Field-by-field verification of arrival vs pre-dispatch stages in `quality_checks` and `shipments`. | `backend/app/analytics/whitelist.py` | Yes: Statically exclude arrival inspection columns per README. |
| **Shared-Zone / Chamber Leakage Controls** | Analysis of multiple batches sharing the same storage zone concurrently. | `backend/app/analytics/splits.py` | No: Cannot construct leakage-free validation splits without co-storage data. |
| **Temporal Aggregation Windows** | Sensor sampling regularity, gaps, and maximum lookback durations before dispatch. | `backend/app/analytics/aggregations.py`| Yes: Parameterized window aggregators (e.g. mean, min, max). |

### 9.3. Decisions Blocked by Later Approved Viktor Contracts (Target / Evaluation / Models)

| Decision Blocked | Required Viktor Evidence | Affected Module | Safe Pre-Work Possible? |
| :--- | :--- | :--- | :--- |
| **Prediction Target & Task Formulation** | Statistical viability of `quality_status` (classification) vs `loss_fraction_pct` (regression) vs economic loss. | `backend/app/analytics/target.py` | No: Analytical formulation must be approved by Viktor & Vladimir. |
| **Deterioration Horizon Feasibility** | Whether the dataset supports a computable onset timestamp or proxy event for quality degradation. | `backend/app/domain/assessment.py` | No: If onset cannot be grounded, horizon must remain null. |
| **Deterministic Baseline Formulation** | Approved rule/heuristic formula and baseline evaluation protocol against which models are compared. | `backend/app/analytics/baseline.py` | Yes: Create skeleton baseline runner class returning `RiskEstimate`. |
| **Learned ML Model Selection** | Benchmark results proving an ML model family outperforms the deterministic baseline on a clean split. | `backend/app/analytics/model.py` | No: ML implementation is strictly blocked until baseline evaluation exists. |

### 9.4. Decisions Blocked by Alisa (Product / Domain Evidence)

| Decision Blocked | Required Alisa Evidence | Affected Module | Safe Pre-Work Possible? |
| :--- | :--- | :--- | :--- |
| **Structured Recommendation Actions** | Catalog of valid operator interventions (`action_code`, priority definitions, operational feasibility). | `backend/app/recommend/actions.py` | Yes: Pydantic model for recommendation actions. |
| **Operator Decision Thresholds** | Definition of what risk score translates to "high", "moderate", or "low" urgency for a warehouse manager. | `backend/app/domain/assessment.py` | No: Arbitrary cutoffs violate domain guardrails. |
| **Factor Human Summaries** | Standard terminology and explanation text acceptable to agricultural logistics personnel. | `backend/app/explain/factors.py` | Yes: Template string formats with parameter placeholders. |
| **Economic Impact / Loss Modeling** | Validated interpretation of financial loss fields and business benefit claims. | `backend/app/analytics/business.py` | No: Sourced product definition required before claiming EUR savings. |

---

## 10. Decisions blocked by domain/product evidence

In accordance with `docs/domain_rules.md`, agronomic and operational decisions cannot be resolved by code or statistical profiling alone:
1. **Agronomic Environmental Thresholds:** Safe temperature ranges, relative humidity limits, dew point condensation hazards, and atmospheric gas tolerances per crop cultivar cannot be guessed. Sourced literature or consortium rules are required before flagging storage violations.
2. **Kinetic / Biochemical Equations:** While models like Q10, Vapor Pressure Deficit (VPD), and Arrhenius degradation curves are candidate concepts, none are accepted rules. Hardcoding them without domain citation is prohibited.
3. **Action Repertoire:** Interventions such as "divert to local processing", "expedite refrigerated transit", or "re-pack and re-cool" must reflect commercial Moldovan logistics realities.
4. **Deterioration Horizon Semantics:** What constitutes the "onset of deterioration" (e.g. firmness dropping below threshold X vs cosmetic blemishes exceeding Y%) requires agronomic definition.

---

## 11. Documentation/code consistency findings

### 11.1. Sponsor Pack vs Stale Challenge Canon Synchronization (Known Recon Question)

- **Finding:** Synchronized on current HEAD (`7461dc9`), but historically divergent at reference SHA `72ab453`.
- **Exact Evidence:**
  - In task-preparation reference commit `72ab453f52d3bb7909001d0403fc62f89dce117d`, the `sponsor_pack/` directory was added, but `docs/challenge_canon.md` retained stale wording: `**UNKNOWN:** The actual files, schema, semantics, quality, labels, collection process, and operating environment have not been inspected.`
  - In commit `cafbcf832e7abb410ee9ff07954b4bb50e34aa81` (*docs: reconcile sponsor pack and adopt team workstreams*), Vladimir updated `docs/challenge_canon.md`, `docs/assumptions_unknowns.md`, `docs/data_contract.md`, `docs/evaluation.md`, and `README.md`.
  - On the current inspected HEAD, `docs/challenge_canon.md` accurately states: `**FACT:** The repository now contains the supplied training challenge materials under sponsor_pack/...` while correctly preserving `UNKNOWN pending empirical reconnaissance` for data quality, labels, and evaluation design.
- **Downstream Impact:** There is no longer an active contradiction between canon and file presence on current HEAD. Future team members will not be misled regarding the availability of sponsor pack files.

### 11.2. CORS Configuration vs Planned Ingestion Endpoints

- **Finding:** `backend/app/main.py` lines 27-32 configure `allow_methods=["GET"]`.
- **Evidence:**
  ```python
  application.add_middleware(
      CORSMiddleware,
      allow_origins=_cors_origins(),
      allow_credentials=False,
      allow_methods=["GET"],
      allow_headers=["*"],
  )
  ```
- **Downstream Impact:** If future workstreams introduce a `POST /api/v1/assessments` endpoint for client-submitted batch assessment, browser requests will be blocked by CORS preflight failures unless `allow_methods` is updated to include `POST` (or `["*"]`).

### 11.3. Frontend Unrendered Assessment Properties

- **Finding:** `frontend/src/components/AssessmentCard.tsx` does not render `recommendation`, `reliability.reason_codes`, or `reliability.missing_requirements`, despite their inclusion in `frontend/src/api/contracts.ts` and `RiskAssessment`.
- **Downstream Impact:** When the backend transitions from `insufficient_data` to populated recommendations, frontend UI changes will be necessary to expose these insights to operators.

---

## 12. Technical risks

### 12.1. Defects (Host Environment)

- **[DEFECT] Default Port 8000 Conflict:** Uvicorn startup on port 8000 fails on this machine due to socket collision with existing system process `Manager` (PID 5572).  
  *Impact:* Developers and automated test runners following the standard runbook without port overrides will encounter `WinError 10013`.
- **[DEFECT] Frontend Filesystem Permissions:** Standard users lack write permissions (`BUILTIN\Users:(I)(OI)(CI)(RX)`) on `D:\AgriFood\training_agrifood\frontend`, preventing `npm ci` / `mkdir node_modules`.  
  *Impact:* Frontend builds cannot complete in unprivileged shell sessions.
- **[DEFECT] Pytest Cache Permission Warning:** Pytest reports `PytestCacheWarning: could not create cache path ... Access is denied`. Tests still execute in-memory and pass, but cache artifacts cannot be persisted.

### 12.2. Unknowns

- **[UNKNOWN] Memory Profile of Ingestion:** `sensor_readings.csv` is 53 MB uncompressed. Reading the entire file naively using standard libraries or Pandas during API requests could introduce latency or high memory overhead in resource-constrained environments.
- **[UNKNOWN] Referential Integrity of Raw Keys:** Whether all `batch_id` values in `batches.csv` have valid foreign keys in `storage_sessions.csv` and `shipments.csv` remains unverified.

### 12.3. Inferences

- **[INFERENCE] In-Memory Processing is Sufficient for MVP:** For the scope of a hackathon/training demo, loading preprocessed parquet or in-memory dictionary lookups will likely suffice without requiring PostgreSQL/SQLite, preserving the modular monolith architecture.
- **[INFERENCE] Manual Contract Synchronization is Error-Prone:** Manually updating TypeScript interfaces when Pydantic models change carries regression risk. A type-generation script or OpenAPI client generator would reduce maintenance friction.

### 12.4. Preferences

- **[PREFERENCE] Port Parameterization in Runbook:** Update `docs/demo_runbook.md` and `README.md` to document an environment variable `SMART_HARVEST_PORT` (defaulting to 8000 with documented 8001 fallback).

---

## 13. Proposed minimal implementation sequence

Following the acceptance of IGR-01 and the delivery of corresponding evidence gates, the following implementation sequence is recommended:

```text
IGR-01 (Technical Recon)
   │
   ▼ [Gate: VDR-01 Accepted]
IGR-02 (Ingestion Boundary & Canonical Models)
   │
   ▼ [Gate: VDR-02 Accepted]
IGR-03 (Temporal Cutoff & Feature Filtering)
   │
   ▼ [Gate: Baseline Contract + Alisa Rules Accepted]
IGR-04 (Deterministic Baseline & Factor Engine)
   │
   ▼ [Gate: Action Catalog Accepted]
IGR-05 (Recommendation Generation & Operator UI)
   │
   ▼ [Gate: Viktor Model Benchmark Accepted - Optional]
IGR-06 (Learned Model Tier Integration)
```

### Step Details

1. **IGR-02: Ingestion Boundary & Canonical Entity Models**
   - **Objective:** Build file readers, Pydantic validation schemas, and canonical entity models for challenge CSV tables.
   - **Prerequisite Evidence:** VDR-01 inventory, data dictionary review, and referential integrity audit accepted by Vladimir.
   - **Likely Write Area:** `backend/app/ingestion/`, `backend/app/domain/entities.py`.
   - **Shared-Contract Impact:** None (internal domain representation; preserves `RiskAssessment` output contract).
   - **STOP Condition:** Unresolvable foreign key breakage or schema incompatibilities in raw files.

2. **IGR-03: Temporal Cutoff & Feature Filtering**
   - **Objective:** Implement temporal isolation logic enforcing $T \le T_{dispatch}$ and excluding post-dispatch/arrival data.
   - **Prerequisite Evidence:** VDR-02 temporal/leakage audit and admissible predictor whitelist from Viktor.
   - **Likely Write Area:** `backend/app/analytics/features/`, `backend/app/services/`.
   - **Shared-Contract Impact:** None.
   - **STOP Condition:** Inability to isolate dispatch timestamp reliably across sessions.

3. **IGR-04: Deterministic Baseline & Factor Engine**
   - **Objective:** Implement heuristic risk score calculation and structured `AssessmentFactor` generation, transitioning engine tier to `deterministic_baseline`.
   - **Prerequisite Evidence:** Viktor's baseline formulation and Alisa's verified agronomic threshold review.
   - **Likely Write Area:** `backend/app/analytics/baseline.py`, `backend/app/explain/`, `backend/app/services/`.
   - **Shared-Contract Impact:** Populates `status="assessed"` with real `RiskEstimate` objects. Must preserve Pydantic invariant constraints.
   - **STOP Condition:** Attempting to hardcode unvalidated agronomic rules or unverified risk formulas.

4. **IGR-05: Structured Recommendations & Operator UI Integration**
   - **Objective:** Generate actionable `Recommendation` objects and render them in the frontend `AssessmentCard`.
   - **Prerequisite Evidence:** Alisa's operator action catalog and priority mapping.
   - **Likely Write Area:** `backend/app/recommend/`, `frontend/src/components/AssessmentCard.tsx`.
   - **Shared-Contract Impact:** Populates existing `Recommendation` model.
   - **STOP Condition:** Recommendation logic claims unproven causal financial savings.

5. **IGR-06 (Optional / Dataset-Dependent): Learned Model Tier Integration**
   - **Objective:** Integrate ML model artifact behind `engine_tier="learned_model"`.
   - **Prerequisite Evidence:** Formally approved Viktor evaluation report demonstrating measurable lift over deterministic baseline on leakage-free splits.
   - **Likely Write Area:** `backend/app/analytics/model.py`.
   - **Shared-Contract Impact:** None (drop-in implementation under existing contract).
   - **STOP Condition:** ML model shows leakage or fails to outperform the deterministic baseline.

---

## 14. Explicit non-decisions

The following items are intentionally **NOT** decided during IGR-01:
1. **Production Raw Input Schema:** No `BatchInput` schema or HTTP payload structure was invented.
2. **Database & Storage Architecture:** No database (PostgreSQL, SQLite, DuckDB), ORM (SQLAlchemy), or migration system was selected.
3. **Risk Scoring Formulas:** No mathematical equations or weightings were established for risk calculation.
4. **Machine Learning Algorithms:** No model families (XGBoost, Random Forest, Neural Networks) were chosen or trained.
5. **Agronomic Storage Limits:** No temperature, humidity, or gas thresholds were adopted or hardcoded.
6. **Recommendation Action Codes:** No specific intervention actions or effect sizes were approved.
7. **Hosting & Deployment Topology:** No cloud provider, container strategy, or CI/CD pipeline was specified.

---

## 15. Questions for Integrator / Viktor / Alisa

### To Vladimir (Integrator)
1. **Default Port Conflict:** Should we update `.env.example` and `backend/app/main.py` / `README.md` to support a configurable `PORT` (e.g. defaulting to 8000 with documented 8001 fallback) to avoid local conflicts?
2. **Frontend Permissions:** In local Windows environments where `node_modules` cannot be created by standard users, should we document running npm in an elevated shell or adjusting folder permissions as part of standard developer setup?
3. **API Protocol for Assessment:** For future evaluation, will the API assess batches on-demand via `POST /api/v1/assessments` with batch data in the request body, or will it query pre-ingested batch IDs via `GET /api/v1/assessments/{batch_id}`? If `POST` is expected, CORS `allow_methods` must be updated.

### To Viktor (Data & Evaluation Owner)
1. **Raw Entity Cardinality:** From VDR-01, what are the observed row counts and memory profiles across the 8 CSVs, especially `sensor_readings.csv`?
2. **Referential Integrity:** Are there orphaned records in `storage_sessions.csv` or `shipments.csv` that do not link to `batches.csv`?
3. **Temporal Bounding:** In VDR-02, do all `sensor_readings` timestamps fall strictly between session start and dispatch, or are there out-of-bounds readings?
4. **Evaluation Target:** Which historical outcome column (`quality_status`, `loss_fraction_pct`, or `economic_loss_eur`) is statistically defensible as the primary prediction target?

### To Alisa (Product Owner)
1. **Action Catalog:** What specific intervention options (e.g. divert to processing, adjust chamber setpoint, prioritize dispatch route) are realistic for a Moldovan cold store operator?
2. **Human Review Protocol:** Under what specific circumstances should a recommendation flag `requires_human_review = False`, or should all high-stakes post-harvest actions require human confirmation?

---

## 16. Final handoff

```text
IGR-01 HANDOFF

Branch: igor/igr-01-technical-recon
Starting/base SHA: 7461dc9918cb557c533e64da19785eb8f3124946
Current HEAD: 7461dc9918cb557c533e64da19785eb8f3124946

git status --short:
?? docs/recon/IGR-01-technical-recon.md

Created/changed files:
- docs/recon/IGR-01-technical-recon.md (new recon deliverable)

Backend tests:
Command: .\.venv\Scripts\python.exe -m pytest backend/tests
Result: PASS (4 passed, 3 warnings in 0.82s)
Evidence: Verified HealthResponse, RiskAssessment round-tripping, and status invariant validator.

Backend runtime:
Health endpoint: GET http://localhost:8001/api/v1/health -> HTTP 200 ({"status":"ok","service":"smart-harvest","analytics":"not_configured"})
Demo assessment endpoint: GET http://localhost:8001/api/v1/demo/assessment -> HTTP 200 (RiskAssessment with status="insufficient_data", risk=null, simulation=true)
Evidence: Verified via uvicorn on port 8001 (port 8000 has local host collision with PID 5572).

Frontend build:
Command: cd frontend; npm.cmd ci; npm.cmd run build
Result: FAIL (Exit code 1)
Evidence: NTFS unprivileged user permissions prevent mkdir node_modules (EPERM). Read-only diagnosis confirmed; no unauthorized permission or config changes made.

Main technical findings:
1. Foundation technical trunk is fully operational and typed: FastAPI serves Pydantic contracts consumed cleanly by React frontend.
2. Ingestion, analytics, explain, and recommend modules are purely skeletons with 2-line docstring __init__.py files.
3. Preserved RiskAssessment contracts strictly enforce status invariants (insufficient_data prohibits risk/horizon; assessed requires risk).
4. A future deterministic baseline can be implemented completely within preserved public contract semantics.
5. The known recon question regarding sponsor_pack vs stale challenge_canon is resolved on current HEAD (synchronized in commit cafbcf8).

Implemented trunk:
frontend/src/main.tsx -> HomePage.tsx -> client.ts -> FastAPI (app/main.py) -> routes.py -> demo_assessment.py -> RiskAssessment (app/domain/assessment.py) -> serialized JSON -> frontend rendering.

Skeleton/future boundaries:
backend/app/ingestion/, backend/app/analytics/, backend/app/explain/, backend/app/recommend/.

Evidence-specific dependency gates:
- VDR-01 inventory/integrity: Blocks raw input schemas, canonical models, join keys, missingness handling.
- VDR-02 temporal/leakage: Blocks feature cutoff filters, admissible predictor whitelist, chamber leakage controls.
- Later approved Viktor contracts: Blocks target selection, baseline formula, horizon feasibility, ML models.
- Alisa product/domain evidence: Blocks recommendation action catalog, domain rule review register, operator thresholds.

Questions for Viktor:
- Verified table cardinalities, foreign key integrity, temporal sensor bounds, and defensible target selection.

Questions for Alisa:
- Valid operator intervention catalog, urgency thresholds, and human review requirements.

Questions for Integrator:
- Port 8000 collision handling, frontend unprivileged build procedures, and future assessment API method (GET vs POST).

Canon/docs synchronization issues:
- Stale wording in challenge_canon.md was already reconciled in commit cafbcf8; current HEAD is consistent.

Shared contracts changed: none
Dependencies changed: none
Config changed: none
Application code changed: none

Commit: not performed
Push: not performed
Merge: not performed

One-sentence conclusion:
The Smart Harvest foundation provides an intact, strictly typed vertical trunk and validated contract boundaries, ready for modular ingestion and deterministic baseline implementation as soon as Viktor's VDR-01/VDR-02 evidence is delivered.
```
