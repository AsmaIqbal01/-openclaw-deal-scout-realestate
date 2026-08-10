---
description: "Task list for PK Pilot Tracking — PILOTS.md"
---

# Tasks: PK Pilot Tracking — PILOTS.md

**Input**: Design documents from `/specs/005-pk-pilot-tracking/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md (all present)

**Tests**: Included. Per `research.md` Decision 1/2, this feature adds no
new runtime agent-logic code — `PILOTS.md` is exclusively manually
maintained. The only engineering work is one `pytest` contract test
(`tests/contract/test_pilots_schema.py`) that structurally validates
`PILOTS.md`'s 4 fenced JSON slots against `contracts/pilot-slot-schema.json`,
plus the fixture files it needs and `PILOTS.md` itself.

**Organization**: Tasks are grouped by user story (US1/US2/US3 from
`spec.md`) to enable independent implementation and testing of each story,
matching features 001-004's convention.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an
  incomplete task)
- **[Story]**: Maps to `spec.md` user stories (US1, US2, US3)
- All file paths are relative to the repository root

## Path Conventions

Single project. One new root-level file (`PILOTS.md`) plus one new test
file and its fixtures — no new component or directory beyond
`tests/fixtures/pilots/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Fixture data covering the valid scaffold and the two invalid
structural cases this feature must detect

- [X] T001 [P] Create `tests/fixtures/pilots/valid_four_slots.md`: a
      well-formed `PILOTS.md`-shaped document — summary line "0 of 4
      confirmed — Phase 1 gate not met" followed by exactly 4 `## Slot N`
      sections, each a fenced JSON block with all 16 fields at their
      `not_started`/placeholder/`null` defaults, valid against
      `contracts/pilot-slot-schema.json` (FR-001/002/003)
- [X] T002 [P] Create `tests/fixtures/pilots/duplicate_tenant_id.md`: a
      4-slot document identical to T001 except Slot 1 and Slot 2 share the
      same non-null `tenant_id` (FR-006's violation case)
- [X] T003 [P] Create `tests/fixtures/pilots/invalid_onboarding_status.md`:
      a 4-slot document identical to T001 except Slot 3's
      `onboarding_status` is set to a value outside the 7-value enum
      (FR-011's violation case)
- [X] T004 [P] Create `tests/fixtures/pilots/three_confirmed.md`: a 4-slot
      document with 3 slots (any 3) at `onboarding_status: confirmed`,
      each with a valid non-null `first_notification_delivered_at` and
      `source_run_id`, and 1 slot at an earlier stage; summary line "3 of 4
      confirmed — Phase 1 gate met — UK-market work (Phase 2) is now
      authorized to begin" (for US3)
- [X] T005 [P] Create `tests/fixtures/pilots/two_confirmed.md`: a 4-slot
      document with 2 slots `confirmed` (valid `source_run_id`s) and 2 at
      earlier stages; summary line "2 of 4 confirmed — Phase 1 gate not
      met" (for US1 and US3)
- [X] T006 [P] Create `tests/fixtures/pilots/confirmed_without_source.md`:
      a 4-slot document with one slot at `onboarding_status: confirmed`
      but `source_run_id: null` — the FR-004/FR-011 rejection case (US2's
      failure path)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The Markdown-parsing helper every user story's tests depend on

**⚠️ CRITICAL**: No user story test can be written until this phase is
complete

- [X] T007 Add `parse_pilot_slots(markdown_text: str) -> list[dict]` to
      `tests/contract/test_pilots_schema.py`: extracts each fenced
      ` ```json ` block appearing under a `## Slot N` heading, in heading
      order, and returns the parsed list of slot dicts (data-model.md)
- [X] T008 Add `parse_summary_line(markdown_text: str) -> str` to the same
      file: returns the first non-blank content line, for comparison
      against the exact strings FR-009 requires
- [X] T009 [P] Add `count_valid_confirmed(slots: list[dict]) -> int` to the
      same file: counts slots that are simultaneously (a) schema-valid
      against `contracts/pilot-slot-schema.json`, (b) not a duplicate
      `tenant_id` (FR-006), and (c) `onboarding_status == "confirmed"` —
      implementing the FR-006/FR-007/FR-011 exclusion rules together, since
      the gate count in FR-007 depends on all three

**Checkpoint**: Foundation ready — user story test-writing can now begin

---

## Phase 3: User Story 1 - See all 4 pilot slots' status at a glance (Priority: P1) 🎯 MVP

**Goal**: Prove the summary line always accurately reflects the underlying
slot data.

**Independent Test**: `pytest tests/contract/test_pilots_schema.py -k summary -v`

- [X] T010 [US1] `test_summary_line_zero_confirmed` — Acceptance Scenario 1:
      using T001's fixture, assert `parse_summary_line(...) == "0 of 4
      confirmed — Phase 1 gate not met"`
- [X] T011 [US1] Add `test_summary_line_two_confirmed` — Acceptance
      Scenario 2: using T005's fixture, assert the summary line reads "2 of
      4 confirmed — Phase 1 gate not met"
- [X] T012 [US1] Add `test_slot_count_is_always_exactly_four` — FR-001:
      using T001's fixture, assert `len(parse_pilot_slots(...)) == 4`

**Checkpoint**: US1 fully testable — the summary-line/slot-data
relationship is verified

---

## Phase 4: User Story 2 - Record and update a slot's fields as onboarding advances (Priority: P2)

**Goal**: Prove the field schema is enforced and a `confirmed` status is
never reachable without a traceable notification record.

**Independent Test**: `pytest tests/contract/test_pilots_schema.py -k slot -v`

- [X] T013 [US2] `test_all_slots_match_pilot_slot_schema` — FR-002/FR-003:
      using T001's fixture, assert every one of the 4 parsed slots passes
      `jsonschema.validate` against `contracts/pilot-slot-schema.json`
- [X] T014 [US2] Add `test_confirmed_slot_requires_source_run_id` —
      Acceptance Scenario 2 (FR-004): using T004's fixture, assert every
      `confirmed` slot has non-null `first_notification_delivered_at` and
      `source_run_id`
- [X] T015 [US2] Add `test_confirmed_without_source_run_id_fails_schema` —
      Acceptance Scenario 3 (FR-004/FR-011, the rejection/failure path):
      using T006's fixture, assert `jsonschema.validate` raises
      `ValidationError` for the slot marked `confirmed` with
      `source_run_id: null`

**Checkpoint**: US1 and US2 both verified — the slot data itself is
trustworthy

---

## Phase 5: User Story 3 - Get an unambiguous signal the moment the Phase 1 gate is met (Priority: P3)

**Goal**: Prove the 3-of-4 threshold is exact, combination-independent, and
that invalid slots never count toward it.

**Independent Test**: `pytest tests/contract/test_pilots_schema.py -k gate -v`

- [X] T016 [US3] `test_gate_not_met_at_two_confirmed` — Acceptance Scenario
      1: using T005's fixture, assert `count_valid_confirmed(...) == 2` and
      the summary line states the gate is not met
- [X] T017 [US3] Add `test_gate_met_at_three_confirmed` — Acceptance
      Scenario 2: using T004's fixture, assert `count_valid_confirmed(...)
      == 3` and the summary line reads "3 of 4 confirmed — Phase 1 gate met
      — UK-market work (Phase 2) is now authorized to begin"
- [X] T018 [US3] Add `test_duplicate_tenant_id_excluded_from_gate_count` —
      FR-006's fallback: using T002's fixture, assert both slots sharing
      the duplicate `tenant_id` are excluded by `count_valid_confirmed`
- [X] T019 [US3] Add `test_invalid_onboarding_status_excluded_from_gate_count`
      — FR-011's fallback: using T003's fixture, assert the slot with the
      out-of-enum `onboarding_status` is excluded by
      `count_valid_confirmed` and does not raise an unhandled exception

**Checkpoint**: All 3 user stories independently verified — full feature
scope covered

---

## Phase 6: Deliverable

**Purpose**: Produce the actual `PILOTS.md` this feature exists to add

- [X] T020 Create `PILOTS.md` at the repository root: summary line "0 of 4
      confirmed — Phase 1 gate not met", followed by 4 `## Slot N`
      sections in order, each a fenced JSON block at its
      `not_started`/placeholder/`null` defaults — identical in shape to
      T001's fixture (FR-001/002/003/009), so the fixture and the real
      file never drift apart from day one

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Regression safety and final validation

- [X] T021 [P] Run `pytest tests/ -v` (full suite) and confirm every
      feature 001-004 test still passes unmodified — the new fixtures and
      test file must be pure additions with no shared mutable state
- [X] T022 [P] Run the exact command from `quickstart.md`'s "Automated test
      suite" section and confirm it passes:
      `pytest tests/contract/test_pilots_schema.py -v`
- [X] T023 Run `/sp.analyze` across `spec.md`/`plan.md`/`tasks.md` to catch
      any cross-artifact drift before implementation is considered
      complete, matching features 001-004's pattern

---

## Phase 8: Remediation (findings from T023's `/sp.analyze` run)

**Purpose**: `/sp.analyze` found 5 real coverage gaps between spec.md and
the delivered test suite — 1 CRITICAL (C1), 1 HIGH (C2), 3 MEDIUM/LOW
(C3/C4/U1). All 5 were remediated in the same session, per user direction.

- [X] T009b [C1] Extend `count_valid_confirmed` in
      `tests/contract/test_pilots_schema.py` with an optional
      `workspace_root` parameter: when given, additionally excludes any
      slot whose `tenant_id` doesn't match the real
      `workspace/tenants/{tenant_id}/USER.md`'s own `tenant_id` field
      (FR-013) via new helper `_tenant_id_mismatches_real_user_md`
- [X] T024 [C1] Add `test_tenant_id_mismatch_with_real_user_md_excluded_from_gate_count`,
      `test_tenant_id_matching_real_user_md_still_counted`, and
      `test_tenant_not_yet_onboarded_is_not_a_mismatch` — proving FR-013's
      exclusion fires, doesn't over-exclude a matching tenant, and doesn't
      penalize a not-yet-onboarded one
- [X] T025 [C2] Add `load_pilots_document(path) -> dict` and
      `gate_met(document) -> bool` to `test_pilots_schema.py`, implementing
      FR-010's `"missing"`/`"malformed"`/`"ok"` states (mirroring
      `dashboard/server.py`'s `load_email_draft_queue_raw` state-string
      pattern), plus `test_missing_pilots_file_treated_as_gate_unmet`,
      `test_malformed_pilots_file_treated_as_gate_unmet`,
      `test_wrong_slot_count_treated_as_malformed`,
      `test_valid_pilots_file_reaches_ok_state_and_gate_met`, and a sanity
      check that the real `PILOTS.md` itself reaches `"ok"`
      (`test_real_pilots_md_reaches_ok_state`)
- [X] T026 [C3] Create `tests/fixtures/pilots/all_withdrawn.md` (all 4
      slots `withdrawn`) and add `test_all_withdrawn_shows_zero_confirmed`
      — FR-008's named edge case
- [X] T027 [C4] Add `test_non_pk_market_mode_fails_schema` — proves FR-012's
      `market_mode` `const: "PK"` constraint actually rejects a UK value,
      not just that it's declared in the schema
- [X] T028 [U1] Add `test_no_runtime_agent_file_references_pilots_md` — a
      regression guard scanning `agents/*/SOUL.md` and `skills/*.md` for
      the literal string `PILOTS.md`, matching feature 004's
      `test_no_approval_actions_in_frontend.py` precedent for hardening a
      negative/absence requirement (FR-005)
- [X] T029 Re-ran `pytest tests/contract/test_pilots_schema.py -v` (21/21
      passing, up from 10) and the full `pytest tests/ -v` suite (106/106
      passing, up from 95) — zero regressions from remediation

**Checkpoint**: All 5 `/sp.analyze` findings closed; FR coverage for
feature 005 is now 13/13 direct-or-partial (was 8/13 fully + 2 partial + 3
uncovered) — see the updated module docstring in `test_pilots_schema.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — T001-T006 are all `[P]`, different
  files
- **Foundational (Phase 2)**: Depends on Setup (needs fixtures to parse
  against while developing the helpers) — BLOCKS all user stories; T007/T008
  are sequential in the same file, T009 is `[P]` with them
- **User Stories (Phase 3-5)**: All depend on Foundational (Phase 2)
  completion
  - US1 (Phase 3) has no dependency on US2/US3
  - US2 (Phase 4) depends only on the shared parsing helpers (T007-T009),
    not on US1's specific tests
  - US3 (Phase 5) depends on T009's `count_valid_confirmed` specifically,
    which itself depends on the FR-006/FR-011 exclusion logic — but not on
    US1/US2's test functions directly
- **Deliverable (Phase 6)**: Depends on all 3 user stories passing against
  T001's fixture shape, so `PILOTS.md` itself is provably correct the
  moment it is created, not created first and validated after
- **Polish (Phase 7)**: Depends on all of the above being complete

### Within Each User Story

- Tests are written first (T010-T012, T013-T015, T016-T019) and must FAIL
  until T007-T009's helpers exist to make them runnable at all
- Fixtures (Phase 1) before tests that consume them

### Parallel Opportunities

- T001-T006 (Setup fixtures) — different files
- T009 (Foundational) — `[P]` with T007/T008 once both exist, since it only
  reads their output shape
- T021, T022 (Polish) — independent verification runs

---

## Parallel Example: Setup

```bash
# Launch together:
Task: "Create tests/fixtures/pilots/valid_four_slots.md"
Task: "Create tests/fixtures/pilots/duplicate_tenant_id.md"
Task: "Create tests/fixtures/pilots/invalid_onboarding_status.md"
Task: "Create tests/fixtures/pilots/three_confirmed.md"
Task: "Create tests/fixtures/pilots/two_confirmed.md"
Task: "Create tests/fixtures/pilots/confirmed_without_source.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T009) — CRITICAL, blocks all
   stories
3. Complete Phase 3: User Story 1 (T010-T012)
4. **STOP and VALIDATE**: `pytest tests/contract/test_pilots_schema.py -k summary -v`
5. Demo: the summary-line/slot-data relationship is provably correct — the
   core value proposition, independently provable before `PILOTS.md` itself
   even exists

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add US1 → validate independently → summary line trustworthy
3. Add US2 → validate independently → slot data trustworthy, confirmation
   unforgeable-by-schema
4. Add US3 → validate independently → gate threshold exact and
   exclusion-aware
5. Deliverable (T020) → `PILOTS.md` itself exists, matching every
   already-passing test's assumptions
6. Polish (T021-T023) → regression-safe, `/sp.analyze`-clean

---

## Notes

- No new agent-logic language or production `src/`/`agents/` code — every
  task here is a fixture, a test-support helper function, one contract
  test file, or (T020) the tracking document itself, per `research.md`
  Decision 1/2 and `adrs/ADR-004-pilots-manual-tracking-boundary.md`
- `[P]` tasks touch different files with no dependency on an incomplete
  task
- `[Story]` label maps each task to its `spec.md` user story for
  traceability
- Verify tests fail before T007-T009's helpers exist to make them
  runnable, then again before T020 creates the real `PILOTS.md`
- Commit after each task or logical group
- Stop at any checkpoint to validate a story independently before moving on
