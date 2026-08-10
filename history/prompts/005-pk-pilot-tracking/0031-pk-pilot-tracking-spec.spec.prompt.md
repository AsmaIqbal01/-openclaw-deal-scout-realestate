---
id: 0031
title: PK pilot tracking spec
stage: spec
date: 2026-08-11
surface: agent
model: claude-sonnet-5
feature: 005-pk-pilot-tracking
branch: 005-pk-pilot-tracking
user: AsmaIqbal000
command: /sp.specify
labels: ["spec", "pilot-tracking", "phase-1-gate", "F012"]
links:
  spec: specs/005-pk-pilot-tracking/spec.md
  ticket: null
  adr: adrs/ADR-004-pilots-manual-tracking-boundary.md
  pr: null
files:
 - specs/005-pk-pilot-tracking/spec.md
 - specs/005-pk-pilot-tracking/checklists/requirements.md
tests:
 - none (spec stage; no code yet)
---

## Prompt

Read CONSTITUTION.md and .spec-kit documentation first. Then run /sp.specify for F005 — PILOTS.md pilot tracking system. This should track 4 PK agency onboarding slots with fields matching the tenant template in workspace/tenants/_template/USER.md. Follow the full SpecifyPlus workflow: spec → plan → ADR → tasks → score.

## Response snapshot

Read `CONSTITUTION.md`, `.spec-kit/AGENTS.md`, `.spec-kit/spec-driven.md`,
`agents/spec-scorer/spec-scorer.md`, and
`agents/constitution-checker/constitution-checker.md` before drafting
anything. Before writing the spec, surfaced one genuine architectural fork
via `AskUserQuestion` (per CLAUDE.md's Human-as-Tool trigger for
"Architectural Uncertainty"): should `PILOTS.md` be fully manual, have the
Orchestrator auto-confirm only, or be fully Orchestrator-managed? User chose
fully manual — this decision shaped the entire spec's Scope Decision and
FR-005.

Ran `create-new-feature.ps1 -Number 5 -ShortName "pk-pilot-tracking"`,
creating branch `005-pk-pilot-tracking` and
`specs/005-pk-pilot-tracking/spec.md`. Wrote 3 user stories (P1: summary
line at a glance; P2: record/update a slot through 7 onboarding stages; P3:
unambiguous Phase 1 gate signal at 3-of-4 confirmed), 13 FRs specifying
`PILOTS.md`'s exact schema (11 fields matching
`workspace/tenants/_template/USER.md` + 4 tracking fields), and 5 success
criteria.

Ran a rigorous self-audit against `spec-scorer.md`'s 7 dimensions (not a
casual first-pass score) and found 3 real gaps before scoring: FR-006
(duplicate `tenant_id`) had no stated fallback behavior; no requirement
covered a `tenant_id`/real-`USER.md` mismatch (a Multi-Tenant Awareness
rubric item, closed by adding FR-013); and a literal grep found 3 casual
"may" hedges, including a real inconsistency where the "gate met" summary
line was quoted two different ways in two places — unified to one exact
string. Final score: 10.0/10, documented in `checklists/requirements.md`
with the full dimension breakdown.

## Outcome

- ✅ Impact: spec ready for `/sp.plan` — scored 10.0/10 against the constitution's 9.6/10 gate (Principle IX), no [NEEDS CLARIFICATION] markers, manual-maintenance boundary confirmed with the feature owner before drafting
- 🧪 Tests: N/A (spec stage)
- 📁 Files: `specs/005-pk-pilot-tracking/spec.md`, `specs/005-pk-pilot-tracking/checklists/requirements.md`
- 🔁 Next prompts: `/sp.plan` for feature 005 (completed in the same session — see PHR 0032)
- 🧠 Reflection: asking the manual-vs-automated question before drafting, rather than defaulting silently, avoided writing an entire spec around an assumption the owner might have rejected — worth doing whenever a spec's FR-005-equivalent (a hard architectural boundary) has no clearly correct default

## Evaluation notes (flywheel)

- Failure modes observed: an inconsistent literal-string quote of the same required summary-line text in two different Acceptance Scenarios — caught only by a targeted grep for hedge words that happened to also expose the mismatch, not by reading alone
- Graders run and results (PASS/FAIL): spec-scorer rubric — PASS (10.0/10)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): grep for exact-string requirements (like FR-009's summary line) being quoted identically everywhere they appear, as a standing check before scoring Ambiguity Elimination on future specs
