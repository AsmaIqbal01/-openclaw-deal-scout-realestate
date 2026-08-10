# ADR-004: PILOTS.md — Manual-Only Tracking Boundary & Structural Validation

> **Scope**: Decision cluster covering how `PILOTS.md` (feature 005's
> Phase 1 pilot tracker) relates to the runtime pipeline and how its
> content is kept checkable — not a single technology choice. Includes the
> manual-vs-automated maintenance boundary (primary decision) and the
> fenced-JSON-plus-contract-test format that makes that boundary
> mechanically verifiable (supporting decision, grouped here rather than
> split into a second ADR since it exists only to make the first decision
> auditable). Excludes the fixed-4-slot sizing choice, which is a minor,
> directly-specified corollary noted in Consequences rather than a
> separate architectural decision.

- **Status:** Accepted
- **Date:** 2026-08-11
- **Feature:** 005-pk-pilot-tracking
- **Context:** `CONSTITUTION.md` Section 2 defines the Phase 1 gate as "3
  Pakistani agencies confirmed — defined as having received at least one
  delivered lead notification through the pipeline — before UK-market work
  begins." No file in the repository tracked progress toward that gate;
  `README.md`'s Build Progress table carried only a single "🔨 In progress"
  line, and `workspace/tenants/` contained only `_template`. Feature 005
  introduces `PILOTS.md` to close that gap. Before drafting the spec, the
  feature owner was presented with three candidate designs for how
  `PILOTS.md` would be kept up to date — differing in how much runtime code
  they required and how directly they touch the boundary
  `CONSTITUTION.md` Section 3 already draws around `MEMORY.md` I/O — and
  chose the least automated of the three.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- **Manual-only maintenance**: `PILOTS.md` is read and written exclusively
  by direct human edit (the founder). No runtime agent — Orchestrator,
  Intake Sub-Agent, or Delivery Sub-Agent — ever reads or writes it, and no
  `agents/*/SOUL.md` file is modified by this feature. This is a permanent
  design constraint, not a placeholder for future automation: any later
  proposal to have the Orchestrator write to `PILOTS.md` requires its own
  spec and a new ADR, not a silent extension of this one.
- **Isolation by construction, not convention**: because no code path from
  any runtime agent into `PILOTS.md` exists at all, cross-tenant leakage or
  gate-gaming via this file is structurally impossible, not merely
  discouraged — mirroring the same "no write path exists" pattern
  ADR-003 used for the dashboard's read-only guarantee (`dashboard/server.py`
  has no write path to `dashboard-state.json` either).
- **Verifiable confirmation, not self-report**: a slot may only be marked
  `onboarding_status: confirmed` once it carries a `source_run_id`
  traceable to a real `notifications_sent` entry in that tenant's
  `MEMORY.md` (spec.md FR-004) — the manual-maintenance decision does not
  mean an ungoverned free-text field; it means a human, not code, performs
  the verification step.
- **Structural format**: each of the 4 fixed slots is stored as a fenced
  JSON block (field-for-field matching
  `workspace/tenants/_template/USER.md`, plus 4 tracking fields), validated
  by one new `pytest` contract test
  (`tests/contract/test_pilots_schema.py`) against
  `contracts/pilot-slot-schema.json`. This test is a dev-time structural
  lint — it never runs inside the 15-minute heartbeat and has no live
  pipeline access — so it does not contradict the manual-only decision
  above.

## Consequences

### Positive

- The manual-only decision keeps this feature's entire blast radius to one
  Markdown file and one structural test — zero new runtime failure modes,
  zero new fields for the Constitution Checker's Architecture gates (A1-A8)
  to verify against a live pipeline run, and zero risk of `PILOTS.md`
  becoming, in ADR-003's words, "a second orchestrator."
- It sidesteps, rather than quietly strains, `CONSTITUTION.md` Section 3's
  "the Orchestrator is the only agent that reads/writes `MEMORY.md`
  directly" — a competing interpretation (letting the Orchestrator also
  write `PILOTS.md`) would have required resolving whether that sentence's
  intent extends beyond `MEMORY.md` literally, before this feature could
  even be specified. Choosing manual-only avoids litigating that question.
- The fenced-JSON format makes `SC-004` ("100% field-identical to the real
  `USER.md`") achievable by direct copy-paste rather than manual
  transcription, and makes 4 of `spec.md`'s `MUST`-level requirements
  (FR-001, FR-003, FR-006, FR-011) mechanically checkable instead of
  resting purely on the founder's attentiveness.
- Sets a reusable precedent: any future founder-facing tracking document in
  this repo (e.g., a UK pilot tracker once Phase 2 begins) can point to this
  ADR for the same manual-only-plus-structural-test pattern, rather than
  re-litigating the automation-boundary question each time.

### Negative

- The Phase 1 gate's confirmation still ultimately depends on the founder
  remembering to check `MEMORY.md` before marking a slot `confirmed` — the
  contract test can verify a `source_run_id` string is *present* and
  well-formed, but cannot itself verify that string actually exists in that
  tenant's `MEMORY.md`, since the test has no runtime access to compare
  against by design (Decision above). A determined or careless entry could
  still self-report a fabricated `run_id`; this is an accepted risk given a
  single-founder, pre-revenue validation stage, not a solved problem.
- If the Phase 1 validation cohort ever needs more than 4 concurrent
  candidates, or if manual cross-referencing against `MEMORY.md` proves
  error-prone in practice, this ADR's manual-only boundary would need to be
  revisited — the "Orchestrator auto-confirms only" alternative below
  remains the natural next step, not a dead end.
- `PILOTS.md` and the real `workspace/tenants/{tenant_id}/USER.md` can
  silently drift once a tenant goes live (FR-013 defines the mismatch as
  invalid, but nothing automatically detects or alerts on it between
  manual runs of the contract test).

## Alternatives Considered

- **Orchestrator auto-confirms only** (founder manages slot
  assignment/status by hand; Orchestrator automatically stamps
  `first_notification_delivered_at`/`source_run_id` the moment it sends a
  tenant's first real notification): rejected for this feature — removes
  the self-report risk noted above, but requires a new, narrowly-scoped
  runtime write path with its own spec, tests, and Constitution Checker
  surface, disproportionate to a 4-slot tracker for a single founder at
  this stage. Left as the documented next step if the accepted risk above
  proves costly in practice.
- **Fully Orchestrator-managed** (the Orchestrator owns slot assignment,
  status transitions, and confirmation end-to-end): rejected outright —
  would make `PILOTS.md` a second state file the runtime depends on,
  directly cutting against Principle IV (OpenClaw as Sole Runtime
  Orchestrator) and Constitution Section 3's `MEMORY.md`-exclusivity
  language; would require a constitutional amendment before any spec for
  it could even be written.
- **A Markdown table instead of fenced JSON per slot**: rejected — 15
  fields per slot makes a table either unreadably wide or forces a second,
  transposed table per slot, with no unambiguous way to encode
  `null`/typed values the way JSON already does natively.
- **No automated validation at all (pure prose document)**: rejected —
  would leave 4 of `spec.md`'s `MUST`-level requirements
  (FR-001/003/006/011) with no way to verify they hold, breaking from this
  project's established pattern of backing every `MUST` requirement with
  at least one automated check.

## References

- Feature Spec: `specs/005-pk-pilot-tracking/spec.md`
- Implementation Plan: `specs/005-pk-pilot-tracking/plan.md`,
  `specs/005-pk-pilot-tracking/research.md` (Decisions 1-3)
- Related ADRs: `adrs/ADR-003-dashboard-server-architecture.md` (the
  "isolation by construction, not convention" pattern this ADR reuses for
  a non-code-serving document instead of an HTTP server); no conflicts.
- Constitution: `.specify/memory/constitution.md` Principles I, IV, VIII,
  IX; `CONSTITUTION.md` Section 2 (Phase 1 gate definition), Section 3
  (`MEMORY.md` I/O exclusivity), Section 7 gates A6/A8/Q2.
