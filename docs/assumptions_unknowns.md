# Assumptions and unknowns

The foundation does not close the following questions by assumption. Each item is recorded as **UNKNOWN**.

| UNKNOWN | Why it matters | Decision it blocks | How it will be resolved |
| --- | --- | --- | --- |
| Actual field names and types | Determines parsing and validation | Raw/canonical input models | Inspect supplied files and data dictionary |
| Join keys and entity relationships | Controls correct batch/history linkage | Canonical entity boundaries | Profile identifiers and validate joins |
| Dataset size | Affects processing and memory constraints | Execution and storage design | Measure files and representative workloads |
| Measurement frequency | Determines usable temporal resolution | Aggregation and feature windows | Profile timestamps and sampling patterns |
| Presence of time series | Changes model and validation strategy | Temporal analytics design | Inspect ordering, timestamps, and coverage |
| Presence and type of loss labels | Controls whether supervised evaluation is possible | Learned-model feasibility and metrics | Audit targets, provenance, and completeness |
| Deterioration timestamps | Controls horizon evaluation | Horizon method and metrics | Validate event definitions and coverage |
| Intervention records and action outcomes | Required to estimate action effects | Recommendation evidence | Inspect intervention semantics and confounding |
| Monetary and quantity fields | Required for loss-value claims | Business-impact calculations | Confirm units, currencies, and provenance |
| Crop diversity | Rules may not transfer across crops | Segmentation and rule scope | Profile crop identifiers and domain coverage |
| Missing and noisy data | Determines validation and degradation behavior | Quality checks and minimum evidence | Run a documented data-quality probe |
| Realtime source | Would change ingestion needs | Whether realtime is justified | Confirm provider workflow and source capabilities |
| Hosting constraints | Affects packaging and operations | Deployment topology | Obtain target-environment requirements |
| Valid agronomic rules and thresholds | Incorrect rules could cause harmful advice | Deterministic baseline content | Conduct sourced domain review and expert validation |
| Appropriate learned model family | Depends on labels, censoring, size, and task | ML architecture | Compare justified candidates after data probe |
| Persistence needs | Depend on volume, lifecycle, concurrency, and hosting | Storage technology | Derive requirements after data and workflow probe |

## Working assumptions limited to this foundation

- Python 3.11+ and Node.js 20.19+ or 22.12+ are local development prerequisites.
- The demo runs batch/on-demand through HTTP.
- The fixture is synthetic and exists only to prove contract transport.

These are implementation conditions for the skeleton, not claims about challenge data or agricultural operations.
