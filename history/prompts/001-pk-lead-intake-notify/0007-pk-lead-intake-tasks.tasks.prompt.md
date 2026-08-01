---
id: 0007
title: PK lead intake task breakdown
stage: tasks
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: 001-pk-lead-intake-notify
branch: 001-pk-lead-intake-notify
user: Asma
command: /sp.tasks
labels: [tasks, pk-market, pytest, fixture-based, user-stories]
links:
  spec: specs/001-pk-lead-intake-notify/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-pk-lead-intake-notify/tasks.md
tests:
 - tasks.md itself defines the 33-task fixture/pytest suite to be implemented; none executed yet
---

## Prompt

(empty — `/sp.task` invoked with no arguments, operating on the current feature branch `001-pk-lead-intake-notify`)

## Response snapshot

Ran `.specify/scripts/powershell/check-prerequisites.ps1 -Json`, confirming
`research.md`, `data-model.md`, `contracts/`, `quickstart.md` all present
alongside the required `plan.md`/`spec.md`. Generated `tasks.md` organized by
the 3 user stories from `spec.md`, following the strict checklist format
throughout (checkbox, sequential Task ID, `[P]` only where files are
independent and unblocked, `[Story]` label on every user-story-phase task).

33 tasks across 6 phases: Setup (T001–T005, test scaffolding + tenant
config template + `.env.example`), Foundational (T006–T008, shared tenant
fixture + `conftest.py` + baseline lead-schema contract test — blocks all
stories), US1/P1 auto-dispatch (T009–T016, 4 parallel fixtures + 4
sequential test functions), US2/P2 human review (T017–T022, 3 parallel
fixtures/contract-test + 3 sequential test functions), US3/P3 quota guard
(T023–T026, 2 parallel fixtures + 2 sequential test functions), and Polish
(T027–T033, tenant isolation + 4 error-path tests + run-logging test +
final quickstart validation run). Every test task cites the exact FR or
Acceptance Scenario it proves. Documented phase/story dependencies (all 3
stories depend only on Foundational, are mutually independent, and Polish
depends on all three being complete), a parallel-execution example for US1,
and MVP-first/incremental-delivery/parallel-team strategy sections per the
template.

Caught and fixed a self-introduced formatting gap before finalizing: several
tasks (T014–T016, T021–T022, T026, T029–T031) initially referenced a test
file only by name ("add to the same file") without restating its directory
path, violating the "every task needs a file path" rule even though the
path was unambiguous from a prior task in the same block — fixed all 8 by
spelling out the full path in each task description.

## Outcome

- ✅ Impact: `specs/001-pk-lead-intake-notify/tasks.md` — 33 tasks, ready for implementation; MVP scope is Setup + Foundational + US1 (T001–T016).
- 🧪 Tests: tasks.md defines the test suite; grep-verified all 33 lines match the required `- [ ] T### [P?] [Story?] Description` format with an explicit file path in every line.
- 📁 Files: `specs/001-pk-lead-intake-notify/tasks.md`.
- 🔁 Next prompts: begin implementation starting with Phase 1 (Setup) and Phase 2 (Foundational), or run `/sp.analyze` first for a cross-artifact consistency pass across spec/plan/tasks.
- 🧠 Reflection: a grep-based self-check against the exact required regex (`^- \[ \] T\d{3}`) caught the missing-file-path issue faster than eyeballing 33 lines would have — worth doing as a standard last step on any generated checklist file.

## Evaluation notes (flywheel)

- Failure modes observed: initially wrote several "Add X" follow-on tasks referencing a file only by name when the full path had been given one task earlier — technically ambiguous once tasks are read out of order or individually.
- Graders run and results (PASS/FAIL): format validation via grep — PASS (33/33 tasks match the required format after the fix).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
