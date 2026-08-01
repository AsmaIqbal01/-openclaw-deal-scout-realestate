---
id: 0010
title: ADR test simulation pattern
stage: misc
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: 001-pk-lead-intake-notify
branch: 001-pk-lead-intake-notify
user: Asma
command: /sp.adr
labels: [adr, testing-pattern, constitution-checker-followup]
links:
  spec: specs/001-pk-lead-intake-notify/spec.md
  ticket: null
  adr: adrs/ADR-002-openclaw-agent-test-simulation-pattern.md
  pr: null
files:
 - adrs/ADR-002-openclaw-agent-test-simulation-pattern.md
tests:
 - none (documentation only)
---

## Prompt

Yes, run /sp.adr now

(follow-up to the Constitution Checker report flagging Q3 FAIL — no ADR existed for this feature's architectural decisions — and the ADR-suggestion prompt for the test-simulation pattern + threshold reconciliation)

## Response snapshot

Ran `check-prerequisites.ps1 -Json`, confirmed `plan.md` exists. Scanned
`history/adr/` (empty/nonexistent) and found the repo's actual ADR
precedent at `adrs/ADR-001-secrets-hardening.md` instead — a location
mismatch with the constitution's stated `history/adr/` convention, noted but
not reconciled here (out of scope). No `create-adr.sh` at
`.specify/scripts/bash/` (only inside the vendored `.spec-kit` submodule), so
fell back to agent-native creation using `.specify/templates/adr-template.md`.

Applied the clustering rule from the command: two candidate decisions
(the test-simulation pattern, and the Intake/Delivery threshold
reconciliation from `/sp.analyze` finding I1) were evaluated separately.
The threshold fix alone failed the significance bar as a standalone ADR
(a single number change, already fully captured in PHR 0008) — folded it
into the test-simulation ADR's Context as the motivating incident instead of
creating a second, over-granular ADR.

Created `adrs/ADR-002-openclaw-agent-test-simulation-pattern.md` (Accepted):
documents the decision to build `tests/pipeline_sim.py` as a test-only,
never-in-production re-implementation of the exact rules already in
`agents/*/SOUL.md`/`skills/*.md`, so `pytest` can verify OpenClaw-agent
behavior without live calls or quota spend. Filled Decision, Consequences
(positive: CI-testable at zero cost, the I1-style drift becomes an automated
regression check, reusable pattern for future features; negative:
dual-maintenance risk between Python and markdown, doesn't prove the LLM
itself follows the rules at runtime, risk of the file being mistaken for
production code), 3 Alternatives Considered (manual-only verification, live
sandbox integration tests, a custom backend service — each rejected with
reasoning), and References (spec/plan/research, PHRs 0008/0009,
constitution principles/gates).

Verified against the command's Measure checklist: decision clusters/impacts
multiple components (not trivial) ✅, lists ≥1 alternative with rationale
✅ (3 listed) ✅, clear pros/cons for chosen approach and alternatives ✅,
concise but sufficiently detailed ✅. No conflicts with ADR-001 (unrelated
topic).

## Outcome

- ✅ Impact: ADR-002 created, resolving the Constitution Checker's Q3 FAIL for feature 001-pk-lead-intake-notify.
- 🧪 Tests: none (documentation-only step).
- 📁 Files: `adrs/ADR-002-openclaw-agent-test-simulation-pattern.md`.
- 🔁 Next prompts: re-run the Constitution Checker gate to confirm Q3 now passes and the feature clears for merge.
- 🧠 Reflection: applying the clustering/significance test caught an over-granular-ADR failure mode before it happened — the threshold fix alone didn't clear the bar standalone, and folding it into the pattern ADR's context kept it from being lost while avoiding a trivial second ADR.

## Evaluation notes (flywheel)

- Failure modes observed: `history/adr/` (constitution's stated path) vs. `adrs/` (actual repo precedent) location mismatch — flagged, not fixed, since reconciling it wasn't requested and touches conventions beyond this feature.
- Graders run and results (PASS/FAIL): command's own Measure checklist — PASS (4/4 criteria met).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
