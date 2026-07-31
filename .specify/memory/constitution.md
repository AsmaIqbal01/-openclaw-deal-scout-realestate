<!--
Sync Impact Report
==================
Version change: [TEMPLATE] → 1.0.0 (initial ratification)
Rationale for MINOR vs MAJOR vs INITIAL: this is the first concrete fill of a
placeholder template with zero prior ratified content, so it is treated as an
initial adoption (1.0.0), not an amendment bump.

Modified principles: n/a (template had no named principles)
Added sections:
  - Core Principles I–IX (Market Sequencing, Zero Infrastructure Cost,
    Channel Fidelity, OpenClaw Orchestration, Maker/Checker Separation,
    Gemini Quota Guard, Human Approval Gate, Multi-Tenant Isolation,
    Spec Quality Gate)
  - Delivery & Documentation Discipline (Section 2)
  - Development Workflow & Quality Gates (Section 3)
  - Constitution Compliance Test Cases (4 named cases, input/expected/edge case)
  - Governance (amendment procedure, versioning policy, compliance review)
Removed sections: none (template placeholders only)

Templates requiring updates:
  - .specify/templates/plan-template.md ................ ✅ no change needed
    (Constitution Check section already reads dynamically from this file)
  - .specify/templates/spec-template.md ................. ✅ no change needed
    (generic SDD structure remains compatible with new principles)
  - .specify/templates/tasks-template.md ................ ✅ no change needed
    (generic SDD structure remains compatible with new principles)
  - .specify/templates/commands/*.md .................... ⚠ none found in repo
    (no command files present under .specify/templates/commands/ to check)

Follow-up TODOs:
  - RESOLVED: workspace/IDENTITY.md section formerly titled "Lisbon / Visa
    Evidence Trail" (lines 36-39) conflicted with the "real client-delivery
    SaaS" framing mandated by this constitution's "Delivery & Documentation
    Discipline" section. Renamed to "Engineering Rigor & Delivery Discipline"
    and reworded to ground the rigor requirement in client-data handling
    rather than visa/portfolio evidence, in a follow-up edit after initial
    ratification.
  - TODO(RATIFICATION_DATE): no prior ratified version existed in git history
    or embedded docs; RATIFICATION_DATE is set to the date of this initial
    adoption (2026-08-01) rather than an unrecoverable earlier date.
-->

# Deal Scout Real Estate Constitution

## Core Principles

### I. PK-First Market Sequencing (Validation Gate)
The product MUST validate in the Pakistani real estate market before any UK-market
feature ships to a paying or pilot UK client. Exactly 3 Pakistani agencies MUST
confirm active usage — defined as having received at least one delivered lead
notification through the pipeline — before the UK secondary market unlocks. A
single pipeline run MUST NOT mix PK and UK logic: `market_mode` is fixed per
tenant session, read once from `USER.md` at session start. Branching on both
markets within one execution path MUST NOT occur.

**Rationale**: lead sources, language (Roman Urdu vs. English), and notification
channel are structurally different per market. Conflating them before proving
the model works in one market multiplies failure surface for no validated gain.

### II. Zero Infrastructure Cost (NON-NEGOTIABLE)
Paid APIs, paid hosting, and paid infrastructure of any kind MUST NOT be
introduced in Phase 1 (PK validation) or Phase 2 (UK revenue) without an explicit
owner decision captured in an ADR. Gemini's 20-requests/day free tier, HubSpot's
free CRM tier, and Cloudflare Tunnel are the fixed platform ceiling, not a target
to negotiate upward. Any feature whose implementation requires paid infrastructure
MUST be rejected at the spec-scoring stage or redesigned to fit the free-tier
ceiling.

**Rationale**: the business model depends on proving demand at zero marginal
cost before charging; paid infrastructure before revenue inverts the validation
order this product exists to prove out.

### III. Market-Native Channel Fidelity (NON-NEGOTIABLE)
PK-mode tenants MUST receive lead notifications via WhatsApp only, and MUST be
able to originate or forward leads via WhatsApp. UK-mode tenants MUST receive
lead notifications via Discord only, with Gmail as the sole inbound lead-email
source. Substituting the other market's channel MUST NOT occur: PK
notifications MUST NOT fall back to email, and UK notifications MUST NOT fall
back to WhatsApp.

**Rationale**: this matches how agents actually work in each market — PK agents
live in WhatsApp, UK agents live in email/Discord — and keeps the rule
enforceable as a testable gate (see Constitution Checker gate I3).

### IV. OpenClaw as Sole Runtime Orchestrator (NON-NEGOTIABLE)
OpenClaw MUST remain the runtime orchestrator for every pipeline execution.
Claude Code, or any other development-time agent or tool, MUST NOT be introduced
as a runtime orchestrator, coordinator, or scheduler. Claude Code's role is
strictly dev-time: spec scoring, planning, ADR authorship, task generation, and
constitution compliance checks — never production coordination of the Intake
or Delivery sub-agents.

**Rationale**: a single, auditable coordination point for tenant data and quota
state prevents architectural drift toward a second, competing orchestration
layer.

### V. Maker/Checker Separation (NON-NEGOTIABLE)
The Intake Sub-Agent (Maker) MUST only read inboxes and produce structured lead
JSON — it MUST NOT write to CRM or send notifications. The Delivery Sub-Agent
(Checker) MUST validate every required field of Intake's output against the
published schema and MUST reject malformed or duplicate input (`raw_source_id`
already present in `processed_ids`) before taking any real-world action.
Sub-agents MUST communicate via structured JSON only, routed exclusively
through the Orchestrator — sub-agents MUST NOT invoke one another directly.

**Rationale**: separating classification (probabilistic, Gemini-dependent) from
action (deterministic, consequential) ensures a bad classification cannot
directly cause a bad CRM write or client-facing action.

### VI. Gemini Quota Guard
The Orchestrator MUST read `gemini_today_count` from `MEMORY.md` before every
Intake call. At `gemini_today_count ≥ 18`, the full pipeline MUST pause, log
`quota_exhausted: true`, and send exactly one owner alert — no further Intake
calls occur until the daily reset at 00:00 UTC, and the count MUST NOT be reset
manually. This 2-request buffer below the 20/day free-tier ceiling MUST be
preserved in any future change to the classification flow.

**Rationale**: 20/day is a hard external ceiling set by Gemini's free tier; the
18 threshold leaves headroom for manual or debug calls without silently
exceeding the limit and risking cost or service suspension.

### VII. Human Approval Gate for Client-Facing Communication (NON-NEGOTIABLE)
Client-facing email MUST NOT be sent without an explicit `approved: true` flag
set by the operator in the approval queue. Draft emails MUST be queued with
`lead_id`, `draft_body`, `queued_at`, and `approved: false` by default, and the
owner MUST be alerted to any unresolved draft older than 4 hours. This gate
applies regardless of lead score, urgency tier, or market mode.

**Rationale**: an autonomous system can misjudge tone, facts, or client context
in a drafted email; human review is the last line of defense for anything that
reaches a client's inbox directly, distinct from internal CRM writes or agent
notifications which follow their own approval tiers.

### VIII. Multi-Tenant Data Isolation (NON-NEGOTIABLE)
Every data operation (CRM write, notification, `MEMORY.md` update) MUST verify
that the lead's `tenant_id` matches the `tenant_id` declared in the active
session's `USER.md` before proceeding. A mismatch MUST cause immediate
rejection and logging — never a silent skip or cross-tenant fallback.
Sub-agents MUST NOT read or act on another tenant's `MEMORY.md`, `USER.md`, or
queued data during a session.

**Rationale**: this is a multi-tenant SaaS serving independent client agencies;
a single leaked lead or cross-tenant CRM write is a trust-ending incident, not
a recoverable bug.

### IX. Spec Quality Gate — 9.6/10 Minimum (NON-NEGOTIABLE)
A feature specification MUST NOT proceed to `/sp.plan` without scoring at least
9.6/10 against the seven-dimension Spec Scorer rubric (Interface Precision,
Error Path Coverage, Ambiguity Elimination, Market Specificity, Test Coverage
Intent, Multi-Tenant Awareness, Business Gate Linkage). A spec that passed in a
prior session MUST be re-scored against its current version before advancing —
no score carries forward. The Spec Scorer MUST only score and identify gaps; it
MUST NOT suggest fixes or architecture.

**Rationale**: ambiguous specs compound into ambiguous implementations in an
autonomous pipeline that already tolerates no silent failures on quota, tenant
isolation, or approval gates; the 9.6 threshold forces precision before code is
written, not after.

## Delivery & Documentation Discipline

- Every architecturally significant decision MUST be captured in an ADR under
  `history/adr/` and linked from the relevant plan. This is a client-delivery
  quality practice — traceable, auditable decisions for a real SaaS product
  serving paying agencies — not a portfolio or visa-evidence exercise.
  References to visa or "Lisbon evidence" framing MUST NOT appear in specs,
  plans, ADRs, or this constitution.
- Every user prompt MUST produce a Prompt History Record under
  `history/prompts/`, routed by stage (constitution, feature-specific, or
  general) per this project's PHR conventions.
- Every feature MUST be tied to a named milestone in the F008–F017 sequence and
  state which business validation gate it unlocks (e.g., "3rd PK agency
  confirmed").
- Commit history MUST remain clean and descriptive — commit messages describe
  the change and its rationale, not process theater.

## Development Workflow & Quality Gates

- The dev-time sequence is fixed: spec → Spec Scorer (≥ 9.6 required) →
  `/sp.plan` → ADR (if architecturally significant) → `/sp.tasks` →
  implementation → Constitution Checker (PASS required) → merge.
- The Constitution Checker runs the Identity, Architecture, Quality, and
  Business gates defined in `agents/constitution-checker/constitution-checker.md`
  against the final implementation — never the spec — before every merge. A
  single FAIL blocks merge; there are no exceptions or overrides.
- Runtime pipeline routing (Orchestrator → Intake → [`classification_score` ≥
  0.7] → Delivery → `MEMORY.md`) MUST NOT be altered without updating this
  constitution and the affected `SOUL.md` files in the same change.

## Constitution Compliance Test Cases

These prove the principles above are enforceable, not aspirational. The
Constitution Checker MUST be able to verify each against a real implementation.

1. **Quota guard boundary** — Input: `gemini_today_count = 18` at the start of
   an Intake call. Expected output: the pipeline pauses, `quota_exhausted: true`
   is logged, exactly one owner alert is sent, and no Intake call is made.
   Edge case tested: the guard fires at the threshold itself (18), not only
   after exceeding it.
2. **Cross-tenant rejection** — Input: a lead JSON with `tenant_id: "agency-b"`
   arrives while the active session's `USER.md` declares `tenant_id:
   "agency-a"`. Expected output: Delivery rejects the lead, logs the mismatch,
   and takes no CRM or notification action. Edge case tested: the rejection
   path for tenant isolation (Principle VIII) — no silent skip or fallback.
3. **Unapproved email block** — Input: a queued draft with `approved: false`
   reaches the 4-hour mark with no operator response. Expected output: an
   owner alert is sent; the draft remains unsent; no email leaves the system.
   Edge case tested: the approval gate holds even after the review-window
   deadline passes.
4. **Market sequencing gate** — Input: only 2 PK agencies have received a
   delivered lead notification. Expected output: any UK-market feature spec is
   blocked at Constitution Checker gate I1 (single-market target) until the
   3rd PK agency confirmation is logged. Edge case tested: the numeric
   threshold (3) is enforced exactly, not "several" or "a few."

## Governance

This constitution supersedes all other project practices, including any prior
informal agreements in `workspace/IDENTITY.md` or `workspace/AGENTS.md`. Where
those files conflict with this document, this document governs and the
conflicting file MUST be flagged for correction (see Sync Impact Report above).

Amendments require: a documented rationale, a version bump per semantic
versioning (MAJOR: principle removal or redefinition that breaks prior
compliance; MINOR: new principle or materially expanded guidance; PATCH:
clarification or wording fix), and a propagation check across the plan/spec/
tasks templates and affected `SOUL.md` files.

Compliance review is mandatory: the Constitution Checker gate runs before every
merge, with no exemption for urgency. Use `agents/orchestrator/SOUL.md`,
`agents/intake/SOUL.md`, and `agents/delivery/SOUL.md` for runtime behavior
detail beyond what this constitution states as non-negotiable.

**Version**: 1.0.0 | **Ratified**: 2026-08-01 | **Last Amended**: 2026-08-01
