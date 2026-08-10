---
id: 0032
title: PK pilot tracking plan
stage: plan
date: 2026-08-11
surface: agent
model: claude-sonnet-5
feature: 005-pk-pilot-tracking
branch: 005-pk-pilot-tracking
user: AsmaIqbal000
command: /sp.plan
labels: ["plan", "pilot-tracking", "phase-1-gate", "F012"]
links:
  spec: specs/005-pk-pilot-tracking/spec.md
  ticket: null
  adr: adrs/ADR-004-pilots-manual-tracking-boundary.md
  pr: null
files:
 - specs/005-pk-pilot-tracking/plan.md
 - specs/005-pk-pilot-tracking/research.md
 - specs/005-pk-pilot-tracking/data-model.md
 - specs/005-pk-pilot-tracking/quickstart.md
 - specs/005-pk-pilot-tracking/contracts/pilot-slot-schema.json
tests:
 - none (plan stage; tests specified but not yet written — see tasks.md, PHR 0034)
---

## Prompt

(Continuation of the same multi-stage request: "Follow the full SpecifyPlus workflow: spec → plan → ADR → tasks → score.")

## Response snapshot

Filled the Technical Context section mostly with "N/A for runtime
behavior" since this feature introduces no source code in `agents/`,
`dashboard/`, or `skills/` — the only engineering artifact is one
structural `pytest` contract test. Ran the Constitution Check against all 9
numbered Principles from `.specify/memory/constitution.md` (not
`CONSTITUTION.md`'s I1-I5/A1-A8/Q1-Q5/B1-B3 gate IDs, which apply at merge
time via the Constitution Checker, not at plan time): 4 PASS (I, II, IV,
VIII), 4 N/A (III, V, VI, VII — no channel, no lead classification, no
Gemini calls, no client-facing email touched), 1 PASS on the spec-quality
gate itself (IX, citing the 10.0/10 score). No violations, empty Complexity
Tracking table.

Wrote `research.md` with 3 decisions: (1) manual-only maintenance, no
runtime write path — the load-bearing one, with 2 rejected alternatives
(Orchestrator auto-confirms only; fully Orchestrator-managed); (2) slot
data as fenced JSON blocks inside `PILOTS.md`, validated by one new
contract test — chosen over a Markdown table (unreadable at 15 fields/row)
or no validation at all (would leave 4 spec `MUST` requirements
unverifiable); (3) fixed 4 slots, not growable — given directly in the
feature description, not inferred.

`data-model.md` documents the Pilot Slot entity (16 fields, state
transition diagram from `not_started` through `confirmed`, with
`withdrawn` as the only non-terminal reachable-from-anywhere state) and the
document-level summary-line contract. `contracts/pilot-slot-schema.json`
encodes FR-002/003/004's exact schema as JSON Schema, including a
conditional (`allOf`/`if`/`then`) requiring `first_notification_delivered_at`
and `source_run_id` whenever `onboarding_status == "confirmed"` — making
FR-004's precondition mechanically enforceable by `jsonschema.validate`,
not just documented. `quickstart.md` gives 3 manual-check walkthroughs (one
per user story) plus the automated-suite command.

## Outcome

- ✅ Impact: plan ready for ADR/tasks — Constitution Check clean (4 PASS, 4 N/A, 1 PASS on the spec-quality gate), no complexity violations to justify
- 🧪 Tests: N/A (plan stage; `contracts/pilot-slot-schema.json` written but no test file yet — see PHR 0034)
- 📁 Files: `specs/005-pk-pilot-tracking/{plan.md,research.md,data-model.md,quickstart.md,contracts/pilot-slot-schema.json}`
- 🔁 Next prompts: ADR for the manual-tracking-boundary decision (completed in the same session — see PHR 0033), then `/sp.tasks` (PHR 0034)
- 🧠 Reflection: encoding FR-004's confirmation precondition as a JSON Schema conditional (`allOf`/`if`/`then`) rather than only prose meant the "verifiable confirmation, not self-report" requirement from the spec became something `jsonschema.validate` actually enforces at test time, closing the gap between what the spec says MUST happen and what the one automated check can actually catch

## Evaluation notes (flywheel)

- Failure modes observed: none — the plan.md Constitution Check table's principle numbering (I-IX, from `.specify/memory/constitution.md`) initially risked being confused with `CONSTITUTION.md`'s different I1-I5/A1-A8 gate-ID numbering; resolved by reading both files before writing the table, matching feature 004's plan.md precedent exactly
- Graders run and results (PASS/FAIL): Constitution Check — PASS (0 violations)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
