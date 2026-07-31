---
id: 0001
title: Deal Scout Real Estate Constitution
stage: constitution
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: none
branch: master
user: Asma
command: /sp.constitution
labels: [constitution, deal-scout, multi-tenant, non-negotiables, zero-cost]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
 - history/prompts/constitution/0001-deal-scout-constitution.constitution.prompt.md
tests:
 - Constitution Compliance Test Cases section (4 named cases: quota guard boundary, cross-tenant rejection, unapproved email block, market sequencing gate) — governance document, no automated suite executed
---

## Prompt

Deal Scout Real Estate SaaS — PK first, UK second. Read workspace/IDENTITY.md, workspace/AGENTS.md, agents/orchestrator/SOUL.md, agents/spec-scorer/spec-scorer.md first. Apply these non-negotiables: zero infrastructure cost, WhatsApp input+output for PK, Gmail+Discord for UK, OpenClaw as orchestrator, 9.6/10 minimum spec score, maker/checker split enforced, Gemini quota guard at 18/day, operator approval for all client emails, no tenant data leakage, 3 PK agencies before UK launch. No Lisbon references — this is a real client-delivery SaaS. Score the result against the spec-scorer rubric and iterate until 9.6/10.

## Response snapshot

Read workspace/IDENTITY.md, workspace/AGENTS.md, agents/orchestrator/SOUL.md,
agents/spec-scorer/spec-scorer.md, agents/constitution-checker/constitution-checker.md,
agents/delivery/SOUL.md, agents/intake/SOUL.md, and the existing plan/spec/tasks
templates before drafting. Filled the placeholder constitution at
`.specify/memory/constitution.md` with 9 non-negotiable Core Principles (PK-First
Market Sequencing, Zero Infrastructure Cost, Market-Native Channel Fidelity,
OpenClaw as Sole Runtime Orchestrator, Maker/Checker Separation, Gemini Quota
Guard, Human Approval Gate for Client-Facing Communication, Multi-Tenant Data
Isolation, Spec Quality Gate 9.6/10), plus "Delivery & Documentation Discipline,"
"Development Workflow & Quality Gates," a new "Constitution Compliance Test
Cases" section (4 cases with input/expected output/edge case, added specifically
to satisfy the Spec Scorer's Test Coverage Intent dimension), and Governance.
Ratified as v1.0.0 (initial adoption — template had no prior ratified version),
dated 2026-08-01.

Swept the draft for rubric-flagged ambiguous terms ("may", "should", "TBD") and
rewrote 7 instances to MUST/MUST NOT phrasing. Self-scored against the
spec-scorer 7-dimension rubric (adapted to a governance document rather than a
feature spec): Interface Precision 2.0/2.0, Error Path Coverage 2.0/2.0,
Ambiguity Elimination 1.5/1.5, Market Specificity 1.5/1.5, Test Coverage Intent
1.5/1.5 (after adding the compliance test-case section), Multi-Tenant Awareness
1.0/1.0, Business Gate Linkage 0.5/0.5 — total ~10.0/10, above the 9.6 floor.

Flagged (not edited, out of scope): `workspace/IDENTITY.md` lines 36-39 ("Lisbon
/ Visa Evidence Trail") conflicts with the "real client-delivery SaaS" framing
required by this constitution's Delivery & Documentation Discipline section —
recorded as a follow-up TODO in the constitution's Sync Impact Report.
Confirmed no command files exist under `.specify/templates/commands/*.md` and
that plan/spec/tasks templates need no edits (they read the constitution
dynamically / remain generic-compatible).

## Outcome

- ✅ Impact: `.specify/memory/constitution.md` ratified as v1.0.0 with 9 enforceable, testable principles covering every non-negotiable in the request.
- 🧪 Tests: Constitution Compliance Test Cases section added (4 cases: quota boundary, cross-tenant rejection, unapproved-email block, market-sequencing gate).
- 📁 Files: `.specify/memory/constitution.md` (rewritten), this PHR.
- 🔁 Next prompts: consider `/sp.adr` for the OpenClaw-as-sole-orchestrator decision if not already documented; follow-up edit to `workspace/IDENTITY.md` to remove Lisbon/visa framing.
- 🧠 Reflection: the spec-scorer rubric's Test Coverage Intent dimension doesn't map naturally onto a constitution — closed the gap by adding a dedicated compliance-test-case section rather than forcing unrelated content into existing principles.

## Evaluation notes (flywheel)

- Failure modes observed: initial draft used "may" in 7 places, which the rubric's Ambiguity Elimination dimension explicitly penalizes; caught via a targeted grep sweep before finalizing.
- Graders run and results (PASS/FAIL): self-applied spec-scorer rubric — PASS (~10.0/10, threshold 9.6/10).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
