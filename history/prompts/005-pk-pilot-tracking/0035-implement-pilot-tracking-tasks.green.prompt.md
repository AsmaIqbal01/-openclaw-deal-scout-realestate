---
id: 0035
title: Implement pilot tracking tasks
stage: green
date: 2026-08-11
surface: agent
model: claude-sonnet-5
feature: 005-pk-pilot-tracking
branch: 005-pk-pilot-tracking
user: AsmaIqbal000
command: /sp.implement
labels: ["implementation", "pilot-tracking", "phase-1-gate", "F012"]
links:
  spec: specs/005-pk-pilot-tracking/spec.md
  ticket: null
  adr: adrs/ADR-004-pilots-manual-tracking-boundary.md
  pr: null
files:
 - tests/fixtures/pilots/valid_four_slots.md
 - tests/fixtures/pilots/duplicate_tenant_id.md
 - tests/fixtures/pilots/invalid_onboarding_status.md
 - tests/fixtures/pilots/three_confirmed.md
 - tests/fixtures/pilots/two_confirmed.md
 - tests/fixtures/pilots/confirmed_without_source.md
 - tests/contract/test_pilots_schema.py
 - PILOTS.md
 - specs/005-pk-pilot-tracking/tasks.md
tests:
 - tests/contract/test_pilots_schema.py (10 tests, all passing at this stage)
 - full suite: 95 passed
---

## Prompt

for F005. Follow all 23 tasks in order. Do not skip any phase.

## Response snapshot

Ran `check-prerequisites.ps1 -RequireTasks -IncludeTasks`, confirmed
`specs/005-pk-pilot-tracking` with all docs present, and checked
`checklists/requirements.md` — 16/16 items complete, PASS, proceeded
without pausing for user confirmation.

Executed all 7 original phases in strict order, verifying each
checkpoint's independent-test command before moving on:

- **Phase 1 (T001-T006)**: 6 fixture Markdown files under
  `tests/fixtures/pilots/`, each a valid-shaped `PILOTS.md` document with
  fenced JSON slot blocks — one clean scaffold, one duplicate-`tenant_id`
  case, one invalid-enum case, one 3-confirmed case, one 2-confirmed case,
  one confirmed-without-`source_run_id` case. Rewrote `duplicate_tenant_id.md`
  mid-stream once I noticed both duplicate slots needed to *look* confirmed
  for the later exclusion test (T018) to be meaningful — an
  originally-`tenant_configured` pair would have made that test vacuous.
- **Phase 2 (T007-T009)**: `parse_pilot_slots` (regex-based fenced-JSON
  extraction), `parse_summary_line`, `count_valid_confirmed` (schema +
  duplicate-`tenant_id` exclusion) in `tests/contract/test_pilots_schema.py`.
  Sanity-checked the regex against a real fixture via a one-off Python
  invocation before writing any test against it.
- **Phases 3-5 (T010-T019)**: 10 test functions across the 3 user stories,
  run at each phase's own `-k` filter checkpoint (`summary`, then full
  file, then `gate`) before moving to the next phase — all green on first
  write.
- **Phase 6 (T020)**: created the real `PILOTS.md` at the repository root,
  byte-identical in shape to T001's fixture, then independently verified it
  parses and validates via a standalone script (not just by eye).
- **Phase 7 (T021-T022)**: full suite 95/95 passing (85 baseline + 10 new),
  `quickstart.md`'s exact command passing standalone.

Marked all 20 corresponding checkboxes `[X]` in `tasks.md` as each task
completed, matching the harness instruction to track progress in the file
itself, not just narrate completion.

Then invoked `/sp.analyze` (T023) as the final task — this produced a
substantial finding set (5 real coverage gaps, 1 CRITICAL), reported
separately and not auto-remediated per that skill's read-only operating
constraint; remediation is documented in PHR 0036.

## Outcome

- ✅ Impact: F005's original 23-task plan fully executed; `/sp.analyze` (T023) surfaced 5 genuine gaps against spec.md, closed in the same session (PHR 0036) rather than left open
- 🧪 Tests: 95 passed (85 baseline unmodified + 10 new pilot contract tests) at the point `/sp.analyze` ran
- 📁 Files: 6 fixtures, `tests/contract/test_pilots_schema.py`, `PILOTS.md`, `specs/005-pk-pilot-tracking/tasks.md` (checkboxes)
- 🔁 Next prompts: user-directed remediation of `/sp.analyze`'s findings (PHR 0036)
- 🧠 Reflection: running `/sp.analyze` as the literal last numbered task (T023), rather than treating "tasks.md is fully checked off" as done, is what caught FR-013 — a requirement the spec's *own* self-audit had added — shipping with zero implementation. The gap existed because `tasks.md`'s T009 scope description silently narrowed from what `data-model.md` actually specified; worth checking task-scope text against its own data-model.md cross-references, not just against the FR list, in future features.

## Evaluation notes (flywheel)

- Failure modes observed: `tasks.md` T009's own written scope ("implementing the FR-006/FR-007/FR-011 exclusion rules") silently omitted FR-013 despite `data-model.md` naming it as something the same function should enforce — a drift introduced during `/sp.tasks` (PHR 0034) that neither that step nor the initial implementation caught until `/sp.analyze` ran
- Graders run and results (PASS/FAIL): full test suite — PASS (95/95) at this checkpoint; `/sp.analyze` — found 1 CRITICAL, 1 HIGH, 3 MEDIUM/LOW (see PHR 0036 for remediation)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): when a spec requirement is added during a self-audit (rescoring) pass, explicitly cross-check that every downstream artifact (research.md, data-model.md, tasks.md) that should reference it actually does, rather than assuming the rescore alone propagates
