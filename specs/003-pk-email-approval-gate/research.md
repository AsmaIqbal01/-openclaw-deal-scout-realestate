# Research: PK Email Draft & Operator Approval Gate

## Context

Unlike feature 002 (a genuinely new deterministic web server), this feature
is much closer to feature 001 in nature: the draft/queue/notify/approve/
reject/stale-guard flow is Delivery Sub-Agent behavior, already described
in `skills/operator-approval-gate.md` and `agents/delivery/SOUL.md` Step 4
("Email Queue (if applicable)"). It is LLM-interpreted markdown, not
callable production code.

## Decision 1: No new agent-logic code

**Decision**: No new agent-logic code is needed. The engineering work is a
test-only simulation, extending `tests/pipeline_sim.py` (feature 001's
pattern, formalized in ADR-002) with the email-draft-approval decision
rules — fixture-based `pytest`, zero live WhatsApp/email calls, zero real
`approval-queue.json` file I/O (since there is no new production code
touching real files here, unlike feature 002's `dashboard/server.py`).

**Rationale**: every functional requirement in `spec.md` is already
satisfied by `skills/operator-approval-gate.md`'s templates, queue schema,
stale-queue guard, and error handling (after the Decision 2 backfill
below), plus `agents/delivery/SOUL.md`'s Step 4. Writing new agent-logic
content would duplicate what already exists, exactly the risk ADR-002
identified for feature 001.

**Alternatives considered**:
- *Build a real queue-processing service (like feature 002's server.py)*:
  rejected — this flow has no HTTP/web surface; it is pure WhatsApp-reply-
  and-file-append behavior already fully describable as OpenClaw agent
  instructions, unlike the dashboard's genuinely new deterministic
  read/render requirement.

## Decision 2: Backfill the skill file's retry semantics

**Decision**: the rigorous spec-scoring pass (see PHR 0019) added two
requirements — FR-007 (WhatsApp-send retry-then-continue) and FR-009
(email-send retry-then-alert) — that were not originally present in
`skills/operator-approval-gate.md`'s Error Handling section. Rather than
let the spec state behavior the source skill file is silent on (the exact
class of drift ADR-002 exists to prevent), extended
`skills/operator-approval-gate.md`'s Error Handling section now, during
planning, with both retry rules, cross-referencing the equivalent patterns
already established in `agents/delivery/SOUL.md` (WhatsApp-send retry,
HubSpot-write retry).

**Rationale**: a future reader of `operator-approval-gate.md` (the actual
agent instruction file) should see the same retry behavior the spec now
mandates, without needing to cross-reference `specs/003-.../spec.md` to
discover it.

**Alternatives considered**:
- *Leave the skill file as-is, treat the retry semantics as spec-only
  detail*: rejected — this is precisely the "two files silently disagree"
  pattern that caused feature 001's `/sp.analyze` finding I1 (except here
  it would be a silent *omission* rather than a *contradiction*, still
  worth closing at the source).

## Decision 3: Email-send mechanism

**Decision**: use the existing `brevo` ClawHub skill
(`workspace/TOOLS.md`: "brevo # Email send fallback") for the actual
outgoing email send in FR-009. No new email-sending tool or paid service is
introduced.

**Rationale**: `workspace/TOOLS.md`'s Tool Priority Rule ("Always use
existing ClawHub skill before building custom") already names this exact
tool for this exact purpose; Brevo's free tier keeps this within
Constitution Principle II (zero infrastructure cost).

**Alternatives considered**:
- *A new/different transactional email provider*: rejected — no reason to
  introduce a second tool when one is already named for this purpose and
  not yet used by any other feature.

## Resolved Technical Context

- **Language/Version**: No new agent-logic language — OpenClaw runtime
  interprets `agents/delivery/SOUL.md` and `skills/operator-approval-gate.md`
  (extended per Decision 2) directly; test suite: Python 3.11+ with pytest,
  extending `tests/pipeline_sim.py`.
- **Primary Dependencies**: the existing `brevo` ClawHub skill for email
  sending (Decision 3); no new dependencies.
- **Storage**: `workspace/tenants/{tenant_id}/approval-queue.json`
  (append-only array), written by existing Delivery Sub-Agent behavior —
  simulated in-memory in tests, not real file I/O, consistent with feature
  001's pattern.
- **Testing**: `pytest`, extending `tests/pipeline_sim.py` with
  draft/queue/approve/reject/stale-guard decision functions — fixture-based,
  zero live WhatsApp/email calls.
- **Target Platform**: same Linux host as the existing pipeline.
- **Project Type**: single project — no new `src/`, no new `dashboard/`-style
  component.
- **Performance Goals**: draft queued and WhatsApp alert sent within the
  same heartbeat run as the triggering CRM write (SC-002); approval/rejection
  processed on the run following the owner's reply.
- **Constraints**: zero paid infrastructure (Brevo free tier); WhatsApp
  remains the sole PK notification channel for draft-alerts and
  re-notifications (Constitution Principle III); max 50 queue entries per
  tenant (FR-006); email never sent while `approved` is `false` (FR-008).
- **Scale/Scope**: single-tenant through the Phase 1 validation target of 3
  PK agencies, same as features 001 and 002.
