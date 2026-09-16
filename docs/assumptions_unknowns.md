# Assumptions and unknowns

The foundation predated the sponsor pack. The repository can now distinguish what the supplied training materials document from what still requires empirical reconnaissance. A documented field or relationship is not proof that every record conforms to it.

| Area | Supplied/documented state | Remaining UNKNOWN | Decision it blocks / resolution |
| --- | --- | --- | --- |
| Field names and types | Eight CSV schemas and declared types are documented in `sponsor_pack/data/data_dictionary.xlsx` and visible in the supplied headers | Observed type consistency, parsing exceptions, nullability behavior, and validation requirements | Profile the actual files before raw-to-canonical mapping |
| Joins and entity relationships | The pack documents keys among facilities, zones, storage sessions, batches, checks, shipments, outcomes, and zone telemetry | Observed uniqueness, cardinality, orphan counts, and ambiguous or broken references | Viktor validates joins before canonical entity boundaries are accepted |
| Dataset size | Files are supplied and measurable | Actual row counts, memory profile, and representative processing constraints have not been recorded in accepted recon evidence | Measure files and workloads before execution/storage design |
| Measurement frequency and time series | Sensor timestamps exist and the sponsor describes a nominal 30-minute interval | Actual gaps, irregularity, coverage, ordering, out-of-session readings, and usable temporal resolution | Profile timestamps and sampling behavior before feature windows or split design |
| Assessment-time availability | Sponsor semantics fix `T_assess = T_dispatch` and distinguish planned/known information from realized post-dispatch information | Field-level eligibility, transformations, edge cases, and shared-zone leakage require measured audit | VDR-02 must establish evaluation-safe feature windows and leakage constraints |
| Outcomes and candidate labels | Historical outcome fields are supplied, including quality status, loss fraction, arrival quality score, and economic loss | Provenance, completeness, distribution, censoring, target interpretation, label usability, and evaluation design | Viktor evidence plus product meaning is required before choosing a target or metrics |
| Deterioration timing | The desired product outcome mentions when quality may deteriorate | No exact deterioration-onset label or supportable horizon semantics have been established | Validate event/proxy definitions and coverage before horizon implementation or evaluation |
| Intervention and action effects | No validated intervention-effect contract is established | Action availability, causal effects, confounding, and safe recommendation scope | Sourced domain/product evidence and data evidence are required before recommendation claims |
| Monetary and quantity fields | The pack provides weights, loss fraction, and economic-loss fields with declared units | Validity, derivation, provenance, and fitness for business-impact calculations | Validate before any savings or loss-reduction claim |
| Crop diversity | A supplied crop field exists | Observed coverage, subgroup sizes, transferability, and crop-specific rule scope | Profile data and validate domain evidence before segmentation or rules |
| Missing and noisy data | Some dictionary fields are declared nullable | Actual missingness, duplicates, impossible values, and sensor/data-quality behavior | Run documented data-quality reconnaissance and define degradation requirements |
| Realtime source | The current MVP is batch/on-demand | Whether a realtime workflow is required or supported remains unknown | Obtain product/source requirements before changing ingestion architecture |
| Hosting constraints | No platform is selected | Runtime, data-handling, network, cost, and demo requirements | Obtain target-environment needs before deployment topology |
| Agronomic rules and thresholds | None are accepted | Valid rule scope, sources, thresholds, and expert validation | Conduct sourced domain review; do not promote plausible values to rules |
| Learned model family | None is selected; a deterministic baseline is required first | Whether learning is justified, and any model family or performance expectation | Decide only after target, split, metrics, and baseline evidence exist |
| Persistence needs | No persistence technology is selected | Volume, lifecycle, concurrency, audit, and hosting needs | Derive after data and operator workflow reconnaissance |

## Working assumptions limited to this foundation

- Python 3.11+ and Node.js 20.19+ or 22.12+ are local development prerequisites.
- The demo runs batch/on-demand through HTTP.
- The fixture is synthetic and exists only to prove contract transport.

These are implementation conditions for the skeleton, not claims about challenge data or agricultural operations.
