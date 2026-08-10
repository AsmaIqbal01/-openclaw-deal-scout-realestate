# Implementation Plan: PK Pilot Tracking — PILOTS.md

**Branch**: `005-pk-pilot-tracking` | **Date**: 2026-08-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-pk-pilot-tracking/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add `PILOTS.md`, a repository-root Markdown tracking document with exactly 4
named pilot slots, each holding a fenced JSON block whose fields match
`workspace/tenants/_template/USER.md` field-for-field (11 fields) plus 4
pilot-tracking fields (`onboarding_status`, `signup_date`,
`first_notification_delivered_at`, `source_run_id`). Per the feature owner's
explicit decision, `PILOTS.md` is exclusively manually maintained — no
runtime agent (Orchestrator, Intake, or Delivery) ever reads or writes it
(spec.md FR-005). This makes the feature closer in shape to features 001/003
(no new agent-logic code) than to features 002/004 (genuine new production
code): the only artifact this feature produces beyond documentation is one
lightweight structural contract test that validates `PILOTS.md`'s own
scaffold shape — a dev-time lint, not a runtime component (`research.md`
Decision 2).

## Technical Context

**Language/Version**: N/A for runtime behavior — no source code is
introduced or modified in `agents/`, `dashboard/`, or `skills/`. Python
3.11+ is used only for the one structural contract test (`research.md`
Decision 2), matching the existing `pytest` suite's language.
**Primary Dependencies**: none new. The contract test uses the standard
library (`json`, `re`) plus the already-present `pytest`/`jsonschema` (both
already project dependencies per features 002-004).
**Storage**: `PILOTS.md` itself (repository root, plain Markdown with
embedded fenced JSON blocks) — not a database, not under `workspace/`. Reads
(never writes) from `workspace/tenants/{tenant_id}/USER.md` and
`workspace/tenants/{tenant_id}/MEMORY.md` are manual, human cross-references
performed by the founder when updating a slot — not automated by this
feature (FR-004, FR-013).
**Testing**: `pytest`, one new contract test file
(`tests/contract/test_pilots_schema.py`) that parses `PILOTS.md`'s 4 fenced
JSON blocks and validates them against `contracts/pilot-slot-schema.json` —
exactly 4 slots, all 15 required fields present, `onboarding_status` in the
7-value enum, no duplicate `tenant_id` across slots (FR-001/002/003/006/011).
No integration test is needed: no runtime code path exists for this feature
to exercise (FR-005).
**Target Platform**: N/A — a static file read by a human text editor / git,
not served, not deployed, not polled.
**Project Type**: single project — one new root-level file plus one new
test file; no new component, directory, or service.
**Performance Goals**: N/A — no request/response cycle, no polling, no
runtime execution path.
**Constraints**: zero paid infrastructure (a Markdown file); the manual
update model is a hard constraint, not a placeholder for future automation
— any future proposal to make the Orchestrator write to `PILOTS.md` requires
a new spec and, per `CONSTITUTION.md` Section 3 and this feature's ADR, a
documented architectural decision, not a silent extension of this feature.
**Scale/Scope**: exactly 4 slots, fixed — this feature does not support a
variable-length pilot list (spec.md FR-001, Assumptions).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| I. PK-First Market Sequencing (Validation Gate) | ✅ PASS | This feature exists solely to track this exact gate; FR-012 explicitly excludes any UK-market candidate tracking |
| II. Zero Infrastructure Cost | ✅ PASS | A Markdown file plus one `pytest` file; zero new dependencies, zero paid services |
| III. Market-Native Channel Fidelity | N/A | This feature sends no notification of any kind — it is a passive tracking document |
| IV. OpenClaw as Sole Runtime Orchestrator | ✅ PASS | FR-005 keeps `PILOTS.md` entirely outside runtime agent I/O — strengthens this principle rather than risking it, by construction rather than convention |
| V. Maker/Checker Separation | N/A | No lead classification or delivery action is performed by this feature |
| VI. Gemini Quota Guard | N/A | No Gemini calls are made by this feature |
| VII. Human Approval Gate for Client-Facing Communication | N/A | This feature does not touch client-facing email or feature 003's approval queue in any way |
| VIII. Multi-Tenant Data Isolation | ✅ PASS | FR-006/FR-013 define duplicate-`tenant_id` and `tenant_id`-mismatch handling; FR-005's isolation-by-construction means `PILOTS.md` has no code path into the pipeline that could leak tenant data at all |
| IX. Spec Quality Gate — 9.6/10 Minimum | ✅ PASS | `spec.md` scored 10.0/10 after a self-audit that found and closed 3 real gaps (`checklists/requirements.md`) before this plan began |

No violations. Complexity Tracking table is empty.

**Post-Phase 1 re-check**: unchanged — `data-model.md` and `contracts/`
introduce no writes to any runtime-read file, no new orchestration, and no
paid infrastructure. The one new test is a static-structure check, not a
runtime behavior test, so it introduces no new pipeline execution path to
re-verify against the Constitution's runtime-facing principles (III, V, VI).

## Project Structure

### Documentation (this feature)

```text
specs/005-pk-pilot-tracking/
├── plan.md               # This file (/sp.plan command output)
├── research.md            # Phase 0 output
├── data-model.md           # Phase 1 output
├── quickstart.md           # Phase 1 output
├── contracts/
│   └── pilot-slot-schema.json
├── checklists/
│   └── requirements.md
└── tasks.md                # Phase 2 output (/sp.tasks command — NOT created by /sp.plan)
```

### Source Code (repository root)

```text
PILOTS.md                  # new: repository-root tracking document, 4 named
                            # slots, each a fenced JSON block per
                            # contracts/pilot-slot-schema.json

tests/
├── contract/
│   └── test_pilots_schema.py   # new: parses PILOTS.md's 4 fenced JSON
│                                 # blocks, validates against
│                                 # pilot-slot-schema.json, checks slot
│                                 # count, enum values, and tenant_id
│                                 # uniqueness (FR-001/002/003/006/011)
└── fixtures/
    └── pilots/
        ├── valid_four_slots.md        # well-formed scaffold, all not_started
        ├── duplicate_tenant_id.md      # violates FR-006
        └── invalid_onboarding_status.md # violates FR-011
```

**Structure Decision**: Single project. `PILOTS.md` is a new root-level
file, not a new component or service — placed alongside `README.md` and
`CONSTITUTION.md`, not under `workspace/` (spec.md Assumptions). No changes
to `agents/*/SOUL.md`, `skills/*.md`, `dashboard/`, or any existing test
file. The one new test file extends the existing `tests/contract/`
directory established by features 002-004, following their exact pattern of
validating a JSON schema against fixture data — the only difference is the
JSON lives inside a Markdown file's fenced code blocks rather than a
standalone `.json` file on disk, since `PILOTS.md` itself must remain
human-readable at the repository root per FR-001.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — table intentionally left empty.
