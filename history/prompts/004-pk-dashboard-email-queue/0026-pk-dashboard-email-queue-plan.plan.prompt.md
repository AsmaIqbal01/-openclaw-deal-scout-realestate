---
id: 0026
title: PK dashboard email queue plan
stage: plan
date: 2026-08-03
surface: agent
model: claude-opus-5[1m]
feature: 004-pk-dashboard-email-queue
branch: 004-pk-dashboard-email-queue
user: AsmaIqbal000
command: /sp.plan
labels: ["plan", "dashboard-extension", "email-approval-gate", "F011"]
links:
  spec: specs/004-pk-dashboard-email-queue/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/004-pk-dashboard-email-queue/plan.md
 - specs/004-pk-dashboard-email-queue/research.md
 - specs/004-pk-dashboard-email-queue/data-model.md
 - specs/004-pk-dashboard-email-queue/quickstart.md
 - specs/004-pk-dashboard-email-queue/contracts/email-draft-queue-response.md
 - CLAUDE.md
tests:
 - none (plan stage; no code yet)
---

## Prompt

continue with /sp.plan

## Response snapshot

Ran `setup-plan.ps1 -Json`, read the copied `plan.md` template, the spec,
the constitution, and — critically — the actual production code this
feature extends (`dashboard/server.py`, `dashboard/index.html`) rather than
planning against the spec alone, since this feature (like 002, unlike
001/003) touches genuine production code, not agent-logic markdown.

Filled Technical Context and the Constitution Check table (Principle VII
now PASS rather than 002's N/A, since this feature directly displays
email-draft state — FR-005/FR-006 enforce the gate mechanically). Zero
violations; Complexity Tracking left empty.

Discovered a real conflict while grounding the plan in the actual
`dashboard/` code: `tests/integration/test_no_approval_actions_in_frontend.py`
(feature 002) bans the bare substring "reject" anywhere in the frontend,
case-insensitive — which would collide with legitimately displaying a
"Rejected" status label (spec.md FR-003, matching feature 003's own
`rejected` field/response-code naming throughout). Resolved this as
`research.md` Decision 3: keep the "Rejected" label (no spec change, avoids
reintroducing the terminology-drift pattern `/sp.analyze` has caught
before), and refine the guard test from a substring ban to an
actionable-pattern check (endpoint paths, `<button>`/`<form>`/`onclick=`,
and a `reject(?!ed)` regex) that still catches every real action leak the
original did, plus ones it would've missed, while allowing the legitimate
status word. Flagged this as a cross-cutting, alternatives-considered,
long-term-consequence decision — qualifies for an ADR suggestion per
CLAUDE.md's three-part test.

Wrote `research.md` (3 decisions), `data-model.md` (Email Draft Queue
response wrapper + Enriched Entry, built on feature 003's entity, per the
existing `_enrich()` server-side pattern), `contracts/email-draft-queue-response.md`
(extends feature 002's existing endpoint contract, no new endpoint), and
`quickstart.md`. Ran `update-agent-context.ps1 -AgentType claude`, then
manually fixed two mid-sentence-truncated lines its regex extraction
produced in `CLAUDE.md`'s Active Technologies section, and added proper
Recent Changes entries for both 003 and 004 (003 was missing from that
section entirely).

## Outcome

- ✅ Impact: plan complete and internally consistent; ready for `/sp.tasks`
- 🧪 Tests: N/A (plan stage)
- 📁 Files: plan.md, research.md, data-model.md, quickstart.md, contracts/email-draft-queue-response.md (all new), CLAUDE.md (Active Technologies/Recent Changes updated + truncation fixed)
- 🔁 Next prompts: surface the ADR suggestion for Decision 3 to the user (pending, see below); `/sp.tasks` once the user is ready
- 🧠 Reflection: reading the actual dashboard/server.py and the existing guard test before writing the plan (rather than planning purely from spec.md) is what surfaced the reject/Rejected collision — a plan written spec-only would have missed it until implementation broke the existing test

## Evaluation notes (flywheel)

- Failure modes observed: `update-agent-context.ps1`'s regex-based line extraction truncated two Technical Context lines mid-sentence when writing CLAUDE.md — caught by reading the file back immediately rather than trusting the script's success message
- Graders run and results (PASS/FAIL): N/A — plan stage, not independently scored (spec-scorer only runs pre-plan)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
