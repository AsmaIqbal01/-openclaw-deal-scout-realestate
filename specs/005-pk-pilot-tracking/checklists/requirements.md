# Specification Quality Checklist: PK Pilot Tracking — PILOTS.md

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-11
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- Scored against `agents/spec-scorer/spec-scorer.md`'s 7-dimension rubric, after
  a self-audit pass that found and fixed 3 real gaps before this score was
  recorded (not a first-pass self-score):

  ```
  SPEC SCORE: 10.0/10 — PASS

  1. Interface Precision:     2.0/2.0 — no API exists (static tracking file);
     the interface is PILOTS.md's own schema, specified with the same rigor
     features 003/004 gave their JSON schemas: exact file location and slot
     count (FR-001), all 11 tenant-template fields named field-for-field
     against workspace/tenants/_template/USER.md (FR-002), all 4
     pilot-tracking fields with their exact 7-value enum (FR-003), and the
     exact summary-line format (FR-009).
  2. Error Path Coverage:     2.0/2.0 — 5 failure modes each with an explicit
     fallback: unverified confirmation attempt (FR-004/FR-011, excluded from
     gate count), duplicate tenant_id (FR-006, both slots excluded),
     tenant_id/USER.md mismatch (FR-013, excluded), missing or malformed
     PILOTS.md (FR-010, gate treated as unmet), and agency withdrawal
     (FR-008, set to withdrawn not deleted).
  3. Ambiguity Elimination:   1.5/1.5 — a literal grep audit found and fixed
     3 hedge-word instances ("MAY subsequently be reassigned" in FR-008,
     "may now begin" in two Acceptance Scenario quotes with inconsistent
     wording between them, and "may exist elsewhere" in FR-010); all
     rewritten to direct, testable phrasing. Re-audited clean. All
     quantities exact (4 slots, 3-of-4 threshold, 11+4 fields, 7 stages,
     10 seconds, 100%).
  4. Market Specificity:      1.5/1.5 — PK Real Estate named exactly, not UK,
     not "SMBs"; the PK discovery form (discovery/create_form.py) named as
     the candidate-agency intake source; Language/Locale line states
     English-only since this is a founder-facing, non-client-facing
     document, explicitly distinguishing it from features 001-004's
     client-facing locale requirements.
  5. Test Coverage Intent:    1.5/1.5 — 3 user stories, 7 acceptance
     scenarios total, each Given/When/Then naming a concrete input and
     expected output; User Story 2's Acceptance Scenario 3 explicitly
     exercises the failure/rejection path (an unverified confirmation
     attempt, FR-004/FR-011).
  6. Multi-Tenant Awareness:  1.0/1.0 — FR-002/FR-013 tie tenant_id directly
     to workspace/tenants/_template/USER.md's own field; FR-006 defines
     duplicate-tenant_id handling; FR-013 defines mismatch handling; FR-005
     establishes isolation by construction — PILOTS.md has no runtime read/
     write path into the pipeline at all, so it cannot become a cross-tenant
     leak vector by design, not just by convention.
  7. Business Gate Linkage:   0.5/0.5 — tied to F012 in the F008-F017
     milestone sequence; states explicitly which validation milestone it
     unlocks (Phase 1 gate visibility itself, per CONSTITUTION.md Section 2).

  Gaps found and closed before this score:
  1. FR-006 (duplicate tenant_id) originally prohibited duplicates without
     stating a fallback — added the "both slots excluded until corrected"
     clause.
  2. No requirement covered a tenant_id/USER.md mismatch (a Multi-Tenant
     Awareness rubric item) — added FR-013.
  3. Three casual "may" hedges, including one real inconsistency: the
     "gate met" summary-line text was quoted differently in the User Story 3
     narrative versus its Acceptance Scenario 2 ("is now authorized to
     begin" vs. "may now begin") — unified to one exact string used
     consistently everywhere FR-009's summary line is quoted.

  Verdict: PASS — proceed to /sp.plan
  ```

- The "Scope Decision" section records the explicit architectural choice
  (confirmed with the feature owner before drafting) that `PILOTS.md` is
  fully manually maintained — no runtime agent ever reads or writes it —
  ruling out two more complex alternatives (Orchestrator auto-confirms only;
  fully Orchestrator-managed) that were considered and rejected for adding
  unnecessary runtime surface area to a business-tracking concern.
- FR-005's isolation-by-construction argument (no read/write path exists, so
  no cross-tenant leak is possible) is the same pattern this project used
  for feature 004's dashboard read-only guarantee — verified structurally,
  not just asserted.
