# PUX Workstream Report — UX, Demo + QA

**Role:** prscr — UX, Demo + QA  
**Repository:** https://github.com/Slave-of-Skynet/training_agrifood  
**Branch:** `prscr/ux-demo-qa`  
**Base SHA:** `20021656028392a420561c6dc2a0f5434835081f`  
**Working tree:** clean, no code modified  
**Status:** Analytical phase complete (PUX-00 … PUX-07). Implementation blocked pending contracts.  
**Date:** 2026-09-18

---

## 1. Current State (PUX-00)

- Foundation skeleton: React + TypeScript + Vite frontend, Python + FastAPI backend.
- Two endpoints implemented: `GET /api/v1/health`, `GET /api/v1/demo/assessment` (static synthetic fixture).
- Frontend renders: loading → connected (insufficient_data card) → unavailable (error + retry).
- **No** batch inventory, analytics engine, risk scoring, recommendations, or multi-batch navigation.
- Sponsor pack present (8 CSVs, 1 800 batches, 10 facilities, 25 zones, 2024–2025).
- Telemetry truncation defect: 204 batches in 2026 lack sensor data after 2025-12-31.

### Known Contracts
| Endpoint | Response | Key invariant |
|---|---|---|
| `/api/v1/health` | `HealthResponse` | `analytics: "not_configured"` |
| `/api/v1/demo/assessment` | `RiskAssessment` | `status == "insufficient_data"` ⇒ `risk == null`, `deterioration_horizon == null` |

### Temporal Boundary
Prediction moment = `T_dispatch`. Retrospective data (arrival inspection, in-transit telemetry, commercial outcome) is **forbidden** as predictive input.

---

## 2. UX Facts / Decisions / Unknowns (PUX-01)

### Key Facts
- Challenge requires 4 operator outcomes: which batches at risk / when deterioration / contributing factors / prioritized action.
- Eligible dispatch-time info: agronomic metadata, storage telemetry ≤ T_dispatch, pre-dispatch inspection, planned transport.
- No validated agronomic rules exist in repository.

### Key Decisions (team)
- Modular monolith; batch/on-demand only (no WebSockets/streaming).
- Deterministic baseline mandatory before ML.
- LLM excluded from scoring path.
- Structured typed factors/recommendations with `requires_human_review: true`.
- Explicit failure states (`insufficient_data`, reliability levels, reason codes).

### UX-Relevant UNKNOWNs
| # | Unknown | Blocks |
|---|---|---|
| 1 | Operator persona & environment | BEFORE WIREFRAME |
| 2 | Operational action catalog | BEFORE WIREFRAME |
| 3 | Risk score interpretation (probability / loss % / index) | BEFORE WIREFRAME |
| 4 | Deterioration horizon semantics | BEFORE WIREFRAME |
| 5 | Batch inventory API shape & pagination | BEFORE WIREFRAME |
| 6 | Factor dictionary & feature codes | BEFORE WIREFRAME |
| 7 | Handling of 204 truncated-telemetry batches | BEFORE IMPLEMENTATION |

### UI Must NOT Claim
- Agricultural thresholds without domain evidence.
- Retrospective data as predictive evidence.
- Specific unvalidated actions.
- False precision (invented %, dates).
- Proven loss reduction without evaluation.
- Real-time streaming.

---

## 3. UX Research Questions (PUX-02)

14 groups, 40+ questions. Key blocking questions by owner:

**PRODUCT (Alisa):**
- Who is primary operator at T_dispatch? (dispatcher / warehouse manager / exec)
- What decisions can operator take? (upgrade reefer / reroute / discount / re-cool)
- Which batch anchors the demo story?
- Is mobile view required or desktop sufficient?

**DATA (Viktor):**
- Exact definition of `RiskEstimate.score`.
- Validated cut-offs for `RiskBand`.
- `DeteriorationHorizon.starts_at` semantics.
- Factor codes, categories, evidence formats.
- Reliability degradation rules for missing telemetry.

**TECH (Igor / Vladimir):**
- `GET /api/v1/batches` contract, query params, pagination.
- `GET /api/v1/batches/{id}/assessment` contract.
- Transition milestone `fixture` → `deterministic_baseline`.

---

## 4. UX Pattern Research (PUX-03)

Sources: Samsara, Sensitech, Controlant, Afresh, FourKites.

### Adopted Patterns
1. Urgency-first master table (exception triage).
2. Master-Detail split view.
3. Semantic risk badges: color + text + icon (WCAG AA).
4. Structured root-cause callout linked to evidence codes.
5. Prescriptive action card with human-review banner.
6. Data quality / reliability strip.
7. Relative urgency countdown + absolute timestamp.
8. Stateless demo scenario switcher.

### Avoided Patterns
- GIS map as primary view.
- Raw telemetry dumps in operational view.
- Blinking "live" indicators (contradicts batch architecture).
- False-precision radial gauges.
- Intrusive blocking modals.

---

## 5. Operator Flow (PUX-04)

### Architecture: Master-Detail Single Screen
- **Left:** Batch Triage Queue → "Which batches are most at risk?"
- **Right:** Assessment Detail → risk + horizon + factors + action.

### Primary Flow
| Step | User Question | Currently Supported? |
|---|---|---|
| 1. Scan triage queue | Which batches at risk? | **NO** (no batch list endpoint) |
| 2. Inspect risk & horizon | How severe? When? | **PARTIAL** (contract exists, fixture returns null) |
| 3. Read contributing factors | Why at risk? | **PARTIAL** (component exists, placeholder only) |
| 4. Evaluate action | What to do? | **NO** (no action engine, no buttons) |

### Failure Flows
| Flow | Trigger | Currently Supported? |
|---|---|---|
| F1 Loading | API pending | **YES** |
| F2 Backend unavailable | Network / service down | **YES** |
| F3 Insufficient data | Missing validated inputs | **YES** |
| F4 Truncated telemetry | 204 batches, 2026 gap | **NO** |
| F5 Analytics not configured | `analytics: "not_configured"` | **PARTIAL** |
| F6 No high-risk batches | All low | **NO** |
| F7 Single-batch API failure | HTTP 500 on detail | **NO** |

### Minimum Demo Flow
Open → summary bar → click top high-risk batch → risk + horizon → factors → action → switch to insufficient-data batch → show honest fallback → wrap-up.

---

## 6. Wireframe Specification (PUX-05)

### Minimum Viable Screen Set
**One screen**, Master-Detail:
- Global nav + summary bar (`[TOTAL BATCHES]`, `[HIGH RISK COUNT]`, `[CLEARED COUNT]`).
- Left: Batch Triage Queue (sorted by urgency, risk band badge, crop, destination).
- Right top: Risk Severity & Deterioration Horizon (`[RISK INDICATOR]`, `[DETERIORATION HORIZON]`, `[RELIABILITY LEVEL]`).
- Right middle: Contributing Factors (`[CONTRIBUTING FACTORS LIST]`, grouped by category).
- Right bottom: Prioritized Action (`[PRIORITIZED ACTION CALLOUT]`, priority badge, human-review notice, action button).
- Footer: provenance strip (engine version, simulation banner).

### States per section
Every section specifies: EMPTY / LOADING / ERROR / INSUFFICIENT-DATA / UNCERTAINTY.

### Cut list if time-limited
Remove: multi-facility dropdown, telemetry charts, search/filters.  
**Keep at all costs:** Master-Detail layout, 4 core outputs, insufficient_data + backend failure states.

---

## 7. Demo Story (PUX-06)

### Currently Demonstrable (today)
- App shell + health badge.
- Truthful `insufficient_data` card (no fake numbers).
- Backend failure → error panel → retry recovery.

### Target Demo (after analytics integration)
DATA → PROBLEM DETECTED → PRIORITIZED BATCH → WHY → WHEN → ACTION → OPERATOR BENEFIT.

### Core Demo Flow (3 min)
| Time | Moment |
|---|---|
| 0:00–0:30 | Situational awareness: summary bar, triage queue |
| 0:30–1:15 | Click top high-risk batch |
| 1:15–1:50 | Timing + explainability (horizon vs transit, factors) |
| 1:50–2:30 | Prescriptive intervention + human sign-off |
| 2:30–3:00 | Summary & judge wrap-up |

### Failure-Safe Demo Flow
Intentionally show insufficient-data batch → system refuses to guess → flags missing requirements → advises manual inspection → trustworthiness narrative.

### Presenter Must NOT Claim
- "Reduces losses by X%" without evaluation evidence.
- "Predicts exact firmness on arrival."
- "Monitors trucks live in transit."
- "Saved €X on this batch."

---

## 8. QA Plan (PUX-07)

### A. Current Foundation Tests (executable now)
| ID | Case | Key check |
|---|---|---|
| TC-F01 | Initial loading | Spinner → content, no white flash |
| TC-F02 | Slow backend (3G) | No premature timeout |
| TC-F03 | Backend unavailable | Error card + Try again |
| TC-F04 | Retry recovery | Unavailable → Available via button |
| TC-F05 | Rapid click spam | AbortController, no race conditions |
| TC-F06 | Insufficient-data contract | No numeric risk, no fake dates |
| TC-F07 | Null optional fields | No "null"/"undefined" text |
| TC-F08 | Long copy wrapping | No horizontal overflow |
| TC-F09 | Responsive 375px / 768px | Single-column, no scroll |
| TC-F10 | Keyboard nav + focus | Visible focus ring, Enter activates |

### B. Future Analytics UI Tests (FUTURE CONTRACT REQUIRED)
TC-A01…A06: multi-batch list, assessed state, recommendation, truncated telemetry degradation, colour-independent severity, jargon-free copy.

### Risk Audit
- **Demo-critical:** API freeze, master-detail sync, demo switcher.
- **Regression:** breaking Pydantic invariant in UI, Vite proxy in prod build.
- **Accessibility:** color-only encoding, missing aria-live.
- **False-precision:** spurious decimals, fabricated countdowns.
- **Misleading UI:** retrospective leakage, fake streaming indicators.

### 60-Second Pre-Demo Smoke Check
1. `GET /api/v1/health` → `status: "ok"`.
2. Fresh incognito → page loads, "Connected".
3. High-risk batch: risk badge + horizon + 2 factors + action.
4. Switch to insufficient-data scenario → numbers hidden, banner shown.
5. Zoom 100%, 1920×1080 → no horizontal scroll.

---

## 9. Blockers & Dependencies

### BLOCKED BY DATA (Viktor)
- Risk score definition & band thresholds.
- Deterioration horizon semantics & crop coverage.
- Factor dictionary (codes, categories, summaries).
- Reliability degradation rules (truncated telemetry).
- Batch ranking / sort field.

### BLOCKED BY PRODUCT (Alisa)
- Operator persona & decision context.
- Validated operational action catalog.
- Demo anchor batch & narrative.
- Mobile requirement (yes/no).

### BLOCKED BY TECH (Igor / Vladimir)
- `GET /api/v1/batches` contract (filters, pagination).
- `GET /api/v1/batches/{id}/assessment` contract.
- Engine tier transition: `fixture` → `deterministic_baseline`.

---

## 10. Next Steps

1. **Viktor:** answer Data-to-UX contract questions (sent separately).
2. **Alisa:** confirm persona, action catalog, demo narrative.
3. **Vladimir:** freeze integration contract for batch list + detail endpoints.
4. **prscr:** run PUX-08 (Data → UX reconciliation) after Data evidence arrives.
5. **Vladimir:** issue implementation contract with explicit write scope → frontend code.
6. **prscr:** execute QA plan (TC-F01…F10 now, TC-A01…A06 after implementation).

---

## 11. What Was NOT Done (by design)

- No code modified.
- No dependencies added.
- No API changes.
- No agricultural rules invented.
- No risk formulas proposed.
- No dataset fields fabricated.
- No merge / release actions.