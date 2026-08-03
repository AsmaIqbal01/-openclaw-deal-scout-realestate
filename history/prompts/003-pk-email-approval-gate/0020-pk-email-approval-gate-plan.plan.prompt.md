---
id: 0020
title: PK email approval gate implementation plan
stage: plan
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: 003-pk-email-approval-gate
branch: 003-pk-email-approval-gate
user: Asma
command: /sp.plan
labels: [plan, pk-market, email-approval, no-new-code, skill-backfill]
links:
  spec: specs/003-pk-email-approval-gate/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/003-pk-email-approval-gate/plan.md
 - specs/003-pk-email-approval-gate/research.md
 - specs/003-pk-email-approval-gate/data-model.md
 - specs/003-pk-email-approval-gate/contracts/approval-queue-schema.json
 - specs/003-pk-email-approval-gate/contracts/email-approval-commands.md
 - specs/003-pk-email-approval-gate/quickstart.md
 - specs/003-pk-email-approval-gate/checklists/requirements.md
 - skills/operator-approval-gate.md
 - CLAUDE.md
tests:
 - No tests executed in this phase (planning only); quickstart.md documents the pytest suite to be written in /sp.tasks
---

## Prompt

(empty — `/sp.plan` invoked with no arguments, operating on the current feature branch `003-pk-email-approval-gate`, after committing the F002 spec retroactive fix separately per the prior instruction)

[mid-turn interjection: "1" — unclear referent, no pending numbered choice was open; acknowledged and continued the plan work uninterrupted]

## Response snapshot

Ran `setup-plan.ps1 -Json` to scaffold `plan.md`. Confirmed this feature is
Delivery Sub-Agent behavior already described in
`skills/operator-approval-gate.md` and `agents/delivery/SOUL.md` Step 4 —
like feature 001, not feature 002 — so `research.md` Decision 1 concludes
no new agent-logic code is needed.

Made one concrete planning-time fix: the spec's rigorous rescore (PHR 0019)
had added two requirements — FR-007/FR-009's WhatsApp-send and email-send
retry semantics — that weren't originally in `skills/operator-approval-
gate.md`'s Error Handling section. Rather than let the spec state behavior
the source skill file stays silent on (the same class of drift ADR-002
exists to prevent for feature 001), extended `operator-approval-gate.md`'s
Error Handling section now, during planning, with both retry rules,
cross-referencing the equivalent patterns already in `agents/delivery/
SOUL.md` (`research.md` Decision 2). Also confirmed (Decision 3) the actual
email-send mechanism is the existing `brevo` ClawHub skill named in
`workspace/TOOLS.md`, not a new tool decision.

Filled `plan.md`'s Technical Context (fully resolved) and Constitution
Check: 7 PASS (including Principle VII, exercised for the first time) and
1 N/A (Gemini quota guard — no Gemini calls in this feature). Wrote
`data-model.md` (Approval Queue Entry with a full state-transition diagram
including the `send_failed` branch; Email Draft as a conceptual, not
separately-persisted, entity), `contracts/approval-queue-schema.json`, and
`contracts/email-approval-commands.md` (explicitly distinguished from
feature 001's `/confirm`/`/discard` contract — different commands, different
purpose), and `quickstart.md`.

Ran `update-agent-context.ps1 -AgentType claude`; cleaned up its output
manually as with the previous two features (multi-line field truncation is
a known, unfixed bug in that script), adding a third `Recent Changes` entry
alongside features 001 and 002.

Re-evaluated the Constitution Check after Phase 1 design: unchanged, no new
violations.

## Outcome

- ✅ Impact: full Phase 0/1 planning artifact set for `003-pk-email-approval-gate` — `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` — ready for `/sp.tasks`; constitution check passes 7/8 PASS + 1 justified N/A, 0 FAIL. `skills/operator-approval-gate.md` extended (not rewritten) to stay in sync with the spec.
- 🧪 Tests: none executed (planning phase); `quickstart.md` specifies the `pytest` suite extending `tests/pipeline_sim.py` for `/sp.tasks` to implement.
- 📁 Files: see `files` list above.
- 🔁 Next prompts: `/sp.tasks` for this feature.
- 🧠 Reflection: catching the spec-vs-skill-file drift risk *during planning* (before it ever became a `/sp.analyze` finding, unlike feature 001's I1) validates that the rigorous-rescore discipline from this session's F002/F003 audit is already paying for itself — a gap that would otherwise have surfaced later got closed at the cheapest possible point.

## Evaluation notes (flywheel)

- Failure modes observed: `update-agent-context.ps1`'s known multi-line-field truncation recurred a third time; manually cleaned up as established practice, still not fixed at the script level.
- Graders run and results (PASS/FAIL): Constitution Check — PASS (7/8 PASS, 1 N/A justified, 0 FAIL).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
