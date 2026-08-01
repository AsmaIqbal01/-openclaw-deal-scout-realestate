# Research: PK Lead Intake, Classification & WhatsApp Notification

## Context

`agents/orchestrator/SOUL.md`, `agents/intake/SOUL.md`, `agents/delivery/
SOUL.md`, and the PK-relevant skills (`skills/zameen-parser.md`,
`skills/pk-whatsapp-lead.md`, `skills/lead-classifier-pk.md`,
`skills/multi-tenant-router.md`) already exist and were cross-checked against
every functional requirement in `spec.md` — none required content changes.
`backend/`, `dashboard/`, and `tests/` are empty scaffold directories with no
prior code. This research resolves the two unknowns that determine what, if
anything, needs to be built versus verified.

## Decision 1: Where does the "implementation" for this feature actually live?

**Decision**: There is no new agent-logic code to write. The Orchestrator,
Intake, and Delivery agents are OpenClaw agents whose behavior is fully
defined by their `SOUL.md` files, executed natively by the OpenClaw runtime.
The PK parsing and classification behavior is fully defined by the existing
skill markdown files. This feature's engineering work is: (a) per-tenant
runtime configuration (env vars, `USER.md` instance) — configuration, not
code; (b) a fixture-based automated test suite that proves the FR-level
behaviors without spending live Gemini quota or making live Gmail/WhatsApp/
HubSpot calls; (c) installing the named ClawHub skills that this feature
depends on (`agent-rate-limiter`, `agent-memory`, `honcho-setup`,
`agentmail-integration`) per `workspace/TOOLS.md`'s tool-priority rule
(reuse existing skills before building custom).

**Rationale**: every functional requirement in `spec.md` (FR-001 through
FR-015) is already satisfied by content in `agents/*/SOUL.md` and
`skills/{zameen-parser,pk-whatsapp-lead,lead-classifier-pk,
multi-tenant-router}.md`, verified line-by-line during planning. Writing new
agent-definition content would duplicate what already exists and risk drift
between two descriptions of the same behavior. The constitution's tool
priority rule (`workspace/TOOLS.md`) also requires preferring an existing
ClawHub skill over custom-building, which further narrows new work to
configuration and tests.

**Alternatives considered**:
- *Write a custom backend service (Node/Python) that re-implements Gmail
  polling, Gemini calls, and HubSpot writes directly*: rejected — duplicates
  ClawHub skills that already exist for these exact purposes
  (`agentmail-integration`, `apollo`-adjacent HubSpot patterns), and
  introduces a second orchestration surface, which Constitution Principle IV
  (OpenClaw as Sole Runtime Orchestrator) prohibits.
- *Leave verification entirely manual (no automated tests)*: rejected —
  Constitution Checker gate Q2 requires tests covering at least 3 cases per
  feature, and Success Criteria SC-001–SC-006 are not verifiable by
  inspection alone.

## Decision 2: Test language and framework for the fixture-based suite

**Decision**: Python 3.11+ with `pytest`, using static fixture files (sample
Zameen/OLX email bodies, sample WhatsApp message text, recorded Gemini and
HubSpot response payloads) so tests never call live external services or
spend Gemini quota.

**Rationale**: `pytest` is a zero-cost, industry-standard test runner with no
paid infrastructure implication (Constitution Principle II); it is a
reasonable, unopinionated default given this repo has no prior test language
commitment (`tests/` was empty); and fixture-based testing directly satisfies
Constitution Checker gate Q4 (no live secrets in test runs) and this
project's zero Gemini-quota-during-CI requirement, since none of the ~5
Gemini calls per pipeline run counted in `workspace/HEARTBEAT.md`'s scope
limits should be consumed by test execution.

**Alternatives considered**:
- *Node.js/Jest*: rejected only because Python has no competing signal
  either way in this repo and `pytest`'s fixture system maps more directly
  onto "replay a recorded Gmail/Gemini/HubSpot response" than Jest's mocking
  conventions for this kind of file-and-text-fixture-heavy suite — a
  reasonable default, not a hard technical requirement.
- *Live integration tests against sandbox Gemini/HubSpot accounts*: rejected
  — would consume real quota (violates the 18/day guard's intent even in
  testing) and requires paid/sandbox credentials not guaranteed to exist in
  CI.

## Resolved Technical Context

All Technical Context fields below are now resolved (no remaining
`NEEDS CLARIFICATION`):

- **Language/Version**: No new agent-logic language — agent behavior is
  Markdown (`SOUL.md`/skill files) interpreted by OpenClaw. Test suite:
  Python 3.11+.
- **Primary Dependencies**: OpenClaw runtime; ClawHub skills
  `agent-rate-limiter`, `agent-memory`, `honcho-setup`,
  `agentmail-integration`; `pytest` for the test suite.
- **Storage**: `MEMORY.md` (flat-file spine, per `honcho-setup`), per-tenant
  `USER.md` files — no database introduced.
- **Testing**: `pytest`, fixture-based (no live external calls).
- **Target Platform**: Linux server (existing systemd timer host, per
  `workspace/HEARTBEAT.md`).
- **Project Type**: Single project — no frontend/backend split for this
  feature (dashboard work is explicitly out of scope; see spec.md Success
  Criteria, none of which reference the dashboard).
- **Performance Goals**: One heartbeat cycle (15 minutes) end-to-end per
  SC-001; within `workspace/HEARTBEAT.md`'s scope limits (≤20 Gmail
  messages, ≤10 WhatsApp messages, ≤5 Gemini calls per tenant per run).
- **Constraints**: Zero paid infrastructure; ≤18 Gemini calls/day/tenant
  (Constitution Principle VI); WhatsApp-only PK notifications (Principle
  III).
- **Scale/Scope**: Single-tenant through the Phase 1 validation target of 3
  PK agencies (Constitution Principle I) — no multi-hundred-tenant scale
  requirement at this stage.
