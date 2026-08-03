---
id: 0029
title: Generate tasks for dashboard extension
stage: tasks
date: 2026-08-03
surface: agent
model: claude-opus-5[1m]
feature: 004-pk-dashboard-email-queue
branch: 004-pk-dashboard-email-queue
user: AsmaIqbal000
command: /sp.tasks
labels: ["tasks", "dashboard-extension", "email-approval-gate"]
links:
  spec: specs/004-pk-dashboard-email-queue/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/004-pk-dashboard-email-queue/tasks.md
tests:
 - none run yet (task generation only)
---

## Prompt

continue with /sp.tasks

## Response snapshot

Before generating tasks, caught and corrected a planning error from the
prior `/sp.plan` pass (see PHR 0028): retracted `ADR-004` and fixed
`research.md`/`plan.md`, since the guard-test conflict it was based on
doesn't actually occur given the already-chosen server-side status-
derivation design.

Read the actual `dashboard/server.py`, `index.html`, `dashboard.js`,
`dashboard.css`, and `tests/conftest.py`'s `dashboard_workspace_factory`
fixture to ground task generation in the real code this feature extends
(not just the spec/plan). Generated `specs/004-pk-dashboard-email-queue/tasks.md`:
27 tasks across 7 phases (Setup, Foundational, US1/US2/US3, Frontend,
Polish). Foundational phase specifies 4 new functions for
`dashboard/server.py` (`load_email_draft_queue_raw`,
`derive_status_label`, `enrich_email_draft_queue_entry`,
`build_email_draft_queue_response`) with exact signatures and the specific
integration point in `handle_state_request` (T014). Frontend phase (T021-
T023) explicitly notes the JS implementation must be purely data-driven
with no hardcoded status text, per the corrected Decision 3. No task
touches `test_no_approval_actions_in_frontend.py`.

## Outcome

- ✅ Impact: tasks.md generated, grounded in the actual existing dashboard code, with the earlier planning error already excluded from scope
- 🧪 Tests: none run yet — tasks.md specifies test-first tasks per phase
- 📁 Files: specs/004-pk-dashboard-email-queue/tasks.md (created)
- 🔁 Next prompts: implement Phase 1-2 (fixtures + foundational server.py functions), then US1/US2/US3, then frontend
- 🧠 Reflection: reading the real fixture-factory and server.py signatures before writing task descriptions (rather than only the spec/data-model) is what let T007/T009/T010's signatures be concrete enough to implement without further research — worth continuing for any feature touching genuine production code

## Evaluation notes (flywheel)

- Failure modes observed: none in this pass (the earlier error was caught and fixed before this stage)
- Graders run and results (PASS/FAIL): N/A — task generation stage, not independently scored
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
