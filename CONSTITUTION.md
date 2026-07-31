# CONSTITUTION.md — Deal Scout Real Estate

**Version**: 1.0.0 | **Ratified**: 2026-08-01 | **Last Amended**: 2026-08-01

This is the master governing document for Deal Scout — Real Estate Edition. It
synthesizes and supersedes the individual workspace and agent files
(`workspace/IDENTITY.md`, `workspace/AGENTS.md`, `workspace/HEARTBEAT.md`,
`workspace/TOOLS.md`, `agents/*/SOUL.md`, `agents/spec-scorer/spec-scorer.md`,
`agents/constitution-checker/constitution-checker.md`) into one enforceable
reference. Where those files conflict with this document, this document
governs; the conflicting file MUST be corrected in the same change that
introduces the conflict.

> **Note on reconstruction**: this document was assembled after the authoring
> instruction was interrupted mid-paste. The Phase 1, Phase 3, and Phase 4
> gates and the A1–A8 architecture gates below are taken verbatim from what
> was pasted (cross-checked against `agents/constitution-checker/
> constitution-checker.md`, which defines A1–A7; A8 is a new gate added here
> per the pasted instruction). The **Phase 2 gate is inferred**, not sourced
> from the original instruction — see the flag in Section 2 — and requires
> owner confirmation or correction before Phase 2 work begins.

---

## 1. Identity & Mission

**Product**: Deal Scout — Real Estate Edition. *"The AI employee that never
misses a property lead."*

An autonomous AI pipeline that monitors a real estate agent's Gmail and
WhatsApp, identifies property leads using Gemini 2.5 Flash, logs them to
HubSpot CRM, and notifies the agent instantly, with zero manual effort.

**What this product is not**: not a property portal or listing aggregator; not
a CRM replacement (it feeds the CRM); not a conversational chatbot; not a
scraper (all data comes from authorised inboxes).

**Mission** (Orchestrator): ensure every inbound property lead from a client's
Gmail or WhatsApp is (1) classified by the Intake Sub-Agent, (2) validated and
delivered by the Delivery Sub-Agent, (3) logged to CRM and state before any
notification is sent, and (4) never duplicated, never sent without operator
approval for emails.

## 2. Market Phases & Gates

Sequencing is strict: each phase gate MUST be met before the next phase's work
begins. `market_mode` ("PK" or "UK") is fixed per tenant session and read once
from `USER.md`; a single pipeline run MUST NOT mix PK and UK logic.

- **Phase 1 gate (PK Validation)**: 3 Pakistani agencies confirmed — defined as
  having received at least one delivered lead notification through the
  pipeline — before UK-market work begins. Target market: Karachi, Lahore,
  Islamabad agents/small agencies. Price point: free during validation.
- **Phase 2 gate (UK Build-Readiness)** — ⚠ **INFERRED, not from the original
  paste; confirm with owner**: Rightmove/Zoopla parsing (`rightmove-parser.md`)
  and UK classification (`lead-classifier-uk.md`) built and tested against
  sample data; Discord notification channel configured and reachable; a
  concrete UK pricing model drafted with an exact £/month/client figure
  (`workspace/IDENTITY.md` currently has no figure set); zero paid
  infrastructure introduced in the process.
- **Phase 3 gate**: First UK client onboarded, Rightmove leads flowing,
  Discord notifications working.
- **Phase 4 gate**: Client self-serve onboarding working, billing defined,
  second UK client signed.

## 3. Architecture & Agent Roles

| Agent | File | Role | Pattern |
|---|---|---|---|
| Orchestrator | `agents/orchestrator/SOUL.md` | Master coordinator, heartbeat, routing | Always active |
| Intake Sub-Agent | `agents/intake/SOUL.md` | Inbox reader + Gemini classifier (Maker) | Runtime |
| Delivery Sub-Agent | `agents/delivery/SOUL.md` | CRM writer + notifier (Checker) | Runtime |
| Spec Scorer | `agents/spec-scorer/spec-scorer.md` | Score specs before build (≥ 9.6/10 required) | Dev-time only |
| Constitution Checker | `agents/constitution-checker/constitution-checker.md` | PASS/FAIL gate before merge | Dev-time only |

**Runtime routing**: Orchestrator → reads `USER.md` (multi-tenant-router) →
reads Gmail + WhatsApp → Intake Sub-Agent (parser + classifier) → [score ≥ 0.7]
→ Delivery Sub-Agent (validate → CRM → notify → queue) → [score < 0.7] → log
rejection, skip Delivery → Orchestrator updates `MEMORY.md` + dashboard state.

**Dev-time routing**: spec → Spec Scorer (≥ 9.6 required) → `/sp.plan` → ADR →
`/sp.tasks` → implementation → Constitution Checker (PASS required) → merge.

**Agent communication rules**: sub-agents communicate via structured JSON only,
never natural language between agents. The Orchestrator is the only agent that
reads/writes `MEMORY.md` directly. Intake passes output to Delivery only via
the Orchestrator — never directly. Spec Scorer and Constitution Checker are
stateless (no `MEMORY.md` access). Sub-agents MUST NOT invoke one another
directly.

**Maker/Checker contract**: Intake (Maker) produces lead JSON and never acts on
it. Delivery (Checker) validates Intake's output and rejects on schema failure,
then acts. If Delivery rejects, the Orchestrator logs it, notifies the owner,
and does not retry automatically.

**HITL approval tiers** (Delivery Sub-Agent):
- **Tier 1 — Auto-dispatch** (`classification_score` ≥ 0.9): CRM write and
  notification are immediate and automatic (🔴 URGENT flag on notification);
  email draft still queues for operator approval.
- **Tier 2 — Human review** (0.7–0.89): CRM write held; owner is asked to
  `/confirm` or `/discard`; auto-discard after 2 hours of no response.
- **Tier 3 — Blocked** (< 0.7): rejected by Intake before reaching Delivery.

## 4. Pipeline Execution (Heartbeat)

Runs every 15 minutes via systemd timer (`/etc/systemd/system/deal-scout.timer`).

**Pre-flight checks** (abort entire run if any fail): `gemini_today_count < 18`;
HubSpot API reachable (`GET /crm/v3/objects/contacts?limit=1` returns 200);
tenant `USER.md` exists and `active: true`; no unresolved approval-queue entry
older than 4 hours (alert owner if found).

**Execution order**: (1) multi-tenant-router loads tenant context → (2) Intake
reads Gmail (+ WhatsApp if enabled) → (3) Intake parses (`zameen-parser` or
`rightmove-parser`) → (4) Intake classifies (`lead-classifier-pk` or
`lead-classifier-uk`) → (5) [score ≥ 0.7] Delivery validates schema → (6)
Delivery writes HubSpot CRM → (7) Delivery sends WhatsApp/Discord notification
→ (8) [if `auto_email_drafts`] Delivery queues draft via
`operator-approval-gate` → (9) Orchestrator updates `MEMORY.md` spine → (10)
Orchestrator updates dashboard state via `remote-dashboard` skill.

**Scope limits per run, per tenant**: max 20 Gmail messages, 10 WhatsApp
messages, 5 Gemini calls, 50 HubSpot API calls, 10 Discord/WhatsApp
notifications, 5 email drafts queued.

**Run logging**: every run writes `run_id`, `tenant_id`, `started_at`,
`completed_at`, `leads_found`, `leads_classified`, `leads_rejected`,
`crm_writes`, `notifications_sent`, `drafts_queued`, `gemini_calls_this_run`,
and `errors` to `MEMORY.md`.

## 5. Tools & External Dependencies (Zero-Cost Constraint)

No paid APIs, no paid hosting, no paid infrastructure — a hard constraint, not
a preference.

| API | Free Tier Limit | Used By |
|---|---|---|
| Gemini 2.5 Flash | 20 req/day | Intake Sub-Agent |
| HubSpot | Free CRM tier | Delivery Sub-Agent |
| Gmail OAuth | Unlimited | Intake Sub-Agent |
| WhatsApp (OpenClaw) | Built-in | Orchestrator + Delivery |
| Discord (OpenClaw) | Built-in | Delivery Sub-Agent (UK) |
| Cloudflare Tunnel | Free | `remote-dashboard` skill |

**Tool priority rule**: always use an existing ClawHub skill before building
custom; always use an OpenClaw built-in channel before an external API; never
add a paid tool without Constitution Checker gate I2 approval.

## 6. Hard Rules (Non-Negotiables)

1. Never process a lead without `classification_score` ≥ 0.7.
2. Always confirm CRM write before sending any notification.
3. Pause the full pipeline at `gemini_today_count` ≥ 18 — notify the owner, do
   not retry until the daily reset at 00:00 UTC, never reset manually.
4. Require operator approval (`approved: true` in the queue) before any
   client-facing email is sent — regardless of lead score, urgency tier, or
   market mode.
5. Never expose one tenant's data to another — always verify `tenant_id`
   against the active session's `USER.md`.
6. Write to the `MEMORY.md` spine after every pipeline run, successful or not.
7. OpenClaw remains the sole runtime orchestrator; Claude Code is dev-time only
   (spec scoring, planning, ADRs, tasks, constitution checks) and MUST NOT be
   introduced as a runtime coordinator.
8. PK-mode notifications MUST use WhatsApp only; UK-mode notifications MUST
   use Discord only; neither market substitutes the other's channel.

**Failure handling**: HubSpot unreachable → retry once after 30s, then halt
and log. WhatsApp send failure → retry once, then log and continue (does not
block the pipeline). Intake returns malformed JSON → reject, log reason, skip
the lead (does not pass to Delivery). Gemini timeout → mark lead
`unclassified`, log, skip delivery.

## 7. Constitution Checker Gates

Run PASS/FAIL/N/A before every merge, against the final implementation, never
the spec. A single FAIL blocks merge — no exceptions. N/A is valid only when a
gate is genuinely not applicable, with the reason stated. A previous PASS does
not carry forward.

**Identity gates**
- I1: Feature targets exactly one market (PK Real Estate OR UK Estate Agents —
  not both).
- I2: Zero infrastructure cost introduced (no new paid API, no paid hosting).
- I3: WhatsApp channel used for PK-mode notifications (not email, not
  Discord).
- I4: Dashboard remains client-accessible (not localhost-only).
- I5: OpenClaw remains the orchestrator (no Claude Code orchestration
  introduced).

**Architecture gates**
- A1: Maker/Checker split maintained (Intake produces, Delivery validates
  before acting).
- A2: CRM write confirmed before any notification sent.
- A3: `processed_ids` deduplication active per tenant before any CRM write.
- A4: `tenant_id` verified against `USER.md` before every data operation.
- A5: Gemini quota guard active — pipeline halts at `gemini_today_count` ≥ 18.
- A6: `MEMORY.md` spine updated after every pipeline run.
- A7: Operator approval required before any client-facing email is sent.
- A8: No tenant's data exposed to another tenant under any condition.

**Quality gates**
- Q1: All existing tests still pass (489 baseline minimum).
- Q2: New feature has tests covering at least 3 cases from the spec.
- Q3: ADR written and committed for this feature's architectural decisions.
- Q4: Git checkpoint run with credential-leak scan — no secrets in the diff.
- Q5: No "TBD", "TODO", "FIXME" left in production code paths.

**Business gates**
- B1: Feature is tied to a named milestone (F008–F017).
- B2: README updated if the feature changes user-facing behaviour.
- B3: No breaking change to existing tenant configs without a migration path
  defined.

## 8. Constitution Compliance Test Cases

1. **Quota guard boundary** — Input: `gemini_today_count = 18` at the start of
   a heartbeat run. Expected output: Steps 3–4 (parse, classify) are skipped,
   `quota_exhausted: true` is logged, exactly one owner alert is sent, the run
   still completes Step 9 (`MEMORY.md` update). Edge case tested: the guard
   fires at the threshold itself, not only after exceeding it.
2. **Cross-tenant rejection** — Input: a lead JSON with `tenant_id:
   "agency-b"` arrives while the active session's `USER.md` declares
   `tenant_id: "agency-a"`. Expected output: Delivery rejects the lead, logs
   the mismatch, takes no CRM or notification action (gate A4/A8). Edge case
   tested: the rejection path for tenant isolation — no silent skip.
3. **Unapproved email block** — Input: a queued draft with `approved: false`
   reaches the 4-hour mark with no operator response. Expected output: an
   owner alert is sent; the draft remains unsent (gate A7). Edge case tested:
   the approval gate holds even after the review-window deadline passes.
4. **Duplicate lead rejection** — Input: a lead whose `raw_source_id` already
   exists in `processed_ids` for the tenant. Expected output: Delivery rejects
   it before any CRM write (gate A3); no duplicate HubSpot contact/deal is
   created. Edge case tested: dedup applies even when the duplicate's
   classification score is higher than the original.
5. **Market sequencing gate** — Input: only 2 PK agencies have received a
   delivered lead notification. Expected output: any UK-market feature spec is
   blocked at Constitution Checker gate I1 until the 3rd PK agency
   confirmation is logged (Phase 1 gate, Section 2). Edge case tested: the
   numeric threshold (3) is enforced exactly.

## 9. Governance

This constitution supersedes `workspace/IDENTITY.md`, `workspace/AGENTS.md`,
`workspace/HEARTBEAT.md`, `workspace/TOOLS.md`, and the individual
`agents/*/SOUL.md` files wherever a conflict exists; those files remain the
detailed operational reference for runtime behavior not restated here.

Amendments require a documented rationale, a version bump per semantic
versioning (MAJOR: gate or principle removal/redefinition that breaks prior
compliance; MINOR: new gate or materially expanded guidance; PATCH:
clarification or wording fix), and a propagation check across this file, the
SDD-level constitution at `.specify/memory/constitution.md`, and the affected
`SOUL.md` files.

The Constitution Checker gate (Section 7) is mandatory before every merge,
with no exemption for urgency.

**Version**: 1.0.0 | **Ratified**: 2026-08-01 | **Last Amended**: 2026-08-01
