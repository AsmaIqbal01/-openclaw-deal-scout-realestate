# Research: PK Pilot Tracking — PILOTS.md

## Context

Unlike features 002/004 (genuine new production code in `dashboard/`) and
more like features 001/003 (no new agent-logic code), this feature's only
"behavior" is a human editing a Markdown file by hand. The interesting
decisions are about *format* (how `PILOTS.md` is structured so it stays
both human-readable and machine-checkable) and *boundary* (making the
"manual only" decision airtight rather than aspirational).

## Decision 1: Manual-only maintenance, no runtime write path

**Decision**: `PILOTS.md` is read and written exclusively by direct human
edit. No `agents/*/SOUL.md` file is modified by this feature, and no new
runtime code reads or writes `PILOTS.md`.

**Rationale**: this was an explicit architectural choice presented to and
confirmed by the feature owner ahead of drafting the spec, choosing it over
two more automated alternatives. It keeps this feature's blast radius to
"one Markdown file, one structural test" — no new agent behavior to
misfire, no new failure mode in the 15-minute heartbeat, no new field for
the Constitution Checker's Architecture gates to verify against a live
pipeline run. It also sidesteps a real tension: `CONSTITUTION.md` Section 3
states "the Orchestrator is the only agent that reads/writes `MEMORY.md`
directly" — silently having the Orchestrator also write `PILOTS.md` would
either violate that boundary's spirit or require an amendment before this
feature could even be specified. Keeping `PILOTS.md` manual avoids that
question entirely rather than answering it implicitly.

**Alternatives considered**:
- *Orchestrator auto-confirms only* (the founder manages slot
  assignment/status by hand, but the Orchestrator stamps
  `first_notification_delivered_at`/`source_run_id` automatically the
  moment it sends a tenant's first real notification): rejected for this
  feature — it removes the small risk of a self-reported confirmation being
  wrong, but requires a new, narrowly-scoped runtime write path with its
  own spec, tests, and Constitution Checker surface, which is
  disproportionate to a 4-slot tracking document for a single founder. Worth
  reconsidering as a dedicated future feature if manual cross-referencing
  against `MEMORY.md` ever proves error-prone in practice.
- *Fully Orchestrator-managed* (the Orchestrator owns the entire file):
  rejected outright — this would make `PILOTS.md` a second state file the
  runtime depends on, cutting directly against Principle IV (OpenClaw as
  Sole Runtime Orchestrator, no competing coordination layer) and
  Constitution Section 3's `MEMORY.md`-exclusivity language, and would
  require a constitutional amendment before any spec could even be written.

## Decision 2: Slot data as fenced JSON blocks inside PILOTS.md, validated by one contract test

**Decision**: each of the 4 slots is an `## Slot N` heading followed by a
single fenced ` ```json ` block containing all 15 fields (spec.md
FR-002/FR-003) in the same flat-object shape as
`workspace/tenants/_template/USER.md`. One new `pytest` file,
`tests/contract/test_pilots_schema.py`, extracts each fenced block with a
Markdown-aware regex, `json.loads`s it, and validates it against
`contracts/pilot-slot-schema.json` — the same "JSON Schema + `jsonschema`
library" pattern features 002-004 already use for their own contract tests.

**Rationale**: making each slot literal, valid JSON (not a prose table or
free-form bullet list) means SC-004's "100% field-identical to the real
`USER.md`" requirement is satisfied by direct copy-paste, not manual
transcription that could introduce drift. It also makes FR-006 (duplicate
`tenant_id`), FR-011 (invalid `onboarding_status`), and FR-013 (`tenant_id`
mismatch vs. the real `USER.md`) mechanically checkable by a `pytest` run
instead of relying solely on the founder noticing a mistake by eye —
without violating Decision 1, since this test is a dev-time structural
lint (like a schema linter or `jsonschema.validate` call), not a runtime
agent behavior. It never runs as part of the 15-minute heartbeat and has no
access to live tenant data beyond what the founder already typed into
`PILOTS.md` and the fixture files under `tests/fixtures/pilots/`.

**Alternatives considered**:
- *A Markdown table (one row per slot, one column per field)*: rejected —
  15 fields per slot makes a table either unreadably wide or force a second,
  transposed table per slot, and there is no natural place to encode
  `null`/`false`/typed values unambiguously the way JSON already does.
- *No automated validation at all (pure prose document)*: rejected — it
  would leave Constitution Checker gates Q1/Q2 (existing tests still pass;
  new feature has tests covering at least 3 spec cases) with nothing to
  point to for this feature, and would make FR-006/FR-010/FR-011/FR-013's
  "MUST be treated as invalid" language pure intent with no way to verify
  it holds, contradicting this project's established pattern (every prior
  feature backs its `MUST` requirements with at least one automated check).

## Decision 3: Fixed 4 slots, not a growable list

**Decision**: `PILOTS.md` always contains exactly 4 `## Slot N` sections —
never fewer, never more. Reassigning a `withdrawn` slot re-uses that same
numbered heading; it does not create a `## Slot 5`.

**Rationale**: this was given directly in the feature description ("track 4
PK agency onboarding slots"), not inferred — and a fixed cohort size keeps
the structural contract test simple (exactly 4 fenced blocks, always) rather
than needing to handle an open-ended list, which the spec's Assumptions
section already frames as one buffer slot beyond the 3-agency gate
threshold, not a general-purpose CRM pipeline.

**Alternatives considered**:
- *An open-ended/growable pilot list*: rejected — out of scope per the
  feature description's explicit "4 slots," and would turn this from a
  fixed validation-cohort tracker into a small CRM, which is a materially
  different (and unrequested) feature.

## Resolved Technical Context

- **Language/Version**: N/A for runtime behavior; Python 3.11+ for the one
  new `pytest` contract test, matching the existing suite.
- **Primary Dependencies**: none new — `pytest`/`jsonschema` already present.
- **Storage**: `PILOTS.md` (repository root); manual cross-reference only
  against `workspace/tenants/{tenant_id}/USER.md` and `.../MEMORY.md`.
- **Testing**: one new contract test, structural only, no live sockets, no
  runtime agent invocation.
- **Target Platform**: N/A — static file.
- **Project Type**: single project, one new root file + one new test file.
- **Performance Goals**: N/A.
- **Constraints**: manual-maintenance is a hard, deliberate constraint
  (Decision 1), not a temporary simplification.
- **Scale/Scope**: exactly 4 slots, fixed (Decision 3).
