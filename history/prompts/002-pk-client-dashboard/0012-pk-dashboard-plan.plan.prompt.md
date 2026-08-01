---
id: 0012
title: PK client dashboard implementation plan
stage: plan
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: 002-pk-client-dashboard
branch: 002-pk-client-dashboard
user: Asma
command: /sp.plan
labels: [plan, pk-market, dashboard, new-production-code, constitution-check]
links:
  spec: specs/002-pk-client-dashboard/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-pk-client-dashboard/plan.md
 - specs/002-pk-client-dashboard/research.md
 - specs/002-pk-client-dashboard/data-model.md
 - specs/002-pk-client-dashboard/contracts/dashboard-state-schema.json
 - specs/002-pk-client-dashboard/contracts/dashboard-api.md
 - specs/002-pk-client-dashboard/quickstart.md
 - CLAUDE.md
tests:
 - No tests executed in this phase (planning only); quickstart.md documents the pytest suite to be written in /sp.tasks
---

## Prompt

(empty — `/sp.plan` invoked with no arguments, operating on the current feature branch `002-pk-client-dashboard`)

## Response snapshot

Ran `setup-plan.ps1 -Json` to scaffold `plan.md`. Confirmed `backend/` and
`dashboard/` remain empty in this repo (no prior implementation). Made the
key research finding for this feature, a deliberate contrast with feature
001: `skills/remote-dashboard.md` describes the dashboard as "vanilla
HTML/JS" — deterministic web tooling, not LLM-interpreted agent behavior —
so unlike feature 001, this feature genuinely requires new production code
for the read/render side, while the *write* side of `dashboard-state.json`
remains existing Orchestrator behavior needing no new code (`research.md`
Decision 1).

Decided (Decision 2) on a minimal Python 3.11 stdlib `http.server` for the
server, with request-handling logic exposed as plain callable functions so
`pytest` can test it without binding a live socket — no new dependency,
consistent with Constitution Principle II. Decided (Decision 3) to ship the
server standalone on port 18790 rather than blocking on the (not-present-in-
this-repo) MCP Gateway code it's eventually meant to sit alongside.

Filled `plan.md`'s Technical Context (fully resolved) and Constitution
Check: 5 PASS (I, II, III, IV, VIII, IX — six, not five), 3 N/A (Maker/Checker
separation, Gemini quota guard, human approval gate — none apply since this
feature does no classification, Gemini calls, or email sending). Wrote
`data-model.md` (Dashboard State, Recent Lead Entry, and a reused
display-only Approval Queue Entry from feature 001), `contracts/
dashboard-state-schema.json` (JSON Schema for the state document) and
`contracts/dashboard-api.md` (the `GET /state` contract covering FR-011
through FR-014's four response shapes), and `quickstart.md`.

Ran `update-agent-context.ps1 -AgentType claude`; this time `CLAUDE.md` had
the `## Active Technologies`/`## Recent Changes` markers from feature 001's
plan phase, so the script's insertion logic actually fired (unlike feature
001's silent no-op) — but its multi-line-field truncation bug (only
captures the first line of a wrapped Technical Context field) still
produced garbled entries, and it added no `Recent Changes` line for this
feature despite detecting new tech. Cleaned up both issues manually rather
than relying on the script's raw output.

Re-evaluated the Constitution Check after Phase 1 design: unchanged, no new
violations.

## Outcome

- ✅ Impact: full Phase 0/1 planning artifact set for `002-pk-client-dashboard` — `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` — ready for `/sp.tasks`; constitution check passes 6/9 PASS + 3 justified N/A, 0 FAIL.
- 🧪 Tests: none executed (planning phase); `quickstart.md` specifies the `pytest` suite (contract + 4 integration test files) for `/sp.tasks` to implement.
- 📁 Files: see `files` list above.
- 🔁 Next prompts: `/sp.tasks` for this feature; separately, `update-agent-context.ps1`'s multi-line field truncation and missing-Recent-Changes-entry bugs are now confirmed on a second feature and worth fixing at the script level rather than working around each time.
- 🧠 Reflection: verifying the script's output against the actual file content (not just its printed "success" summary) caught a second, different failure mode from feature 001's — this script needs a real fix, not just per-feature manual cleanup, if a third feature is planned soon.

## Evaluation notes (flywheel)

- Failure modes observed: `update-agent-context.ps1`'s `Extract-PlanField` regex only matches a single line after `**Field**: `, truncating any Technical Context value that wraps to a second line; separately, its `Recent Changes` insertion didn't fire this time despite `Active Technologies` insertion working, for reasons not fully diagnosed (worth a closer look if it recurs a third time).
- Graders run and results (PASS/FAIL): Constitution Check — PASS (6/9 PASS, 3 N/A justified, 0 FAIL).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): fix `Extract-PlanField` in `update-agent-context.ps1` to join all lines until the next `**Field**:` marker or blank line, rather than matching only the first line.
