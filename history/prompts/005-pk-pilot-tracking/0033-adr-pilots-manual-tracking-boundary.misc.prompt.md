---
id: 0033
title: ADR pilots manual tracking boundary
stage: misc
date: 2026-08-11
surface: agent
model: claude-sonnet-5
feature: 005-pk-pilot-tracking
branch: 005-pk-pilot-tracking
user: AsmaIqbal000
command: /sp.adr
labels: ["adr", "pilot-tracking", "architecture-boundary"]
links:
  spec: specs/005-pk-pilot-tracking/spec.md
  ticket: null
  adr: adrs/ADR-004-pilots-manual-tracking-boundary.md
  pr: null
files:
 - adrs/ADR-004-pilots-manual-tracking-boundary.md
tests:
 - none (ADR stage; no code)
---

## Prompt

(Continuation of the same multi-stage request: "Follow the full SpecifyPlus workflow: spec → plan → ADR → tasks → score.")

## Response snapshot

Ran the three-part ADR significance test from CLAUDE.md against `plan.md`'s
decisions: Impact (yes — sets a boundary future features must respect or
formally amend), Alternatives (yes — 3 maintenance models considered before
the spec was even drafted, per PHR 0031's `AskUserQuestion`), Scope
(cross-cutting — touches `CONSTITUTION.md` Section 3's `MEMORY.md`-I/O
boundary and Principle IV's "no second orchestrator" guarantee). All 3
true, so an ADR was written (the user's explicit instruction to include
"ADR" in this session's workflow was itself standing consent — no separate
confirmation prompt was needed for this particular ADR).

Wrote `ADR-004-pilots-manual-tracking-boundary.md` as a decision cluster
(matching ADR-003's precedent of grouping related decisions rather than
one ADR per micro-choice): the primary decision (manual-only maintenance,
isolation by construction, verifiable-not-self-reported confirmation) plus
the supporting decision (fenced-JSON format + one structural contract test)
that exists only to make the primary decision auditable. Explicitly scoped
out the fixed-4-slot sizing choice as a minor corollary, not a separate
decision, following the same anti-over-granularity discipline ADR-003's
Scope note demonstrated.

Documented both rejected alternatives with their real tradeoffs (Orchestrator
auto-confirms only; fully Orchestrator-managed) and one honestly-stated
Negative consequence: the contract test can verify a `source_run_id` is
present and well-formed but cannot verify it corresponds to a real
`MEMORY.md` entry, since by design no runtime access exists — an accepted
risk at this single-founder, pre-revenue stage, not a solved problem.

## Outcome

- ✅ Impact: ADR-004 accepted and cross-referenced from `plan.md`'s Constitution Check and `research.md` Decision 1; closes Constitution Checker gate Q3 ahead of any future implementation of this feature
- 🧪 Tests: N/A (ADR stage)
- 📁 Files: `adrs/ADR-004-pilots-manual-tracking-boundary.md`
- 🔁 Next prompts: `/sp.tasks` for feature 005 (completed in the same session — see PHR 0034)
- 🧠 Reflection: naming the accepted risk (self-reported `source_run_id` can't be runtime-verified by the manual-only design) directly in Consequences, rather than only in the spec's Assumptions, keeps the tradeoff visible at the architectural-decision layer where a future reader deciding whether to revisit this ADR would actually look first

## Evaluation notes (flywheel)

- Failure modes observed: none — checked `adrs/` directory before numbering and confirmed no `ADR-004` file existed yet, despite `history/prompts/004-pk-dashboard-email-queue/0028-retract-adr-004-guard-test-unneeded.explainer.prompt.md` referencing an "ADR-004" that was drafted and retracted during feature 004's planning without ever being written to disk — avoided a false assumption that the number was taken
- Graders run and results (PASS/FAIL): ADR significance test — PASS (all 3 criteria true)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
