---
id: 0008
title: Analyze remediation applied
stage: misc
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: 001-pk-lead-intake-notify
branch: 001-pk-lead-intake-notify
user: Asma
command: /sp.analyze (remediation follow-up)
labels: [analyze, remediation, score-band-fix, tasks-renumber]
links:
  spec: specs/001-pk-lead-intake-notify/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - agents/intake/SOUL.md
 - specs/001-pk-lead-intake-notify/spec.md
 - specs/001-pk-lead-intake-notify/data-model.md
 - specs/001-pk-lead-intake-notify/tasks.md
tests:
 - tasks.md T009/T010 (new) will test the corrected 0.65/0.69/0.70 rejection boundary; T015/T020 (renumbered) will test intake trigger/routing — not yet executed, planning-stage only
---

## Prompt

apply all edits now

(follow-up to: "yes" approving remediation suggestions for /sp.analyze findings I1 and G1)

## Response snapshot

Applied the remediation plan proposed after `/sp.analyze` for its two blocking
findings:

**I1 (CRITICAL — 0.5–0.69 score-band contradiction)**: `agents/intake/
SOUL.md` only rejected `<0.5` while `agents/delivery/SOUL.md`'s Tier 3 treated
`<0.7` as "should never reach Delivery," so a 0.5–0.69 lead correctly
forwarded by Intake would be bounced by Delivery as `unexpected_low_score`.
Resolved by moving Intake's reject threshold to `<0.7` (Scoring Rules and
Hard Rule #1 in `agents/intake/SOUL.md`), updating `spec.md` FR-003 and its
matching Edge Case bullet to `<0.7`, and simplifying `data-model.md`'s Lead
state-transition diagram to merge the former 0.5–0.69 branch into the
`<0.70` rejection path. `agents/delivery/SOUL.md` needed no change — its
existing Tier 3 boundary was already correct; Intake now matches it.

**G1 (HIGH — FR-001 intake trigger/routing untested)**: added two new tasks
to `tasks.md`'s User Story 1 phase — a fixture for an email matching neither
Zameen/OLX sender domains nor PK keywords, and a test asserting Zameen→
`zameen-parser.md`, WhatsApp→`pk-whatsapp-lead.md`, and no-match→no candidate.

Renumbering: inserted 2 new Foundational tasks (rejection-boundary fixture +
test, T009–T010) and 2 new US1 tasks (non-matching fixture + routing test),
growing the suite from 33 to 37 tasks. Caught and fixed a self-introduced
ordering bug mid-edit: the first renumbering pass put the new US1 fixture
(T019) after the existing test tasks (T015–T018) in file order despite its
higher ID — non-monotonic. Corrected by renumbering the whole US1 phase so
all 5 fixtures (T011–T015) precede all 5 tests (T016–T020), which had no
knock-on effect on Phase 4 onward since the total count crossing that
boundary (20) was unchanged. Verified via grep that final IDs T001–T037 are
contiguous, unique, and appear in strictly increasing order matching file
position, and that no stale task-ID references remain anywhere else in the
feature directory.

Deliberately did not create the actual new fixture/test files yet (only
updated the planning documents) — consistent with how the other 33
pre-existing tasks work too: `tasks.md` describes what implementation will
create, it doesn't jump ahead of `/sp.implement`.

## Outcome

- ✅ Impact: the score-band contradiction between two existing agent files is fixed at the source (not papered over in the spec); FR-001 now has planned test coverage; `tasks.md` grew from 33 to 37 tasks, fully renumbered and verified contiguous/monotonic.
- 🧪 Tests: none executed (still planning stage) — new tasks T009, T010, T015, T020 will implement the missing coverage when `/sp.implement` runs.
- 📁 Files: `agents/intake/SOUL.md`, `spec.md`, `data-model.md`, `tasks.md`.
- 🔁 Next prompts: `/sp.implement`, or address the remaining non-blocking `/sp.analyze` findings (G2 — SC-002's statistical claim, I2 — `_template/` convention missing from `plan.md`, L1 — Polish dependency overstatement) if desired first.
- 🧠 Reflection: a mid-edit grep check (`^- \[ \] T\d{3}` with `-o`) caught a non-monotonic ID/file-order mismatch immediately rather than shipping a renumbered tasks.md that read confusingly top-to-bottom — worth doing after any renumbering, not just after the original generation.

## Evaluation notes (flywheel)

- Failure modes observed: initial renumbering pass appended new tasks at the end of their thematic subsection without checking that resulting IDs still increased monotonically through the file — caught via grep with line numbers before finalizing.
- Graders run and results (PASS/FAIL): format/ID-contiguity check via grep — PASS (37/37 unique, contiguous, monotonic); stale-reference check via grep — PASS (no old T0xx IDs remain outside tasks.md).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
