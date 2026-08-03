# Implementation Plan: PK Email Draft & Operator Approval Gate

**Branch**: `003-pk-email-approval-gate` | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-pk-email-approval-gate/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Give agents a drafted follow-up email for every dispatched lead with a
known contact email, queued for their explicit WhatsApp approval before
anything is sent — the first feature to actually exercise Constitution
Principle VII. Like feature 001 and unlike feature 002, this is Delivery
Sub-Agent behavior already described in `skills/operator-approval-gate.md`
and `agents/delivery/SOUL.md` Step 4 — no new agent-logic code is needed
(`research.md` Decision 1). During planning, backfilled two retry-semantics
requirements the spec added (via its own rigorous rescore, see PHR 0019)
into `skills/operator-approval-gate.md`'s Error Handling section, so the
source-of-truth skill file doesn't silently lag the spec (`research.md`
Decision 2).

## Technical Context

**Language/Version**: No new agent-logic language — OpenClaw runtime
interprets `agents/delivery/SOUL.md` and `skills/operator-approval-gate.md`
directly; test suite: Python 3.11+ with pytest, extending
`tests/pipeline_sim.py`.
**Primary Dependencies**: the existing `brevo` ClawHub skill for email
sending (`workspace/TOOLS.md`); no new dependencies.
**Storage**: `workspace/tenants/{tenant_id}/approval-queue.json`
(append-only), written by existing Delivery Sub-Agent behavior — simulated
in-memory in tests, not real file I/O.
**Testing**: `pytest`, extending `tests/pipeline_sim.py` with
draft/queue/approve/reject/stale-guard decision functions — fixture-based,
zero live WhatsApp/email calls.
**Target Platform**: same Linux host as the existing pipeline.
**Project Type**: single project — no new `src/`, no new server component.
**Performance Goals**: draft queued and WhatsApp alert sent within the same
heartbeat run as the triggering CRM write (SC-002).
**Constraints**: zero paid infrastructure (Brevo free tier); WhatsApp
remains the sole PK notification channel (Principle III); max 50 queue
entries per tenant (FR-006); email never sent while `approved` is `false`
(FR-008).
**Scale/Scope**: single-tenant through the Phase 1 validation target of 3
PK agencies, same as features 001 and 002.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| I. PK-First Market Sequencing | ✅ PASS | PK-mode template only; UK template explicitly deferred |
| II. Zero Infrastructure Cost | ✅ PASS | Brevo free tier, an existing named ClawHub skill — no new paid tool |
| III. Market-Native Channel Fidelity | ✅ PASS | Draft-alerts and re-notifications are WhatsApp-only; the email itself is the approved deliverable, not a notification channel |
| IV. OpenClaw as Sole Runtime Orchestrator | ✅ PASS | No new orchestration; entirely within Delivery Sub-Agent's existing Step 4 role |
| V. Maker/Checker Separation | ✅ PASS | Runs only after Delivery's own CRM-write step already succeeded; Intake is untouched |
| VI. Gemini Quota Guard | N/A | No Gemini calls in this feature |
| VII. Human Approval Gate for Client-Facing Communication | ✅ PASS | This is the feature that implements the gate — FR-008/009/010 enforce it directly |
| VIII. Multi-Tenant Data Isolation | ✅ PASS | FR-011 and the cross-tenant edge case explicitly reject replies naming another tenant's `queue_id` |
| IX. Spec Quality Gate — 9.6/10 Minimum | ✅ PASS | `spec.md` scored 10.0/10 under rigorous re-audit (PHR 0019) before this plan began |

No violations. Complexity Tracking table is empty.

**Post-Phase 1 re-check**: unchanged — `data-model.md` and `contracts/`
introduce no new orchestration, no paid infrastructure beyond the
already-approved Brevo skill, and no channel other than WhatsApp for
PK notifications.

## Project Structure

### Documentation (this feature)

```text
specs/003-pk-email-approval-gate/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/            # Phase 1 output
│   ├── approval-queue-schema.json
│   └── email-approval-commands.md
├── checklists/
│   └── requirements.md
└── tasks.md              # Phase 2 output (/sp.tasks command — NOT created by /sp.plan)
```

### Source Code (repository root)

```text
agents/
└── delivery/SOUL.md          # existing — no changes required

skills/
└── operator-approval-gate.md # existing — Error Handling section extended
                               # during this plan's research phase (2 new
                               # retry rules, backfilled to match spec.md)

tests/
├── pipeline_sim.py           # existing (feature 001) — extended with
│                              # draft/queue/approve/reject/stale-guard
│                              # decision functions
├── fixtures/
│   └── email_approval/       # new: fixture leads, queue entries, WhatsApp
│                              # reply payloads, Brevo send outcomes
└── integration/
    ├── test_us1_email_draft_queued.py
    ├── test_us2_email_approval_reply.py
    └── test_us3_stale_draft_guard.py
```

**Structure Decision**: Single project. No new `src/` or server code — per
`research.md` Decision 1, this feature's behavior already lives in
`skills/operator-approval-gate.md` and `agents/delivery/SOUL.md`, extended
in place (Decision 2) rather than duplicated. All new work is test
functions added to the existing `tests/pipeline_sim.py` plus new fixture
data — matching feature 001's pattern, not feature 002's.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — table intentionally left empty.
