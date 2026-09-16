# Vladimir / Integrator — challenge workstream tasks

## Document status

**Project:** SoS — Training Challenge #3 — AgriFood\
**Challenge:** Smart Harvest: Reduce Post-Harvest Losses\
**Owner:** Vladimir\
**Role:** Integrator\
**Status:** DRAFT FOR REVIEW / TRAINING WORKFLOW\
**Purpose:** Define Vladimir's own challenge work beyond routine team coordination.

This document describes Vladimir's challenge-specific ownership and the sequence of integration work that should connect requirements, data, backend, UX, evidence, demo, and pitch.

It does **not** authorize commit, merge, release, architecture expansion, or changes to team authority. Those remain human decisions.

---

# 0. Context and boundaries

## 0.1. Current role

Vladimir is the team **Integrator**.

Primary responsibility:

- preserve continuity between requirements, product meaning, architecture, implementation, evidence, demo, and pitch;
- decompose cross-cutting work into bounded implementation steps;
- own integration boundaries and shared-contract decisions;
- detect conflicts between workstreams;
- make sure one person's output can actually be consumed by the next workstream;
- assemble the final working solution.

The Integrator should prevent divergence in the chain:

```text
requirements
    ↓
product meaning
    ↓
data semantics
    ↓
architecture / contracts
    ↓
implementation
    ↓
verification evidence
    ↓
demo
    ↓
pitch
```

## 0.2. What Vladimir should NOT absorb by default

The Integrator is not expected to duplicate another owner's primary work.

Do not take over without a specific integration reason:

- dataset reconnaissance and evaluation owned by Viktor;
- backend/application implementation owned by Igor;
- UX/demo/exploratory QA owned by prscr;
- challenge interpretation, user/problem framing, clarification tracking, and product narrative owned by Alisa.

Cross-workstream assistance is allowed, but ownership should remain visible.

## 0.3. Current committed baseline

At the time this task document was prepared, the committed repository foundation contains:

- React + TypeScript + Vite frontend;
- FastAPI + Pydantic backend;
- typed `RiskAssessment` output semantics;
- health endpoint;
- synthetic demo assessment;
- explicit `insufficient_data` behavior;
- architecture, challenge canon, data-contract, domain-rule, evaluation, demo, and role documentation.

The foundation intentionally does **not** yet contain:

- challenge-dataset ingestion;
- a production raw input schema;
- validated feature engineering;
- a real risk formula;
- validated crop/storage rules;
- an ML model;
- persistence;
- authentication;
- realtime processing;
- deployment integration.

These are not omissions that Vladimir should independently fill by guessing. They remain unresolved until the corresponding evidence exists.

## 0.4. Challenge outcomes that integration must eventually prove

The finished solution should help an operator understand:

1. which batches are most at risk;
2. when product quality may begin to deteriorate;
3. what factors contribute to the risk;
4. what action should be prioritized to reduce potential losses.

The integration work is successful only if those outcomes are connected to actual evidence and implemented behavior rather than being present only in slides or UI copy.

---

# VLD-01 — Build the Integration Contract and Workstream Dependency Map

## Status

**START NOW**

This is Vladimir's first independent challenge task.

It should be done before implementation work from different owners begins to depend on incompatible assumptions.

## Goal

Create an explicit integration map that explains:

- what each workstream is expected to produce;
- which outputs are consumed by other workstreams;
- which boundaries are already stable;
- which boundaries are still `UNKNOWN`;
- what evidence is required before an `UNKNOWN` may become a `DECISION`;
- which changes would affect shared contracts and therefore require an integration gate.

The purpose is **not** to design the missing dataset schema, risk model, or agronomic rules.

The purpose is to ensure that when those things become known, the team has a controlled way to connect them.

## Required inputs

Read the current committed versions of at least:

```text
Sponsor/high-priority training sources:
sponsor_pack/README.md
sponsor_pack/brief/Training Challenge #3 — AgriFood.md
sponsor_pack/data/data_dictionary.xlsx
sponsor_pack/data/ (relevant supplied headers/schema material)

README.md
docs/team_roles.md
docs/challenge_canon.md
docs/architecture.md
docs/data_contract.md
docs/assumptions_unknowns.md
docs/domain_rules.md
docs/evaluation.md
docs/demo_runbook.md
docs/decisions/
```

Use source precedence: current sponsor materials first for supplied challenge facts; then accepted SoS decisions/contracts; then challenge canon; then process guidance; then workstream notes. Sponsor materials remain **SIMULATION / training sources** and do not establish facts about a real GigaHack provider.

Also inspect any accepted workstream artifacts that exist at the time of execution.

Expected future inputs include, without assuming their conclusions:

- Viktor's data reconnaissance and evaluation evidence;
- Alisa's challenge/product/domain research;
- Igor's technical reconnaissance or implementation plans;
- prscr's UX/demo findings.

## Work

### Step 1 — Inventory stable contracts

Identify the contracts that already exist in the committed repository.

For each one record:

- path;
- what it currently guarantees;
- who consumes it;
- whether it may be extended without breaking consumers;
- what kind of change would be considered cross-cutting.

At minimum inspect:

- public `RiskAssessment` semantics;
- `assessed` vs `insufficient_data`;
- reliability semantics;
- provenance semantics;
- structured factors;
- structured recommendations;
- current API boundary.

Do not silently rewrite these contracts.

### Step 2 — Map workstream outputs to consumers

Build a dependency map such as:

```text
Alisa
  └─ validated product/domain findings
          ↓
Vladimir integration gate
          ↓
domain / product decisions
          ↓
Igor + Viktor + prscr

Viktor
  └─ dataset schema + quality + usable labels + evaluation evidence
          ↓
Vladimir integration gate
          ↓
production input / analytics decisions
          ↓
Igor
          ↓
public RiskAssessment
          ↓
prscr

prscr
  └─ operator workflow + failure-state requirements
          ↓
Vladimir integration gate when shared API behavior is affected
          ↓
Igor / frontend implementation

All implementation
          ↓
Vladimir end-to-end gate
          ↓
demo + pitch
```

The final map must reflect actual accepted outputs, not assumptions about what another person will discover.

### Step 3 — Define boundary ownership

For every major boundary identify:

- producer;
- consumer;
- current contract;
- unresolved questions;
- decision owner;
- evidence needed before changing it.

Important boundaries include:

```text
raw dataset
→ ingestion

ingestion
→ canonical representation

canonical representation
→ analytics

analytics
→ RiskAssessment

RiskAssessment
→ API

API
→ frontend

assessment semantics
→ demo

verified behavior
→ product claims / pitch
```

### Step 4 — Reference the canonical UNKNOWN register and add integration relationships

Use `docs/assumptions_unknowns.md` as the canonical project UNKNOWN register. Do not maintain a second independent global list that can drift.

In the integration contract, reference canonical UNKNOWNs and record only integration-specific relationships: affected producer/consumer boundary, current blocker, evidence owner/task, decision trigger, and downstream impact.

Examples of legitimate UNKNOWNs at the current stage:

- observed integrity of documented joins;
- usable target interpretation;
- supportable deterioration horizon;
- evaluation-safe feature windows;
- validated recommendation evidence;
- runtime and deployment requirements.

The supplied raw schema and documented temporal boundary are not blanket UNKNOWNs. Their observed integrity, usability and safe implementation mapping still require evidence. Do not convert supplied content into fictional fields or accepted production contracts.

### Step 5 — Define change triggers

For each important UNKNOWN state what evidence would trigger a decision.

Example:

```text
UNKNOWN:
Can deterioration horizon be estimated?

Required evidence before DECISION:
- dataset has usable temporal evidence or defensible proxy;
- Viktor documents leakage risks and evaluation implications;
- Alisa/domain research shows the output has meaningful operator interpretation;
- proposed semantics fit or explicitly revise the current RiskAssessment contract.
```

### Step 6 — Identify integration STOP conditions

The map must explicitly state when downstream work must stop and surface the problem instead of making a local assumption.

At minimum STOP when:

- a workstream needs to alter a shared API or domain contract;
- a task requires a dataset field that has not been verified;
- an agronomic threshold is being introduced without evidence;
- a recommendation implies causal benefit not supported by evidence;
- a dependency/config/schema change unexpectedly expands scope;
- two accepted workstream artifacts contradict one another;
- a product claim cannot be traced to implementation/evidence;
- the only available justification is an AI agent's self-report.

### Step 7 — Produce the integration artifact

Preferred deliverable:

```text
docs/integration_contract.md
```

Possible supporting artifact if useful:

```text
an integration-specific dependency table inside docs/integration_contract.md
```

Do not create a second global UNKNOWN register or duplicate `challenge_canon.md` / `assumptions_unknowns.md`. Reference them and capture only cross-workstream integration semantics.

## Acceptance criteria

### Positive acceptance

VLD-01 is acceptable when:

- every major workstream has an explicit producer/consumer relationship;
- current stable contracts are clearly separated from unresolved boundaries;
- the document does not invent the raw dataset schema;
- cross-cutting changes have defined human integration gates;
- downstream owners can tell when they may proceed and when they must stop;
- there is a traceable path from future evidence to shared decisions;
- the map is consistent with current committed architecture and role ownership.

### Negative / failure cases

VLD-01 is **not** acceptable if it:

- invents challenge data fields;
- chooses a risk formula;
- chooses an ML algorithm without dataset evidence;
- introduces agronomic thresholds as facts;
- selects persistence or hosting without need/evidence;
- transfers another owner's responsibility to Vladimir without reason;
- changes public contract semantics merely to simplify a local task;
- treats expected future reports as if their conclusions were already known.

## Evidence / handoff

Provide:

- base ref / SHA used for the review;
- list of repository paths inspected;
- resulting integration document;
- list of unresolved cross-cutting UNKNOWNs;
- list of existing contracts preserved;
- list of proposed shared-contract changes, or explicit `none`;
- any contradictions found between existing documents.

---

# VLD-02 — Run the Cross-Cutting Decision Gate

## Status

**WAIT FOR EVIDENCE**

Do not attempt to complete this task merely because VLD-01 exists.

VLD-02 begins when relevant owner outputs produce enough evidence to resolve one or more cross-cutting UNKNOWNs.

## Goal

Convert evidence from separate workstreams into explicit, recorded team decisions without allowing local implementation assumptions to silently become global architecture.

Typical decisions may include:

- production input/canonical batch semantics;
- how raw dataset fields map into canonical concepts;
- what the deterministic baseline may legitimately compute;
- semantics of risk;
- semantics of deterioration horizon;
- reliability behavior;
- action/recommendation semantics;
- how missing or conflicting data degrades;
- whether persistence is actually required;
- whether the current API contract must be versioned or extended.

This list is not permission to decide every item. A decision is made only when necessary and evidence-supported.

Do not finalize predictive input semantics until accepted Viktor temporal/leakage evidence establishes assessment-time availability, forbidden future information, and shared-zone/time risks. VDR-01 inventory/integrity evidence alone is not sufficient for that gate.

## Inputs

Use accepted evidence from the relevant owners.

Likely sources:

### From Viktor

- actual dataset structure;
- field semantics where known;
- missingness;
- temporal structure;
- joins;
- label availability;
- leakage risks;
- possible evaluation design;
- limitations.

For predictive input semantics, accepted VDR-02 temporal/leakage evidence is mandatory. Later target/evaluation/model-dependent decisions require separately approved Viktor work beyond VDR-01/VDR-02.

### From Alisa

- confirmed challenge interpretation;
- user/operator needs;
- validated domain findings;
- domain limitations;
- mentor/owner clarification if any;
- clear separation of facts, recommendations, assumptions, and unknowns.

### From Igor

- implementation constraints discovered through relevant repository inspection;
- interface implications;
- technical conflicts;
- narrowly justified proposals for contract changes.

### From prscr

- required operator states;
- UX failure modes;
- presentation needs that may affect API semantics;
- demo constraints.

## Work

### Step 1 — Build a decision packet

For each proposed cross-cutting decision record:

```text
Question:
Current status:
Why a decision is needed now:
Evidence:
Affected owners:
Affected files/contracts:
Alternatives:
Risks:
Recommended decision:
Remaining UNKNOWNs:
```

### Step 2 — Check source hierarchy

Before accepting a decision, verify that it does not conflict with:

1. direct challenge materials;
2. newer explicit clarification;
3. accepted SoS operating decisions;
4. challenge canon;
5. general preparation guidance.

A lower-level technical convenience must not override a higher-level challenge constraint.

### Step 3 — Check contract impact

For every decision ask:

- Does this change `RiskAssessment` meaning?
- Does this add/change a public API field?
- Does this alter frontend assumptions?
- Does this alter evaluation semantics?
- Does this alter provenance?
- Does this require a dependency/config/schema change?
- Does this invalidate existing tests or fixtures?
- Does this introduce new domain claims?

If yes, treat it as a shared-contract change.

### Step 4 — Record the decision

Use the appropriate canonical destination.

Examples:

```text
docs/challenge_canon.md
docs/data_contract.md
docs/domain_rules.md
docs/evaluation.md
docs/architecture.md
docs/decisions/<ADR>.md
docs/assumptions_unknowns.md
```

Do not place everything in one mega-document.

Preserve requirement history. If new evidence changes an older assumption, record the change rather than silently rewriting the past as though the earlier state never existed.

### Step 5 — Issue downstream implementation contracts

Only after the cross-cutting decision is accepted should a new implementation task rely on it.

The Integrator should ensure that downstream task contracts identify:

- accepted decision;
- source evidence;
- write scope;
- preserved contracts;
- forbidden changes;
- verification;
- required evidence;
- STOP conditions.

## Acceptance criteria

VLD-02 is acceptable for a given decision when:

- the decision was actually necessary;
- its evidence is cited;
- affected owners are known;
- alternatives/risks are visible where material;
- canonical documents were updated consistently;
- downstream tasks use the accepted semantics;
- no unsupported assumption was promoted to FACT.

## Failure cases

Reject or defer the decision when:

- evidence is missing;
- owner reports conflict and the conflict has not been resolved;
- the decision exists only because an AI suggested it;
- a metric has no valid interpretation;
- a crop/storage threshold has no defensible source;
- the team is trying to decide an implementation detail that does not need global standardization;
- the choice would prematurely lock architecture without challenge benefit.

## Evidence / handoff

For every closed decision gate provide:

- decision ID or ADR path;
- source artifacts used;
- affected contracts/files;
- exact downstream tasks unblocked;
- remaining UNKNOWNs;
- explicit statement of whether shared API/data semantics changed.

---

# VLD-03 — End-to-End Integration and Behaviour Gate

## Status

**WAIT FOR IMPLEMENTABLE WORKSTREAM OUTPUTS**

Start when data/analytics/backend/frontend pieces exist in a form that can be integrated.

## Goal

Prove that the solution works as one product rather than as several individually plausible workstreams.

Target conceptual chain:

```text
actual/supplied input data
        ↓
validation / ingestion
        ↓
canonical representation
        ↓
analytics / assessment
        ↓
RiskAssessment
        ↓
explanation + recommendation
        ↓
API
        ↓
operator UI
```

The integrated product must preserve the four challenge outcomes:

- risky batches;
- deterioration timing when supportable;
- contributing factors;
- prioritized action when supportable.

## Work

### Step 1 — Establish integration base

Before changing anything record:

- repository ref / base SHA;
- relevant branches/PRs being integrated;
- accepted contracts;
- known unresolved items.

Do not infer uncommitted local state from GitHub.

### Step 2 — Verify each boundary independently

Check actual producer/consumer behavior.

Examples:

- ingestion produces what analytics expects;
- analytics uses validated canonical fields rather than raw accidental names;
- `insufficient_data` still works;
- assessment does not fabricate unsupported horizon;
- factors have traceable evidence;
- recommendation semantics match accepted domain rules;
- API serializes the accepted contract;
- frontend handles both successful and degraded assessments.

Future integration verification must also explicitly test that:

- arrival inspection is not required for prediction;
- final outcomes cannot influence a prediction;
- actual post-dispatch delay, incidents, realized transport telemetry, or equivalent future observations do not leak into prediction or explanation;
- storage telemetry reaches batches through storage sessions and the appropriate zone/time semantics (`batches <- storage_sessions -> storage_zones -> sensor_readings`), not a fictitious direct batch-sensor relation;
- planned transport information known at dispatch is distinguished from realized transport outcomes.

These are required future checks, not claims that the current foundation has already passed them.

### Step 3 — Test happy path

Use an evidence-backed case that can produce a valid assessment.

Verify end-to-end:

```text
input
→ assessment
→ API response
→ UI presentation
```

Record actual values/output used as proof.

### Step 4 — Test negative/failure paths

At minimum cover cases relevant to the final implementation, such as:

- missing required evidence;
- malformed input;
- partially missing measurements;
- unknown/unsupported batch;
- analytics failure;
- backend unavailable;
- no supportable recommendation;
- no supportable deterioration horizon.

Expected behavior should fail safely rather than fabricate precision.

### Step 5 — Check provenance and simulation labels

Training fixtures and synthetic examples must remain visibly distinguishable from challenge data.

No synthetic fixture may silently become evidence for model/business performance.

### Step 6 — Resolve integration defects narrowly

When a defect is found:

1. identify the broken boundary;
2. identify the owner;
3. determine whether the fix is local or shared-contract level;
4. create a bounded fix-up contract;
5. require evidence;
6. re-run the affected integration path.

Do not use an integration bug as permission for unrelated architecture cleanup.

## Acceptance criteria

VLD-03 is acceptable when:

- the end-to-end happy path actually runs;
- important degraded paths behave correctly;
- current shared contracts remain coherent;
- UI output corresponds to backend output;
- backend output corresponds to actual analytics behavior;
- analytics behavior corresponds to validated input semantics;
- no unsupported value is fabricated to make the demo look complete;
- evidence includes actual executed checks, not only screenshots or self-report.

## Required evidence

Collect, as appropriate:

- base and HEAD;
- changed files;
- relevant diff/hunks;
- executed tests and exact results;
- API sample output;
- UI/demo evidence;
- negative-case evidence;
- unresolved failures;
- contract/config/dependency changes or explicit `none`.

---

# VLD-04 — Runtime, Deployment and Demo Operational Readiness

## Status

**DEFER UNTIL PRODUCT SHAPE IS STABLE ENOUGH**

This work may be delegated later, but Vladimir owns ensuring it is not forgotten.

## Goal

Make the integrated product reproducible and demonstrable under realistic hackathon conditions.

This is not an instruction to prematurely select a hosting provider.

## Work

### Step 1 — Define the minimum operational requirement

Decide what the final demo actually needs.

Possible examples:

- one-command or clearly documented local startup;
- frontend + backend startup sequence;
- required environment variables;
- seed/demo dataset;
- offline fallback if external connectivity is not required;
- remote deployment only if it materially improves the final demo.

Choose only what is needed.

### Step 2 — Reproduce from a clean state

The runbook should allow a teammate who did not build the system to:

1. obtain the accepted code;
2. install required dependencies;
3. provide allowed configuration;
4. start the solution;
5. load the intended demo case;
6. verify health;
7. complete the demo flow.

Hidden machine-specific setup is a failure.

### Step 3 — Stabilize configuration

Document:

- runtime versions;
- install commands;
- environment variables;
- data locations;
- startup commands;
- build commands;
- verification commands.

Secrets must not be committed.

### Step 4 — Deployment decision gate, if needed

If deployment is useful, explicitly decide:

```text
Why deployment is needed:
Chosen environment:
Constraints:
Cost:
Cold start / sleep behavior:
Network dependency:
Data handling:
Fallback:
```

Do not introduce complex infrastructure for prestige.

### Step 5 — Demo fallback

Prepare a recovery strategy for likely failures.

Examples:

- remote deployment unavailable;
- network unavailable;
- backend not ready;
- demo dataset missing;
- browser cache/stale frontend;
- one scenario cannot be assessed.

The fallback must not fake successful model behavior.

## Acceptance criteria

VLD-04 is acceptable when:

- another teammate can reproduce the intended demo;
- required configuration is documented;
- startup dependencies are understood;
- deployment, if any, has an explicit purpose;
- demo has a legitimate fallback;
- synthetic/demo data remains labeled;
- operational work has not silently changed product semantics.

## Evidence

Provide:

- clean-start commands actually executed;
- build/test result;
- health/smoke result;
- demo startup procedure;
- environment requirements;
- known limitations;
- fallback procedure.

---

# VLD-05 — Final Evidence, Demo and Pitch Consistency Gate

## Status

**FINAL INTEGRATION GATE**

Do not treat this as a documentation-only task.

## Goal

Verify that the story presented to judges is the same system that exists in code and is supported by evidence.

The final solution should not have separate realities for:

```text
code
demo
metrics
slides
spoken pitch
```

## Work

### Step 1 — Create a claim inventory

Extract concrete claims from:

- UI;
- demo script;
- README/product description;
- presentation;
- pitch;
- evaluation report.

Examples of claims that require evidence:

- "identifies high-risk batches";
- "predicts deterioration in N hours/days";
- "explains major risk drivers";
- "recommends the highest-priority action";
- "reduces expected loss";
- "achieves X accuracy";
- "works for multiple crops";
- "scales to ...".

### Step 2 — Classify every material claim

For each claim mark it as:

- **FACT**
- **DECISION**
- **OBSERVED PRACTICE**
- **INFERENCE**
- **RECOMMENDATION**
- **UNKNOWN**
- **SIMULATION**

A pitch claim must not be stronger than its evidence classification allows.

### Step 3 — Trace claim to evidence

Each important claim should point to one or more of:

- official challenge material;
- accepted domain source;
- dataset evidence;
- evaluation result;
- executed test;
- implemented behavior;
- reproducible demo evidence.

If there is no traceable support, weaken or remove the claim.

### Step 4 — Audit challenge outcomes

Explicitly verify the final product against:

#### A. Which batches are at risk?

Check:

- actual ranking/score behavior;
- missing-data behavior;
- evidence for risk semantics.

#### B. When may quality deteriorate?

Check:

- whether horizon is genuinely supportable;
- whether it is an estimate, range, proxy, or unavailable;
- whether UI/pitch represents that limitation correctly.

#### C. What factors contribute?

Check:

- factor provenance;
- correlation vs causal language;
- data-quality blockers.

#### D. What action should be prioritized?

Check:

- recommendation source;
- whether action is actually supported;
- human-review conditions;
- whether claimed loss reduction is measured, simulated, inferred, or unknown.

### Step 5 — Audit evaluation criteria

Check what evidence the team can legitimately present for:

- agricultural/business usefulness;
- accuracy/reliability;
- usability/explainability;
- potential food-loss reduction;
- scalability;
- innovation.

Do not invent a score for a criterion that has not been measured.

### Step 6 — Run final demo gate

Perform the actual demo sequence using the intended final environment.

Verify:

- expected UI state;
- expected data;
- expected assessment;
- explanation;
- recommendation;
- degraded/failure state if included;
- timing;
- recovery path.

### Step 7 — Produce final integration verdict

Use only:

- `ACCEPTABLE`
- `FIX REQUIRED`
- `BLOCKED: MISSING EVIDENCE`

`ACCEPTABLE` means the solution is ready for the next human integration gate.

It does **not** mean automatic permission to commit, merge, deploy, release, or submit.

## Acceptance criteria

VLD-05 is acceptable when:

- every material pitch claim is evidence-backed or properly qualified;
- demo behavior matches implemented behavior;
- metrics have reproducible provenance;
- synthetic/training results are clearly labeled;
- negative/degraded behavior is not hidden by fabricated output;
- known limitations are documented;
- remaining UNKNOWNs do not masquerade as solved features.

## Evidence / final handoff

Collect:

- final base/HEAD;
- integrated changed-file summary;
- test/build/evaluation commands actually run;
- actual results;
- final demo run evidence;
- claim → evidence mapping;
- unresolved limitations;
- shared-contract changes;
- dependency/config/schema changes;
- final verdict.

---

# 1. Execution order

Recommended order:

```text
NOW
│
├─ VLD-01 Integration Contract
│
│   wait for workstream evidence
│
├─ VLD-02 Cross-Cutting Decision Gate
│      └─ may occur multiple times as evidence arrives
│
│   implementation work becomes integrable
│
├─ VLD-03 End-to-End Integration
│
│   product shape becomes stable
│
├─ VLD-04 Runtime / Deployment / Demo Readiness
│
│   final integrated candidate exists
│
└─ VLD-05 Evidence / Demo / Pitch Consistency Gate
```

VLD-02 is intentionally repeatable.

There may be several small decision gates rather than one large architecture session.

---

# 2. Dependency rules

## VLD-01

Can begin immediately.

Does not require the team to have finished research.

## VLD-02

Requires actual evidence for the specific decision being considered.

Do not close dataset-dependent decisions before the relevant Viktor evidence exists. VDR-01 may support inventory/integrity decisions; VDR-02 is required before predictive input and leakage semantics are finalized; later target/evaluation/model choices require separately approved Data & Evaluation contracts.

Do not close domain-dependent decisions before the relevant product/domain evidence exists.

## VLD-03

Requires actual implementable outputs.

A plan, AI recommendation, screenshot, or architecture diagram alone is not an integrable subsystem.

## VLD-04

Requires enough product stability to know what needs to be operated.

Do not optimize hosting before knowing whether hosting is necessary.

## VLD-05

Requires the final candidate solution, evaluation evidence, and demo/pitch material.

---

# 3. Global STOP conditions for Vladimir

Stop the current task and surface the issue when:

- official challenge material conflicts with a current team decision;
- a newer clarification changes a previous interpretation;
- two workstream owners provide incompatible evidence;
- raw-data semantics are ambiguous enough to affect correctness;
- a requested implementation requires changing a shared contract unexpectedly;
- a dependency, lockfile, config, schema, or architecture change appears outside agreed scope;
- a metric cannot be reproduced;
- an agronomic rule cannot be sourced or validated;
- a recommendation implies unsupported causal effect;
- a demo requirement would require faking unavailable product behavior;
- GitHub committed state is being confused with someone's local/uncommitted state;
- available evidence is insufficient for an integration verdict.

The correct response is not to guess.

Record the issue as `UNKNOWN` or return `BLOCKED: MISSING EVIDENCE` until the required evidence exists.

---

# 4. Integrator working principle

For any substantial cross-cutting step use:

```text
INTENT
  ↓
CONTEXT
  ↓
RECON if needed
  ↓
CONTRACT
  ↓
EXECUTION
  ↓
EVIDENCE
  ↓
REVIEW
  ↓
FIX-UP or ACCEPTABLE
  ↓
HUMAN INTEGRATION
```

Do not collapse:

```text
agent says "done"
```

into:

```text
verified and ready to integrate
```

Those are different states.

---

# 5. Suggested GitHub issue structure

Using GitHub Issues for Vladimir's integration work is recommended.

The cleanest structure is:

## Umbrella issue

```text
VLD — Integrator workstream: Smart Harvest
```

Purpose:

- show the overall integration sequence;
- link all VLD tasks;
- record blocked/unblocked state;
- expose dependencies on other owners;
- provide one place for the final integration status.

Suggested checklist:

```text
- [ ] VLD-01 — Integration Contract and Dependency Map
- [ ] VLD-02 — Cross-Cutting Decision Gate(s)
- [ ] VLD-03 — End-to-End Integration
- [ ] VLD-04 — Runtime / Deployment / Demo Readiness
- [ ] VLD-05 — Final Evidence / Demo / Pitch Consistency Gate
```

## Separate issues

Create a separate issue for each VLD task when it becomes active.

Benefits:

- focused evidence/history;
- easy linking to PRs;
- clear dependencies;
- no giant discussion thread;
- easier audit by Astra;
- easier human close/reopen decisions.

VLD-02 may need multiple child issues, for example:

```text
VLD-02A — Decide production canonical input semantics
VLD-02B — Decide deterioration-horizon semantics
VLD-02C — Decide recommendation evidence boundary
```

Create those only when the decision actually becomes necessary.

Do not create speculative decision issues merely to fill a roadmap.

---

# 6. Suggested issue states

Use labels or simple title/status conventions such as:

```text
READY
BLOCKED
IN PROGRESS
EVIDENCE READY
REVIEW
FIX REQUIRED
ACCEPTABLE
```

Important:

`ACCEPTABLE` is an evidence-review state.

It is not equivalent to:

```text
MERGED
DEPLOYED
RELEASED
SUBMITTED
```

Those remain explicit human actions.

---

# 7. Audit note for Astra

Before this document is adopted into the challenge repository, Astra should audit it against:

1. current committed `training_agrifood` repository state;
2. current official/simulated challenge brief;
3. accepted SoS team roles;
4. current preparation repository process rules;
5. any newer workstream documents that appeared after this draft was prepared.

Astra should specifically look for:

- tasks that duplicate another owner's responsibility;
- premature decisions;
- missing integration boundaries;
- missing acceptance/failure cases;
- contradictions with committed architecture;
- unsupported assumptions;
- missing STOP conditions;
- insufficient evidence requirements;
- issue structure that creates unnecessary coordination overhead.

Any proposed correction should distinguish:

- existing FACT;
- existing DECISION;
- new INFERENCE;
- proposed RECOMMENDATION;
- unresolved UNKNOWN.

Astra should not silently convert recommendations into project canon.

---

# 8. Definition of success for Vladimir's workstream

Vladimir's workstream is successful when the team can move from independently produced work to one coherent solution while answering all of the following:

- What requirement does this behavior satisfy?
- What evidence supports the decision?
- Which data semantics does it rely on?
- Which shared contract defines it?
- Which code implements it?
- Which tests/evaluation verify it?
- What does the user actually see?
- What will the team demonstrate?
- What may the team legitimately claim in the pitch?
- What remains unknown?

If any important link in that chain is missing, integration is not complete.
