# Implementation Plan: PK Dashboard Email Draft Queue Extension

**Branch**: `004-pk-dashboard-email-queue` | **Date**: 2026-08-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-pk-dashboard-email-queue/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Extend the existing client dashboard (feature 002) to display feature
003's email draft queue read-only, in a new "Email Draft Queue" section
distinct from the existing Tier-2-lead Approval Queue. Like feature 002,
this is genuine new production code (`research.md` Decision 1: extends
`dashboard/server.py` and the vanilla frontend, not agent-logic markdown).
The server-side enrichment pattern feature 002 already established
(`_enrich()`, adding `tier_color`/`seconds_remaining` without touching the
on-disk schema) is extended the same way for status labels and reminder/
archive countdowns (`research.md` Decision 2). Planning initially flagged
an apparent conflict with feature 002's frontend action-guard test (which
bans the substring "reject") over displaying a "Rejected" status — on
closer inspection this doesn't actually arise: Decision 2's server-side
status derivation means `dashboard.js` never needs to hardcode that word
(`research.md` Decision 3). No guard-test change is needed.

## Technical Context

**Language/Version**: Python 3.11+ (standard library only) for
`dashboard/server.py`; vanilla HTML/CSS/JavaScript (ES6, no framework, no
build step) for the frontend — same stack as feature 002, no new
dependencies.
**Primary Dependencies**: Python standard library (`http.server`, `json`)
only. No charting library needed for this feature (Chart.js remains
feature 002's, for the unrelated Score Radar — untouched here).
**Storage**: `workspace/tenants/{tenant_id}/approval-queue.json` (feature
003, append-only) — read-only from this feature, a new read path added to
`dashboard/server.py`. `dashboard-state.json` (feature 002) is unchanged;
its schema is not modified.
**Testing**: `pytest`, calling `dashboard/server.py`'s request-handling
functions directly against fixture files (feature 002's Decision 2
pattern — no live socket needed for the primary suite), plus a refined
version of the existing frontend action guard. Frontend rendering
(`dashboard.js`) verified manually per `quickstart.md`, matching feature
002's precedent.
**Target Platform**: same Linux host, port 18790, same already-provisioned
Cloudflare Tunnel.
**Project Type**: single project — extends the existing `dashboard/`
component in place; no new component.
**Performance Goals**: the Email Draft Queue reflects `approval-queue.json`
within the same existing 30-second poll cycle (unchanged cadence, feature
002).
**Constraints**: zero paid infrastructure; strictly read-only with respect
to `approval-queue.json` (spec.md FR-006); WhatsApp remains the sole
`/approve`/`/reject` channel — no action control of any kind in the UI
(FR-005, Constitution Principle VII); zero cross-tenant reads (FR-007,
Principle VIII); no new endpoint or request type (FR-011).
**Scale/Scope**: same Phase 1 validation target of 3 PK agencies; display
capped at the 10 most recently queued entries (FR-010), though the
underlying file can hold up to 50 (feature 003 FR-006).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| I. PK-First Market Sequencing | ✅ PASS | Reads PK-tenant `approval-queue.json` only; no UK-mode logic introduced |
| II. Zero Infrastructure Cost | ✅ PASS | Python stdlib only; no new dependency, no paid service |
| III. Market-Native Channel Fidelity | ✅ PASS | No new notification channel introduced; pure read/render, same as feature 002 |
| IV. OpenClaw as Sole Runtime Orchestrator | ✅ PASS | `dashboard/server.py` remains a passive read/render layer — no writes, no pipeline decisions |
| V. Maker/Checker Separation | N/A | No lead classification or delivery action performed by this feature |
| VI. Gemini Quota Guard | N/A | No Gemini calls |
| VII. Human Approval Gate for Client-Facing Communication | ✅ PASS | FR-005/FR-006 directly enforce the gate stays intact: read-only display, WhatsApp remains the sole resolution channel, no approve/reject control ever rendered — feature 002's existing frontend guard test already covers this and needs no change (`research.md` Decision 3) |
| VIII. Multi-Tenant Data Isolation | ✅ PASS | FR-007 extends feature 002's existing per-tenant scoping to the new data source; tested by User Story 3 |
| IX. Spec Quality Gate — 9.6/10 Minimum | ✅ PASS | `spec.md` scored 10.0/10 under a rigorous audit (PHR 0025) before this plan began |

No violations. Complexity Tracking table is empty.

**Post-Phase 1 re-check**: unchanged — `data-model.md` and `contracts/`
introduce no writes, no new orchestration, no paid infrastructure, and no
notification channel. The server remains strictly read/render, and feature
002's existing frontend action-guard test already covers the new section
without modification (Decision 3).

## Project Structure

### Documentation (this feature)

```text
specs/004-pk-dashboard-email-queue/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/            # Phase 1 output
│   └── email-draft-queue-response.md
├── checklists/
│   └── requirements.md
└── tasks.md              # Phase 2 output (/sp.tasks command — NOT created by /sp.plan)
```

### Source Code (repository root)

```text
dashboard/
├── index.html            # add Section 9: Email Draft Queue card, after
│                          # the existing Approval Queue section
├── dashboard.css          # add status-label badge styles (Pending / Sent /
│                          # Send Failed / Rejected / Auto-Archived)
├── dashboard.js           # render email_draft_queue data on each existing
│                          # 30s poll — no new poll/timer introduced
└── server.py               # extend: load_email_draft_queue(), status-label
                             # derivation, reminder/archive countdowns,
                             # merged into handle_state_request's "ok"
                             # response (existing function, extended)

tests/
├── contract/
│   └── test_email_draft_queue_response.py   # validates the enrichment
│                                              # wrapper shape; reuses
│                                              # feature 003's
│                                              # approval-queue-schema.json
│                                              # for the base entry shape
│                                              # (not duplicated)
├── integration/
│   ├── test_us1_email_draft_queue_pending.py
│   ├── test_us2_email_draft_queue_history.py
│   └── test_us3_email_draft_queue_isolation.py
│   # test_no_approval_actions_in_frontend.py (feature 002) needs no
│   # change — see research.md Decision 3
└── fixtures/
    └── dashboard/          # extend existing fixture dir with
                             # approval-queue.json variants: pending,
                             # mixed-status, malformed, missing
```

**Structure Decision**: Single project. Extends the existing `dashboard/`
component in place — no new component or directory, consistent with this
being an additive extension of feature 002 rather than a new subsystem.
`agents/*/SOUL.md` and `skills/*.md` remain unchanged: this feature reads
feature 003's already-produced `approval-queue.json`, it does not change
how or when that file is written. Tests extend the existing `tests/` suite
from features 001-003.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — table intentionally left empty.
