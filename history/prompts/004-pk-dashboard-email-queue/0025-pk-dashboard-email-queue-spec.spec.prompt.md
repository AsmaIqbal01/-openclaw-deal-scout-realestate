---
id: 0025
title: PK dashboard email queue spec
stage: spec
date: 2026-08-03
surface: agent
model: claude-opus-5[1m]
feature: 004-pk-dashboard-email-queue
branch: 004-pk-dashboard-email-queue
user: AsmaIqbal000
command: /sp.specify
labels: ["spec", "dashboard-extension", "email-approval-gate", "F011"]
links:
  spec: specs/004-pk-dashboard-email-queue/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/004-pk-dashboard-email-queue/spec.md
 - specs/004-pk-dashboard-email-queue/checklists/requirements.md
tests:
 - none (spec stage; no code yet)
---

## Prompt

draft a spec for the dashboard extension

(Context carried into the /sp.specify invocation, synthesized from the
conversation: "Fourth PK feature: extend the client dashboard (feature 002,
F009) to display the email-draft approval queue introduced by feature 003
(F010) — showing each tenant's queued/pending/approved/rejected/
auto-archived email drafts read-only, alongside the existing Tier 2 lead
Approval Queue section, per skills/remote-dashboard.md and
skills/operator-approval-gate.md. This was explicitly deferred by feature
002's Scope Decision (dashboard originally scoped to Tier 2 lead review
only) and feature 003's Scope Decision (the draft/approve loop stays
WhatsApp-only, no dashboard extension) until now. Strictly read-only,
matching feature 002's design: never writes approval-queue.json, never
processes drafts, never exposes an approve/reject action in the UI —
WhatsApp remains the sole /approve or /reject channel, per Constitution
Principle VII.")

## Response snapshot

Checked for existing branches/specs with short-name
`pk-dashboard-email-queue` (none found) and ran
`create-new-feature.ps1 -Number 4 -ShortName "pk-dashboard-email-queue"`,
creating branch `004-pk-dashboard-email-queue` and
`specs/004-pk-dashboard-email-queue/spec.md`.

Grounded the spec in both source specs (002's dashboard FRs/Interface
Contract pattern, 003's Approval Queue Entry data-model and status
semantics) and `skills/remote-dashboard.md`'s existing "Approval Queue"
section (dashboard section 4) and "Approve/Reject from Dashboard" section
(the `POST /approve|reject/{queue_id}` endpoints described there but never
built). Explicitly disambiguated feature 002's existing Tier-2-lead
"Approval Queue" from this feature's new "Email Draft Queue" section in a
dedicated Scope Decision paragraph, since the two are easy to conflate
(same word, different data source). Stated read-only as a *permanent*
design constraint (Constitution Principle VII — WhatsApp is the sole
resolution channel) rather than a temporary deferral, and specified that
`skills/remote-dashboard.md`'s approve/reject-button vision is explicitly
not implemented by this or any currently planned feature.

Wrote 3 user stories (P1: see pending drafts in full; P2: see resolved
history with a distinct "Send Failed" status derived from feature 003's
`approved: true` + `sent_at: null` state; P3: tenant isolation + partial-
failure resilience), 11 FRs, an Interface Contract table (3 states: entries
present / no drafts yet / unable to load), and 5 success criteria.

Ran a rigorous, literal audit against `agents/spec-scorer/spec-scorer.md`
(not a casual self-score) — grepped for hedge words, found and fixed one
("should never happen" in an Edge Case, reworded to state feature 003's
write-path guarantee as fact) — then added the Interface Contract table to
strengthen Interface Precision before finalizing. Final score: 10.0/10,
documented in `checklists/requirements.md` with the full dimension
breakdown.

## Outcome

- ✅ Impact: spec ready for `/sp.plan` — scored 10.0/10 against the constitution's 9.6/10 gate (Principle IX), no [NEEDS CLARIFICATION] markers
- 🧪 Tests: N/A (spec stage)
- 📁 Files: `specs/004-pk-dashboard-email-queue/spec.md`, `specs/004-pk-dashboard-email-queue/checklists/requirements.md`
- 🔁 Next prompts: `/sp.plan` for feature 004, once the user is ready to proceed past spec drafting
- 🧠 Reflection: the terminology collision between feature 002's "Approval Queue" (Tier 2 leads) and this feature's "Email Draft Queue" (feature 003's drafts) was worth catching at spec time — naming it explicitly in the Scope Decision avoids a repeat of the kind of drift `/sp.analyze` has caught in prior features (e.g. 003's I1/C1 findings)

## Evaluation notes (flywheel)

- Failure modes observed: initial draft had one ambiguous hedge phrase ("should never happen") in an edge case, caught by a literal grep-based ambiguity audit rather than eyeballing
- Graders run and results (PASS/FAIL): spec-scorer rubric — PASS (10.0/10)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
