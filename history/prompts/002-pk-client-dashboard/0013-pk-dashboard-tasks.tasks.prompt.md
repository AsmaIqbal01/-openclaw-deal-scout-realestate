---
id: 0013
title: PK client dashboard task breakdown
stage: tasks
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: 002-pk-client-dashboard
branch: 002-pk-client-dashboard
user: Asma
command: /sp.tasks
labels: [tasks, pk-market, dashboard, new-production-code, user-stories]
links:
  spec: specs/002-pk-client-dashboard/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-pk-client-dashboard/tasks.md
tests:
 - tasks.md defines the 23-task suite (pytest for server.py logic + manual quickstart checks for frontend JS); none executed yet
---

## Prompt

(empty — `/sp.tasks` invoked with no arguments, operating on the current feature branch `002-pk-client-dashboard`)

## Response snapshot

Ran `check-prerequisites.ps1 -Json`, confirmed `research.md`,
`data-model.md`, `contracts/`, `quickstart.md` present alongside required
`plan.md`/`spec.md`. Generated `tasks.md` with 23 tasks across 6 phases —
smaller than feature 001's 37 since this feature's scope (one endpoint plus
a static frontend) is naturally more contained.

Unlike feature 001, this tasks.md mixes real implementation tasks with
tests, since `research.md` Decision 1 established that the dashboard needs
genuine new production code: Setup (T001–T003, directory scaffolding +
`index.html`/`dashboard.css` shells), Foundational (T004–T007, two fixture
files + `dashboard/server.py`'s core request-handling functions + the
schema contract test — blocks all stories), US1/P1 (T008–T010, 2 tests +
wiring `dashboard.js` for Pipeline Status/Lead Counter/Quota gauge), US2/P2
(T011–T013, 2 tests + wiring `radar.js` for the Score Radar), US3/P3
(T014–T017, 2 tests + wiring the read-only Approval Queue section + an
automated static-content guard test that fails if "approve"/"reject"
strings ever appear in the frontend, enforcing the spec's Scope Decision
mechanically rather than by convention alone), and Polish (T018–T023,
tenant isolation across 4 response shapes + final full-suite run).

Explicitly scoped frontend JS/HTML (`dashboard.js`, `radar.js`,
`index.html`) as manually verified per `quickstart.md` rather than
`pytest`-covered, since automating browser-side rendering checks would
require a new browser-automation dependency (e.g. Playwright) not otherwise
justified for a small reporting page — documented this decision in the
tasks.md header so it doesn't read as a coverage gap on a later
`/sp.analyze` pass. `dashboard/server.py`'s logic, being plain Python, gets
full automated coverage instead.

Verified all 23 task IDs (T001–T023) are contiguous, unique, and appear in
strictly increasing order matching file position, learned as a standard
post-generation check from feature 001's `/sp.analyze` finding.

## Outcome

- ✅ Impact: `specs/002-pk-client-dashboard/tasks.md` — 23 tasks, ready for implementation; MVP scope is Setup + Foundational + US1 (T001–T010).
- 🧪 Tests: tasks.md defines the automated suite (contract + 4 integration test files, including a novel static-content guard test) plus the manual quickstart checks for frontend interactivity.
- 📁 Files: `specs/002-pk-client-dashboard/tasks.md`.
- 🔁 Next prompts: consider `/sp.analyze` before implementation (worked well for feature 001 — caught a real cross-file bug), or proceed directly to `/sp.implement`.
- 🧠 Reflection: adding an automated test that asserts an absence (no "approve"/"reject" strings in the frontend) turns a scope-decision into an enforced invariant rather than something that could silently drift back in during a future edit — a pattern worth reusing whenever a spec makes a deliberate "not doing X" call.

## Evaluation notes (flywheel)

- Failure modes observed: none — applied the monotonic-ID lesson from feature 001 proactively this time instead of discovering the issue after the fact.
- Graders run and results (PASS/FAIL): format/ID-contiguity check via grep — PASS (23/23 unique, contiguous, monotonic).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
