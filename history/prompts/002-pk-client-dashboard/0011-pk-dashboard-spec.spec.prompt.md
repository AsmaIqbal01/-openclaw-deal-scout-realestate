---
id: 0011
title: PK client dashboard spec
stage: spec
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: 002-pk-client-dashboard
branch: 002-pk-client-dashboard
user: Asma
command: /sp.specify
labels: [spec, pk-market, dashboard, multi-tenant, read-only-approval]
links:
  spec: specs/002-pk-client-dashboard/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-pk-client-dashboard/spec.md
 - specs/002-pk-client-dashboard/checklists/requirements.md
tests:
 - 3 Independent Test cases (one per user story), each with input/expected-output/edge-case
---

## Prompt

Run /sp.specify for the second PK feature

## Response snapshot

Scoped "second PK feature" as F009 — PK Client Dashboard, based on
`skills/remote-dashboard.md`, which already fully specifies a dashboard
state schema and 8 sections but had never been built as a feature. Checked
for an existing F009 definition anywhere in the repo first (none found) —
this scoping is a reasoned choice, not a pre-existing requirement: the
dashboard is the natural next need after feature 001 made the pipeline work
invisibly, is explicitly gated by Constitution Checker gate I4 ("Dashboard
remains client-accessible"), and is referenced in `workspace/HEARTBEAT.md`'s
execution order.

Ran `create-new-feature.ps1 -Number 2 -ShortName "pk-client-dashboard"` —
confirmed the earlier PowerShell 5.1 `Join-Path` fix held: both
`specs/002-pk-client-dashboard/` and `history/prompts/002-pk-client-dashboard/`
were created cleanly this time, no manual workaround needed.

Made one explicit scope-narrowing decision, documented in the spec's own
"Scope Decision" section rather than left ambiguous: `remote-dashboard.md`'s
Approval Queue section describes email-draft approve/reject buttons, but
email drafting (`operator-approval-gate.md`) is a separate, unbuilt feature.
Rescoped the Approval Queue as read-only, showing feature 001's Tier 2
held-for-review leads and their time-to-timeout, keeping WhatsApp as the
sole confirm/discard channel per Constitution Principle III. Cloudflare
Tunnel provisioning (one-time server setup) was also placed out of scope.

Wrote 3 prioritized user stories (P1 pipeline status/quota at a glance, P2
Score Radar understanding, P3 read-only Tier-2-queue visibility), 6 edge
cases, 14 functional requirements, 3 key entities, and 5 success criteria —
all derived from `skills/remote-dashboard.md`'s existing schema/sections and
feature 001's `data-model.md`, so zero `[NEEDS CLARIFICATION]` markers were
needed. Created the requirements checklist (all 15 items pass).

Self-scored against the spec-scorer rubric: Interface Precision 1.8/2.0
(same structural cap as feature 001 — the spec-template's "no APIs" rule
prevents literal endpoint definitions), Error Path Coverage 2.0/2.0, Ambiguity
Elimination 1.5/1.5, Market Specificity 1.5/1.5, Test Coverage Intent 1.5/1.5,
Multi-Tenant Awareness 1.0/1.0, Business Gate Linkage 0.5/0.5 — **9.8/10,
PASS** on first pass, no rewrite iteration needed.

## Outcome

- ✅ Impact: `specs/002-pk-client-dashboard/spec.md` ready for `/sp.plan`; branch `002-pk-client-dashboard` checked out; scored 9.8/10 against the spec-scorer rubric.
- 🧪 Tests: requirements checklist fully passing; 3 Independent Test cases with explicit edge-case labels.
- 📁 Files: `specs/002-pk-client-dashboard/spec.md`, `specs/002-pk-client-dashboard/checklists/requirements.md`, this PHR.
- 🔁 Next prompts: `/sp.plan` for this feature.
- 🧠 Reflection: documenting a scope-narrowing choice explicitly in the spec (the "Scope Decision" section) rather than leaving it as an implicit assumption kept it from reading as a [NEEDS CLARIFICATION] gap during self-scoring, and gives a future reader the "why" without needing to cross-reference two other skill files.

## Evaluation notes (flywheel)

- Failure modes observed: none — the earlier PowerShell 5.1 fix (`history/prompts/general/0005-...`) verified working on the first real re-use.
- Graders run and results (PASS/FAIL): self-applied spec-scorer rubric — PASS (9.8/10, threshold 9.6/10).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
