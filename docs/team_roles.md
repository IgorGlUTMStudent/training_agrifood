# SoS team roles and ownership

## Status

**DECISION:** This document records the current challenge-specific operating roles for the SoS team in the Smart Harvest training challenge.

It is an internal team decision, not a challenge requirement and not part of the external challenge canon.

Team roster:

- Vladimir
- Igor
- Viktor
- prscr
- Alisa

Roles define **primary ownership**, not exclusive permission to work in an area. Any team member may help in another workstream when needed, but the owner remains responsible for ensuring that the area is not lost, left inconsistent, or left without evidence.

## Vladimir — Integrator

Primary ownership:

- overall project structure and architectural continuity;
- decomposition of large work into implementation steps;
- coordination of shared contracts and integration boundaries;
- integration gates between data, backend, frontend, demo, and product narrative;
- resolution of cross-workstream conflicts;
- final assembly of the solution.

Vladimir is responsible for preventing divergence between:

`requirements → product → code → evidence → demo → pitch`

Important boundary:

- the Integrator remains the final coordination point for cross-cutting scope and architecture decisions;
- commit, merge, release, and integration actions remain human decisions.

## Igor — Technical Deputy

Primary ownership:

- backend and application-layer implementation;
- difficult technical tasks and technical problem solving;
- integration of technical subsystems;
- helping maintain technical coherence across implementation workstreams;
- acting as Vladimir's technical deputy when Vladimir is unavailable for a technical issue.

Secondary responsibility:

- support other implementation owners when a task crosses technical boundaries;
- assist with integration debugging and technical review.

Authority boundary:

Technical Deputy is **not a second Integrator**. Igor may coordinate or decide implementation details inside an agreed technical scope, but cross-cutting product scope, global architecture, shared-contract changes, and team authority changes still go through the Integrator or the relevant human owner.

## Viktor — Data & Evaluation Owner

Primary ownership:

- dataset reconnaissance and profiling;
- data quality assessment;
- identifying usable labels, temporal structure, joins, missingness, and limitations;
- evaluation methodology and baseline comparison;
- checking whether outputs are supported by evidence rather than only presented convincingly;
- guarding against false precision, leakage, misleading metrics, and unsupported claims.

Viktor is responsible for making sure that the team can answer:

- what the data actually contains;
- what conclusions the data can and cannot support;
- whether the analytical result is useful and defensible;
- how the result is verified against an appropriate baseline.

Dataset-dependent ML work may later fall under this ownership if the dataset justifies it, but no specific ML method is implied by the role.

## prscr — UX, Demo + QA

Primary ownership:

- frontend and operator-facing workflow;
- usability and clarity of screens and states;
- demo flow and demonstration reliability;
- exploratory QA and user-visible failure states;
- checking whether the product is understandable without internal implementation context.

Secondary responsibility:

- additional technical implementation when frontend workload is lighter;
- cross-workstream QA and integration checks.

prscr is responsible for preventing a situation where the system is technically functional but difficult to understand, awkward to use, or unreliable during the demo.

## Alisa — Product Owner

Primary ownership:

- challenge interpretation and product meaning;
- user/problem framing;
- tracking requirements and clarifications;
- communication with mentors/challenge representatives when applicable;
- recording new clarification without silently overwriting requirement history;
- checking that the team is solving the intended problem for the intended user;
- helping shape product narrative, demo story, and presentation.

Alisa is responsible for preventing requirement drift and for distinguishing:

- confirmed requirement;
- mentor/advisor recommendation;
- team decision;
- hypothesis or assumption.

Any new external clarification that conflicts with an internal decision must be surfaced to the Integrator and reflected in the relevant canonical documents before downstream tasks are silently changed.

## Task routing

Default routing for substantial work:

- **cross-cutting scope, architecture, shared contracts, integration:** Vladimir;
- **backend, application layer, difficult technical integration:** Igor;
- **dataset, analytics evidence, evaluation:** Viktor;
- **frontend, UX, demo behavior, exploratory QA:** prscr;
- **requirements, mentor clarification, user/problem fit, product narrative:** Alisa.

Routing determines the primary reviewer/owner, not the only allowed executor.

A task that changes a shared contract or crosses multiple ownership areas should be treated as an integration task and surfaced to Vladimir before the contract is changed.

## Collaboration rule

Ownership is intentionally flexible:

- team members may help each other across workstreams;
- an owner may delegate execution while retaining responsibility for the outcome;
- AI agents may implement or research within a scoped contract, but they do not replace the human owner;
- a local implementation task does not gain authority to change global architecture, requirements, dependencies, schemas, or shared contracts on its own.

## Current ownership map

| Area | Primary owner | Typical secondary support |
| --- | --- | --- |
| Integration / architecture continuity | Vladimir | Igor |
| Backend / application integration | Igor | Vladimir, prscr |
| Data reconnaissance / analytics / evaluation | Viktor | Igor, Vladimir |
| Frontend / UX / demo / exploratory QA | prscr | Igor, Vladimir |
| Requirements / product / mentor clarification / pitch narrative | Alisa | Vladimir, prscr |

This map may be revised by an explicit human team decision if the challenge evolves, but changes must be recorded rather than inferred from temporary task assignment.
