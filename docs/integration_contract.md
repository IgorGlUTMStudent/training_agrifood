# Integration Contract and Workstream Dependency Map

## Document status

- **Project:** SoS — Training Challenge #3 — AgriFood
- **Challenge:** Smart Harvest: Reduce Post-Harvest Losses
- **Human owner:** Vladimir — Integrator
- **Task:** VLD-01 — Build the Integration Contract and Workstream Dependency Map
- **Deliverable:** `docs/integration_contract.md`
- **Status:** VLD-01 ACCEPTED / INTEGRATED through [PR #6](https://github.com/Slave-of-Skynet/training_agrifood/pull/6).
- **Reconciliation:** VLD-R3 working update against accepted, integrated VLD-02A (ADR 0002, PR #16), VDR-03 (PR #18), and APR-01 (PR #17) at `9cff00ce177f32dc2562d3458e0659281438d4c3`, prepared for human review on 2026-09-20. This documentation reconciliation makes no new decision.
- **Governing workstream:** [`docs/workstreams/vladimir-integration.md`](./workstreams/vladimir-integration.md)

---

# 1. Status, scope and source hierarchy

## 1.1. Purpose and scope

This document records the accepted VLD-01 integration contract and workstream dependency map for the SoS team in the Smart Harvest challenge. Its current-state entries have subsequently been reconciled against accepted Layer-1 evidence; this reconciliation awaits human review and does not change the existing architecture or shared-contract gates. It connects requirements, domain understanding, dataset reconnaissance, application implementation, evaluation, user experience, demonstration, and final presentation claims. The original pre-recon baseline remains part of project history; the current snapshot and evidence references are recorded in Section 8.

The scope of this document covers:

1. **Existing stable contracts:** Guarantees already implemented, tested, and accepted.
2. **Workstream producer → consumer dependencies:** Exact ownership, current accepted outputs, planned outputs, and downstream consumers across all team roles.
3. **Integration boundary matrix:** Producers, consumers, current contracts, unresolved questions, evidence requirements, and decision ownership across every major system boundary.
4. **UNKNOWN → evidence → decision triggers:** Explicit dependency links connecting canonical UNKNOWNs from [`docs/assumptions_unknowns.md`](./assumptions_unknowns.md) to evidence-producing tasks and decision gates.
5. **Shared-contract change triggers:** Mandatory human integration gates before modifying public or cross-cutting boundaries.
6. **Integration STOP conditions:** Explicit circumstances where downstream implementation or claims must halt.
7. **Current blocked / unblocked dependency state:** A concrete audit of what work may proceed immediately versus what is blocked awaiting evidence.
8. **Traceability rules:** The verified path from evidence to decision, shared contract, implementation, and evaluation.
9. **Current limitations:** Clear boundaries defining what this integration contract does not resolve.

### Explicit non-scope for VLD-01

This document intentionally does **not** decide, invent, or assume:

- A production `BatchInput` schema or raw-to-canonical mapping;
- Observed dataset quality, referential integrity, or row-level statistics;
- A risk calculation formula, heuristic, or scoring baseline;
- A machine learning model family, split design, target choice, or evaluation metric;
- Deterioration-horizon onset semantics or temporal estimation algorithms;
- Agronomic rules, crop-specific storage thresholds, or quality decline rates;
- Action-intervention efficacy or causal loss-reduction claims;
- Persistence technology, database engine, or ORM;
- Hosting, deployment platform, or cloud infrastructure;
- New API endpoints or breaking public contract modifications.

Those decisions belong to subsequent evidence-backed decision gates (VLD-02) and will be established only when the required evidence is provided by the responsible workstream owners.

---

## 1.2. Source authority and implementation-state authority

All workstream owners and automated agents must adhere to two explicitly separate authority rules:

### A. Challenge / requirement / decision authority

When determining requirements, specifications, challenge constraints, and architectural decisions, the following order of precedence is strictly authoritative:

1. **Current supplied challenge materials and newer explicit challenge clarification:** [`sponsor_pack/`](../sponsor_pack/), challenge briefs, and official sponsor Q&A or clarifications.
2. **Accepted SoS challenge-specific decisions and shared contracts:** [`docs/decisions/`](./decisions/), [`docs/architecture.md`](./architecture.md), [`docs/data_contract.md`](./data_contract.md), [`docs/domain_rules.md`](./domain_rules.md), [`docs/evaluation.md`](./evaluation.md), [`docs/demo_runbook.md`](./demo_runbook.md), [`docs/team_roles.md`](./team_roles.md).
3. **Challenge canon:** [`docs/challenge_canon.md`](./challenge_canon.md).
4. **General / process guidance:** General engineering guidelines, process runbooks, and team operating conventions.
5. **Current task / workstream notes:** Working notes, task descriptions, and checklists in [`docs/workstreams/`](./workstreams/).

**Core constraint:** Lower-level implementation convenience cannot override a higher-level challenge constraint.

**Simulated context notice:** Sponsor materials are a **SIMULATION / training package**. Statements in the sponsor pack must not be presented as empirical facts about a real GigaHack sponsor, real Moldovan agricultural businesses, or real commercial cold-storage operations.

### B. Current implementation-state authority

The committed application repository (`backend/`, `frontend/`) is authoritative for what is actually implemented, enforced, tested, or absent:

- Application code must **not** be used to infer challenge requirements.
- Conversely, roadmaps, task checklists, and design plans do **not** prove implementation exists if the committed code does not contain it.
- Application code is **not** classified as "Level 5" under the requirements hierarchy; it represents the ground truth of runtime software execution, not a source of business or challenge rules.
- When documentation claims an implementation exists that is not in the codebase, the committed codebase reflects the true state (e.g. SKELETON or UNIMPLEMENTED).

---

## 1.3. Standard claim classification

To prevent speculation from masquerading as verified capability, every technical assertion, documentation statement, and presentation claim must be classified into one of the following canonical categories:

| Classification | Meaning | Rule |
| --- | --- | --- |
| **FACT** | Directly supported by supplied challenge materials or empirically verified evidence. | Must cite an exact file path, commit, test result, or sponsor document. |
| **DECISION** | An explicit team engineering or product choice with recorded rationale. | Must cite an accepted ADR or canonical document under `docs/`. |
| **OBSERVED PRACTICE** | Behavior concretely observed in executed code or tests. | Must cite source code lines or test runs. |
| **INFERENCE** | A logical deduction from facts, but not yet empirically proven. | Must be labeled as an inference; cannot justify production claims. |
| **RECOMMENDATION** | A proposed future action or design option. | Cross-cutting recommendations affecting shared contracts, architecture, or product semantics require an integration decision gate (VLD-02). Local implementation recommendations within an already approved contract may be handled within their bounded task. |
| **UNKNOWN** | An unresolved question where data, evidence, or external clarity is lacking. | Local or task-specific UNKNOWNs remain within task recon evidence. Only cross-cutting project UNKNOWNs affecting shared decisions belong in canonical `docs/assumptions_unknowns.md`. Unresolved UNKNOWNs block only the downstream work that actually depends on them. |
| **SIMULATION** | Synthetic fixture or training simulation context. | Must be visibly labeled; must never be claimed as real operational data. |

---

# 2. Stable shared contracts and constraints

This section catalogs the foundational contracts, constraints, and architecture baselines governing the repository. To avoid conflating runtime code guarantees with project decisions or external challenge rules, every entry is explicitly categorized into one of four governance states:

1. **`IMPLEMENTED / ENFORCED CONTRACT`:** Codified, tested, and actively enforced in repository code (domain models, API routes, UI connection states).
2. **`ACCEPTED DECISION`:** Formal team architectural and methodology agreements recorded in accepted ADRs and documentation.
3. **`FIXED CHALLENGE / SPONSOR CONSTRAINT`:** Non-negotiable external invariants supplied by the training challenge specification ($T_{assess} = T_{dispatch}$).
4. **`DOCUMENTED BUT NOT YET IMPLEMENTED/ENFORCED`:** Specifications described in design documents or schemas but not yet implemented, executed, or verified in application code.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        React + TS Operator UI                          │
│     (HomePage.tsx, AssessmentCard.tsx, BackendStatus.tsx)              │
│     [IMPLEMENTED / ENFORCED CONTRACT]                                  │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                             HTTP GET /api/v1/*
                             [IMPLEMENTED / ENFORCED CONTRACT]
                                     │
┌────────────────────────────────────▼───────────────────────────────────┐
│                        FastAPI + Pydantic API                          │
│     (/api/v1/health, /api/v1/demo/assessment)                          │
│     [IMPLEMENTED / ENFORCED CONTRACT]                                  │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                           Enforces Domain Models
                                     │
┌────────────────────────────────────▼───────────────────────────────────┐
│                    Pydantic Contract: RiskAssessment                   │
│   - status: assessed | insufficient_data                               │
│   - risk: RiskEstimate (score ∈ [0,1]) | null                          │
│   - deterioration_horizon: DeteriorationHorizon | null                 │
│   - factors: list[AssessmentFactor]                                    │
│   - recommendation: Recommendation | null                              │
│   - reliability: Reliability                                           │
│   - provenance: Provenance                                             │
│   [IMPLEMENTED / ENFORCED CONTRACT on synthetic fixture]               │
└────────────────────────────────────────────────────────────────────────┘
```

## 2.1. Detailed contract inventory

**Public contract extension rule:** For public and shared contracts, even an apparently additive optional field or enum extension is not automatically non-breaking; it still requires consumer impact review across backend and frontend consumers and must pass through the appropriate shared-contract gate before adoption.

| Contract Symbol / Concept | Governance Category | Source Path | Current Guarantee & Invariants | Producer / Owner | Primary Consumers | Potential Extension Direction / Impact Notes | Cross-Cutting Change (Requires Gate) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **`RiskAssessment`** | `IMPLEMENTED / ENFORCED CONTRACT` | [`backend/app/domain/assessment.py`](../backend/app/domain/assessment.py), [`frontend/src/api/contracts.ts`](../frontend/src/api/contracts.ts) | Core domain entity. Strict invariant: `insufficient_data` strictly forbids `risk` and `deterioration_horizon`; `assessed` strictly requires non-null `risk`. Extra fields forbidden (`extra="forbid"`). | Igor (Backend) / Vladimir (Contract) | Frontend UI, API serializers, Demo runner | Adding optional fields with default `None` (must update backend and frontend in sync following shared-contract review). | Modifying invariants, renaming fields, altering nullability rules, adding mandatory fields. |
| **`AssessmentStatus`** | `IMPLEMENTED / ENFORCED CONTRACT` | [`backend/app/domain/assessment.py`](../backend/app/domain/assessment.py), [`frontend/src/api/contracts.ts`](../frontend/src/api/contracts.ts) | Enum with exactly two values: `"assessed"` and `"insufficient_data"`. Governs degraded state handling. | Igor (Backend) / Vladimir (Contract) | Frontend UI (`HomePage.tsx`, `AssessmentCard.tsx`), Analytics engine | None without coordinated contract version bump. | Adding new statuses (e.g. `"degraded"`, `"error"`), changing string values. |
| **`RiskEstimate`** | `IMPLEMENTED / ENFORCED CONTRACT` | [`backend/app/domain/assessment.py`](../backend/app/domain/assessment.py), [`frontend/src/api/contracts.ts`](../frontend/src/api/contracts.ts) | `score: float` bounded in `[0.0, 1.0]`. Optional `band: RiskBand` (`"low"`, `"moderate"`, `"high"`). Not guaranteed to be a calibrated probability. | Analytics layer (future) / Igor | Frontend UI, Evaluation framework | Adding metadata (e.g. quantile intervals) as optional fields following consumer impact review. | Removing score, altering `[0,1]` bounds, changing `RiskBand` enum values. |
| **`DeteriorationHorizon`** | `IMPLEMENTED / ENFORCED CONTRACT` | [`backend/app/domain/assessment.py`](../backend/app/domain/assessment.py), [`frontend/src/api/contracts.ts`](../frontend/src/api/contracts.ts) | Strictly nullable enclosing object. When present, `starts_at: datetime` required; `ends_at: datetime | null` optional. Must remain null when horizon is unsupported. | Analytics layer (future) / Igor | Frontend UI, Operator decision display | Adding optional duration fields (e.g. `hours_remaining`) following consumer impact review. | Making horizon mandatory, inferring fake dates under `insufficient_data`. |
| **`AssessmentFactor`** | `IMPLEMENTED / ENFORCED CONTRACT` | [`backend/app/domain/assessment.py`](../backend/app/domain/assessment.py), [`frontend/src/api/contracts.ts`](../frontend/src/api/contracts.ts) | Structured list of factors. Each has `code: str`, `category: FactorCategory`, `effect: FactorEffect`, `summary: str`, and `evidence_references: list[str]`. Not a causal claim by default. | Explainability layer (future) / Igor | Frontend UI (`AssessmentCard.tsx`), Audit trail | Adding new `FactorCategory` or `FactorEffect` enum members (requires coordinated review). | Turning factors into unstructured strings, removing evidence references. |
| **`Recommendation`** | `IMPLEMENTED / ENFORCED CONTRACT` | [`backend/app/domain/assessment.py`](../backend/app/domain/assessment.py), [`frontend/src/api/contracts.ts`](../frontend/src/api/contracts.ts) | Structured object: `action_code`, `label`, `priority: RecommendationPriority`, `rationale_codes: list[str]`, and `requires_human_review: bool` (default `True`). Absent in current foundation fixture. | Recommend layer (future) / Igor | Frontend UI, Operator workflow | Adding optional fields such as expected turnaround window (requires review). | Free-form LLM text generation, removing `requires_human_review`, claiming causal loss reduction without validation. |
| **`Reliability`** | `IMPLEMENTED / ENFORCED CONTRACT` | [`backend/app/domain/assessment.py`](../backend/app/domain/assessment.py), [`frontend/src/api/contracts.ts`](../frontend/src/api/contracts.ts) | Always present. Contains `level: ReliabilityLevel` (`"unavailable"`, `"low"`, `"medium"`, `"high"`), optional `confidence_score: float` in `[0,1]`, `reason_codes: list[str]`, and `missing_requirements: list[str]`. | Analytics / Orchestration / Igor | Frontend UI (`AssessmentCard.tsx`), Operator trust | Adding new reason codes following consumer impact review. | Populating fake confidence scores without validated interpretation, omitting missing requirements. |
| **`Provenance`** | `IMPLEMENTED / ENFORCED CONTRACT` | [`backend/app/domain/assessment.py`](../backend/app/domain/assessment.py), [`frontend/src/api/contracts.ts`](../frontend/src/api/contracts.ts) | Contains `contract_version` (`"1.0.0"`), `engine_tier` (`"fixture"`, `"deterministic_baseline"`, `"learned_model"`), `engine_version`, `generated_at: datetime`, optional `source_dataset_id`, `simulation: bool`, and `notice: str`. | Orchestration / Igor | Frontend UI, Pitch audit, Evaluation logging | Upgrading `engine_tier` as real analytics tiers are implemented; updating version strings following review. | Omitting simulation flags for synthetic fixtures, misrepresenting fixture results as real model outputs. |
| **API Endpoints** | `IMPLEMENTED / ENFORCED CONTRACT` | [`backend/app/api/routes.py`](../backend/app/api/routes.py) | `GET /api/v1/health` returns `HealthResponse` (`status="ok"`, `service="smart-harvest"`, `analytics="not_configured"`). `GET /api/v1/demo/assessment` returns synthetic `RiskAssessment`. | Igor (Backend) | Frontend API client (`client.ts`), Smoke tests, Demo runbook | Adding new versioned routes (e.g. `POST /api/v1/assess/batch`) following API design review. | Altering existing route paths, changing HTTP status codes, removing existing endpoints. |
| **Frontend Consumption** | `IMPLEMENTED / ENFORCED CONTRACT` | [`frontend/src/api/client.ts`](../frontend/src/api/client.ts), [`frontend/src/pages/HomePage.tsx`](../frontend/src/pages/HomePage.tsx) | React shell handles 3 explicit connection states: `loading`, `available`, and `unavailable` (with error message & retry). Renders `BackendStatus` and `AssessmentCard`. Respects `insufficient_data` without inventing values. | prscr (UX/Demo/QA) | Operator, Demo presenter | Adding new presentation components, styles, or detailed inspection views within existing API contracts. | Hardcoding mock numbers that bypass backend responses, failing to handle unavailable/error states. |
| **Prediction Boundary ($T_{assess} = T_{dispatch}$)** | `FIXED CHALLENGE / SPONSOR CONSTRAINT` | [`sponsor_pack/README.md`](../sponsor_pack/README.md), [`docs/challenge_canon.md`](./challenge_canon.md), [`docs/evaluation.md`](./evaluation.md) | Prediction moment is strictly $T_{assess} = T_{dispatch}$. Features must only use data available at or before dispatch. Arrival checks, actual transit delay/incidents, realized en-route telemetry, and final outcomes are strictly forbidden prediction inputs. Non-negotiable challenge invariant. | Sponsor (Rule) / Viktor (Audit) | Feature engineering, Analytics, Model training, Evaluation | None (Fixed challenge constraint). | Using arrival inspection, realized transit delay, or final outcomes in features or explanations. Cannot be altered by VLD-02 for technical convenience. |
| **Modular Monolith Architecture** | `ACCEPTED DECISION` | [`docs/architecture.md`](./architecture.md), [`docs/decisions/0001-foundation-architecture.md`](./decisions/0001-foundation-architecture.md) | Single repository modular monolith: React+TS frontend, FastAPI+Python backend, typed HTTP boundaries, batch/on-demand MVP, deterministic baseline first, ML optional, LLM outside critical path, stateless foundation. | Vladimir (Integrator) / SoS Team | Entire team | Internal refactoring within existing layer directories. | Introducing microservices, message queues, Docker/Kubernetes requirements, external DB dependencies without a formal decision gate. |
| **Production Ingestion & BatchInput** | `ACCEPTED DECISION (VLD-02A) / NOT YET IMPLEMENTED IN CODE` | [`docs/data_contract.md`](./data_contract.md), [`docs/decisions/0002-predictive-input-semantics.md`](./decisions/0002-predictive-input-semantics.md) | Canonical `BatchAssessmentInput` semantics, eligibility matrix across all 73 fields, and temporal leakage boundary accepted under VLD-02A ([ADR 0002](./decisions/0002-predictive-input-semantics.md)). Not yet implemented in code. | Vladimir (Decision) / Igor (Implementation) | Ingestion pipeline, Analytics engine | Unblocks bounded implementation task IGR-03 to create Pydantic domain models in `backend/app/domain/batch.py` and CSV ingestion mappers in `backend/app/ingestion/`. | Implementing feature engineering, imputation, or analytics scoring inside the ingestion task. |
| **Analytics Baseline & Deterioration Horizon** | `DOCUMENTED BUT NOT YET IMPLEMENTED/ENFORCED` | [`docs/domain_rules.md`](./domain_rules.md), [`docs/evaluation.md`](./evaluation.md) | No risk calculation formula, heuristic, or deterioration onset calculation exists in application code. Synthetic fixture returns `insufficient_data`. | Viktor (D&E) / Alisa (Domain) / Igor (Engine) | Risk Assessment service, Operator UI | Drafting candidate rules in `docs/domain_rules.md`. Baseline requires accepted target and evaluation semantics from Viktor, plus method-specific evidence (with domain rules required conditionally if baseline relies on agronomic thresholds). | Computing synthetic scores or dates without approved baseline definitions and target evidence. |

---

# 3. Workstream producer → consumer map

This map establishes the flow of dependencies across the five human workstream owners. Rather than a rigid waterfall, four parallel evidence streams feed into the Integrator decision gates, while downstream implementation proceeds along task-specific dependency paths.

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    PARALLEL RECONNAISSANCE EVIDENCE                     │
│                                                                         │
│  Alisa product/domain evidence ────────┐                                │
│  Viktor data/evaluation evidence ──────┤                                │
│  Igor technical recon/evidence ────────┼──► Vladimir integration /      │
│  prscr UX/demo evidence ───────────────┘    decision gate (VLD-02)      │
└────────────────────────────────────────────────────┬────────────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              TASK-SPECIFIC DOWNSTREAM IMPLEMENTATION PATHS              │
│                                                                         │
│  • Ingestion & Input Pipelines:                                         │
│    VDR-01 Accepted ──► Technical raw parsing / validation helpers       │
│    VDR-01 + VDR-02 Accepted ──► VLD-02A Accepted (ADR 0002) ──►        │
│    Canonical BatchAssessmentInput & predictive mapping (IGR-03 unblocked)│
│                                                                         │
│  • Deterministic Baseline & Risk Engine:                                │
│    Target & Evaluation Semantics (Viktor) + Method Evidence             │
│    [+ Domain Rules (Alisa) if method relies on agronomic thresholds]    │
│    ──► VLD-02 ──► Igor Analytics Baseline Engine                        │
│                                                                         │
│  • User Experience & Operator Dashboard:                                │
│    PUX Recon/Flow ──► Stable API Contracts ──► prscr Operator UI        │
│                                                                         │
│  • Predictive Modeling (Optional ML Tier):                              │
│    Accepted Baseline + Justification (Viktor) ──► VLD-02 ──► Igor Model │
└────────────────────────────────────────────────────┬────────────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     VLADIMIR FINAL INTEGRATION GATES                    │
│  • VLD-03: End-to-End Functional Verification & Integration Test Suite  │
│  • VLD-04: Runtime Readiness & Operational Demo Runbook                 │
│  • VLD-05: Pitch Consistency & Traceable Evidence Audit                 │
└─────────────────────────────────────────────────────────────────────────┘
```

### Downstream dependencies are task-specific, not monolithic

Downstream implementation does not wait for an all-or-nothing milestone across all workstreams. Decision gates and downstream tasks are bounded strictly to their required evidence:

- **Viktor sequence:** `VDR-02` (temporal chronology and leakage audit) starts only after `VDR-01` (dataset inventory and referential integrity) has been completed and reviewed.
- **Predictive input semantics vs raw parsing:** Accepted `VDR-01` may be sufficient to support a narrowly scoped implementation task for factual raw parsing and structural validation where the task only reflects measured schema and integrity evidence. However, `VDR-02` (temporal leakage audit) is mandatory before predictive/canonical assessment input semantics (`BatchAssessmentInput`) are finalized, including feature eligibility at $T_{dispatch}$, leakage-sensitive transformations, and any mapping that determines what enters predictive analytics. Production `BatchAssessmentInput` and equivalent predictive canonical semantics require the relevant VLD-02 decision before implementation. Technical CSV-reading helpers do not automatically require VDR-02 if they do not establish shared predictive semantics.
- **Later analytical and model work:** A deterministic baseline requires accepted analytical target and evaluation semantics from Viktor, plus whatever evidence its actual method relies upon. Alisa/domain evidence (`APR-01`) is additionally required when the chosen baseline method depends on agronomic thresholds, crop-specific rules, domain interpretation, or action/recommendation semantics. Domain evidence is conditional on the baseline design, not universally mandatory for every possible baseline.
- **Product and domain evidence:** Sourced domain research and operator workflow evidence from Alisa (`APR-01`) is required only for decisions that depend on product or domain meaning (such as action codes, recommendation priorities, operator workflow scope, and domain rule admission). Technical pipeline and data-loading tasks that do not alter domain semantics proceed once their technical evidence is accepted.
- **UX and UI development:** prscr's user interface work proceeds through UX reconnaissance, screen flows, and fixture-backed wireframes under its own sequential workflow (`PUX-00–07`), binding to production backend endpoints once Igor's routes are approved and operational.

## 3.1. Detailed ownership inventory

### Vladimir — Integrator
- **Currently owns:** System architecture continuity, cross-workstream contracts, boundary definitions, integration gates (VLD-01 to VLD-05), conflict resolution, and final solution assembly.
- **Accepted output that currently exists:** The VLD-01 baseline of [`docs/integration_contract.md`](./integration_contract.md), [`docs/team_roles.md`](./team_roles.md), [`docs/architecture.md`](./architecture.md), [`docs/decisions/0001-foundation-architecture.md`](./decisions/0001-foundation-architecture.md), [`docs/decisions/0002-predictive-input-semantics.md`](./decisions/0002-predictive-input-semantics.md) (VLD-02A / ADR 0002, PR #16), [`docs/data_contract.md`](./data_contract.md), [`docs/domain_rules.md`](./domain_rules.md), [`docs/evaluation.md`](./evaluation.md), [`docs/challenge_canon.md`](./challenge_canon.md), [`docs/assumptions_unknowns.md`](./assumptions_unknowns.md), [`docs/demo_runbook.md`](./demo_runbook.md), [`docs/workstreams/vladimir-integration.md`](./workstreams/vladimir-integration.md). This VLD-R3 current-state update is prepared for human review, not a new accepted decision.
- **Future planned output:** Subsequent VLD-02 decision records (target, evaluation protocol, baseline/analytics, deterioration-horizon runtime representation, reliability policy), VLD-03 end-to-end integration test reports, VLD-04 operational runbook, VLD-05 claim audit and pitch gate verdict.
- **Who consumes output:** All workstream owners (Igor, Viktor, prscr, Alisa).
- **Downstream work blocked until evidence exists:** Decision gates are task-specific. VLD-02A ([ADR 0002](./decisions/0002-predictive-input-semantics.md)) accepted canonical predictive-input semantics and the 73-field eligibility taxonomy, unblocking bounded implementation task IGR-03 (`BatchAssessmentInput` Pydantic models and CSV mappers). Analytics engine decisions remain BLOCKED on accepted target/evaluation semantics and method-specific evidence (with domain rules required conditionally if the baseline relies on agronomic thresholds). Cannot authorize backend production models or frontend dashboard implementations ahead of their specific prerequisite evidence.

### Viktor — Data & Evaluation Owner
- **Currently owns:** Dataset profiling, schema verification, data quality analysis, join validation, temporal analysis, leakage prevention, identifying usable labels, producing target/evaluation evidence and proposals, evaluation methodology, baseline comparison, and guarding against false precision and misleading metrics.
- **Accepted output that currently exists:** [`docs/data_recon/01_dataset_inventory.md`](./data_recon/01_dataset_inventory.md) (VDR-01, PR #7); [`docs/data_recon/02_temporal_leakage.md`](./data_recon/02_temporal_leakage.md) (VDR-02, PR #14); [`docs/data_recon/03_target_horizon_feasibility.md`](./data_recon/03_target_horizon_feasibility.md) (VDR-03, PR #18, ACCEPTED / INTEGRATED); workstream contract [`docs/workstreams/viktor-data-recon.md`](./workstreams/viktor-data-recon.md). The supplied dataset remains the source snapshot.
- **Pending work / future output:** Subsequent evaluation protocol, split design, and predictability feasibility analysis (VDR-04 / VDR-04A), baseline results, and model evaluation reports are future work.
- **Who consumes output:** Vladimir (integration gates), Igor (ingestion, canonical entity modeling, analytics), prscr (realistic data distributions and batch scenarios), Alisa (grounding product workflows in real data limits).
- **Downstream work blocked until evidence exists:** Accepted VDR-01, VDR-02, and VDR-03 satisfy the inventory, temporal/leakage, and target/horizon feasibility evidence prerequisites. Canonical predictive-input semantics were accepted under ADR 0002. VDR-03 established that candidate outcomes have known relationships and that exact continuous deterioration countdown is unsupported, but explicitly did not select a target, metric, split, baseline, model, or runtime horizon policy. Later evaluation and model work requires separately contracted Viktor evidence (evaluation design, baseline results, predictability feasibility).

### Igor — Technical Deputy
- **Currently owns:** Backend and application-layer implementation, API routes, implementation of backend/application models within accepted shared contracts, ingestion logic, deterministic baseline engine, optional learned model integration, explainability and recommendation services. Igor may decide implementation details inside agreed technical scope, but does not independently own changes to global/shared domain contracts.
- **Accepted output that currently exists:** [`docs/recon/IGR-01-technical-recon.md`](./recon/IGR-01-technical-recon.md) (IGR-01, PR #8); FastAPI application skeleton (`backend/app/main.py`, `backend/app/api/routes.py`), Pydantic output models (`backend/app/domain/assessment.py`), synthetic demo fixture (`backend/app/services/demo_assessment.py`), backend tests (`backend/tests/`), workstream contract [`docs/workstreams/igor-technical-recon.md`](./workstreams/igor-technical-recon.md).
- **Future planned output:** Separately contracted raw parsing/structural diagnostics (bounded IGR-02), ingestion implementation (`backend/app/ingestion/`), analytics engine (`backend/app/analytics/`), explainability service (`backend/app/explain/`), recommendation service (`backend/app/recommend/`), batch assessment API routes. IGR-01's proposed implementation sequence is not an accepted canonical-input contract.
- **Who consumes output:** prscr (API responses for UI consumption), Vladimir (system coherence and test verification).
- **Downstream work blocked until evidence exists:** Accepted VDR-01 and VDR-02 satisfied inventory and temporal/leakage prerequisites, and VLD-02A ([ADR 0002](./decisions/0002-predictive-input-semantics.md)) accepted canonical predictive-input semantics, unblocking IGR-03 for canonical models and ingestion mapping. This does not authorize feature windows, imputation/exclusion policy, target selection, or analytics logic. Analytics remains blocked on accepted target/evaluation semantics and method-specific baseline evidence.

### prscr — UX, Demo + QA
- **Currently owns:** Frontend implementation and operator-facing workflow, user interface, presentation of risks, factors, and actions, loading/degraded/insufficient-data states, demo reliability, and exploratory QA.
- **Accepted output that currently exists:** [`prscr_ux_demo_qa_report.md`](../prscr_ux_demo_qa_report.md) (PUX-00–07, PR #9, repository root); React+TS+Vite shell (`frontend/src/`), connection state management (`HomePage.tsx`), synthetic assessment rendering (`AssessmentCard.tsx`), health status display (`BackendStatus.tsx`), typed API client (`api/client.ts`, `api/contracts.ts`), workstream contract [`docs/workstreams/prscr-ux-demo-qa.md`](./workstreams/prscr-ux-demo-qa.md). Acceptance of the recon does not make its provisional wireframes, API proposals, or policies accepted decisions, or its planned QA cases executed tests.
- **Future planned output:** PUX-08 data-to-UX reconciliation, agreed UX specifications, interactive batch dashboard, detailed factor inspection UI, demo flow execution, and automated/exploratory QA execution evidence.
- **Who consumes output:** Vladimir (demo verification and UI claim audit), Igor (API usability requirements), judges/operators (user interface experience).
- **Downstream work blocked until evidence exists:** Implementation of final batch selection tables, risk meters, and recommendation widgets is blocked until Igor delivers assessment endpoints and Alisa/Viktor define what data fields and actions are legitimately supported. PUX-00–07 recon is accepted; PUX-08 remains the future reconciliation step under its existing workflow, without bypassing implementation prerequisites.

### Alisa — Product Owner
- **Currently owns:** Challenge interpretation, user and operator problem framing, requirement and mentor clarification tracking, domain research (post-harvest practices, cold chain management), recommendation semantics, and pitch/presentation narrative.
- **Accepted output that currently exists:** Workstream contract [`docs/workstreams/alisa-product-recon.md`](./workstreams/alisa-product-recon.md); research evidence package [`docs/product_recon/`](./product_recon/) (APR-01 steps 0–5, PR #17).
- **Current APR-01 status:** APR-01 steps 0–5 are **DELIVERED / INTEGRATED through [PR #17](https://github.com/Slave-of-Skynet/training_agrifood/pull/17)** and **ACCEPTED AS PRODUCT/DOMAIN RESEARCH EVIDENCE**. Individual research notes retain their own `FACT`, `DOMAIN FACT`, `INFERENCE`, `UNKNOWN`, and `NOT CANON` labels; APR-01 research is **NOT AUTOMATICALLY CANON AS A WHOLE** and does not override official challenge materials or accepted data evidence.
- **Future planned output:** Candidate rule reviews for `docs/domain_rules.md`, pitch deck narrative structure, and follow-up domain clarifications.
- **Who consumes output:** Vladimir (ensuring solution solves the right problem), prscr (operator mental model and information hierarchy), Igor (business logic constraints), Viktor (interpreting target meaning and business error costs).
- **Downstream work blocked until evidence exists:** Final recommendation labels and operator action scopes are blocked until external agricultural and post-harvest sources are reviewed and accepted as decisions. Product/domain evidence is required only for decisions that depend on product/domain meaning (including agronomic thresholds if required by the chosen baseline). Pitch claims regarding economic loss reduction are blocked until evaluation evidence is obtained.

---

# 4. Integration boundary matrix

Every transition across system layers represents an integration boundary. This matrix defines the contracts, current statuses, governing UNKNOWN areas, evidence requirements, and decision authorities for every boundary.

| Boundary | Producer | Consumer | Current Contract | Current Status | Relevant Canonical UNKNOWN Area(s) | Evidence Owner & Task | Evidence Required Before Decision | Decision / Gate Owner | What Downstream Work is Unsafe if Unresolved |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **B1: Raw Dataset → Ingestion** | Sponsor pack (`sponsor_pack/data/*.csv`) | Ingestion layer (`backend/app/ingestion/`) | Supplied schema plus accepted [VDR-01 snapshot inventory/integrity evidence](./data_recon/01_dataset_inventory.md); no production parsing policy accepted. | **FACT: SUPPLIED SNAPSHOT EMPIRICALLY PROFILED**; observed schema/types, counts, integrity and relationships measured. **NO INGESTION IMPLEMENTATION.** | Field names and types, Joins and entity relationships, Dataset size | Viktor (`VDR-01`, accepted); Igor (future bounded task) | VDR-01 satisfies the snapshot evidence prerequisite for factual raw parsing/structural diagnostics. Production validation, unseen-data behavior, repair/exclusion policy and canonical predictive mapping remain UNKNOWN / NOT DECIDED. | Vladimir (separate bounded contract / VLD-02 if shared contract changes) | A separately contracted raw-only IGR-02 may reflect measured evidence. It must not silently repair/drop data, assume future datasets have identical cardinalities, or establish production/predictive semantics. |
| **B2: Ingestion → Canonical Representation** | Ingestion layer (`backend/app/ingestion/`) | Canonical entity models (`backend/app/domain/batch.py`) | **BatchAssessmentInput: ACCEPTED under [ADR 0002](./decisions/0002-predictive-input-semantics.md).** Not yet implemented in code. | **ACCEPTED DECISION (VLD-02A); unblocks bounded task IGR-03.** | Field names and types, Joins and entity relationships, Assessment-time availability, Missing and noisy data | Viktor (`VDR-01` accepted; `VDR-02` accepted) | VDR-01 supplies observed grain and join paths; VDR-02 supplies dispatch-time availability and leakage evidence; VLD-02A accepts canonical input semantics and mapping. | Vladimir (VLD-02A Decision Gate accepted; Igor implements schema in IGR-03) | Implementing feature engineering, imputation, or analytics scoring inside the ingestion task. |
| **B3: Canonical Representation → Analytics Engine** | Canonical entity models (`backend/app/domain/batch.py`) | Analytics engine (`backend/app/analytics/`) | `BatchAssessmentInput` accepted under [ADR 0002](./decisions/0002-predictive-input-semantics.md); `RiskAssessment` output contract defined; VDR-03 target/horizon feasibility evidence accepted. | **BLOCKED FOR ANALYTICS:** canonical input semantics accepted under ADR 0002 and VDR-03 target/horizon feasibility evidence accepted, but target, evaluation protocol, baseline/method, feature-engineering policy, and runtime deterioration-horizon policy remain unresolved / unaccepted. Additional evaluation/predictability evidence and an Integrator decision gate are required. | Measurement frequency and time series, Assessment-time availability, Outcomes and candidate labels, Deterioration timing, Agronomic rules and thresholds | Viktor (`VDR-02` and `VDR-03` accepted, `VDR-04/VDR-04A` future) & Alisa (domain research accepted, conditionally) | Accepted VDR-02 and VDR-03 satisfy temporal/leakage and target/horizon feasibility prerequisites; additional evaluation/predictability evidence (VDR-04/VDR-04A); temporal window rules and method-specific baseline evidence (domain rules required conditionally if the baseline relies on agronomic thresholds). | Vladimir (VLD-02 Decision Gate to accept baseline logic; Igor implements in subsequent task) | Analytics implementation before target/evaluation/baseline gates; inventing feature transformations; inventing targets or risk formulas; synthetic risk scoring (IGR-03 unblocked for canonical models and ingestion mapping only). |
| **B4: Analytics → RiskAssessment** | Analytics engine / Services | Public domain model (`backend/app/domain/assessment.py`) | Stable `RiskAssessment` contract: `status`, `risk`, `deterioration_horizon`, `factors`, `recommendation`, `reliability`, `provenance`. | **ENFORCED ON FIXTURE ONLY** (Synthetic fixture returns `insufficient_data`). | Outcomes and candidate labels, Deterioration timing, Intervention and action effects, Missing and noisy data | Viktor (target/baseline), Alisa (action meaning), Igor (orchestration) | Proof that risk score reflects defensible ranking or probability; proof that horizon has measurable onset proxy; verified action codes. | Vladimir (VLD-02 Decision Gate / VLD-03 Verification Gate) | Returning fake risk scores, ungrounded deterioration dates, or unverified recommendations to the public contract. |
| **B5: RiskAssessment → API** | FastAPI routes (`backend/app/api/routes.py`) | HTTP response / JSON serialization | `GET /api/v1/health` and `GET /api/v1/demo/assessment` serialized via Pydantic `ContractModel` (`extra="forbid"`). | **OPERATIONAL (FOUNDATION)** | Realtime source, Persistence needs | Igor (`IGR-01`, API implementation) | Technical verification of serialization, error handling, performance, and endpoint parameterization. | Vladimir (VLD-02 Gate) with Igor | Altering existing public routes; adding unversioned breaking parameters; exposing internal errors. |
| **B6: API → Frontend** | API endpoints | React UI client (`frontend/src/api/client.ts`, `contracts.ts`) | TypeScript interfaces mirroring Pydantic models; fetch client with AbortSignal; handling loading/success/error. | **OPERATIONAL (FOUNDATION)** | Realtime source | prscr (`PUX-00-07`, UI implementation) & Alisa (`APR-01`) | Tested HTTP communication, error recovery, network timeout handling, type agreement verification, and operator workflow requirements as empirical input to settling Realtime source / UI presentation needs. | Vladimir (VLD-02 / VLD-03 Gate) with prscr & Igor | Manual divergence between TypeScript interfaces and Python Pydantic models; UI crashing on missing optional fields; building workflows disconnected from operator realities. |
| **B7: Assessment Semantics → Demo** | Application UI & Backend | Demo script & Operator experience | [`docs/demo_runbook.md`](./demo_runbook.md): Verified local startup, health check, synthetic fixture rendering, failure states. | **FOUNDATION ONLY** (Proves connectivity, not agricultural validity). | Hosting constraints, Persistence needs | prscr (Demo flow), Vladimir (Runbook readiness) | Reproducible step-by-step runbook; proven fallback for offline/backend failure; clearly labeled synthetic data. | Vladimir (VLD-04 Gate) | Presenting synthetic demo data as real prediction results; live demo failure due to unhandled exceptions or network dependencies. |
| **B8: Verified Behaviour → Product Claims / Pitch** | Implemented system & Evaluation reports | Pitch deck, README, team claims | Canon rule: Every claim must be classified (FACT, DECISION, UNKNOWN, etc.) and backed by reproducible evidence. | **STRICTLY CONSTRAINED** (No performance, accuracy, or loss-reduction claims permitted today). | Monetary and quantity fields, Crop diversity, Learned model family, Outcomes and candidate labels | Vladimir (VLD-05 Gate), Viktor (evaluation), Alisa (narrative) | Fully executed test suites, reproducible evaluation notebooks/reports, cited domain literature, verified audit trail. | Vladimir (VLD-05 Gate) | Discrediting team credibility before judges with exaggerated claims, unsubstantiated loss-reduction figures, or fabricated accuracy metrics. |

---

# 5. UNKNOWN → evidence → decision triggers

[`docs/assumptions_unknowns.md`](./assumptions_unknowns.md) is and remains the **sole canonical global UNKNOWN register** for the project.

The table below does **not** reproduce or duplicate the descriptions or general questions from that register. Instead, it defines strictly the **operational integration relationships** around those UNKNOWN areas: which integration boundary is affected, who owns the evidence task, what specific evidence triggers a VLD-02 decision gate, and which downstream workstream consumers are blocked until that gate is closed. The required-evidence column includes both already accepted observations and outstanding decision inputs; the current-status column separates them. No compound UNKNOWN is closed solely because inventory evidence exists.

| Canonical UNKNOWN Area (from [`assumptions_unknowns.md`](./assumptions_unknowns.md)) | Affected Boundary | Evidence Owner & Task | Specific Evidence Required | Decision Trigger & Gate | Downstream Consumers Blocked | Current Status |
| --- | --- | --- | --- | --- | --- | --- |
| **Field names and types** | B1 (Ingestion), B2 (Canonical) | Viktor (`VDR-01`), Vladimir (`VLD-02A`) | Measured row counts, parsing exceptions, column null percentages, type conformance across all 8 tables; normative mapping table. | VLD-02A Gate ([ADR 0002](./decisions/0002-predictive-input-semantics.md)): Adopted canonical input contract and 73-field eligibility matrix. | Igor: Factual raw parsing helpers and validator implementation (unblocked by VDR-01 and VLD-02A). | **VLD-02A ACCEPTED:** canonical input contract and 73-field eligibility matrix established under ADR 0002. Production validation implementation and unseen-value policy in code remain for IGR-03. |
| **Joins and entity relationships** | B1 (Ingestion), B2 (Canonical) | Viktor (`VDR-01`), Vladimir (`VLD-02A`) | Tested join integrity among facilities, zones, sessions, batches, checks, shipments, telemetry, outcomes. Orphan counts. | VLD-02A Gate ([ADR 0002](./decisions/0002-predictive-input-semantics.md)): Adopted canonical entity boundaries and join rules. | Igor: Canonical data structure and relational join implementation (unblocked for IGR-03). | **VLD-02A ACCEPTED:** canonical entity boundaries, authoritative identity sources, and join-verification rules across all 5 batch_id occurrences established under ADR 0002. Unexpected-cardinality handling remains for IGR-03. |
| **Dataset size** | B1 (Ingestion), Storage architecture | Viktor (`VDR-01`), Igor (`IGR-01`) | Exact file sizes, memory footprint when loading tables (especially `sensor_readings.csv`), query latency. | VLD-02 Gate: Decide whether in-memory processing suffices or indexed storage is required. | Igor: Data loading architecture; Vladimir: Operational demo hardware requirements. | **VDR-01 / IGR-01 ACCEPTED:** snapshot counts/sizes known; runtime memory, latency, concurrency and storage choice remain UNKNOWN. |
| **Measurement frequency and time series** | B2 (Canonical), B3 (Analytics) | Viktor (`VDR-01`, `VDR-02`) | Actual sampling intervals (nominal 30 min), timestamp continuity, gap frequencies, out-of-session readings. | VLD-02 Gate: Adopt sensor aggregation windows and missing-telemetry imputation/rejection rules. | Igor: Time-series feature extraction pipelines; Viktor: Baseline feature definitions. | **VDR-01 / VDR-02 ACCEPTED:** sampling/gaps/coverage and dispatch staleness measured (non-truncated batches <= 29.4 min; 204 batches truncated on 2025-12-31). Feature aggregation windows, staleness tolerance, and imputation/rejection policy await later evidence and VLD-02 decision. |
| **Assessment-time availability** | B2 (Canonical), B3 (Analytics) | Viktor (`VDR-02`), Vladimir (`VLD-02A`) | Audit of all fields at dispatch; list of strictly forbidden future fields (arrival checks, transit delays, final outcomes); shared-zone/chamber leakage audit. | VLD-02A Gate ([ADR 0002](./decisions/0002-predictive-input-semantics.md)): Adopted canonical input semantics, feature eligibility filter, and telemetry boundary ($T_{entry} \le t \le T_{dispatch}$). | Igor: Bounded implementation task IGR-03 for predictive `BatchAssessmentInput` (UNBLOCKED); Viktor: Leakage-free split design. | **VLD-02A ACCEPTED:** dispatch boundary $T_{assess} = T_{dispatch}$ enforced; safe pre-dispatch vs forbidden future/arrival fields codified in ADR 0002. Unblocks bounded implementation task IGR-03. Analytics, target, and split remain blocked on subsequent evidence. |
| **Outcomes and candidate labels** | B3 (Analytics), B4 (RiskAssessment) | Viktor (`VDR-03` accepted, `VDR-04A` future) & Alisa (`APR-01` accepted as research evidence) | Distribution of outcome fields (`quality_status`, `loss_fraction_pct`, `quality_score`, `economic_loss_eur`); definition of business risk target. | VLD-02 Gate: Adopt formal analytical target definition and evaluation metrics. | Viktor: Model training & evaluation; Igor: Analytics engine risk calculation; prscr: UI risk gauge. | **VDR-01 / VDR-03 ACCEPTED:** candidate outcome distributions and historical mathematical/statistical relationships profiled. Primary target, task framing, score meaning, label fitness, and evaluation metrics remain UNKNOWN / PENDING LATER D&E (VDR-04A). |
| **Deterioration timing** | B3 (Analytics), B4 (RiskAssessment) | Viktor (`VDR-03` accepted, `VDR-04` future) & Alisa (`APR-01` accepted as research evidence) | Analysis of whether intermediate `quality_checks` or telemetry provide supportable onset timestamps or shelf-life proxies. | VLD-02 Gate: Decide whether `deterioration_horizon` can be computed or must remain null. | Igor: Horizon estimation logic; prscr: Timeline visualization on frontend. | **VDR-03 ACCEPTED:** 3 discrete QC checkpoints verified; no exact deterioration-onset timestamp exists; continuous deterioration countdown is unsupported by observations. Runtime representation (null, coarse interval, proxy, or no horizon output) remains UNKNOWN / DECISION REQUIRED. |
| **Intervention and action effects** | B3 (Analytics), B4 (RiskAssessment) | Alisa (`APR-01`), Viktor (later D&E contract) | Sourced domain literature on post-harvest interventions; check if dataset contains action-outcome pairs. | VLD-02 Gate: Adopt structured `action_code` catalog and human review guardrails. | Igor: Recommendation service; prscr: Action recommendation cards. | **APR-01 DELIVERED / ACCEPTED AS RESEARCH EVIDENCE (NOT CANON); LATER D&E PENDING:** no accepted action/effect semantics. |
| **Monetary and quantity fields** | B3 (Analytics), B8 (Pitch) | Viktor (`VDR-01`, `VDR-03`), Alisa (`APR-01`) | Verification of `economic_loss_eur` derivation and validity for business impact claims. | VLD-02 Gate: Decide if financial impact estimation is supportable in MVP. | Alisa: Pitch ROI claims; Igor: Potential financial loss display. | **VDR-01 / VDR-03 ACCEPTED:** historical formula deterministically reproduced within reported tolerance. Business interpretation, prevented loss, ROI and causal savings remain UNKNOWN; APR-01 accepted as research evidence, not canon. |
| **Crop diversity** | B2 (Canonical), B3 (Analytics) | Viktor (`VDR-01`), Alisa (`APR-01`) | Distribution of crop types in batches; domain storage requirements per crop. | VLD-02 Gate: Decide single-crop MVP focus or multi-crop segmentation. | Igor: Model/rule scoping; Viktor: Subgroup evaluation protocol. | **VDR-01 ACCEPTED; APR-01 ACCEPTED AS RESEARCH EVIDENCE:** crop/cultivar coverage and biological profiles measured. Transferability, rule scope and subgroup sufficiency remain UNKNOWN; APR-01 not automatically canon. |
| **Missing and noisy data** | B2 (Canonical), B4 (RiskAssessment) | Viktor (`VDR-01`), Igor (`IGR-01`) | Frequency of missing sensor readings or missing checks; criteria for triggering `insufficient_data`. | VLD-02 Gate: Adopt minimum data sufficiency requirements for an assessment. | Igor: Invariant enforcement in application services; prscr: Degraded UI rendering. | **VDR-01 / IGR-01 ACCEPTED:** observed missingness and technical foundation known. Repair/exclusion, minimum sufficiency and degradation policies remain UNKNOWN. |
| **Realtime source** | B1 (Ingestion), B5 (API) | Alisa (`APR-01`), Igor (`IGR-01`) | Confirmation of operator workflow needs (batch upload vs scheduled batch vs simulated stream). | VLD-02 Gate: Confirm MVP runtime processing mode (retains batch/on-demand by default). | Igor: API route design; prscr: Upload/run workflow in UI. | **IGR-01 ACCEPTED; APR-01 ACCEPTED AS RESEARCH EVIDENCE:** batch/on-demand decision retained; additional source/workflow requirements unresolved. |
| **Hosting constraints** | B7 (Demo) / Runtime Environment | Vladimir (`VLD-04`), Igor (`IGR-01`), prscr (Demo needs) | Target demonstration environment needs, network connectivity requirements, hardware resources, deployment complexity. | VLD-04 Gate: Environment and platform selection remains under VLD-04 unless an earlier blocker requires a human decision. No hosting provider preselected; remote hosting not required by default. | Vladimir: Demo deployment runbook, final runtime environment setup. | **IGR-01 / PUX-00–07 ACCEPTED AS RECON:** target demo environment remains unresolved; VLD-04 still required. |
| **Agronomic rules and thresholds** | B3 (Analytics), `docs/domain_rules.md` | Alisa (`APR-01`), Viktor (`VDR-01`) | Primary literature sources (FAO, university extension) for temperature/humidity thresholds; data compatibility. | VLD-02 Gate: Formal admission of candidate rules into `docs/domain_rules.md`. | Igor: Deterministic baseline rule implementation (if baseline design relies on agronomic thresholds); prscr: Explanatory factor text. | **VDR-01 ACCEPTED; APR-01 ACCEPTED AS RESEARCH EVIDENCE:** data compatibility and literature sources compiled; formal admission into docs/domain_rules.md remains pending. |
| **Learned model family** | B3 (Analytics) | Viktor (later D&E contract) | Measured performance of deterministic baseline; empirical proof that ML provides meaningful improvement. | VLD-02 Gate: Authorize learned tier implementation in `backend/app/analytics/`. | Igor: Model serialization and inference pipeline integration. | **PENDING LATER D&E:** no accepted baseline comparison or learned-tier justification. |
| **Persistence needs** | Architecture, Storage layer | Igor (`IGR-01`), Viktor (`VDR-01`), Alisa (`APR-01`) | Volume, lifecycle, concurrency, audit, and operator workflow needs; whether in-memory processing suffices or disk/DB persistence is needed. | VLD-02 Gate: May become a VLD-02 cross-cutting decision if accepted evidence shows persistence is required for application implementation. | Igor: Database setup/storage layer (if needed); Vladimir: Architecture consistency. | **VDR-01 / IGR-01 ACCEPTED:** file volume and technical state known; runtime/workflow needs and storage decision remain unresolved. |

---

### Additional VDR-01 cross-cutting triggers

These reference the corresponding entries in the sole global UNKNOWN register; target ambiguity is already covered by the Outcomes and candidate labels row above.

| Canonical UNKNOWN area | Affected boundary | Evidence available | Evidence / decision still required | Owner / blocked consumers |
| --- | --- | --- | --- | --- |
| Telemetry truncation | B2, B3, B4 | Accepted VDR-01 identifies the truncated-coverage batch group | Later feature/evaluation evidence and relevant VLD-02 decisions on treatment, sufficiency and degradation; no imputation/exclusion policy selected | Viktor + Igor → Vladimir; feature, evaluation and UI consumers |
| Shared chamber / zone-time dependence | B2, B3 | Accepted VDR-01 establishes concurrent chamber sharing; accepted VDR-02 measures 96.33% chamber sharing, 157 chamber-time clusters, and an average of 95.79% of test batches sharing an identical chamber microclimate cluster with training batches in standard randomized 80/20 splits | VDR-02 prerequisite satisfied; later split/evaluation evidence (VDR-04) and decision still required, including residual facility/zone dependence; no claim that cluster blocking solves leakage | Viktor → Vladimir; analytics/evaluation consumers |
| Nominal capacity exceedance | B3, B4, B8 | Accepted VDR-01 records exceedance observations | Data/domain/product interpretation and explicit decision before use in risk logic; neither a defect nor a valid risk signal is established here | Viktor + Alisa → Vladimir; analytics, explanations and claims |

---

# 6. Shared-contract change triggers

Any proposed modification that alters the boundary between workstreams, changes public API contracts, or impacts external claims represents a **shared-contract change**.

No individual developer or automated agent may implement a shared-contract change locally. A formal integration gate (VLD-02 or equivalent human approval) is strictly required before changing:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   SHARED-CONTRACT CHANGE TRIGGERS                      │
│                                                                        │
│  1. Public RiskAssessment Contract: fields, nullability, enums         │
│  2. HTTP API Surface: routes, methods, request/response models         │
│  3. Canonical Input Model: BatchInput fields, validation, types        │
│  4. Prediction Semantics: changes to T_assess = T_dispatch boundary    │
│  5. Evaluation & Split Protocol: target choice, metric definitions     │
│  6. Domain Rules & Thresholds: adding active rules to domain_rules.md  │
│  7. Recommendation Meaning: action codes, priority, causal claims      │
│  8. Provenance & Tiering: engine_tier semantics, simulation flags      │
│  9. Application Persistence / Storage: storage layer, DB/ORM adoption │
│  10. System Dependencies: pyproject.toml, package.json, lockfiles      │
└────────────────────────────────────────────────────────────────────────┘
```

### Protection of sponsor prediction boundary ($T_{assess} = T_{dispatch}$)

The prediction boundary ($T_{assess} = T_{dispatch}$) is a higher-authority supplied challenge constraint. A VLD-02 decision cannot override it for technical convenience.

If newer authoritative challenge clarification changes it, the change procedure must:

1. **Surface the conflict:** Explicitly identify the discrepancy between the existing constraint and new sponsor guidance.
2. **Update canon and history:** Record the new authoritative clarification in `docs/challenge_canon.md` and document the requirement evolution.
3. **Reconsider internal decisions:** Formally re-evaluate dependent data contracts, feature definitions, and evaluation designs at an integration gate.

### Persistence vs deployment governance

- **Application persistence / storage:** May become a VLD-02 cross-cutting decision if accepted evidence shows persistence is required for application implementation.
- **Deployment / hosting:** Environment and platform selection remains under VLD-04 unless an earlier blocker requires a human decision. No hosting provider is preselected, and remote hosting does not require VLD-02 by default.

### Change gate procedure

When an owner discovers that a shared-contract change is necessary:

1. **STOP local implementation:** Do not modify the shared contract file.
2. **Prepare a Decision Packet (VLD-02 format):**
   - Exact problem and why existing contract is insufficient;
   - Cited evidence (from VDR, APR, or IGR);
   - Proposed exact diff/schema;
   - Impacted workstreams and files;
   - Alternatives considered and rejection rationale.
3. **Submit to Integrator (Vladimir):**
   - Integrator evaluates impact against challenge canon and existing guarantees.
   - Record the accepted decision in the appropriate canonical destination (`docs/decisions/<ADR>.md`, `docs/data_contract.md`, `docs/evaluation.md`, `docs/domain_rules.md`, `docs/architecture.md`, `docs/challenge_canon.md`, `docs/assumptions_unknowns.md`). Use an ADR when the decision is architectural or when an explicit durable decision record is useful.
4. **Coordinated Implementation:**
   - Producer and consumer contracts are updated synchronously with automated tests validating compatibility in subsequent bounded implementation tasks.

---

# 7. Integration STOP conditions

To protect the project from requirement drift, technical debt, and unjustified claims, all workstreams must immediately **STOP** and surface the issue when any of the following conditions occur:

1. **Unauthorized Contract Modification:** A task requires modifying `backend/app/domain/assessment.py`, `docs/data_contract.md`, or `frontend/src/api/contracts.ts` without an approved VLD-02 decision.
2. **Unverified Raw Field Behavior or Semantic Promotion:** Implementation code:
   - Relies on a dataset field not present in supplied challenge materials or accepted evidence;
   - Assumes unverified observed type, nullability, or referential integrity behavior;
   - Assigns unverified semantic meaning to raw columns;
   - Promotes a raw sponsor field into canonical or predictive semantics without the required evidence and decision gate.
3. **Unsourced Agronomic Thresholds:** A formula, threshold, or baseline rule uses hardcoded numbers (e.g. "temperature > 4°C is high risk") that have no approved entry in [`docs/domain_rules.md`](./domain_rules.md).
4. **Unsubstantiated Causal Claims:** A recommendation or factor description claims that taking an action will reduce loss by a specific percentage without validated empirical evidence.
5. **Leakage & Prediction Boundary Violation:** An analytics or feature engineering step accesses post-dispatch data (arrival checks, transit delays, destination outcomes) for predictive inference at $T_{dispatch}$.
6. **Contradiction Between Accepted Artifacts:** Two approved documents make incompatible assertions (e.g. data recon finds a table structure that invalidates an architecture assumption).
7. **Scope-Expanding Infrastructure Changes:** A pull request or task introduces external databases (PostgreSQL, Redis), Docker/Kubernetes requirements, message queues, or streaming protocols without explicit authorization.
8. **Untraceable Product Claims:** Pitch slides, README text, or UI labels make claims regarding accuracy, loss reduction, or scalability that cannot be traced to executed tests or evaluation reports.
9. **AI Self-Report as Verification:** An automated agent asserts that code or data is "verified" or "clean" without providing the exact executed commands, exit codes, and output snippets.
10. **Challenge Requirement Conflict:** New information or clarification indicates that an accepted team decision violates official challenge specifications.
11. **Local vs Committed State Confusion:** A task is initiated on a dirty repository base or confuses uncommitted local files with canonical repository state.
12. **Insufficient Evidence for Decision:** Pressure to make progress leads to deciding a model, target, or threshold while the underlying evidence remains classified as UNKNOWN.

When a STOP condition is triggered:
- The executor must halt work on the affected path immediately.
- Output a clear report starting with: `BLOCKED: <reason>`.
- Provide the exact file paths, diffs, or contradictions observed.
- Identify the specific human decision or missing evidence required to unblock.

---

# 8. Current blocked / unblocked dependency state

**History:** VLD-01 was prepared from `cafbcf832e7abb410ee9ff07954b4bb50e34aa81`, before the subsequent evidence deliveries. VLD-R1 reconciled the initial Layer-1 state at `54d233f1822f730a26fa225ec00d746e116875aa`. VLD-R2 reconciled post-VDR-02 evidence at `f9ca1d7bd29940e6b925884c7becae65dc921f7c`. The following VLD-R3 current-state reconciliation incorporates accepted, integrated VLD-02A (ADR 0002, PR #16), VDR-03 (PR #18), and APR-01 (PR #17) at `9cff00ce177f32dc2562d3458e0659281438d4c3`; it does not rewrite the earlier sequence or introduce unaccepted decisions.

### Accepted and integrated reconnaissance evidence

| Workstream | Current state | Existing artifact | Integration evidence |
| --- | --- | --- | --- |
| VLD-01 | ACCEPTED / INTEGRATED | VLD-01 baseline of [integration_contract.md](./integration_contract.md) | [PR #6](https://github.com/Slave-of-Skynet/training_agrifood/pull/6) |
| VDR-01 | ACCEPTED / INTEGRATED | [01_dataset_inventory.md](./data_recon/01_dataset_inventory.md) | [PR #7](https://github.com/Slave-of-Skynet/training_agrifood/pull/7) |
| IGR-01 | ACCEPTED / INTEGRATED | [IGR-01-technical-recon.md](./recon/IGR-01-technical-recon.md) | [PR #8](https://github.com/Slave-of-Skynet/training_agrifood/pull/8) |
| PUX-00–07 | ACCEPTED / INTEGRATED AS RECON | [prscr_ux_demo_qa_report.md](../prscr_ux_demo_qa_report.md), at repository root | [PR #9](https://github.com/Slave-of-Skynet/training_agrifood/pull/9) |
| VDR-02 | ACCEPTED / INTEGRATED | [02_temporal_leakage.md](./data_recon/02_temporal_leakage.md) | [PR #14](https://github.com/Slave-of-Skynet/training_agrifood/pull/14) |
| VLD-02A / ADR 0002 | ACCEPTED DECISION / INTEGRATED | [0002-predictive-input-semantics.md](./decisions/0002-predictive-input-semantics.md) | [PR #16](https://github.com/Slave-of-Skynet/training_agrifood/pull/16) |
| VDR-03 | ACCEPTED / INTEGRATED | [03_target_horizon_feasibility.md](./data_recon/03_target_horizon_feasibility.md) | [PR #18](https://github.com/Slave-of-Skynet/training_agrifood/pull/18) |
| APR-01 (steps 0–5) | DELIVERED / INTEGRATED / ACCEPTED RESEARCH EVIDENCE | [`docs/product_recon/`](./product_recon/) | [PR #17](https://github.com/Slave-of-Skynet/training_agrifood/pull/17) |

Acceptance of a research/report artifact does not adopt all its recommendations as DECISION or prove implementation. APR-01 research documents retain their own epistemic labels (`FACT`, `DOMAIN FACT`, `INFERENCE`, `UNKNOWN`, `NOT CANON`) and are not automatically challenge canon as a whole. IGR-01 records historical backend verification and host-specific runtime/build limitations; PUX distinguishes planned QA from executed checks. No fresh application verification is claimed by this documentation update.

### Readiness under existing task-specific gates

| Work | Current readiness | Required next evidence / gate |
| --- | --- | --- |
| Bounded raw-only IGR-02 | **VDR-01 prerequisite satisfied; may be issued as a separate bounded contract.** No implementation exists or is created by this reconciliation | Factual raw parsing / structural validation only, under Section 3's existing rule |
| VDR-02 | **COMPLETE / ACCEPTED / INTEGRATED** through [PR #14](https://github.com/Slave-of-Skynet/training_agrifood/pull/14) | Prerequisite satisfied; evidence consumed by VLD-02 gate and subsequent D&E tasks |
| VDR-03 | **COMPLETE / ACCEPTED / INTEGRATED** through [PR #18](https://github.com/Slave-of-Skynet/training_agrifood/pull/18) | Prerequisite satisfied for candidate outcome profiling and horizon feasibility; subsequent evaluation/predictability evidence (VDR-04A) and Integrator decision gates still required |
| APR-01 (steps 0–5) | **DELIVERED / INTEGRATED / ACCEPTED RESEARCH EVIDENCE** through [PR #17](https://github.com/Slave-of-Skynet/training_agrifood/pull/17) | Research notes retain FACT/DOMAIN FACT/INFERENCE/UNKNOWN/NOT CANON labels; does not automatically make research canon as a whole |
| PUX-08 | Future data-to-UX reconciliation step; accepted VDR-01, VDR-02, VDR-03, and APR-01 research are available for inspection | Follow existing PUX workflow; unsupported semantic/UI elements remain gated |
| VLD-02A / IGR-03 predictive input | **VLD-02A ACCEPTED ([ADR 0002](./decisions/0002-predictive-input-semantics.md))**; IGR-03 UNBLOCKED for canonical input models and ingestion mapping (without analytics/feature engineering) | VDR-02 prerequisite satisfied; VLD-02A decision adopted by Integrator; unblocks bounded IGR-03 implementation |
| Later Viktor target/evaluation work; VLD-02B; analytics engine | **BLOCKED FOR ANALYTICS**; VDR-03 evidence accepted, but target UNKNOWN, baseline/evaluation protocol NOT ACCEPTED, runtime horizon policy UNKNOWN | Additional evaluation/predictability evidence (VDR-04A) and subsequent Integrator decision gate; domain evidence conditional on the method |
| Final interactive dashboard | **BLOCKED** on its existing implementation prerequisites | Assessment endpoints/contracts, reconciled UX and supported data/product semantics |
| VLD-03 / VLD-04 / VLD-05 | **BLOCKED** on their respective integration, runtime and claims prerequisites | Working backend/frontend plus evaluation evidence → stable reproducible demo → traceable claims |

**Raw-only boundary:** Accepted VDR-01 is sufficient prerequisite for a separately contracted factual raw parsing / structural validation task. This does **not** authorize production `BatchAssessmentInput`, predictive eligibility decisions, feature windows, imputation/exclusion policy, target selection, or analytics logic. This is reconciliation of the existing integration rule, not a new VLD-02 decision or an implementation contract.

---

# 9. Traceability rules

Every feature, formula, metric, and public statement in Smart Harvest must follow an unbroken, auditable trail from evidence to output.

Rather than forcing all work through a single rigid linear sequence, the traceability model branches based on whether an integration boundary or shared contract is affected:

```text
Evidence
  │  (Sponsor data profiling, domain literature, mentor clarification)
  ▼
Does it require a new or changed shared decision?
  │
  ├─► YES ──► Relevant Human Integration Gate (such as VLD-02)
  │             │
  │             ▼
  │           Canonical / Shared Contract Update
  │             │  (docs/data_contract.md, app/domain/, frontend contracts)
  │             ▼
  │           Bounded Implementation Contract
  │             │  (Scoped write branch, task-specific PR)
  │             ▼
  │           Verification
  │              (Automated tests, contract compatibility checks)
  │
  └─► NO  ──► Existing Accepted Contract
                │
                ▼
              Bounded Implementation Task
                │  (Local code within agreed technical scope)
                ▼
              Verification
                 (pytest, npm test, lint, local tests)

Verified Product Behavior / Evaluation Evidence
  │
  ▼
VLD-05 Final Consistency & Pitch Claim Gate
  │  (Audit against reproducible evidence, canon, and test results)
  ▼
Final Solution & Truthful Pitch Presentation
```

### Local implementation vs shared-contract gates

- **Local implementation within accepted contracts does not require VLD-02:** Workstream owners may implement internal logic, algorithms, helper functions, tests, and UI components that strictly conform to existing accepted contracts and boundaries without triggering an integration gate.
- **Shared-contract changes require VLD-02:** When an evidence finding necessitates altering a boundary, adding or modifying public model fields, redefining input semantics, or introducing architectural dependencies, the change must pass through a formal human integration gate (such as VLD-02) before downstream implementation begins.
- **Pitch claims pass VLD-05 rather than VLD-02:** Pitch deck assertions, README statements, and demo claims do not pass through VLD-02. All claims regarding model performance, loss reduction, operational impact, or system capabilities must pass through the **VLD-05 Final Consistency & Pitch Claim Gate**, where they are audited directly against verified product behavior and reproducible evaluation evidence.

### Verification standards

1. **No Phantom Verification:** Assertions that code "works" or tests "pass" must include the exact command executed, exit status, and console output summary.
2. **Synthetic Data Quarantine:** Synthetic fixtures and demo stubs must permanently carry `simulation: true` and the notice `SIMULATION / synthetic fixture / not challenge data`. They may never be substituted for evaluation data.
3. **Auditability:** Every metric cited in the pitch or README must be reproducible by running an inspection command or script from a clean repository state.
4. **History Preservation:** When new evidence invalidates an earlier assumption, the change must be recorded as an evolution of requirements, not by silently editing commit history or pretending the earlier state never existed.

---

# 10. Current limitations

To ensure absolute clarity regarding the boundaries of VLD-01, the following limitations are explicitly recorded:

1. **No Ingestion Logic Created:** The raw CSV files under `sponsor_pack/data/` remain unparsed by application code. Their observed snapshot structure and integrity have been established in accepted VDR-01; this supports a separately contracted raw-only IGR-02, not predictive semantics or an existing ingestion implementation.
2. **No Production Ingestion / Input Models in Code:** Canonical predictive-input semantics and the `BatchAssessmentInput` definition were accepted under [ADR 0002](./decisions/0002-predictive-input-semantics.md) (VLD-02A), unblocking bounded implementation task IGR-03. However, no Pydantic input models or CSV ingestion mappers exist in application code yet.
3. **No Risk Formula or Heuristic Selected:** The backend does not calculate risk scores. The demo endpoint continues to return a synthetic `insufficient_data` fixture.
4. **No Deterioration Horizon Defined:** The system makes no prediction regarding when quality degradation will begin. The horizon field remains null.
5. **No Active Agronomic Rules:** The domain rule register ([`docs/domain_rules.md`](./domain_rules.md)) remains empty of validated active rules.
6. **No Machine Learning Model Selected:** No model training, hyperparameter tuning, or split selection has occurred.
7. **No Persistence Configured:** No persistence layer is currently configured; the current foundation is stateless. Application persistence/storage may become a VLD-02 cross-cutting decision if accepted evidence shows persistence is required for application implementation. No database engine or ORM is introduced.
8. **No Remote Deployment Selected:** No remote deployment platform or hosting provider is preselected. Environment and platform selection remains under VLD-04 unless an earlier blocker requires a human decision. The current foundation demo runbook describes local execution.
