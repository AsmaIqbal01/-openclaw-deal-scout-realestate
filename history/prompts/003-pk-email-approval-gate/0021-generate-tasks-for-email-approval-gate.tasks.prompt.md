---
id: 0021
title: Generate tasks for email approval gate
stage: tasks
date: 2026-08-03
surface: agent
model: claude-opus-5[1m]
feature: 003-pk-email-approval-gate
branch: 003-pk-email-approval-gate
user: AsmaIqbal000
command: /sp.tasks
labels: ["tasks", "email-approval-gate", "pipeline_sim"]
links:
  spec: specs/003-pk-email-approval-gate/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/003-pk-email-approval-gate/tasks.md
tests:
 - none run yet (task generation only; tests are specified as tasks, not yet written)
---

## Prompt

Resume work on branch 003-pk-email-approval-gate. Check the current state of the spec and plan, then continue with /sp:tasks and implementation. Score must be ≥ 9.6 before any implementation begins.

## Response snapshot

Checked out `003-pk-email-approval-gate` (was on `master`). Confirmed
`spec.md` scored 10.0/10 against the spec-scorer (PHR 0019, rigorous
re-audit) and `plan.md`'s Constitution Check confirms the 9.6/10 Principle
IX gate passes — both comfortably clear the ≥9.6 bar before any
implementation. Read all Phase 0/1 artifacts (research.md, data-model.md,
quickstart.md, contracts/approval-queue-schema.json,
contracts/email-approval-commands.md), the existing
`tests/pipeline_sim.py`, `skills/operator-approval-gate.md`, and
`agents/delivery/SOUL.md` to ground task generation in the actual codebase
conventions (feature 001's test-only-simulation pattern, not feature 002's
real-server pattern).

Found a real pre-flight gap: `plan.md`'s Summary and `research.md` Decision
2 both claim the WhatsApp-send and email-send retry semantics (FR-007,
FR-009) were already backfilled into `skills/operator-approval-gate.md`'s
Error Handling section during planning — a direct read of that file shows
this never actually happened (the section still only has its original 3
bullets). Added T001 to close this before any test encodes behavior the
skill file doesn't document, and flagged it explicitly in tasks.md's
pre-flight note.

Generated `specs/003-pk-email-approval-gate/tasks.md`: 32 tasks across 6
phases (Setup, Foundational, US1/US2/US3 in priority order, Polish), each
task following the strict checklist format with exact file paths, FR-
references, and (where relevant) exact function signatures for the new
`tests/pipeline_sim.py` decision functions (`queue_email_draft`,
`resolve_email_approval_reply`, `apply_stale_queue_guard`,
`render_pk_email_draft`) to be implemented in Phase 3-5. Marked US1 as the
MVP checkpoint. No new agent-logic code or production `src/` — consistent
with `research.md` Decision 1.

## Outcome

- ✅ Impact: tasks.md generated and validated against the checklist format; ready to begin implementation starting with Phase 1 (T001 skill-file fix) and Phase 2 (foundational pipeline_sim.py additions + fixtures)
- 🧪 Tests: none run yet — tasks.md specifies test-first tasks (T009-T016, T018-T024, T026-T028) to be written before their corresponding implementation tasks
- 📁 Files: specs/003-pk-email-approval-gate/tasks.md (created)
- 🔁 Next prompts: implement Phase 1-2 (skill-file backfill + fixtures + foundational functions), then US1/US2/US3 in order
- 🧠 Reflection: cross-checking plan.md's claims against the actual skill file caught a real drift before it became load-bearing in tests — worth doing this check on every /sp.tasks run for features whose plan.md describes a "during planning" file edit

## Evaluation notes (flywheel)

- Failure modes observed: plan.md/research.md asserted a file edit that was never applied (aspirational documentation vs. actual state) — caught by direct file read, not by trusting the artifact's own claim
- Graders run and results (PASS/FAIL): N/A — task generation stage, not a scored artifact
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
