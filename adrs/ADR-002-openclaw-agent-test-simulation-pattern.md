# ADR-002: Test-Only Pipeline Simulation Pattern for OpenClaw Agent Features

> **Scope**: Decision cluster covering how Deal Scout tests OpenClaw-agent-driven
> pipeline behavior (Orchestrator/Intake/Delivery) without a live runtime,
> live LLM calls, or live external API calls — not a single technology choice.

- **Status:** Accepted
- **Date:** 2026-08-01
- **Feature:** 001-pk-lead-intake-notify
- **Context:** Deal Scout's Orchestrator, Intake, and Delivery agents are
  OpenClaw agents whose entire behavior lives in `agents/*/SOUL.md` and
  `skills/*.md` markdown, interpreted by the OpenClaw runtime — there is no
  callable Python/production code implementing this logic
  (`specs/001-pk-lead-intake-notify/research.md` Decision 1 deliberately
  avoided writing new agent-logic code, to not duplicate what SOUL.md already
  specifies). At the same time, Constitution Principle IX / Constitution
  Checker gate Q2 requires automated tests proving functional requirements,
  and Principles II/VI (zero infrastructure cost, Gemini quota guard) forbid
  tests that make live Gemini/HubSpot/WhatsApp calls or spend real quota.
  This is a structural gap: there was no way to write a meaningfully
  assertive, CI-runnable test suite for behavior that only exists as
  LLM-interpreted markdown, without either paying for live calls or writing
  "tests" that are really just manual runbooks. The gap became concrete
  during `/sp.implement` for this feature, sharpened by a `/sp.analyze`
  finding (I1): `agents/intake/SOUL.md` and `agents/delivery/SOUL.md`
  disagreed on the lead-rejection score threshold (Intake used `< 0.5`,
  Delivery's Tier 3 assumed `< 0.7`) — two independently-maintained markdown
  files silently drifting apart on the same decision boundary, which the
  spec had never resolved either. That contradiction would have shipped
  invisibly without something machine-checking the documented rules.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- Introduce a test-only Python module (`tests/pipeline_sim.py`) that
  re-implements the exact thresholds and control flow already documented in
  the relevant `agents/*/SOUL.md` and `skills/*.md` files — nothing more,
  nothing invented. It is documented in its own module docstring as
  test-only.
- This module is permanently out of the production path: never imported by,
  called by, or deployed alongside the actual OpenClaw runtime. Its only
  purpose is giving `pytest` something deterministic to assert against.
- Any time a threshold or rule changes in a SOUL.md/skill file, the
  corresponding simulation code MUST change in the same commit (and vice
  versa) — this coupling is the point: it turns "two markdown files silently
  disagreeing" into "a failing pytest test."
- Fixtures (sample emails/WhatsApp text, recorded Gemini/HubSpot response
  payloads) drive the simulation; the test suite makes zero live external
  API calls and spends zero real Gemini quota.
- Applied immediately as the first use of this pattern: reconciled the
  Intake/Delivery threshold drift found by `/sp.analyze` (Intake's reject
  boundary moved from `< 0.5` to `< 0.7` to match Delivery's Tier 3),
  encoded directly in `tests/pipeline_sim.py` and cross-referenced in
  `spec.md`/`data-model.md`.

## Consequences

### Positive

- Makes OpenClaw-agent behavior testable in CI with zero live API cost and
  zero quota spend, satisfying Constitution Principles II/VI and Checker
  gate Q2 at the same time.
- The exact class of bug `/sp.analyze` caught (cross-file threshold drift
  between two SOUL.md files) becomes a repeatable, automated regression
  check going forward, instead of something only a manual analysis pass
  would catch.
- Establishes a reusable pattern: future PK/UK features that test
  Intake/Delivery/Orchestrator behavior can extend the same module rather
  than each inventing its own ad hoc mocking approach.

### Negative

- Dual-maintenance risk: the simulation module and the SOUL.md/skill files
  describe the same rules in two places (Python vs. markdown-for-LLM
  interpretation) and must be kept in sync manually — nothing currently
  automates that sync beyond code review discipline and PHR/ADR
  documentation.
- The simulation proves the *rules* are internally consistent and correctly
  encoded, not that OpenClaw's actual LLM-driven interpretation of SOUL.md
  reliably follows them at runtime — a prompt that fails to elicit the
  documented behavior from the model itself would not be caught by this
  suite.
- Adds a file whose test-only purpose must be clearly understood by future
  contributors, or it risks being mistaken for real agent logic and
  imported somewhere it shouldn't be.

## Alternatives Considered

- **Manual-only verification** (`quickstart.md` runbooks, no automated
  suite): rejected — fails Constitution Checker gate Q2 (tests required),
  and would not have caught the I1 threshold drift automatically; relies
  entirely on a human remembering to manually re-check cross-file
  consistency on every change.
- **Live integration tests against sandbox Gemini/HubSpot/WhatsApp
  accounts**: rejected — violates the zero-cost constraint's intent even in
  testing, consumes real Gemini quota (undermining the very quota guard
  being tested), and requires sandbox credentials not guaranteed to exist in
  CI.
- **A custom backend service that re-implements Gmail polling/Gemini
  calls/HubSpot writes as production code**, rather than a test-only
  simulation: rejected in `research.md` Decision 1 for this feature —
  duplicates ClawHub skills that already exist for these exact purposes and
  introduces a second orchestration surface, which Constitution Principle IV
  (OpenClaw as Sole Runtime Orchestrator) prohibits.

## References

- Feature Spec: `specs/001-pk-lead-intake-notify/spec.md`
- Implementation Plan: `specs/001-pk-lead-intake-notify/plan.md`,
  `specs/001-pk-lead-intake-notify/research.md` (Decision 1, Decision 2)
- Related ADRs: none (ADR-001 covers an unrelated secrets-hardening topic;
  no conflict)
- Evaluator Evidence / PHRs:
  `history/prompts/001-pk-lead-intake-notify/0008-analyze-remediation-applied.misc.prompt.md`
  (I1 finding and threshold fix),
  `history/prompts/001-pk-lead-intake-notify/0009-pk-lead-intake-implementation.green.prompt.md`
  (`tests/pipeline_sim.py` introduced, 28/28 tests passing)
- Constitution: `.specify/memory/constitution.md` Principles II, IV, VI, IX;
  `CONSTITUTION.md` Section 7 gates A5/Q2
