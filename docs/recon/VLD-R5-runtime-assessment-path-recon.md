# VLD-R5 — Runtime Assessment Path & Baseline Lifecycle Recon

## 1. Status / base / executor

**FACT — Status:** read-only application reconnaissance; decision packet for Project Brain review. Executor: Vladimir — Integrator. Date: 2026-09-22. This document makes no new Human decision, ADR, API or implementation change.

**FACT — Git base:** initial local HEAD was `d2767685f7be82dfcdf5b30958e142dfbcf6d386`, on clean `main`. Fetch found the expected remote base. `git switch main` and `git pull --ff-only origin main` advanced local main to `e8e14e3da7921a1d87f7bfc6e474f639ef87aa53`. Before branch creation, HEAD and origin/main both equalled that required SHA, status was empty, and branch was main. Recon branch: `vladimir/vld-r5-runtime-assessment-recon`. Starting inspection HEAD and final HEAD are the same required SHA; no commit was made.

**FACT — Scope:** only this new report is a deliverable. All inspected application content is committed content at the recorded base. PUX-10A and pending/local Denis work are not assumed integrated or used as evidence.

**INFERENCE — Stop-condition assessment:** a viable single-batch path can retain `RiskAssessment`, `BatchAssessmentInput`, ADR 0002/0003, dispatch clock, risk transformation and target unchanged. No mandatory conflict with those protected semantics was found. Runtime policy and API/health decisions below gate future implementation, not completion of this recon.

## 2. Objective

**RECOMMENDATION — Minimal direction:** controlled offline fitting into a separate application artifact; load that artifact and a pinned serving snapshot once; backend maps a requested recorded batch through IGR-03; call IGR-04B; expose the existing `RiskAssessment` through a reviewed single-batch GET route. Keep fitting, serving and evaluation distinct. No database, worker queue, learned model or frontend integration is part of this proposed slice.

**UNKNOWN:** runtime partition, artifact/version identity, dataset-reference interpretation, dataset-backed simulation boolean, notice and HTTP/health policies are not fully selected by accepted sources. This packet prepares those choices; it does not accept them.

## 3. Sources inspected

**FACT — Source key:** references below identify repository-relative files at the base in §1. Code symbols, document sections and JSON keys narrow the evidence. Some large documents were inspected by relevant sections/search rather than treated as wholesale authority.

| Key | Inspected files / anchors | Authority and use |
| --- | --- | --- |
| S1 | `docs/decisions/0002-predictive-input-semantics.md`, §§1–4; `docs/data_contract.md` | DECISION: input, joins, dispatch anchor, forbidden fields and missingness; contract description |
| S2 | `docs/decisions/0003-assessment-evaluation-semantics.md`, D1–D10, consequences and UNKNOWNs | DECISION: baseline, training/evaluation, sufficiency, score and version comparability |
| S3 | `docs/decisions/0004-mvp-product-scope.md`, APR2-D1–D6 and downstream consequences | DECISION: replay/view product semantics, baseline label, presentation limits |
| S4 | `docs/integration_contract.md`, §§2–3, §8–9; `docs/architecture.md` | DECISION boundaries, API design review, ownership, local vs shared changes; historical implementation summaries checked against code |
| S5 | `docs/assumptions_unknowns.md`; `docs/challenge_canon.md`; `README.md`; `sponsor_pack/README.md` §§1–4; `docs/demo_runbook.md` setup/expected responses | FACT/DECISION context: supplied training simulation, dataset and environment; sponsor commercial narrative is not verified real deployment |
| S6 | `backend/app/analytics/crop_median_baseline.py`: both dataclasses, fit and prediction functions | FACT: IGR-04A current implementation |
| S7 | `backend/app/services/baseline_assessment.py`: `build_baseline_assessment`; `backend/app/services/__init__.py` | FACT: IGR-04B signature, output and lack of lifecycle |
| S8 | `backend/app/ingestion/raw_reader.py`: snapshot/reader; `canonical_mapper.py`: errors, joins, temporal filters, construction; `diagnostics.py`; `structural_manifest.py` definition/manifest | FACT: raw ingestion, diagnostic reporting and IGR-03 mapping |
| S9 | `backend/app/domain/batch.py`; `backend/app/domain/assessment.py` | FACT: current input/output and health schemas |
| S10 | `backend/app/api/routes.py`; `backend/app/main.py`; `backend/app/services/demo_assessment.py` | FACT: only health/demo routes, CORS, fixture and absence of runtime ownership |
| S11 | `backend/tests/test_analytics_baseline.py`; `test_baseline_assessment.py`; `test_api.py` (all under `backend/tests/`) | FACT: test coverage and actual targeted execution, not new policy |
| S12 | `frontend/src/api/contracts.ts`; `client.ts`; `frontend/src/pages/HomePage.tsx`; `frontend/src/components/AssessmentCard.tsx`; `BackendStatus.tsx` | FACT: committed consumer only |
| S13 | `docs/data_recon/06a_baseline_evaluation.md`, §§2–5, 8–12; `06a_baseline_evaluation_results.json`: metadata, split_definitions, prediction_coverage, evaluation_results; `scripts/vdr06a_baseline_evaluation.py`: `run_evaluation`, imports and metadata | OBSERVED PRACTICE: evaluation fits/partitions/hashes/parity; no serving authorization |
| S14 | `docs/product_recon/10_mvp_demo_narrative_claim_freeze.md`, implementation snapshot, narrative/claim and provenance boundaries | Derived narrative; not a new decision or runtime verification |
| S15 | `docs/recon/IGR-01-technical-recon.md`, API question §15 / question to Vladimir, CORS §11.2, historical contracts/runtime observations | Historical recon; GET vs POST explicitly open, not accepted route design |
| S16 | `backend/pyproject.toml`; `.gitignore`; tracked file inventory and runtime-symbol search across `backend/app` | FACT: installed dependency declarations, ignored environment and absence checks |

**FACT — Stale-summary reconciliation:** S4 architecture still describes services as fixture-only and says baseline integration into an assessment service is pending; portions of the integration contract still say no risk scoring exists. S7 and S14 supersede those historical implementation descriptions: the internal assessment service exists, but real HTTP/runtime wiring does not. Broad historical “degrade to insufficient_data” prose does not override S2 D7's engine-specific meaning.

## 4. Current runtime dependency graph

**FACT / UNKNOWN — Arrow classification:** IMPLEMENTED describes a callable code edge, not a working HTTP path. MISSING RUNTIME WIRING describes absent application composition. UNKNOWN POLICY describes an unresolved choice. An edge can have both a policy and wiring gap.

```text
historical outcomes + crop/session identities
  -- UNKNOWN POLICY: runtime training partition
  -- MISSING RUNTIME WIRING: explicit runtime training-record producer
  --> sequence[CropMedianTrainingRecord]
  -- IMPLEMENTED: fit_crop_median_baseline()
  --> CropMedianBaseline(crop_medians, global_median)
  -- MISSING RUNTIME WIRING / UNKNOWN POLICY: serialize/load/version/lifetime
  --> baseline available to application request orchestration

raw dataset path
  -- MISSING RUNTIME WIRING / UNKNOWN POLICY: discovery, pinning, startup load
  --> read_raw_snapshot(data_dir)
  -- IMPLEMENTED --> RawSnapshot (tables + structural diagnostics)
  -- IMPLEMENTED: build_batch_assessment_input(snapshot, batch_id)
  --> BatchAssessmentInput

CropMedianBaseline + BatchAssessmentInput + caller provenance
  -- IMPLEMENTED: build_baseline_assessment()
  --> RiskAssessment
  -- MISSING RUNTIME WIRING / UNKNOWN POLICY: new route and HTTP errors
  --> versioned real assessment HTTP response
```

**OBSERVED PRACTICE — Offline edge:** S13 already joins batches/sessions/outcomes, selects evaluation train indices and constructs training records; that is an evaluation harness, not an application runtime record producer. S6 accepts an explicit record sequence and does not accept `RawSnapshot` or choose a split.

**FACT — Current public graph:** `GET /api/v1/demo/assessment → build_demo_assessment() → synthetic RiskAssessment`; `GET /api/v1/health → fixed HealthResponse`. Neither route reaches S6–S8.

## 5. Confirmed implementation state

**FACT — Baseline:** fit validates explicit nonempty records, nonblank crop and finite labels, strips crop keys, computes deterministic standard-library medians and orders crop keys. Inference reads only `batch_input.batch.crop_type.strip()`, with global training median fallback for unseen crops. Score is clipped predicted loss divided by 100 (S6). There is no serialization, persistence or loader.

**FACT — Validation caveat:** `CropMedianBaseline` is a frozen dataclass, but its dictionary is mutable and the fitted object constructor has no validating `__post_init__`. Prediction checks object types, not artifact integrity. Loader validation cannot be replaced by simply calling that constructor. This is a lifecycle concern, not authorization to edit IGR-04A.

**FACT — Assessment service:** S7 always builds `assessed`, non-null risk, null band/horizon/recommendation, empty factors, unavailable reliability, null confidence and empty limitation lists. It fixes `engine_tier=deterministic_baseline`, `contract_version=1.0.0`; engine version, generation time, dataset ID, simulation and notice come from the caller. It does not fit/load/persist, read a dataset, resolve IDs, define HTTP or own state. It implements no insufficient-data branch.

**FACT — Ingestion:** default raw loading uses the manifest, including historical outcomes and all raw QC/shipment fields. It returns diagnostics rather than universally raising on invalid snapshots. The caller decides whether loading succeeded. The mapper requires six tables (batches, sessions, zones, facilities, QC, sensors); shipments are optional. It excludes outcomes entirely, admits only harvest/pre-dispatch QC, bounds telemetry, uses only planned logistics, verifies parent/cardinality/chronology rules and constructs the larger typed input (S8).

**FACT — Runtime absence:** full `backend/app` inventory/search and S10 show no FastAPI lifespan, `app.state` baseline, dependency provider, artifact loader, baseline repository or runtime context. The module-global `app` is an application object, not an analytics singleton. The mapper does cache a telemetry zone index inside the mutable `RawSnapshot`; this local cache is not a baseline lifecycle.

## 6. Gap matrix

**FACT / UNKNOWN — Reading rule:** “existing” refers to the base; “proposed” is RECOMMENDATION. Owners below are proposed delivery/review assignments using S4 workstreams, not new ownership decisions. V = Vladimir/Human Gate; I = Igor/backend; D = Viktor/data; P = Alisa/product; U = Denis/UX. Yes in the decision column means an explicit choice is still needed, not that this report makes it.

| Topic | Current state / authoritative source | Classification | Decision needed? | Implementation needed? | Owner |
| --- | --- | --- | --- | --- | --- |
| Dataset discovery/path | Reader takes path; evaluation uses `sponsor_pack/data`; app has no setting (S8/S13/S10) | FACT + MISSING RUNTIME WIRING | Yes, supported snapshot/path | Yes | I; V review |
| Dataset identity | No runtime ID derivation; evidence has per-table hashes (S9/S13) | UNKNOWN POLICY | Yes | Yes | V + D; I |
| Snapshot lifecycle | RawSnapshot and index cache exist; no app lifecycle (S8/S10) | FACT + MISSING RUNTIME WIRING | Yes, lifetime/failure behavior | Yes | I; V |
| Training partition | Train-only semantics accepted, P1 used in evaluation (S2 D5/S13) | DECISION + UNKNOWN runtime policy | Yes | Yes, producer | V + D; I |
| Fitting lifecycle | Explicit fit exists; no serving caller (S6/S10) | FACT + MISSING RUNTIME WIRING | Yes, A vs B | Yes | I; V + D |
| Artifact representation | Only Python dataclass (S6) | UNKNOWN POLICY | Yes | Yes if A | I; V + D |
| Persistence/loading | None (S6/S10) | MISSING RUNTIME WIRING | Yes, local artifact lifecycle | Yes if A | I; V |
| engine_version | Required caller string; accepted family label (S7/S3 D4) | FACT + UNKNOWN fitted version | Yes | Yes, bind to fit | V + D; I |
| source_dataset_id | Nullable string, caller-supplied (S7/S9) | UNKNOWN POLICY | Yes | Yes | V + D; I |
| generated_at | Caller datetime; fixture uses UTC now (S7/S10) | FACT + OBSERVED PRACTICE | Yes, generation/cache rule in contract | Yes | I; V review |
| simulation | Fixture true; broader training context labeled simulation (S4/S5/S10) | DECISION fixture; UNKNOWN boolean scope | Yes for dataset-backed serving | Yes | V + P; I |
| notice | Nonempty caller text; exact fixture text only (S7/S9/S10) | FACT + UNKNOWN dataset notice | Yes | Yes | P + V; I |
| Batch lookup | Mapper raises BatchNotFoundError (S8) | IMPLEMENTED internally | HTTP policy yes | Route adapter yes | I; V |
| Canonical mapping failure | Explicit error hierarchy; no HTTP mapping (S8/S10) | FACT + UNKNOWN HTTP policy | Yes | Yes | I; V |
| Runtime assessment service | IGR-04B exists, not application composition (S7) | IMPLEMENTED + MISSING RUNTIME WIRING | Wiring boundary yes | Yes, orchestrator | I |
| HTTP route | Health/demo only (S10/S4 endpoint row) | MISSING RUNTIME WIRING | API design review | Yes | V + I |
| Request semantics | GET ID vs POST canonical open (S15) | UNKNOWN POLICY | Yes | Yes | V + I; U consulted |
| HTTP errors | No real-route contract (S8/S10) | UNKNOWN POLICY | Yes | Yes | V + I; U consulted |
| Health | Backend/TS literal not_configured (S9/S12) | FACT + shared conflict | Yes | Yes for truthful configured health | V + I + U |
| CORS | GET only (S10) | FACT | No change for GET; review for POST | No for recommended GET | I; V if changed |
| Frontend consumer | Fixture-only client/HomePage (S12) | FACT + MISSING downstream wiring | Separate bounded consumer contract | Later | U; V |
| Multi-batch queue | No endpoint; replay intent accepted (S3 D2/S10/S12) | DECISION intent + UNKNOWN membership | Later, outside this recon | Deferred | V + I + U |

## 7. Baseline lifecycle alternatives

**RECOMMENDATION — Alternatives comparison:** all options below are evaluated for the supplied-snapshot MVP, not accepted production designs.

| Option | Separation, reproducibility, provenance | Cost, failure modes, drift and suitability |
| --- | --- | --- |
| A — controlled offline fit → separate versioned runtime artifact → load | Clearest fit/serve boundary. Explicit approved training membership, source hashes and fitted identity support reproduction. Serving needs medians, not labels. | Small standard-library JSON loader; snapshot mapping still has startup cost. Adds producer, artifact validation and release pairing. Missing/corrupt/mismatched artifact blocks real assessment. Good demo predictability if artifact and snapshot are pinned; otherwise drift risk is substantial. |
| B — fit once on application startup | Outcomes can stay on fitting side if an explicit partition is selected before record construction and labels are kept out of canonical requests. Deterministic with identical data/code/policy; provenance should record the actual fit. | Fewer artifact-distribution steps, but every worker/restart reads training outcomes and repeats fitting. Median calculation is small; CSV/telemetry loading can dominate and is unmeasured. Bad dataset/empty train set stops configuration. Tests can inject snapshots/clock but startup now owns training policy. Reasonable controlled demo fallback; less separation for serving. |
| C — fit per assessment request | Reproducible only with pinned data/partition/code; mutable disk data can silently change results/version meaning. Increases opportunities to include the requested outcome or full snapshot. | Repeated IO/fit/validation; longer, less predictable request path and more failures. No legitimate benefit for a fixed deterministic replay snapshot compared with A/B. Dynamic retraining is a different requirement, absent here. Reject for this MVP. |
| D — hardcoded medians/constants | Loses traceable fitting lineage and duplicates IGR-04A output. Fixed numbers are repeatable but do not prove approved training membership. | Easy to unit-test copied values, hard to detect manual drift or evidence/runtime divergence. Updating code becomes an undocumented model release. Reject; test fixtures can still use explicit synthetic training records. |
| E — directly load VDR-06A evidence JSON | Has useful source hashes and P1 medians, but `vdr-06a.v1` describes evaluation results, multiple protocols, library versions and parity. It is not a selected serving fit/version contract. | Convenient initially; couples availability and releases to `docs/data_recon` structure and Viktor's evidence ownership. Re-running evidence can alter runtime meaning. Runtime importing the harness also pulls scientific dependencies. Reject direct runtime dependency; use evidence for independently generated artifact parity only. |

**RECOMMENDATION — RECOMMENDED MINIMAL OPTION: A.** “Minimal” means the smallest auditable inference-only serving path, including its one-time controlled producer, rather than the fewest lines. The existing fit function and standard library suffice; no model registry, database or general artifact platform is proposed.

**RECOMMENDATION — SECOND-BEST OPTION: B.** If the Human Gate explicitly prioritizes avoiding an artifact release step, a deterministic startup fit on an approved pinned partition is a bounded demo alternative. It is not permission to fit all 1,800 outcomes or silently discover a split.

**RECOMMENDATION — REJECTED OPTIONS: C, D, E** for the reasons above. These are recon recommendations, not adopted project rejections.

## 8. Training partition / artifact question

**DECISION — S2 D5:** training-only medians, unseen-crop global training fallback, P1 forward-season primary evaluation and P2 grouped robustness are accepted. Evaluation fits use each split/fold's training subset. None of that authorizes an arbitrary runtime refit.

**OBSERVED PRACTICE — S13:** P1 selects `dispatch_datetime < 2025-05-01` and asserts 900 training / 900 test batches. The harness joins labels separately, builds canonical inputs, constructs records for training indices and predicts held-out canonical inputs. P2 fits five different baselines; OOF evidence is not one deployable fit.

**INFERENCE:** P1's accepted evaluation role does not automatically select it as runtime artifact training policy. S2 explicitly leaves fitted artifact/version management to a later bounded contract. Evidence parity does not fill that gap.

**RECOMMENDATION:** ask the Human Gate to adopt that P1 training subset explicitly for the initial training-challenge artifact, with the verified supplied snapshot and preserved 900/900 disjointness. It is the most evidence-aligned candidate, not a selected production policy. Do not refit on held-out labels, combine P2 fits or use P3 as serving justification.

**UNKNOWN — Replay eligibility:** serving a recorded training batch using a fit containing its own outcome would be in-sample replay, not a held-out or historically available prediction. Even the earlier training-season fit may contain labels later than that batch's dispatch. The candidate demo should use held-out-season requests if it is to demonstrate forward evaluation alignment. Whether the route permits other recorded IDs, and how that restriction is expressed, needs explicit review; this is not a new queue-membership policy. No claim that the service reconstructed an actual historical deployment is supported.

**RECOMMENDATION — Future producer contract:** define source file set and byte hashes, approved membership predicate/list and fingerprint, target join cardinality, finite-label validation, crop normalization consistent with IGR-04A, empty/malformed training failure, count checks, deterministic serialization and code/fit identity. Define demo inference eligibility and separation from held-out evaluation labels. No fitting or artifact generation was performed by this recon beyond existing synthetic unit tests.

**RECOMMENDATION — Artifact representation:** a small, separately owned application JSON document containing exact fitted crop/global medians and sufficient metadata to resolve its algorithm, concrete fit, source hashes and partition. Use existing Python JSON/hashlib and Pydantic or explicit validators; no pickle or evaluation-harness dependency is needed. A private artifact schema/version is new and needs review, but it need not alter either public assessment schema. Names, paths, identifier syntax and final field layout remain UNKNOWN.

**RECOMMENDATION — Loader checks:** supported artifact format; expected engine/fit binding; nonempty crop keys and map; finite numeric medians (no bool/NaN/infinity masquerading as valid numbers); required lineage; snapshot/partition compatibility; no fabricated defaults. Preserve fitted values rather than rounding report medians. Do not introduce a new [0,100] fitting bound: existing scoring clips and current fit permits finite targets outside that interval. Record exact-content identity without inventing a self-referential hash convention.

## 9. Provenance lifecycle

### 9.1 Engine version

**FACT:** S3 APR2-D4 uses `baseline-crop-median-v1` as the deterministic baseline label. S2 D5 describes the algorithm, without a fitted-release naming convention. S7 accepts any nonempty caller version, and S14 explicitly warns against inventing a deployed version.

**INFERENCE:** accepted sources support the label as an algorithm/family reference, but not an unlimited permission to give every different fit that same public `engine_version`. Different partition medians can change scores while preserving the algorithm; S2 D3 prohibits unvalidated cross-version ranking.

**RECOMMENDATION:** distinguish algorithm label from concrete fitted identity in artifact metadata. Have the Human Gate decide how the existing public `engine_version` binds to one concrete fit. Direct use of `baseline-crop-median-v1` could be approved for exactly one pinned initial fit, but later refits should not silently retain that identity. No version syntax or deployed value is chosen here; no new public field is necessary for this bounded path.

### 9.2 Source dataset identity

**FACT:** `source_dataset_id` is an optional string; S1/S9 describe a dataset reference, not a runtime derivation. S13 records separate per-table SHA256 hashes, not an accepted value for this field.

| Candidate | INFERENCE — meaning and limitation |
| --- | --- |
| Human-readable snapshot ID | Good operator reference; insufficient alone to detect changed bytes; needs an immutable registry/metadata binding. |
| Dataset hash/fingerprint | Identifies exact source bytes once the file set, ordering and hashing procedure are defined; not a training-membership identity. |
| Training-partition fingerprint | Distinguishes fits from one snapshot, but does not by itself identify the serving snapshot. |
| Artifact metadata ID | Can resolve both source and partition lineage, but overloading a dataset-named field with a model artifact ID needs explicit semantic approval. |

**RECOMMENDATION:** define `source_dataset_id` as the pinned source snapshot used to resolve the assessed batch for this MVP; hold training snapshot hashes, partition identity and concrete fit identity separately in artifact metadata. Initially use one compatible supplied snapshot for training and replay. Different partitions could then share a source dataset ID, but could not rely on that ID to establish model equivalence; their fitted identity remains distinct. Include byte hashes separately even if the public ID is human-readable. Bind all metadata at load time rather than invent strings per request.

**UNKNOWN / HUMAN DECISION REQUIRED:** source snapshot vs training lineage interpretation, exact ID resolution and hash procedure, handling of different serving/training snapshots, whether a null ID is ever acceptable for dataset-backed responses. Schema-nullability alone is not adequate provenance policy. No arbitrary ID is supplied.

### 9.3 Generation time and assessment clock

**FACT:** S7 passes `generated_at` through; the fixture uses UTC wall-clock time. The canonical assessment timestamp remains recorded dispatch time (S1). They are different concepts.

**RECOMMENDATION:** generate a timezone-aware response creation timestamp from an injectable clock. Do not put fit time or dispatch time in that field merely to stabilize output. Keep fit metadata separately. For identical snapshot/fit/input, scores and fixed provenance are deterministic; responses need not be byte-identical if generation time changes. GET cache behavior needs review (§10); no new competing assessment clock is introduced.

### 9.4 Simulation and notice

**DECISION — S4 §9:** synthetic fixtures carry `simulation=true` and exact notice `SIMULATION / synthetic fixture / not challenge data`. That fixture contract remains unchanged.

**FACT:** S4's simulated-context notice and S5 identify the sponsor package as training simulation, despite the sponsor README's commercial framing. The deterministic dataset-backed service is real computation on that package; this does not establish real commercial data, deployment or validation.

**UNKNOWN / HUMAN DECISION REQUIRED:** accepted materials do not fully define the public boolean across all three categories below. Tests passing both booleans prove caller passthrough only.

| Category | Established / proposed treatment |
| --- | --- |
| Synthetic fixture | DECISION: true, exact existing fixture notice, tier fixture. |
| Dataset-backed training-challenge assessment | RECOMMENDATION: true under a reviewed meaning of simulation covering training context; disclose supplied-snapshot computation and avoid calling it a synthetic fixture. Exact boolean policy and fixed text await Human Gate. |
| Real production/commercial assessment | UNKNOWN: false would require verified non-simulation origin/use and an accepted policy; use of the baseline engine alone does not authorize false or prove operational validity. |

**FACT:** S9 enforces only nonempty `notice`; there is no fixed dataset-baseline notice. Accepted unavailable-recommendation and insufficient-data UI copy in S3 serves those UI states, not automatically `Provenance.notice`.

**RECOMMENDATION:** a reviewed fixed runtime notice should disclose training/simulation context and dataset-backed baseline scope without fictional commercial claims. Keep exact tier/version/dataset/time in their structured provenance fields; notice does not replace them. Product + Integrator should approve exact copy. This report designs no marketing text and does not reuse the fixture's false “not challenge data” claim for challenge-backed output.

## 10. API alternatives

**FACT:** S15 leaves the protocol open. S4's endpoint row permits new versioned routes only following API design review. Existing health and demo paths are preserved in every recommendation.

| Candidate | RECOMMENDATION analysis |
| --- | --- |
| API-A: `GET /api/v1/assessments/{batch_id}` | Fits S3 APR2-D2's recorded replay/view: backend resolves ID against a pinned snapshot, retains S1/IGR-03 mapping ownership and returns a computed representation. Consumer sends only an identifier; arbitrary input fields cannot enter scoring. Side-effect-free inference is a plausible GET use; it does not create a stored assessment resource. GET needs no CORS method widening. Later multi-batch orchestration can reuse the internal path without making HTTP calls to itself. |
| API-B: `POST /api/v1/assessments` with `BatchAssessmentInput` | Useful for future external canonical clients. Current frontend has no input model/raw ingestion, so this adds construction responsibility and a duplicated large schema. Typed JSON validation alone would not prove raw provenance or all mapper-enforced join/chronology checks. Allows arbitrary data beyond the pinned replay snapshot, making source identity and validation policy harder. Cross-origin JSON POST needs intentional CORS POST allowance and tests. |
| API-C: POST with batch_id only | Retains backend mapping and could fit future persisted/job-producing requests. No such side effect or job exists here, so it adds a request-body schema and POST/CORS work without a material MVP benefit. Not preferred. |

**RECOMMENDATION — RECOMMENDED MVP ROUTE SHAPE:** method GET; candidate path `/api/v1/assessments/{batch_id}`; nonempty path identifier; no request body or caller-supplied provenance; response `RiskAssessment` using IGR-04B. Runtime selects the reviewed snapshot/fit. This is not an accepted route.

**RECOMMENDATION — HTTP/cache review:** retain side-effect-free request computation and no fitting on GET. Because the same URL can represent a different fit after restart/release and `generated_at` changes, use conservative no-store behavior initially rather than assume cacheability from GET alone. Future ETags or versioned resource URLs are deferred. No cache header policy currently exists for this route.

**RECOMMENDATION — Canonical-input ownership:** backend owns raw→canonical mapping for this dataset-backed MVP. IGR-03 already implements S1 joins/temporal constraints, S12 has only response contracts, and S3 APR2-D2 describes selecting recorded assessments, not entering raw predictive forms. Canonical-body POST remains a future integration option with its own validation/provenance review.

**UNKNOWN:** permitted recorded batch set (including training-season requests), path-ID validation, exact error envelope, version-release behavior and cache policy await API review. Selecting GET here is grounded in replay semantics and mapping ownership, not merely easier CORS.

## 11. Failure taxonomy

**FACT:** `BatchNotFoundError`, `CardinalityError` and `CanonicalValidationError` derive from `CanonicalMappingError`, itself `ValueError`. Invalid/empty IDs also raise BatchNotFoundError. Missing required tables raise the base mapping error. Pydantic validation may raise its own `ValidationError`; the mapper does not wrap all exceptions. None carries HTTP status policy. Catching the base mapping exception before the not-found subclass would lose the distinction (S8).

**RECOMMENDATION — Decision table:** all statuses below are candidates, unaccepted. This table concerns the proposed GET, where the server owns source data. No public error schema or reason-code vocabulary is established here.

| Case | Candidate HTTP status | RiskAssessment insufficient_data? | Error kind and reason | Decision status |
| --- | --- | --- | --- | --- |
| Batch ID not present in otherwise available snapshot | 404 | No | Lookup/application error; no assessable entity was resolved | RECOMMENDATION; API review |
| Batch-specific raw/canonical mapping fails (including join cardinality, parsing or model validation) | 500 | No automatic conversion | Server-owned source/contract failure; client supplied only an ID. 422 would be more appropriate to reviewed invalid canonical-body POST, not automatically to GET | RECOMMENDATION; API review |
| Runtime dataset unavailable or rejected during load | 503 if service is running | No | Required service resource unavailable, not engine minimum failure | RECOMMENDATION; startup/readiness review |
| Baseline artifact unavailable | 503 if service is running | No | Runtime not ready; no synthetic default or hidden fit | RECOMMENDATION; startup/readiness review |
| Baseline artifact invalid, wrong version or incompatible snapshot | 503 after configuration is marked unavailable | No | Loader refuses configuration; validation details stay diagnostic. Unexpected corruption of supposedly valid live state would be 500 | RECOMMENDATION; loader/API review |
| Engine cannot assess otherwise-valid canonical input due to declared unmet minimum | 200 with insufficient_data only after such a case/policy is defined | Conditional | Engine semantic per S2 D7, factual limitations and null risk/horizon; no current S7 branch implements this | UNKNOWN exact minimum/case; future policy required |
| Internal unexpected failure | 500 | No | Implementation failure; do not fabricate assessment/provenance | RECOMMENDATION; API review |

**RECOMMENDATION:** distinguish a startup-global malformed dataset (unavailable runtime, 503) from a batch-local mapping failure found during a request (500). If the approved alternative is to abort process startup, there is no HTTP response from that process; 503 rows apply only to a running degraded service. Return bounded error information rather than raw rows, paths or tracebacks. Exact envelope is a shared HTTP contract to review.

**FACT — Engine minimum vs input validity:** S6 mathematically reads only crop type, but its API expects a `BatchAssessmentInput`. S1/S8 require a much larger valid object, including joins, QC chronology and eligible telemetry. A failed mapper cannot be bypassed by constructing a crop-only request. Unseen crop has an existing global median fallback; it is not missing crop or insufficient data. Optional logistics/channel absence and telemetry truncation alone do not mandate insufficiency (S2 D4/D7).

**UNKNOWN:** exhaustive runtime sufficiency criteria and factual reason vocabulary remain absent. With a valid baseline and current canonical inputs, S7 returns assessed; a thrown engine exception is not evidence of unmet minima. This recon adds no repair, fallback, sufficiency branch or new `AssessmentStatus`.

## 12. Runtime ownership/state alternatives

| Option | RECOMMENDATION analysis |
| --- | --- |
| Lifespan-loaded runtime state | Explicit startup ownership and validation; one stable context per application process; easy to report configured/unavailable. Appropriate for the small MVP. Multi-worker duplication remains a measured resource question. |
| Module/global baseline singleton | Fewer plumbing lines, but import-time IO, test isolation, stale state and worker behavior become implicit. Not preferred. |
| Per-request construction | Fresh object isolation but repeated dataset/fit/artifact IO and risk of request-to-request drift. Not preferred for this fixed snapshot. |
| Explicit dependency/provider | Makes the context and clock replaceable in tests; complements lifespan instead of replacing its load/lifetime semantics. No repository framework needed. |

**RECOMMENDATION:** one lifespan-loaded context per app process, passed through a small explicit dependency/provider to request orchestration. Pin baseline, snapshot and provenance together; reload only through a deliberate restart/release in the first slice. Treat baseline data as read-only by ownership and avoid mutation/exposing its dictionary. Snapshot rows likewise stay fixed; the existing mapper cache is an implementation detail, not a new immutable type claim. Tests should address first-use cache behavior and prevent data mutation.

**RECOMMENDATION:** if loading fails, keep the foundation health and synthetic demo routes available, mark real analytics unavailable and return reviewed service errors on the real route. Publish context only after successful validation so requests never see a half-loaded fit/snapshot. This degraded-running choice depends on the reviewed health semantics; fail-fast startup is the simpler alternative but would also make health/demo unreachable until recovery. No automatic retry/retraining system is proposed.

**UNKNOWN:** actual snapshot memory, startup load time, per-batch mapper latency and concurrent request behavior are unmeasured. The snapshot has 669,665 sensor readings per S13; artifact loading does not remove the larger canonical-mapping cost. Start with a bounded single-process demo assumption subject to measurement, not an asserted scalability guarantee.

## 13. Health/CORS/shared-contract impact

### Health alternatives

| Option | Truthfulness / scope / consumer and test impact |
| --- | --- |
| A — leave health unchanged | INFERENCE: `not_configured` becomes misleading when real analytics are configured; no code/test changes, but contradictory demo status. Not recommended as the final slice. |
| B — widen analytics literal/status | RECOMMENDATION: smallest truthful change. Preserve route and service identity; distinguish configured readiness from absent/failed configuration with reviewed values. Backend schema/route, TS mirror and exact API assertions need coordinated updates. |
| C — structured analytics health | RECOMMENDATION alternative: could describe engine/artifact/readiness detail, but changes response shape and consumer/rendering/tests more substantially. Unnecessary for this one-fit MVP. |
| D — defer reconciliation | INFERENCE: temporarily avoids shared edits but leaves an acknowledged false status once configured. Could support internal development only with explicit gate acceptance; not a truthful completed demo. |

**RECOMMENDATION:** choose B through Human Gate. Exact literal names, treatment of failed vs absent configuration, whether health means liveness or readiness, and whether its HTTP status stays 200 are unresolved. Keeping `status=ok` as process liveness and reporting analytics availability separately is a candidate, not an existing decision. Review all of this together with §12's degraded-running option.

**FACT — Consumer effect:** S12's BackendStatus displays the literal, while HomePage also hardcodes “Analytics and dataset integration are not configured yet.” A TS mirror edit is contract maintenance; changing HomePage copy/real-flow behavior is separate frontend integration. The next backend slice alone should not be presented as a truthful integrated user demo.

**FACT / RECOMMENDATION — CORS:** current methods are GET only. Recommended GET needs no method change for the already allowed frontend origins. Any POST candidate needs explicit POST allowance and browser preflight coverage; changing origins remains a separate deployment/config question. No CORS edit is made here.

### Dependency and configuration impact

| Item | RECOMMENDATION / impact |
| --- | --- |
| New Python dependency | Not expected: existing FastAPI/Pydantic and standard-library csv/statistics/json/hashlib/pathlib can cover the bounded path. Do not import the numpy/pandas/scipy/sklearn evidence runner into runtime. |
| New config file | Not inherently needed; a small explicit runtime settings/provider surface is enough. Exact default-path policy remains unselected. |
| New env variable | Explicit dataset/artifact path settings are recommended for portability; names/defaults are not chosen. Review environment contract/documentation and whether an existing example file should be updated. |
| New artifact file | Yes for A, separately generated and owned by the application release; none for B. Exact location, distribution and source-control treatment require approval. |
| New schema | Private artifact validation/format for A and reviewed health literal widening; possibly a transport error envelope. No required change to RiskAssessment or BatchAssessmentInput. |
| New lockfile | No inherent need and no new dependency expected. Reassess only if the bounded contract selects a legitimately necessary dependency. |

**RECOMMENDATION — SHARED CHANGE REQUIRES HUMAN GATE:** new endpoint/errors, health backend/TS contract, provenance interpretation, runtime training/artifact policy and new runtime configuration/distribution surface. No restriction here justifies hiding a necessary contract change to keep the task small.

## 14. Frontend/downstream impact

**FACT — Base-qualified frontend:** S12 client offers only `getHealth` and `getDemoAssessment`; `getJson` casts JSON to TypeScript without runtime validation and throws a generic HTTP-status error on failure. HomePage loads both in Promise.all and models connection states, not batch selection. AssessmentCard can render a score but still says “Contract proof” / “Synthetic assessment”; it does render reason codes/missing requirements, unlike older IGR-01 observations. It does not establish a real user assessment flow.

**RECOMMENDATION — Later frontend task:** add a typed single-ID fetch using proper path encoding; handle reviewed not-found/service/data errors separately from insufficient assessment data; reconcile health mirror and stale copy; distinguish fixture/dataset-backed provenance. `RiskAssessment` already fits the response. Do not add a TypeScript `BatchAssessmentInput` for the recommended GET. Rich factual batch context is not present in this response; a future context surface is separately reviewed rather than smuggled into factors or notice.

**RECOMMENDATION — Future multi-batch boundary only:** establish a stable baseline instance and concrete engine/version, pinned snapshot and lineage, backend canonical mapping, deterministic scores, traceable generation time and distinct failure semantics. A future replay endpoint can reuse the internal single-batch service. Same tier/version is the accepted necessary ranking condition; stable concrete fit prevents a misleading same-version comparison. Preserve S2/S3 ordering and exclude insufficient-data results from numeric ranking. Do not rank arbitrary different fits merely because their family labels match.

**UNKNOWN / DEFERRED:** queue membership/window/capacity, pagination, queue error aggregation, live updates and context-detail transport. The sequence runtime single-batch → separate multi-batch/replay → frontend queue → VLD-03 is an INFERENCE consistent with S4 dependencies, not authorization or a newly accepted schedule. PUX-10A remains outside this inspected frontend snapshot.

## 15. Leakage review

**DECISION — Invariants (S1/S2):** historical outcomes belong only to training fitting and isolated offline evaluation targets, never `BatchAssessmentInput`, request prediction input, explanation or batch context output. Arrival QC, realized transit and post-dispatch telemetry are excluded. Generation time does not move the assessment cutoff. No runtime fitting may exploit the requested batch's held-out target.

| Lifecycle | RECOMMENDATION — leakage control / risk |
| --- | --- |
| A | Offline producer alone reads training targets; serialized medians are legitimate learned statistics, not per-batch outcome context. Runtime request scoring sees only fitted baseline + canonical input. Review partition and artifact/snapshot pairing. |
| B | Startup fitting alone may read approved training targets; request orchestration does not read them. Retain clear partition and source boundaries in the same process and discard/separate label access after fitting. |
| C | Every request reopens the training boundary; repeated joins tempt full-snapshot or requested-label fitting. Strict separation would still be possible, but provides no fixed-MVP advantage and is easier to get wrong. |
| D | Constants can conceal fitting provenance or accidental test-label inclusion. Absence of labels in source constants does not prove leakage-free fitting. |
| E | Evidence includes labels-derived metrics and multiple evaluation protocols, not an approved serving release. Loading it confuses evaluation output with serving authority even if only the medians are extracted. |

**FACT — Raw presence is not inference use:** default `read_raw_snapshot` loads outcomes, and raw quality/shipments include forbidden fields. IGR-03 excludes them from the predictive object. There is currently no serving context to isolate those tables from request orchestration.

**RECOMMENDATION:** for A, use the existing reader's explicit manifest parameter to omit historical outcomes from the serving snapshot, while leaving authoritative manifest definitions and canonical schema unchanged. Keep any full-source integrity verification separate from scoring; do not erase training metadata. An alternative full raw snapshot can preserve field-level safety through IGR-03, but broad label access should not be exposed to request services. QC/shipments still need the existing stage/field filters. The exact loading policy requires the bounded contract; no new generalized ingestion behavior is proposed.

**RECOMMENDATION — Verification boundary:** demonstrate that changes to held-out outcomes cannot alter the fitted baseline or scores, forbidden raw fields do not enter serialized inputs/output, and request handling neither fits nor reads labels. Changing bytes may correctly trigger an integrity refusal rather than silently updating the model. Assertions should distinguish refusal from numerical invariance under a permitted test fixture.

**FACT:** S13 parity is evaluation/application-function evidence at its own base, not new VLD-R5 HTTP or commercial validation. No VDR evidence was mutated or consumed as runtime state.

## 16. Recommendation matrix

**RECOMMENDATION — All rows are proposals, not DECISION.** Human decision means the unresolved choice needed for a future bounded contract; detailed alternatives and sources are above.

| Topic | Recommended option | Alternatives | Why preferred | Shared-contract impact | Risks | Remaining UNKNOWN | Human decision? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline lifecycle | A, controlled offline fit/load | B startup; C per request; D constants; E evidence JSON | Clear training/serving separation | Runtime artifact/distribution | Stale artifact pairing | Release ownership/path | Yes |
| Training partition | Explicit initial P1 adoption candidate | Full snapshot; other approved fit | Closest accepted parity evidence | Runtime training policy | In-sample replay misclaims | Allowed assessment set | Yes, V + D |
| Artifact representation | Separate validated JSON + metadata | Python constants/pickle/evidence | Small, reproducible, existing dependencies | Private format/schema | Weak validation or rounded values | Exact schema/storage | Yes |
| engine_version | Bind public version to a concrete fit; family separate internally | Reuse family for every fit | Protect same-version comparability | Provenance meaning, no new public field assumed | Hidden refits under one version | Naming/release rule | Yes |
| source_dataset_id | Pinned assessment-source snapshot; fit lineage separately | Partition ID/artifact ID/hash only | Separates data and fit identity | Field interpretation | ID reused for changed bytes | Exact ID/hash resolution | Yes |
| simulation | True candidate for training context | Fixture-only boolean; false | Honest challenge disclosure | Provenance/product meaning | Treating computation as commercial validation | Full boolean definition | Yes |
| notice | Approved dataset-baseline disclosure | Reuse fixture text/ad hoc copy | Avoid false “synthetic/not challenge” label | Product wording, no field change | Conflicting UI copy | Exact text | Yes, P + V |
| Runtime ownership | Lifespan context + provider | Global/per-request | Explicit stable lifetime, tests | Startup/readiness policy | Mutable data, per-worker memory | Measured resources/failure policy | Contract review |
| Single-batch endpoint | GET candidate with ID | POST canonical / POST ID | Dataset replay and backend mapping | New versioned API | Cache/version ambiguity | Errors, eligibility, cache | Yes, API design review |
| Failure taxonomy | Separate HTTP failures from engine insufficiency | Collapse into insufficient_data | Preserves S2 D7 | Error envelope/statuses | Misclassifying malformed source | Minimums/reason vocabulary | Yes |
| Health contract | Small literal widening | Unchanged/structured/defer | Truthful readiness with limited surface | Backend + TS + tests | Liveness/readiness confusion | Exact values/status behavior | Yes |
| CORS | Retain GET methods | Add POST if chosen | GET route fits current allowance | None for GET | Confusing origin/method issues | Only if route/deployment changes | No separate change for GET |

## 17. Human decisions required

### CAN IMPLEMENT UNDER EXISTING DECISIONS

**DECISION / FACT — Semantic building blocks:** use IGR-03 with unchanged ADR 0002 eligibility/clock; explicitly fit IGR-04A on a supplied approved training collection; pass fitted baseline and canonical input to IGR-04B; preserve current null/unavailable/empty baseline outputs; retain both existing endpoints and synthetic labeling. Standard-library implementation details and tests within an accepted bounded contract do not inherently require a new ADR (S2/S4).

**INFERENCE — Limit:** these accepted building blocks do not establish a fully authorized runtime contract. This VLD-R5 task authorizes no code changes, even for already accepted semantics.

### REQUIRES HUMAN DECISION FIRST

**UNKNOWN / HUMAN DECISION REQUIRED:**

1. Runtime fit policy: A or B, explicit training membership, relation to P1, held-out/in-sample replay limits and release ownership (Vladimir with Viktor).
2. Artifact format/distribution, identity, snapshot compatibility and the binding from algorithm label to concrete public engine version (Vladimir with Igor/Viktor).
3. Meaning/resolution of source_dataset_id, separate dataset/partition fingerprints and admissible provenance for dataset-backed requests (Vladimir with Viktor/Igor).
4. Simulation boolean meaning and fixed truthful dataset notice (Vladimir with Alisa; Igor implements).
5. API design: route/method, ID/eligibility, errors/envelope, generation/cache policy, no caller-provided provenance (Vladimir/Igor, consumer review with Denis).
6. Runtime readiness and health literals/HTTP behavior, synchronized backend/TS contract and tests; configuration paths/defaults (Vladimir/Igor/Denis).
7. If an insufficient-data branch is requested, exact engine minimums and factual reason semantics before implementation; no invented fallback from mapping/service errors (Vladimir/Igor, data review).

**RECOMMENDATION:** record these as explicit bounded approvals before Igor implementation. A new ADR is not automatically necessary for each internal detail, but neither this report nor evidence acceptance substitutes for the shared Human Gate. No new Human decision is made here.

## 18. Proposed next implementation slice

**RECOMMENDATION — PROPOSED NEXT IMPLEMENTATION SLICE:** after the decisions in §17, one Igor contract implements approved baseline lifecycle plus one dataset-backed assessment route, preserving the input/output schemas and old endpoints. This is a proposal, not authorization.

| Boundary | RECOMMENDATION — concrete content |
| --- | --- |
| Observable behavior | Approved producer creates a reproducible independent runtime artifact from the approved training partition; startup validates artifact/snapshot and binds provenance; GET ID invokes IGR-03 then IGR-04B and returns a real scored RiskAssessment. Errors/readiness follow the reviewed contract; requests do not fit. Existing demo remains synthetic. |
| Likely existing files touched | `backend/app/main.py` (lifetime/provider wiring), `backend/app/api/routes.py` (route/health adapter), `backend/app/domain/assessment.py` (HealthResponse only if approved), `backend/tests/test_api.py`, `frontend/src/api/contracts.ts` (health mirror only), separately scoped relevant config/run instructions. No presumed edit to baseline math, mapper semantics or assessment/input models. |
| Likely new files | Small internal runtime/provider and artifact loader/validator modules under backend/app; a bounded offline artifact producer under an approved tools/scripts location; one separate application artifact at an approved path; focused artifact/runtime/route tests. Exact filenames and write allowlist belong to Igor's reviewed contract. No such files are created in this recon. |
| Shared contracts affected | New HTTP route/errors and cache policy; health literal and TS mirror; runtime configuration; artifact/provenance policy. Existing RiskAssessment and BatchAssessmentInput remain unchanged. Any unexpected need to change those semantics returns to the Human Gate. |
| Required future tests | Reproducible fit/serialization with approved membership and held-out exclusion; artifact round-trip and invalid/missing/mismatched lineage refusal; startup success/unavailable and provider isolation; same-fit repeat score and injected generation clock; known/unseen crop; route integration through real mapper/service; each approved failure status without synthetic success; null/unavailable output invariants; old endpoint regressions; health/TS compatibility and GET CORS; no request-time fit/label leakage or state mutation. Measure startup memory/time and representative mapping latency for the demo assumption. |
| Explicitly deferred | Multi-batch/ranked/replay API, window/capacity/membership design, full frontend integration/copy/UI, deployment/VLD-03 execution, generalized arbitrary canonical POST, learned models, database/registry, hot reload, background workers, new engine fallback/minimum policy unless separately approved, context-detail API. |

**RECOMMENDATION — Keep slice narrow:** a TS health mirror update is coordinated contract maintenance, not frontend flow integration. If that shared edit is assigned to a separate owner, coordinate the approved companion change before claiming compatibility. Do not add queue + frontend + deployment to this contract.

## 19. Risks / retained UNKNOWNs

**UNKNOWN:** runtime memory/concurrency/startup and request latency; future dataset drift and missingness; exact private artifact format, ID/version conventions, configuration packaging; provenance/simulation/copy choices; allowed demo request cohort; errors and health semantics; engine-specific minima; external generalization and operational usefulness. Existing unknowns are not closed by passing unit tests.

**INFERENCE — Principal risks:** stale implementation summaries can hide IGR-04B's actual scope; a family-only engine version can hide refit changes; in-sample replay can be mistaken for held-out evidence; malformed artifact values can pass a bare dataclass constructor; mapper cache and mutable dictionaries complicate claims of immutability; a configured backend with fixture-only UI remains an incomplete demo. Mitigations are proposed above, not implemented.

**FACT — Scope matrix:**

```text
Backend changed: NO
Frontend changed: NO
API changed: NO
Schemas changed: NO
ADRs changed: NO
Evidence artifacts changed: NO
Dependencies changed: NO
Config changed: NO
Generated runtime artifact created: NO
New Human decision made: NO
PUX-10A assumed integrated: NO
```

## 20. Verification evidence

**FACT — Executed from repository root:**

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_analytics_baseline.py backend/tests/test_baseline_assessment.py backend/tests/test_api.py -v
```

**FACT — Actual result:** exit 0; Python 3.11.9 / pytest 8.4.2; collected 20 items: 12 baseline, 6 assessment-service, 2 existing API tests. `20 passed, 2 warnings in 0.86s`. Warnings: Starlette TestClient httpx deprecation and anyio BlockingPortal alias deprecation. Dependencies were not modified. These tests use synthetic training/input fixtures and existing health/demo HTTP paths; they do not verify a future real endpoint or the supplied dataset's full runtime path.

**FACT — Not executed:** full backend suite, frontend build/tests, VDR-06A regeneration, supplied-dataset fitting, new runtime artifact generation, live server/browser demo, deployment, memory/concurrency benchmarks. They are outside this read-only deliverable; recorded VDR parity is cited evidence, not a fresh execution result.

**FACT — Final repository checks:** final `git fetch origin` succeeded; origin/main and HEAD remained `e8e14e3da7921a1d87f7bfc6e474f639ef87aa53`. Branch remained `vladimir/vld-r5-runtime-assessment-recon`. Status and untracked enumeration showed only this file. `git diff --name-only` and `git diff --stat` were empty; `git diff --check` produced no errors. Because the report is untracked, those ordinary diff commands do not cover its content. Full `Get-Content` was executed. A no-index comparison to `/dev/null` produced no whitespace-error diagnostics (exit 1 for the added-file difference); Git initially also reported its LF-to-CRLF normalization warning. Rechecking with command-local `core.autocrlf=false` removed that warning without changing configuration. An independent trailing-whitespace scan found zero offending lines. No stage/commit/push/PR/merge occurred.

**RECOMMENDATION — PROPOSED NEXT IMPLEMENTATION SLICE (completion boundary):** review this packet, obtain the explicit runtime/API/provenance/health choices, then issue the narrow Igor lifecycle + single-batch contract described in §18. Separate multi-batch/replay and frontend integration follow later.

**FACT — STOP FOR PROJECT BRAIN REVIEW.** No Igor implementation is started. No commit, push, PR creation or merge before Project Brain review and the subsequent Human decision/integration gate.
