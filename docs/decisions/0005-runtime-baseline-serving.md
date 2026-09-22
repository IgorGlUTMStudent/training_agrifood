# ADR 0005 — Runtime Baseline Serving and Single-Batch Assessment

- **Status:** ACCEPTED HUMAN DECISION
- **Decision owner:** Vladimir — Integrator
- **Date:** 2026-09-22
- **Decision source:** HG-R5 D1–D7
- **Recon source:** [docs/recon/VLD-R5-runtime-assessment-path-recon.md](../recon/VLD-R5-runtime-assessment-path-recon.md)
- **Evidence/reference base HEAD:** `e8e14e3da7921a1d87f7bfc6e474f639ef87aa53`
- **Reconciliation task:** VLD-R5-HG1R; documentation only

## Human-decision provenance and scope

Vladimir explicitly accepted HG-R5 D1–D7 on 2026-09-22. Acceptance was a Human Integrator decision. It was not inferred from an AI recommendation. It was not inferred from a commit or merge.

The VLD-R5 report supplied recommendations and UNKNOWNs. It remains a RECON / DECISION PACKET, preserved with SHA256 `6041ed4df14c614807c4f96ffd64272304df72f93bf1fe8ccfc44c7ad5680ea7`. This ADR records only the accepted bounded Human Gate outcome; it does not promote all VLD-R5 prose into decision. This reconciliation makes no new decision.

HG-R5 records challenge-specific SoS runtime, architecture and integration decisions, not new external challenge facts, provider requirements or dataset observations. ADR 0005 is their authoritative carrier. ADRs 0002–0004 and their historical unresolved-state records remain unchanged; this later decision resolves only the initial runtime case described below.

**FACT — Implementation at the reference base:** IGR-03 canonical mapping, IGR-04A crop-median fitting/scoring and IGR-04B `build_baseline_assessment()` are implemented internally. Runtime artifact loading, lifespan analytics context and real assessment HTTP serving are not implemented. The public routes remain health and synthetic demo. The following serving decisions are **ACCEPTED DECISION — NOT YET IMPLEMENTED**.

## D1 — Baseline fitting and initial training cohort

**DECISION — HG-R5-D1:**

```text
controlled offline fit
→ versioned runtime artifact
→ inference-only serving
```

The initial runtime deterministic baseline training partition is:

```text
dispatch_datetime < 2025-05-01
900 Season-2024 batches
```

The initial dataset-backed assessment/demo cohort is:

```text
dispatch_datetime >= 2025-05-01
900 Season-2025 held-out batches
```

P1 training membership is now intentionally adopted for the initial runtime deterministic baseline artifact. This is not the future production training policy.

Runtime requests **MUST NOT fit or refit the model**. Application startup **MUST NOT silently fit on all 1,800 outcomes**. Future refitting requires an explicit new release decision and a distinct concrete `engine_version`.

Historical outcomes remain on the fitting/evaluation side only, never in request-time predictive input. ADR 0002's dispatch assessment clock and leakage boundary are unchanged.

## D2 — Runtime artifact and provenance identity

**DECISION — HG-R5-D2:** use a separate validated JSON application artifact. The application must not consume `docs/data_recon/06a_baseline_evaluation_results.json` directly as runtime model state. VDR-06A remains evaluation/parity evidence.

Required artifact semantics include:

- Artifact format version.
- Algorithm/family identity.
- Concrete `engine_version`.
- `source_dataset_id`.
- Training partition identity.
- Source table hashes.
- Training-membership fingerprint.
- Crop medians.
- Global median.

Accepted initial identities:

| Meaning | Value |
| --- | --- |
| Algorithm/family label | `baseline-crop-median-v1` |
| Concrete engine version | `baseline-crop-median-v1-p1-s2024` |
| Source dataset ID | `training-agrifood-snapshot-v1` |

`source_dataset_id` identifies the pinned assessment-source snapshot. It does not uniquely identify the model fit, training membership or engine release; those belong in artifact lineage. Exact artifact path and private JSON arrangement remain implementation details. No additional artifact fields are adopted as Human decisions here.

## D3 — Simulation and notice semantics

**DECISION — HG-R5-D3:** preserve the existing synthetic fixture:

```text
simulation = true
engine_tier = fixture
notice = "SIMULATION / synthetic fixture / not challenge data"
```

For initial dataset-backed deterministic-baseline responses:

```text
simulation = true
engine_tier = deterministic_baseline
engine_version = "baseline-crop-median-v1-p1-s2024"
source_dataset_id = "training-agrifood-snapshot-v1"
notice = "SIMULATION / training challenge dataset / deterministic baseline / not production deployment"
```

**Dataset-backed != synthetic fixture.** The accepted dataset-backed output is computation on the training-challenge snapshot, not the synthetic fixture and not a production deployment. HG-R5 does not authorize `simulation = false` for any production/commercial scenario; those semantics remain outside this gate.

## D4 — Runtime ownership and readiness

**DECISION — HG-R5-D4:**

```text
FastAPI lifespan
    ↓
load + validate pinned serving snapshot
    +
load + validate baseline artifact
    ↓
publish complete runtime context
    ↓
explicit dependency/provider
    ↓
request orchestration
```

No request-time fitting, import-time fitting, automatic refitting, hot reload, background training or hidden artifact regeneration is admitted.

If analytics resources fail, the application may remain running, health remains reachable, the synthetic demo remains reachable, and the real assessment route is unavailable. The runtime context must not become visible until all required analytics resources have passed validation. This bounded degraded-startup behavior is not a production high-availability or scaling policy.

## D5 — Initial real assessment API

**DECISION — HG-R5-D5:** accept `GET /api/v1/assessments/{batch_id}` with no body. No POST route is accepted for this slice.

The backend owns:

```text
batch_id
→ pinned snapshot
→ IGR-03 canonical mapper
→ BatchAssessmentInput
→ pinned deterministic baseline
→ IGR-04B
→ RiskAssessment
```

The frontend does not construct `BatchAssessmentInput`. The client does not supply `engine_version`, `source_dataset_id`, `generated_at`, `simulation` or `notice`.

Only the initial held-out cohort (`dispatch_datetime >= 2025-05-01`) is eligible. A known batch in the training partition receives HTTP 409, meaning: **Batch is not eligible for this assessment release.** This is not queue membership or an operational disposition.

Accepted transport failures:

| Condition | HTTP status |
| --- | --- |
| Unknown `batch_id` | 404 |
| Known but release-ineligible batch | 409 |
| Runtime dataset unavailable | 503 |
| Baseline artifact unavailable | 503 |
| Artifact invalid/incompatible | 503 |
| Batch-specific canonical mapping / server-owned malformed source | 500 |
| Unexpected internal failure | 500 |

These failures are not `RiskAssessment(status="insufficient_data")`. `insufficient_data` remains governed by ADR 0003 D7. No new deterministic-baseline minimum-input policy is introduced.

Accepted initial response cache policy: `Cache-Control: no-store`.

Preserve both existing endpoints:

```text
GET /api/v1/health
GET /api/v1/demo/assessment
```

## D6 — Health, CORS and runtime configuration

**DECISION — HG-R5-D6:** accepted `analytics` health states:

| State | Meaning |
| --- | --- |
| `not_configured` | Runtime analytics not configured. |
| `ready` | Snapshot + artifact successfully loaded and validated. |
| `unavailable` | Analytics configured but required resources failed loading/validation. |

Top-level `status = "ok"` continues to represent process/application liveness. Health remains HTTP 200 while the application process is alive.

**ACCEPTED SHARED-CONTRACT CHANGE — NOT YET IMPLEMENTED:** future implementation must synchronize backend `HealthResponse`, frontend TypeScript `HealthResponse`, API tests and health presentation where applicable. At the reference base, backend and frontend still constrain `analytics` to `"not_configured"`. This reconciliation changes none of those implementations.

The accepted GET endpoint requires no CORS method expansion: `allow_methods=["GET"]` may remain unchanged.

Accepted runtime setting names:

```text
SMART_HARVEST_DATA_DIR
SMART_HARVEST_BASELINE_ARTIFACT
```

No additional required environment variables are introduced. Exact defaults and path packaging remain implementation details.

## D7 — Next bounded implementation slice

**DECISION — HG-R5-D7:** the next backend slice may implement only:

- Offline artifact generation/validation.
- Runtime artifact + snapshot loading.
- Lifespan/provider composition.
- Single-batch GET assessment.
- Health reconciliation.
- Focused verification.

Reuse ADR 0002, ADR 0003, ADR 0004, IGR-03, IGR-04A, IGR-04B, `RiskAssessment` and `BatchAssessmentInput`. No change to their existing assessment/input semantics is adopted here.

Explicitly deferred: multi-batch endpoint; ranked/replay queue; facility filtering API; pagination; frontend queue integration; database; learned model; recommendation engine; deterioration model; new confidence policy; cross-engine comparability; background retraining; hot reload; deployment; VLD-03.

Also deferred: a new deterministic-baseline `insufficient_data`/minimum policy. If implementation discovers a valid canonical input that the existing baseline cannot legitimately assess:

```text
STOP — HUMAN DECISION REQUIRED
```

This reconciliation does not start Igor implementation. The next slice requires its own bounded implementation contract after review and the subsequent Human integration gate.

## Retained UNKNOWNs and non-decisions

**UNKNOWN — Not closed by HG-R5:** future production/commercial training policy; future retraining cadence; production model registry; `simulation=false` semantics; future learned-engine artifact lifecycle; queue window/capacity/membership; cross-engine comparability; generalized data beyond the supplied snapshot; hosting/scaling/concurrency; engine minimum-input policy beyond the current baseline; action/recommendation policy; deterioration prediction; business effectiveness. Future engine versions/release scheme remain open beyond D1's explicit new-release/distinct-version rule.

Exact artifact path, private JSON arrangement, settings defaults and path packaging remain implementation details; no extra decision is inferred from VLD-R5 recommendations. No database, registry service, worker, message queue, microservice or background retraining architecture is introduced.

## Reconciliation and completion boundary

This ADR is synchronized only into [architecture](../architecture.md), [integration contract](../integration_contract.md) and the [UNKNOWN register](../assumptions_unknowns.md). The reviewed recon is unchanged. Existing ADRs, challenge canon, implementation-facing documents, APR-03A's historical snapshot, code, schemas, configuration and dependencies are not rewritten. No artifact is generated and no baseline is fitted in this task.

**STOP FOR PROJECT BRAIN REVIEW.** No commit, push, PR creation, merge or Igor implementation before review. An ACCEPTABLE review establishes documentation coherence for the subsequent Human integration gate; it does not itself authorize merge.
