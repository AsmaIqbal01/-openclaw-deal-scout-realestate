---
id: 0006
title: PK lead intake implementation plan
stage: plan
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: 001-pk-lead-intake-notify
branch: 001-pk-lead-intake-notify
user: Asma
command: /sp.plan
labels: [plan, pk-market, openclaw, no-new-code, pytest, constitution-check]
links:
  spec: specs/001-pk-lead-intake-notify/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-pk-lead-intake-notify/plan.md
 - specs/001-pk-lead-intake-notify/research.md
 - specs/001-pk-lead-intake-notify/data-model.md
 - specs/001-pk-lead-intake-notify/contracts/lead-schema.json
 - specs/001-pk-lead-intake-notify/contracts/approval-commands.md
 - specs/001-pk-lead-intake-notify/quickstart.md
 - CLAUDE.md
tests:
 - No tests executed in this phase (planning only); quickstart.md documents the pytest suite to be written in /sp.tasks
---

## Prompt

(empty — `/sp.plan` invoked with no arguments, operating on the current feature branch `001-pk-lead-intake-notify`)

## Response snapshot

Ran `.specify/scripts/powershell/setup-plan.ps1 -Json` to get FEATURE_SPEC/
IMPL_PLAN/SPECS_DIR/BRANCH and scaffold `plan.md`. Loaded `spec.md` and
`.specify/memory/constitution.md`, then cross-checked every functional
requirement in the spec against the existing `agents/*/SOUL.md` and PK skill
files (`zameen-parser.md`, `pk-whatsapp-lead.md`, `lead-classifier-pk.md`,
`multi-tenant-router.md`) line-by-line — all FRs were already satisfied by
existing content, so `research.md` Decision 1 concludes no new agent-logic
code is needed; the engineering work is per-tenant configuration plus a
fixture-based test suite (Decision 2: Python 3.11 + pytest, no live external
calls, to avoid spending real Gemini quota or requiring paid sandbox
credentials during testing).

Filled `plan.md`'s Technical Context (fully resolved, no
`NEEDS CLARIFICATION` markers) and Constitution Check (9 principles
evaluated: 8 PASS, 1 N/A — Human Approval Gate for Client-Facing
Communication, since this feature has no email-send path). Wrote
`data-model.md` (4 entities: Lead, Tenant, Pipeline Run, Approval Queue
Entry, with fields/validation/state transitions), `contracts/lead-schema.json`
(JSON Schema for the Intake→Delivery contract, FR-004) and
`contracts/approval-commands.md` (the WhatsApp `/confirm` `/discard` command
contract, FR-006–008), and `quickstart.md` (manual verification steps per
user story plus the automated pytest invocation).

Ran `update-agent-context.ps1 -AgentType claude` to update `CLAUDE.md`; it
reported success but its marker-based insertion logic (looking for literal
`## Active Technologies` / `## Recent Changes` headings) silently no-op'd
because this project's custom `CLAUDE.md` has neither heading — confirmed via
`git diff` showing no actual change despite the "success" message. Its field
extraction also truncates multi-line plan fields to their first line (visible
in the script's own log output). Rather than rely on the broken automation,
added the two missing sections to `CLAUDE.md` manually with accurate,
non-truncated content. Did not attempt to fix the script itself — separate,
out-of-scope maintenance task, noted as a follow-up.

Re-evaluated the Constitution Check after Phase 1 design: unchanged, no new
violations (no new services, no new orchestration layer, no paid
infrastructure, no channel other than WhatsApp for PK).

## Outcome

- ✅ Impact: full Phase 0/1 planning artifact set for `001-pk-lead-intake-notify` — `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` — ready for `/sp.tasks`; constitution check passes 8/9 with 1 justified N/A.
- 🧪 Tests: none executed (planning phase); `quickstart.md` specifies the `pytest tests/contract tests/integration` suite for `/sp.tasks` to implement.
- 📁 Files: see `files` list above.
- 🔁 Next prompts: `/sp.tasks` for this feature; separately, `update-agent-context.ps1`'s marker-detection should be made to warn (not silently succeed) when its expected headings are absent from the target file — noted, not fixed, since out of scope for this planning step.
- 🧠 Reflection: verifying the script's claimed success against `git diff` caught a silent no-op that would otherwise have left `CLAUDE.md` stale while every future `/sp.plan` run kept reporting "success."

## Evaluation notes (flywheel)

- Failure modes observed: `update-agent-context.ps1` reports "Updated existing Claude Code context file" even when its anchor-based insertion finds no matching headings and makes zero changes — a false-positive success signal.
- Graders run and results (PASS/FAIL): Constitution Check — PASS (8/9 principles PASS, 1 N/A with stated justification, 0 FAIL).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): have `Update-ExistingAgentFile` in `update-agent-context.ps1` emit a warning when it completes without finding `## Active Technologies` or `## Recent Changes` in the target file, instead of reporting unconditional success.
