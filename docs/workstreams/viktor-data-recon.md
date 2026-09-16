# Viktor Data Recon Workstream

Repository: `Slave-of-Skynet/training_agrifood`\
Base branch: `main`\
Reference commit when this workstream was prepared: `72ab453f52d3bb7909001d0403fc62f89dce117d`

Owner: **Viktor — Data & Evaluation Owner**

This document contains two evidence-producing tasks:

- `VDR-01` — dataset inventory / integrity reconnaissance;
- `VDR-02` — temporal semantics / leakage reconnaissance.

Do not combine them into one large implementation step. Each task should be handled in its own step-chat and should produce its own evidence/handoff before the next task begins. Additional Data & Evaluation work is expected later, but it is intentionally deferred to separately approved task contracts.

The sponsor pack is a **SIMULATION / training challenge source**. Do not present its organizations, operational claims, or dataset as verified facts about real Moldovan agricultural businesses.

---

# VDR-01 — Dataset Inventory and Relational Integrity

## Objective

Establish what the sponsor dataset actually contains.

Produce a factual inventory of every supplied table, its grain, keys, schema, size, relationships, temporal coverage, and basic integrity.

This task must resolve dataset-structure UNKNOWNs through direct inspection of the supplied files rather than by repeating `README.md` or `data_dictionary.xlsx`.

## Starting state

Base repository:

`Slave-of-Skynet/training_agrifood`

Base:

`main @ 72ab453f52d3bb7909001d0403fc62f89dce117d`

Before starting, record:

```text
git rev-parse HEAD
git status --short
```

At activation, fetch and record the actual accepted `main` base. Do not reset to the historical reference SHA. If the fresh base materially invalidates this task contract or the working tree has unexpected changes, stop before writing and report the mismatch.

## Required sources

Inspect at minimum:

```text
sponsor_pack/README.md

sponsor_pack/brief/Training Challenge #3 — AgriFood.md

sponsor_pack/data/
  batches.csv
  facilities.csv
  storage_zones.csv
  storage_sessions.csv
  sensor_readings.csv
  quality_checks.csv
  shipments.csv
  historical_quality_outcomes.csv
  data_dictionary.xlsx

docs/challenge_canon.md
docs/assumptions_unknowns.md
docs/data_contract.md
docs/evaluation.md
```

Relevant inspection outside these paths is allowed.

## Write scope

Create only:

```text
docs/data_recon/01_dataset_inventory.md
```

Temporary local analysis scripts are allowed.

Do not add notebooks, analysis scripts, generated datasets, dependencies, or tooling to the repository without Integrator approval.

## Do not modify

```text
sponsor_pack/**
backend/**
frontend/**
data/**
docs/challenge_canon.md
docs/assumptions_unknowns.md
docs/data_contract.md
docs/evaluation.md
docs/domain_rules.md
dependency files
lockfiles
configuration
```

## Investigation requirements

For every supplied table determine from the actual data:

- row count;
- column count;
- exact column names;
- observed data types;
- apparent row grain;
- candidate primary key;
- uniqueness of that key;
- foreign-key-like fields;
- null counts;
- duplicate-row counts;
- file size;
- timestamp range where applicable.

Compare the observed schema against:

- `sponsor_pack/README.md`;
- `data_dictionary.xlsx`.

Record every meaningful mismatch.

## Relational integrity

Validate the actual relationships among:

```text
facilities → storage_zones
batches ← storage_sessions → storage_zones → sensor_readings
```

and:

```text
batches
  ↓
quality_checks
shipments
historical_quality_outcomes
```

Also determine how `sensor_readings` joins to storage activity.

Measure:

- orphan IDs;
- duplicate identifiers;
- unexpected many-to-many joins;
- missing referenced entities;
- entities with no expected child records;
- ambiguous joins.

Do not infer a relationship only from similar column names. Verify it.

## Data quality reconnaissance

Identify clear evidence of:

- missing values;
- duplicated records;
- invalid categories;
- impossible values;
- suspicious numeric values;
- contradictory records;
- malformed timestamps;
- unit inconsistencies.

Do not automatically classify statistical outliers as errors.

Separate:

- confirmed defect;
- suspicious observation;
- UNKNOWN.

## Required report structure

`docs/data_recon/01_dataset_inventory.md` must contain:

```text
# VDR-01 Dataset Inventory and Relational Integrity

## Executive summary
## Source files inspected
## Dataset inventory
## Entity grain and identifiers
## Relational model observed
## Referential-integrity findings
## Missingness and duplicate findings
## Documentation-vs-data mismatches
## Resolved UNKNOWNs
## Remaining UNKNOWNs
## New UNKNOWNs
## Risks / limitations
## Reproduction and evidence
```

## Positive acceptance

The task is ready for review only if:

- all eight CSV files were actually inspected;
- `data_dictionary.xlsx` was inspected;
- row/column counts are measured;
- candidate identifiers were tested for uniqueness;
- major joins were validated;
- orphan counts are known;
- missingness and duplicates were measured;
- README/dictionary claims were compared with actual data;
- all significant numerical claims have reproducible evidence.

## Negative acceptance

The task fails if:

- the report merely restates documentation;
- joins are assumed rather than tested;
- "data looks clean" is reported without measurements;
- suspicious values are silently removed or repaired;
- sponsor files are modified;
- application code or shared contracts are changed.

## Verification

Use reproducible inspection commands or scripts.

Record:

- tools used;
- relevant versions;
- exact commands or scripts executed;
- output summaries;
- what was not checked.

## Stop conditions

Stop and report to the Integrator if:

- source files are unreadable or corrupt;
- actual data materially contradicts the sponsor specification and no defensible interpretation exists;
- inspection requires modifying shared dependencies or architecture;
- repository state is inconsistent with the assigned base.

## Handoff

Return:

```text
Starting/base SHA:
Current HEAD:
Branch:
git status --short:

Files changed:

Commands/scripts actually executed:

Key evidence:
1.
2.
3.
...

Resolved UNKNOWNs:

Remaining UNKNOWNs:

New UNKNOWNs:

Shared changes:
dependencies: no
lockfile: no
config: no
application schema: no
shared contracts: no
sponsor_pack: unchanged

What the Integrator should verify:
```

Do not commit, push, merge, or modify canonical documents unless explicitly instructed by the Integrator.

---

# VDR-02 — Temporal Semantics and Leakage Audit

## Dependency

Start only after VDR-01 has been reviewed and its factual dataset structure is considered sufficient for the next step.

Use the reviewed VDR-01 report as evidence, not as a replacement for inspecting the underlying data where necessary.

## Objective

Determine exactly what information exists at the prediction moment and identify every important source of temporal, group, entity, or shared-environment leakage.

The key decision moment is:

```text
T_assess = T_dispatch
```

The analysis must model what the operator could have known at dispatch time.

## Required sponsor rule

According to the sponsor specification, post-dispatch information must not become prediction input.

Potentially unavailable future information includes:

- actual transit delays;
- refrigeration failures after dispatch;
- en-route telemetry;
- arrival inspections;
- final quality outcomes;
- final economic loss.

Do not assume the actual CSV structure follows this perfectly. Verify it.

## Write scope

Create only:

```text
docs/data_recon/02_temporal_leakage.md
```

## Do not modify

Same restrictions as VDR-01.

Especially do not modify or clean:

```text
sponsor_pack/**
```

## Temporal reconstruction

For representative and aggregate data, establish the actual order of events such as:

```text
harvest
storage start
sensor history
intermediate inspection
pre-dispatch inspection
dispatch
transport
arrival inspection
final outcome
```

Measure where possible:

- timestamp ranges;
- event ordering violations;
- sensor sampling intervals;
- irregular sampling;
- missing sensor periods;
- overlapping storage sessions;
- readings occurring outside an active session;
- readings after dispatch;
- multiple batches sharing the same zone/chamber over time.

Verify whether the claimed approximately 30-minute telemetry interval is actually observed.

## Leakage matrix

Build an explicit feature-source matrix.

For each important field or feature group record:

```text
Source
Field / feature group
Available at T_dispatch? yes / no / conditional
Reason
Potential leakage type
Safe for predictive input? yes / no / requires transformation
```

At minimum inspect:

- batch metadata;
- harvest data;
- storage metadata;
- storage duration;
- environmental telemetry;
- pre-dispatch quality checks;
- arrival quality checks;
- planned shipment data;
- actual shipment outcomes;
- transit delays;
- final quality outcomes;
- financial losses.

## Non-temporal leakage

Investigate whether evaluation could leak through:

- repeated rows from the same batch;
- multiple quality checks from the same batch;
- batches sharing a storage zone;
- simultaneous batches sharing the same sensor history;
- facility-specific patterns;
- repeated cultivars or producers if present;
- retrospective aggregates containing future information.

The sponsor README explicitly notes that multiple batches may share environmental physics within one chamber. Treat this as a serious split-design issue and verify its actual prevalence.

## Required report structure

```text
# VDR-02 Temporal Semantics and Leakage Audit

## Executive summary
## Prediction-time contract
## Observed event timeline
## Sensor sampling behaviour
## Storage-session overlap
## Feature availability at T_dispatch
## Temporal leakage findings
## Group/entity/shared-environment leakage
## Candidate-safe feature families
## Features that must be excluded
## Implications for train/validation/test splitting
## Resolved UNKNOWNs
## Remaining UNKNOWNs
## New UNKNOWNs
## Reproduction and evidence
```

## Positive acceptance

Ready for review only if:

- actual event chronology was checked;
- sampling behaviour was measured;
- post-dispatch fields were explicitly identified;
- arrival information is treated as unavailable to hidden prediction;
- final outcomes are treated as labels, not features;
- shared-zone/shared-sensor leakage is examined;
- at least one defensible split strategy is described at a conceptual level;
- claims have measured evidence.

## Negative acceptance

The task fails if:

- arrival-stage features are considered normal prediction inputs;
- final losses appear in the feature set;
- retrospective availability is confused with prediction-time availability;
- random row splitting is proposed without considering batch/chamber/group leakage;
- post-dispatch fields are silently transformed into "features";
- the task starts model training.

## Stop conditions

Stop if the prediction-time semantics cannot be reconciled with the supplied data or if an ambiguity materially changes what is legally available at `T_dispatch`.

Report the exact conflict instead of choosing an interpretation silently.

## Handoff

Same state/evidence format as VDR-01.

Additionally include:

```text
Critical leakage risks:

Definitely forbidden prediction inputs:

Conditionally safe inputs:

Recommended split constraints:
```

Do not train a model in this task.

---

# Deferred continuation — later Data & Evaluation contracts

VDR-01 and VDR-02 do not complete the full Data & Evaluation workstream. After their evidence is reviewed, later work is expected to address the following under separately approved task contracts:

- label/target usability;
- risk-target interpretation;
- deterioration-horizon feasibility;
- evaluation design;
- baseline definition and comparison;
- learned-tier justification, only if evidence warrants it.

This section is a handoff boundary, not a specification for VDR-03 or later implementation. It does not choose a target, metric, split, model family, numerical threshold, or performance claim. Those choices require accepted VDR-01/VDR-02 evidence and the relevant product/integration decisions first.
