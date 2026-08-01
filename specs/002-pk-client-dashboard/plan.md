# Implementation Plan: PK Client Dashboard — Pipeline Visibility & Read-Only Approval Queue

**Branch**: `002-pk-client-dashboard` | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-pk-client-dashboard/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Give PK agencies a client-accessible, per-tenant dashboard showing pipeline
status, lead counts, Gemini quota usage, CRM sync status, recent leads with
a Score Radar explanation, and a read-only view of leads currently awaiting
a WhatsApp confirm/discard reply. Unlike feature 001, this requires genuine
new production code (research.md Decision 1): the dashboard is deterministic
"vanilla HTML/JS" web tooling, not LLM-interpreted agent behavior. The
Dashboard State document it reads is already written by existing
Orchestrator behavior; this feature builds the read/render side only — a
minimal Python-stdlib server plus a vanilla HTML/CSS/JS frontend, with no
approve/reject action (deferred, per spec.md's Scope Decision, until the
email-draft-approval feature exists).

## Technical Context

**Language/Version**: Python 3.11+ (standard library only) for the server;
vanilla HTML/CSS/JavaScript (ES6, no framework, no build step) for the
frontend, per `skills/remote-dashboard.md`.
**Primary Dependencies**: Python standard library (`http.server`, `json`)
only for the server; Chart.js (already mandated by `skills/remote-dashboard.md`
Section 8) for the Score Radar chart — no new dependency decisions made
here beyond what the skill file already specifies.
**Storage**: `workspace/tenants/{tenant_id}/dashboard-state.json`, written
by existing Orchestrator behavior — read-only from this feature.
**Testing**: `pytest`, calling the server's request-handling functions
directly against fixture `dashboard-state.json` files — no live socket
required for the primary suite (research.md Decision 2).
**Target Platform**: same Linux host as the pipeline, port 18790, exposed
via the already-provisioned Cloudflare Tunnel (provisioning out of scope).
**Project Type**: single project — adds a `dashboard/` static-file +
minimal-server component; no frontend framework/build split.
**Performance Goals**: dashboard reflects state within one 30-second poll
cycle, per `skills/remote-dashboard.md`.
**Constraints**: zero paid infrastructure; strictly read-only with respect
to the pipeline (no writes, no notifications, no lead processing —
Constitution Principle IV); WhatsApp remains the sole PK approval channel
(Principle III) — Approval Queue section is view-only.
**Scale/Scope**: single-tenant through the Phase 1 validation target of 3
PK agencies, same as feature 001.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| I. PK-First Market Sequencing | ✅ PASS | Feature verifies PK-tenant data only; schema is market-agnostic but no UK verification performed here |
| II. Zero Infrastructure Cost | ✅ PASS | Python stdlib + Chart.js (open-source); no paid hosting/API introduced |
| III. Market-Native Channel Fidelity | ✅ PASS | Dashboard introduces no notification channel of its own; Approval Queue is view-only, WhatsApp remains the sole confirm/discard channel |
| IV. OpenClaw as Sole Runtime Orchestrator | ✅ PASS | `dashboard/server.py` is a passive read/render layer — no writes, no pipeline decisions, never a second orchestrator |
| V. Maker/Checker Separation | N/A | This feature performs no lead classification or delivery action |
| VI. Gemini Quota Guard | N/A | This feature makes no Gemini calls; it only displays a quota number already computed elsewhere |
| VII. Human Approval Gate for Client-Facing Communication | N/A | No email-send path introduced (spec.md Scope Decision explicitly defers this) |
| VIII. Multi-Tenant Data Isolation | ✅ PASS | FR-011/012/014 and `contracts/dashboard-api.md`'s isolation guarantee: server only ever reads the exact requested `tenant_id`'s file |
| IX. Spec Quality Gate — 9.6/10 Minimum | ✅ PASS | `spec.md` scored 9.8/10 before this plan began |

No violations. Complexity Tracking table is empty.

**Post-Phase 1 re-check**: unchanged — `data-model.md` and `contracts/`
introduce no writes, no new orchestration, no paid infrastructure, and no
notification channel. The server remains strictly read/render.

## Project Structure

### Documentation (this feature)

```text
specs/002-pk-client-dashboard/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/            # Phase 1 output
│   ├── dashboard-state-schema.json
│   └── dashboard-api.md
├── checklists/
│   └── requirements.md
└── tasks.md              # Phase 2 output (/sp.tasks command — NOT created by /sp.plan)
```

### Source Code (repository root)

```text
dashboard/
├── index.html            # dashboard shell: sections 1,2,3,5,6,7 + read-only section 4
├── dashboard.css          # vanilla CSS, no framework
├── dashboard.js           # fetch /state every 30s, render sections, tenant selector
├── radar.js               # Chart.js Score Radar rendering (Section 8)
└── server.py              # Python stdlib HTTP server: static files + GET /state

tests/
├── contract/
│   └── test_dashboard_state_schema.py   # validates dashboard-state-schema.json (FR-002)
├── integration/
│   ├── test_us1_pipeline_status.py      # User Story 1 fixtures
│   ├── test_us2_score_radar.py          # User Story 2 fixtures
│   ├── test_us3_approval_queue_visibility.py  # User Story 3 fixtures
│   └── test_dashboard_tenant_isolation.py     # FR-011/012/014
└── fixtures/
    └── dashboard/         # normal, missing, unknown-tenant dashboard-state.json variants
```

**Structure Decision**: Single project. New `dashboard/` directory holds the
static frontend and the minimal Python-stdlib server (research.md Decision
2/3) — the only genuinely new production code this project has needed so
far, since the dashboard is deterministic web tooling rather than
LLM-interpreted agent behavior. `agents/*/SOUL.md` and `skills/*.md` remain
unchanged; the Dashboard State document they already write is this
feature's sole input. Tests extend the existing `tests/` suite from feature
001 with a `tests/fixtures/dashboard/` fixture set.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — table intentionally left empty.
