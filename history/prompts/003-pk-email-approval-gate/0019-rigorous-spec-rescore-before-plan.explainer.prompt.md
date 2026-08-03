---
id: 0019
title: Rigorous spec rescore before plan
stage: explainer
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: 003-pk-email-approval-gate
branch: 003-pk-email-approval-gate
user: Asma
command: /sp.specify (rigorous re-audit)
labels: [spec-scorer, audit, pre-plan-gate]
links:
  spec: specs/003-pk-email-approval-gate/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/003-pk-email-approval-gate/spec.md
tests:
 - none (spec-level fixes only, no implementation started)
---

## Prompt

(continuation of: "Stop F003 work. First go back and run /sp:specify on F002 (pk-client-dashboard) retroactively... Once F002 scores 9.6, then return to F003 and do the same before any implementation.")

## Response snapshot

Applied the same literal, adversarial rescoring lens just used on F002 to
`specs/003-pk-email-approval-gate/spec.md`, before touching `/sp.plan` or
any implementation. Initial score (the spec as originally drafted, before
this session's earlier casual self-score of 9.8 in PHR 0017):
**8.5/10 — BLOCKED**, with 2 real gaps:

1. Error Path Coverage (-1.0): FR-007 and FR-012's WhatsApp sends never
   addressed send failure, despite feature 001 already establishing a
   retry-once-then-continue pattern for exactly this (its FR-013) that this
   spec never referenced; FR-009's email send never addressed send
   failure, despite feature 001 establishing an analogous
   retry-once-then-halt pattern for HubSpot writes (its FR-012).
2. Market Specificity (-0.5): the drafted email's language was never
   stated, despite quoting a template from a skill file whose own heading
   ("PK Mode (Roman Urdu + English)") doesn't match its actual English-only
   template body — a pre-existing tension this spec inherited without
   resolving.

Notably, this spec's Test Coverage Intent held up under the same scrutiny
that found feature 002's original draft short: US2's Independent Test
already explicitly exercised a failure/rejection path (unknown `queue_id`
ignored), and US3's already exercised a permanence/rejection property
(archived drafts can't be revived by a late approval) — so this dimension
scored full marks on the first rigorous pass, unlike feature 002's.

Fixed both gaps: extended FR-007 with WhatsApp-send retry semantics
(explicitly cross-referenced to feature 001 FR-013) and FR-009 with
email-send retry semantics (cross-referenced to feature 001 FR-012,
including the "sent_at stays unset, owner alerted" failure branch so an
approved-but-unsent draft can never go silently missing); added a
Language/Locale line resolving the skill file's heading/content mismatch by
fixing the actual drafted output as English-only, consistent with every
other PK client-facing artifact already built; added matching Edge Cases
entries for both new failure paths.

Rescored after fixes: **10.0/10 — PASS**.

## Outcome

- ✅ Impact: `specs/003-pk-email-approval-gate/spec.md` now has a real ≥9.6 score under the same rigorous standard just applied to F002, before any planning or implementation work began on this feature.
- 🧪 Tests: none — no implementation exists yet for this feature.
- 📁 Files: `specs/003-pk-email-approval-gate/spec.md`.
- 🔁 Next prompts: `/sp.plan` for F003 can now proceed against a genuinely-scored spec; separately, decide whether to commit the F002 retroactive spec fix (PHR 0018) before or alongside F003's work.
- 🧠 Reflection: cross-referencing feature 001's already-established retry patterns (FR-012/FR-013) by name, rather than re-deriving similar-but-not-identical failure handling from scratch for each new feature, is both faster and keeps the three features' error-handling vocabulary consistent — worth doing proactively in future specs rather than only when a rigorous rescore catches the gap.

## Evaluation notes (flywheel)

- Failure modes observed: the original spec named specific external interactions (WhatsApp send, email send) without carrying over the failure-handling precedent already established for structurally identical interactions in feature 001 — an omission a casual self-score didn't catch but a literal, side-by-side comparison against feature 001's FRs did.
- Graders run and results (PASS/FAIL): literal spec-scorer rubric application — first rigorous pass FAIL (8.5/10), second pass PASS (10.0/10) after 2 gaps closed.
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): when drafting a new feature's spec that reuses an existing external interaction (WhatsApp send, CRM write, email send) from a prior feature, explicitly check that prior feature's FRs for an already-established failure-handling pattern before writing a new one from scratch.
