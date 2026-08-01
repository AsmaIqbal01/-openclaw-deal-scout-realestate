# Implementation Plan: PK Lead Intake, Classification & WhatsApp Notification

**Branch**: `001-pk-lead-intake-notify` | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-pk-lead-intake-notify/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Deliver the core PK value loop: read Zameen/OLX Gmail alerts and
WhatsApp-forwarded leads, classify them with Gemini 2.5 Flash, and either
auto-dispatch (score ≥ 0.9: HubSpot write + WhatsApp notification), hold for
owner review (0.70–0.89), or reject (< 0.5) — while never exceeding the
18/day Gemini quota and never leaking data across tenants. Research (see
`research.md`) established that no new agent-logic code is required: the
Orchestrator, Intake, and Delivery behavior is already fully specified by
existing `agents/*/SOUL.md` and PK skill files, cross-checked line-by-line
against every functional requirement in `spec.md`. The engineering work for
this feature is per-tenant configuration plus a fixture-based `pytest` suite
that proves the spec's functional requirements and success criteria without
spending live Gemini quota or making live external calls.

## Technical Context

**Language/Version**: No new agent-logic language — agent behavior is
Markdown (`SOUL.md`/skill files) interpreted natively by the OpenClaw
runtime. Test suite: Python 3.11+.
**Primary Dependencies**: OpenClaw runtime; ClawHub skills
`agent-rate-limiter`, `agent-memory`, `honcho-setup`, `agentmail-integration`
(per `workspace/TOOLS.md`); `pytest` for the test suite.
**Storage**: `MEMORY.md` (flat-file spine) and per-tenant `USER.md` files —
no database introduced.
**Testing**: `pytest`, fixture-based — no live Gmail/Gemini/HubSpot/WhatsApp
calls (see `research.md` Decision 2).
**Target Platform**: Linux server (existing systemd timer host, per
`workspace/HEARTBEAT.md`).
**Project Type**: Single project — no frontend/backend split; dashboard work
is out of scope for this feature (no Success Criteria reference it).
**Performance Goals**: End-to-end within one 15-minute heartbeat cycle
(SC-001); within `workspace/HEARTBEAT.md`'s per-run scope limits (≤20 Gmail
messages, ≤10 WhatsApp messages, ≤5 Gemini calls per tenant per run).
**Constraints**: Zero paid infrastructure (Constitution Principle II); ≤18
Gemini calls/day/tenant (Principle VI); WhatsApp-only PK notifications
(Principle III).
**Scale/Scope**: Single-tenant through the Phase 1 validation target of 3 PK
agencies (Constitution Principle I).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| I. PK-First Market Sequencing | ✅ PASS | Feature is PK-only; `market_mode` fixed per session; no UK logic touched |
| II. Zero Infrastructure Cost | ✅ PASS | Uses only free-tier Gemini/HubSpot/Gmail/WhatsApp/OpenClaw built-ins; `pytest` is free/open-source |
| III. Market-Native Channel Fidelity | ✅ PASS | FR-005/FR-006 use WhatsApp only for PK notifications; no email or Discord fallback introduced |
| IV. OpenClaw as Sole Runtime Orchestrator | ✅ PASS | No new orchestration layer introduced; Orchestrator remains OpenClaw (research.md Decision 1 explicitly rejects a custom backend service for this reason) |
| V. Maker/Checker Separation | ✅ PASS | FR-004 keeps Intake (Maker) producing JSON only and Delivery (Checker) validating before acting |
| VI. Gemini Quota Guard | ✅ PASS | FR-009 implements the 18/day halt exactly |
| VII. Human Approval Gate for Client-Facing Communication | N/A | This feature has no client-facing email path (SC-003 confirms none is introduced); gate applies to `operator-approval-gate.md`, out of scope here |
| VIII. Multi-Tenant Data Isolation | ✅ PASS | FR-010 enforces `tenant_id` verification before every CRM write, notification, or `MEMORY.md` update |
| IX. Spec Quality Gate — 9.6/10 Minimum | ✅ PASS | `spec.md` scored 9.8/10 against the spec-scorer rubric before this plan began |

No violations. Complexity Tracking table is empty — no principle-violating
complexity was introduced.

**Post-Phase 1 re-check**: unchanged — `data-model.md`, `contracts/`, and
`quickstart.md` introduce no new services, no new orchestration layer, no
paid infrastructure, and no channel other than WhatsApp for PK. All rows
above still hold after design.

## Project Structure

### Documentation (this feature)

```text
specs/001-pk-lead-intake-notify/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/            # Phase 1 output
│   ├── lead-schema.json
│   └── approval-commands.md
├── checklists/
│   └── requirements.md
└── tasks.md              # Phase 2 output (/sp.tasks command — NOT created by /sp.plan)
```

### Source Code (repository root)

```text
agents/
├── orchestrator/SOUL.md      # existing — no changes required
├── intake/SOUL.md            # existing — no changes required
└── delivery/SOUL.md          # existing — no changes required

skills/
├── zameen-parser.md          # existing — no changes required
├── pk-whatsapp-lead.md       # existing — no changes required
├── lead-classifier-pk.md     # existing — no changes required
└── multi-tenant-router.md    # existing — no changes required

workspace/
└── tenants/{tenant_id}/       # new per-tenant runtime state (USER.md, created
                                # per quickstart.md; MEMORY.md entries keyed by
                                # tenant_id per multi-tenant-router.md)

tests/
├── contract/
│   ├── test_lead_schema.py        # validates lead-schema.json (FR-004)
│   └── test_approval_commands.py  # validates approval-commands.md (FR-006/007/008)
└── integration/
    ├── test_us1_auto_dispatch.py  # User Story 1 fixtures
    ├── test_us2_human_review.py   # User Story 2 fixtures
    └── test_us3_quota_guard.py    # User Story 3 fixtures
```

**Structure Decision**: Single project. No new `src/` or `backend/` code —
per `research.md` Decision 1, the existing `agents/*/SOUL.md` and PK
`skills/*.md` files already fully satisfy every functional requirement and
are the implementation, interpreted by the OpenClaw runtime. All new work
for this feature lives under `tests/contract/` and `tests/integration/`
(fixture-based `pytest`, per Decision 2) plus per-tenant configuration under
`workspace/tenants/{tenant_id}/`. `backend/` and `dashboard/` remain
untouched — dashboard integration is out of scope for this feature (see
Technical Context, Project Type).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — table intentionally left empty.
