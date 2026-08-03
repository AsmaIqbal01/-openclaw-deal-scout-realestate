---
id: 0017
title: PK email approval gate spec
stage: spec
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: 003-pk-email-approval-gate
branch: 003-pk-email-approval-gate
user: Asma
command: /sp.specify
labels: [spec, pk-market, email-approval, constitution-principle-vii, multi-tenant]
links:
  spec: specs/003-pk-email-approval-gate/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/003-pk-email-approval-gate/spec.md
 - specs/003-pk-email-approval-gate/checklists/requirements.md
tests:
 - 3 Independent Test cases (one per user story), each with input/expected-output/edge-case
---

## Prompt

Run /sp.specify for the third PK feature

[mid-turn interjections: "ls specs/*/spec.md 2>/dev/null" (checking existing spec files instead of a full git fetch); "Before writing spec content for F003, run /sp:specify on it first and score it against the spec-scorer rubric in agents/spec-scorer/spec-scorer.md. Do not write implementation until score is ≥ 9.6/10. Show the dimension breakdown and iterate until passing." — confirmed the workflow already underway]

## Response snapshot

Scoped "third PK feature" as F010 — PK Email Draft & Operator Approval
Gate, based on `skills/operator-approval-gate.md`. This is the most
clearly signposted next feature: both feature 001 (Constitution Principle
VII marked N/A, "no email path in this feature") and feature 002
(Scope Decision: "email drafting... is a separate, not-yet-built feature")
explicitly deferred this exact capability. It's also the one core
constitution principle never yet exercised by a real implementation.

User interjected mid-turn to skip a full `git fetch --all --prune` in favor
of just checking `ls specs/` directly — adjusted immediately, confirmed
numbering (003 next) from local state only. Ran
`create-new-feature.ps1 -Number 3 -ShortName "pk-email-approval-gate"` —
branch and spec.md scaffolded cleanly (the PowerShell 5.1 fix continues to
hold on its third use).

Wrote the spec: a "Scope Decision" section (no dashboard extension for the
email queue, PK-mode template only — UK deferred), 3 prioritized user
stories (P1 draft-and-queue, P2 approve/reject via WhatsApp, P3 stale-draft
safety net: one reminder at 4h, permanent auto-archive at 24h), 7 edge
cases, 15 functional requirements, 2 key entities, and 5 success criteria —
all derived directly from `skills/operator-approval-gate.md`'s existing
templates/schema and `agents/delivery/SOUL.md`'s Step 4, so zero
`[NEEDS CLARIFICATION]` markers were needed. One explicit design decision
not directly stated in the source skill file: a late `/approve` arriving
after 24-hour auto-archival is treated as `unknown_queue_id_reply` (FR-013)
rather than left undefined, closing a gap the source doc was silent on.

Swept for ambiguous terms and fixed one instance ("no queue entry may be
modified" → "MUST NOT be modified"). Created the requirements checklist
(15/15 pass). Self-scored against the spec-scorer rubric per the user's
explicit request: Interface Precision 1.8/2.0, Error Path Coverage 2.0/2.0,
Ambiguity Elimination 1.5/1.5, Market Specificity 1.5/1.5, Test Coverage
Intent 1.5/1.5, Multi-Tenant Awareness 1.0/1.0, Business Gate Linkage
0.5/0.5 — **9.8/10, PASS** on first pass, matching both prior features'
scores exactly, no rewrite iteration needed.

## Outcome

- ✅ Impact: `specs/003-pk-email-approval-gate/spec.md` ready for `/sp.plan`; branch `003-pk-email-approval-gate` checked out; scored 9.8/10 against the spec-scorer rubric (threshold 9.6, per explicit user instruction not to implement below that bar).
- 🧪 Tests: requirements checklist fully passing; 3 Independent Test cases with explicit edge-case labels.
- 📁 Files: `specs/003-pk-email-approval-gate/spec.md`, `specs/003-pk-email-approval-gate/checklists/requirements.md`, this PHR.
- 🔁 Next prompts: `/sp.plan` for this feature.
- 🧠 Reflection: when a source skill file is silent on a specific interaction (what happens to a late approval after permanent archival), stating the resolved rule explicitly in the spec (rather than leaving it implicit) closes a real ambiguity the upstream doc has — worth actively looking for these silent gaps rather than only transcribing what's already fully specified.

## Evaluation notes (flywheel)

- Failure modes observed: one instance of "may" crept in during drafting (permission-style ambiguity flagged by the rubric) — caught via the standard grep sweep before scoring.
- Graders run and results (PASS/FAIL): self-applied spec-scorer rubric — PASS (9.8/10, threshold 9.6/10), per explicit user request to show the dimension breakdown and not proceed below threshold.
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
