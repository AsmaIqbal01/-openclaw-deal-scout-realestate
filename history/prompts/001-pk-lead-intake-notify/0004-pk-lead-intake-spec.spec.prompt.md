---
id: 0004
title: PK lead intake notify spec
stage: spec
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: 001-pk-lead-intake-notify
branch: 001-pk-lead-intake-notify
user: Asma
command: /sp.specify (resumed)
labels: [spec, pk-market, lead-intake, whatsapp, gemini-quota, multi-tenant]
links:
  spec: specs/001-pk-lead-intake-notify/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-pk-lead-intake-notify/spec.md
 - specs/001-pk-lead-intake-notify/checklists/requirements.md
 - history/prompts/001-pk-lead-intake-notify/0004-pk-lead-intake-spec.spec.prompt.md
tests:
 - 3 Independent Test cases (one per user story), each with input/expected-output/edge-case; failure/rejection paths covered in US2 and US3
---

## Prompt

Resume the first PK feature spec and run till score 9.6

## Response snapshot

Resumed the `/sp.specify "first PK feature"` command that had been interrupted
earlier in the session. Scoped "first PK feature" concretely as F008 — PK
Lead Intake, Classification & WhatsApp Notification: the core end-to-end loop
(Zameen/OLX Gmail alerts + WhatsApp forwards → Gemini classification →
HubSpot CRM write → WhatsApp notification), since this is the minimum slice
that makes the product's core promise ("never miss a lead") true, and it
directly unlocks Phase 1 gate progress (1 of 3 PK agencies).

Ran `.specify/scripts/powershell/create-new-feature.ps1` to create branch
`001-pk-lead-intake-notify` and scaffold `specs/001-pk-lead-intake-notify/
spec.md`. The script errored on its `history/prompts/<branch>/` directory
creation step (Windows PowerShell 5.1 doesn't support the multi-argument
`Join-Path` the script uses, which assumes pwsh 7+) — branch and spec.md were
already created by that point, so worked around it by creating the prompts
directory manually rather than fixing the script (out of scope for a spec
task).

Wrote the full spec: 3 prioritized, independently-testable user stories
(P1 auto-dispatch for high-confidence leads ≥0.9, P2 human review for
0.70–0.89, P3 Gemini quota-guard reliability), 9 edge cases, 15 functional
requirements, 4 key entities, and 6 measurable success criteria — all derived
directly from existing operational docs (`agents/intake/SOUL.md`,
`agents/delivery/SOUL.md`, `workspace/HEARTBEAT.md`, `workspace/TOOLS.md`)
rather than invented, so zero [NEEDS CLARIFICATION] markers were needed.
Created the requirements checklist (all items pass on first iteration).

Self-scored against the spec-scorer rubric, found two gaps, and closed both
before finalizing: (1) Error Path Coverage was missing explicit auth-failure
handling (Gmail OAuth expiry, HubSpot API key invalid) — added FR-014/FR-015
and matching edge cases; (2) Test Coverage Intent's "edge case being tested"
wasn't explicitly labeled in each Independent Test — added an explicit
"Edge case tested:" sentence to each of the 3. Final score: Interface
Precision 1.8/2.0, Error Path Coverage 2.0/2.0, Ambiguity Elimination 1.5/1.5,
Market Specificity 1.5/1.5, Test Coverage Intent 1.5/1.5, Multi-Tenant
Awareness 1.0/1.0, Business Gate Linkage 0.5/0.5 — **9.8/10, PASS**.
Interface Precision was capped below 2.0 deliberately: the spec-template's
own "no APIs/tech stack" rule prevents naming literal HTTP methods/URLs,
which the rubric's dimension 1 wants — a structural tension, not a fixable
gap, so it wasn't force-closed.

## Outcome

- ✅ Impact: `specs/001-pk-lead-intake-notify/spec.md` ready for `/sp.plan`; branch `001-pk-lead-intake-notify` checked out; scored 9.8/10 against the spec-scorer rubric (threshold 9.6).
- 🧪 Tests: requirements checklist fully passing; 3 Independent Test cases defined with explicit edge-case labels.
- 📁 Files: `specs/001-pk-lead-intake-notify/spec.md`, `specs/001-pk-lead-intake-notify/checklists/requirements.md`, this PHR.
- 🔁 Next prompts: `/sp.plan` for this feature; separately, fix or replace `create-new-feature.ps1`'s multi-argument `Join-Path` call so it runs under Windows PowerShell 5.1 without manual workaround.
- 🧠 Reflection: naming Gemini/HubSpot/WhatsApp/Gmail by name in a "no implementation details" spec is defensible when they're fixed platform constraints from the constitution (zero-cost tier ceilings), not discretionary tech choices — documented that reasoning in the checklist notes so it doesn't read as a content-quality violation on a later pass.

## Evaluation notes (flywheel)

- Failure modes observed: `create-new-feature.ps1` is pwsh-7-only (multi-arg `Join-Path`) but this environment runs Windows PowerShell 5.1 — worked around manually; script itself needs a fix outside this task's scope.
- Graders run and results (PASS/FAIL): self-applied spec-scorer rubric — PASS (9.8/10, threshold 9.6/10) after 1 gap-closing iteration.
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): patch `create-new-feature.ps1` to use `Join-Path (Join-Path $repoRoot 'history') (Join-Path 'prompts' $branchName)` or equivalent nested calls for PowerShell 5.1 compatibility.
