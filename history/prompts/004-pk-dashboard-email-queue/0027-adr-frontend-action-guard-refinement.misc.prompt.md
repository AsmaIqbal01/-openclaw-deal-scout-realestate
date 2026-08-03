---
id: 0027
title: ADR frontend action guard refinement
stage: misc
date: 2026-08-03
surface: agent
model: claude-opus-5[1m]
feature: 004-pk-dashboard-email-queue
branch: 004-pk-dashboard-email-queue
user: AsmaIqbal000
command: /sp.adr
labels: ["adr", "dashboard-extension", "testing-infrastructure"]
links:
  spec: specs/004-pk-dashboard-email-queue/spec.md
  ticket: null
  adr: adrs/ADR-004-frontend-action-guard-pattern-refinement.md
  pr: null
files:
 - adrs/ADR-004-frontend-action-guard-pattern-refinement.md
tests:
 - none (documentation only; no code changed yet)
---

## Prompt

run /sp.adr refine-frontend-action-guard-pattern

## Response snapshot

Ran `check-prerequisites.ps1 -Json` to confirm `plan.md` exists for
004-pk-dashboard-email-queue. No `create-adr.sh` exists in this repo (the
skill's generic instructions assume one), and this project's actual ADRs
live in `adrs/` at repo root, not `history/adr/` as the skill's generic
template assumes — created the file agent-natively at
`adrs/ADR-004-frontend-action-guard-pattern-refinement.md`, matching the
exact structure of the 3 existing ADRs (Scope blockquote, Status/Date/
Feature/Context, significance-checklist comment, Decision, Consequences
Positive/Negative, Alternatives Considered, References).

Applied the significance test from `research.md` Decision 3: impact
(long-term — governs how every future dashboard section satisfies
Constitution Principle VII), alternatives (3 considered: rename the label,
add a parallel guard test, drop the check entirely), scope (cross-cutting —
spans features 002 and 004's shared test infrastructure). All three true,
so this qualified as a real ADR rather than a PHR-only note — single
decision cluster, not over-granular.

Documented the decision: keep "Rejected" as the display label (no rename,
avoids reintroducing terminology drift `/sp.analyze` has caught before),
refine `test_no_approval_actions_in_frontend.py` from a bare-substring ban
to an actionable-pattern check (`reject(?!ed)` regex plus endpoint-path/
button/form/onclick patterns) that is strictly at least as strong as the
original, one test extended in place rather than a second parallel guard.
Cross-referenced ADR-003 (which introduced the original guard test) as the
decision this one extends, not reverses.

## Outcome

- ✅ Impact: architectural decision now has a permanent, reviewable record before the guard test is actually refined in implementation
- 🧪 Tests: N/A (documentation stage; the refined test itself is implementation work, not yet done)
- 📁 Files: `adrs/ADR-004-frontend-action-guard-pattern-refinement.md` (new)
- 🔁 Next prompts: `/sp.tasks` for feature 004 (the refined guard test becomes a concrete task), or implementation directly
- 🧠 Reflection: this ADR only exists because planning was grounded in the actual existing test file rather than the spec alone — worth continuing to read the real code a plan will touch before finalizing it, not just the spec/contracts

## Evaluation notes (flywheel)

- Failure modes observed: the skill's generic workflow assumed `create-adr.sh` and `history/adr/` exist in every project — neither does here; fell back to agent-native file creation matching this repo's actual established `adrs/` convention rather than creating a new, inconsistent directory
- Graders run and results (PASS/FAIL): significance test (3-part) — PASS; anti-over-granularity check — PASS (one decision cluster, not split into separate ADRs for label-naming vs. test-refinement)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
