---
description: "Task list for PK Email Draft & Operator Approval Gate"
---

# Tasks: PK Email Draft & Operator Approval Gate

**Input**: Design documents from `/specs/003-pk-email-approval-gate/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md (all present)

**Tests**: Included. Per `research.md` Decision 1 (matching feature 001, not
feature 002), this feature adds no new agent-logic code — the
draft/queue/notify/approve/reject/stale-guard flow already lives in
`skills/operator-approval-gate.md` and `agents/delivery/SOUL.md` Step 4. All
engineering work is `pytest` coverage: new decision functions in
`tests/pipeline_sim.py`, new fixtures under `tests/fixtures/email_approval/`,
and three new integration test files, one per user story, exactly as named
in `plan.md`'s Project Structure.

**Pre-flight note (found during task generation)**: `plan.md`'s Summary and
`research.md` Decision 2 both state that the two retry-semantics
requirements added by the spec's rescore (FR-007 WhatsApp-send retry, FR-009
email-send retry) were "backfilled ... during this plan's research phase"
into `skills/operator-approval-gate.md`'s Error Handling section. Checking
the file directly (this session) shows that backfill was never actually
applied — the Error Handling section still only has its original 3 bullets,
no retry language. T001 closes this real gap before any test encodes
behavior the source-of-truth skill file doesn't yet document, which is
exactly the drift pattern `research.md` Decision 2 says it exists to
prevent.

**Organization**: Tasks are grouped by user story (US1/US2/US3 from
`spec.md`) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an
  incomplete task)
- **[Story]**: Maps to `spec.md` user stories (US1, US2, US3)
- All file paths are relative to the repository root

## Path Conventions

Single project. Per `plan.md`'s Structure Decision: no new `src/` or server
code. All new work is functions added to the existing `tests/pipeline_sim.py`
plus new fixtures and integration/contract test files, extending feature
001's pattern (not feature 002's).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Close the pre-flight skill-file gap and scaffold fixtures

- [X] T001 Add the two retry rules to `skills/operator-approval-gate.md`'s
      `## Error Handling` section: (1) "Draft-alert or re-notification
      WhatsApp send fails: retry once, then log the failure and continue —
      the draft remains queued and awaiting reply regardless" (FR-007/FR-012)
      and (2) "Approved email send fails: retry once after 30 seconds; if
      the retry also fails, leave `sent_at` unset, log the failure, and
      alert the owner so an approved-but-unsent draft is never silently
      lost" (FR-009) — cross-reference `agents/delivery/SOUL.md`'s existing
      HubSpot-write-retry (Step 2) and WhatsApp-send patterns, matching
      `research.md` Decision 2's intent
- [X] T002 [P] Create `tests/fixtures/email_approval/leads_with_email.json`:
      an array of 2 leads reusing feature 001's `Lead` shape, each with a
      non-null `contact.email` — one `classification_score: 0.95` (Tier 1
      auto-dispatch path) and one representing a Tier-2 lead already
      `/confirm`ed (US1 Acceptance Scenario 1 covers both origins per FR-001)
- [X] T003 [P] Create `tests/fixtures/email_approval/leads_without_email.json`:
      one lead identical in shape but with `contact.email: null` (FR-002)
- [X] T004 [P] Create `tests/fixtures/email_approval/tenant_auto_email_drafts.json`:
      a copy of `tests/fixtures/tenants/test_tenant.json` with
      `auto_email_drafts: true` (the shared `tenant_context` fixture's
      default is `false`, which every other feature's tests rely on staying
      untouched — this feature needs its own override, not a mutation of
      the shared fixture)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared constants, template renderer, and queue-entry shape
every user story depends on

**⚠️ CRITICAL**: No user story test can be written until this phase is
complete

- [X] T005 Add approval-queue constants to `tests/pipeline_sim.py`:
      `MAX_APPROVAL_QUEUE_SIZE = 50` (FR-006), `STALE_REMINDER_HOURS = 4`
      (FR-012), `STALE_ARCHIVE_HOURS = 24` (FR-013), and
      `EMAIL_DRAFT_ALERT_TEMPLATE = "📧 New email draft awaiting your
      approval. Lead: {name}. Reply /approve {queue_id} or /reject
      {queue_id}"` (FR-007/FR-012) — mirroring
      `skills/operator-approval-gate.md`'s Queue Storage and Stale Queue
      Guard sections verbatim
- [X] T006 Add `render_pk_email_draft(lead: dict, tenant: dict) -> dict` to
      `tests/pipeline_sim.py`, returning `{"subject": ..., "body": ...}` per
      FR-003's exact template: subject
      `"Property Enquiry — {property.type} in {property.location}"`; body
      addressing `contact.name` (or `"Sir/Madam"` if null), stating
      `property.type`, `property.location`, `property.budget_pkr` (or
      `"to be discussed"` if null), `property.size` (or `"flexible"` if
      null), signed with `tenant["agent_name"]` and the tenant's agency name
- [X] T007 [P] Create `tests/contract/test_approval_queue_schema.py`,
      following `tests/contract/test_lead_schema.py`'s pattern: load
      `specs/003-pk-email-approval-gate/contracts/approval-queue-schema.json`,
      assert a fully-populated valid entry passes `jsonschema.validate`,
      assert an entry missing `sent_at` fails, and assert
      `recipient_email: "not-an-email"` fails the `format: email` check
- [X] T008 [P] Create `tests/fixtures/email_approval/queue_entries.json`: a
      dict of named example entries (`pending`, `approved_and_sent`,
      `rejected`, `auto_archived`) matching the schema, reused by both the
      US2 and US3 test files below

**Checkpoint**: Foundation ready — user story test-writing can now begin

---

## Phase 3: User Story 1 - A follow-up email is drafted and queued automatically (Priority: P1) 🎯 MVP

**Goal**: Prove a qualifying dispatched lead gets a queued draft and a
WhatsApp alert, and that every non-qualifying or failure path is a no-op
that never queues or sends anything.

**Independent Test**: `pytest tests/integration/test_us1_email_draft_queued.py -v`

- [X] T009 [US1] `tests/integration/test_us1_email_draft_queued.py::test_draft_queued_for_dispatched_lead_with_email`
      — Acceptance Scenario 1: call `queue_email_draft(lead, tenant, existing_queue=[])`
      using T002's fixture and T004's tenant override; assert the returned
      entry has `approved: False`, `sent_at is None`, `queue_id` is set, and
      the notification message references that `queue_id`
- [X] T010 [US1] Add `test_no_draft_for_null_email` — Acceptance Scenario 2
      (FR-002): using T003's fixture, assert status is `"no_email_address"`,
      no entry is returned/appended, and the logged reason is
      `"no email address for lead {lead_id}"`
- [X] T011 [US1] Add `test_no_draft_when_auto_email_drafts_disabled` — Edge
      Case: using the default `tenant_context` fixture (`auto_email_drafts:
      false`), assert no draft is attempted regardless of `contact.email`
- [X] T012 [US1] Add `test_queue_append_only_never_overwrites` — FR-005:
      queue two drafts sequentially into the same list; assert the first
      entry's fields are unchanged after the second append
- [X] T013 [US1] Add `test_queue_full_halts_new_drafts` — FR-006: pass an
      `existing_queue` with 50 entries (from T008, replicated); assert
      status `"queue_full"`, no entry added, owner alerted, halt logged
- [X] T014 [US1] Add `test_draft_generation_failure_skips_only_that_lead` —
      FR-014: call with `draft_render_outcome=False`; assert status
      `"draft_generation_failed"`, the failure is logged with `lead_id`, and
      no queue entry is added — while asserting this does **not** touch any
      CRM-write/notification result fields from an earlier `process_lead`
      call for the same lead (they remain whatever they already were)
- [X] T015 [US1] Add `test_queue_write_failure_not_queued` — FR-015: call
      with `queue_write_ok=False`; assert status `"queue_write_failed"`,
      owner alerted, no entry added
- [X] T016 [US1] Add `test_draft_alert_retry_then_continue` — FR-007: call
      with `whatsapp_outcomes=(False, False)`; assert
      `notification_sent is False` after exactly 2 attempts, but the entry
      is still present in the returned queue (queuing succeeds independent
      of notification delivery)
- [X] T017 [US1] Implement `queue_email_draft(lead: dict, tenant: dict,
      existing_queue: list, *, draft_render_outcome: bool = True,
      queue_write_ok: bool = True, whatsapp_outcomes=(True,)) -> dict` in
      `tests/pipeline_sim.py`, covering FR-001/002/004/005/006/007/014/015:
      null-email skip, `auto_email_drafts` gate, `render_pk_email_draft`
      (T006) for content, `MAX_APPROVAL_QUEUE_SIZE` halt (T005),
      `_attempt_with_one_retry` (existing helper) for the WhatsApp alert,
      and the `draft_generation_failed`/`queue_write_failed` failure paths.
      Returns `{"status": ..., "entry": dict | None, "queue": list,
      "notification_sent": bool}`

**Checkpoint**: US1 fully functional and independently testable — this is
the MVP

---

## Phase 4: User Story 2 - The agent approves or rejects the draft via WhatsApp (Priority: P2)

**Goal**: Prove `/approve` sends the email and sets the right fields,
`/reject` never sends, and any reply naming an unknown, already-resolved, or
cross-tenant `queue_id` is a no-op.

**Independent Test**: `pytest tests/integration/test_us2_email_approval_reply.py -v`

- [X] T018 [P] [US2] Create `tests/contract/test_email_approval_commands.py`,
      following `tests/contract/test_approval_commands.py`'s pattern: test
      `/approve` and `/reject` from the correct tenant against a pending
      entry (using T008's fixture), an unknown `queue_id`, and a `queue_id`
      belonging to a different tenant — all against
      `resolve_email_approval_reply` (T023)
- [X] T019 [US2] `tests/integration/test_us2_email_approval_reply.py::test_approve_sends_email_and_sets_fields`
      — Acceptance Scenario 1: reply `/approve {queue_id}` to T008's
      `pending` entry; assert `approved is True`, `approved_at` is set, the
      email is sent to `recipient_email`, `sent_at` is set, and no other
      queue entry in the same list is modified
- [X] T020 [US2] Add `test_reject_marks_rejected_never_sent` — Acceptance
      Scenario 2 (FR-010): reply `/reject {queue_id}` to a different pending
      entry; assert it is logged rejected and no email send is attempted
- [X] T021 [US2] Add `test_unknown_queue_id_reply_ignored` — Acceptance
      Scenario 3 (FR-011): reply naming a `queue_id` not present in the
      tenant's queue; assert status `"unknown_queue_id_reply"` and no entry
      is modified
- [X] T022 [US2] Add `test_already_resolved_queue_id_reply_ignored` —
      FR-011: reply `/approve` to T008's `approved_and_sent`, `rejected`,
      and `auto_archived` entries in turn; assert all three are treated as
      `unknown_queue_id_reply`, never re-sent or re-processed
- [X] T023 [US2] Add `test_cross_tenant_queue_id_rejected` — Edge Case tied
      to Constitution Principle VIII: a reply's `queue_id` matches an entry
      belonging to a different `tenant_id`; assert it resolves identically
      to `unknown_queue_id_reply`, never resolved across tenants
- [X] T024 [US2] Add `test_approve_email_send_retry_then_alert` — FR-009:
      call with `email_send_outcomes=(False, False)`; assert `sent_at`
      stays `None`, `approved`/`approved_at` are still set (the approval
      itself is not rolled back), status is `"send_failed"`, the failure is
      logged, and the owner is alerted
- [X] T025 [US2] Implement `resolve_email_approval_reply(entry: dict, *,
      reply_command: str, reply_queue_id: str, reply_tenant_id: str,
      reply_from_number: str, email_send_outcomes=(True,)) -> dict` in
      `tests/pipeline_sim.py`, covering FR-009/010/011: derive the entry's
      resolved/pending state from `auto_archived`/`rejected`/`approved`
      (an entry is `pending` only when none of those three is set), reject
      cross-tenant and unknown/already-resolved `queue_id`s identically,
      and use `_attempt_with_one_retry` (existing helper, 30s-retry
      semantics per FR-009) for the email send on `/approve`

**Checkpoint**: US1 and US2 both work independently — the full draft →
approve/reject loop is testable end to end

---

## Phase 5: User Story 3 - Stale drafts never linger or self-send (Priority: P3)

**Goal**: Prove the one-time 4-hour reminder and the permanent 24-hour
auto-archive both fire exactly once and never resurrect a stale entry.

**Independent Test**: `pytest tests/integration/test_us3_stale_draft_guard.py -v`

- [X] T026 [US3] `tests/integration/test_us3_stale_draft_guard.py::test_four_hour_reminder_sent_exactly_once`
      — Acceptance Scenario 1 (FR-012): call
      `apply_stale_queue_guard(entry, hours_since_queued=4.083)` on a fresh
      pending entry (`re_notified: False`); assert `action ==
      "re_notified"`, `re_notified` becomes `True`, and one notification
      message is returned; call again at the same age and assert
      `action == "none"` (no second reminder)
- [X] T027 [US3] Add `test_twenty_four_hour_auto_archive_permanent` —
      Acceptance Scenario 2 (FR-013): call with
      `hours_since_queued=24.083`; assert `auto_archived` becomes `True`,
      `action == "auto_archived"`, no send occurs; then call
      `resolve_email_approval_reply` with `/approve` against that same
      now-archived entry and assert `"unknown_queue_id_reply"` (revival is
      impossible)
- [X] T028 [US3] Add `test_stale_guard_skips_already_resolved_entries` —
      using T008's `approved_and_sent`, `rejected`, and `auto_archived`
      fixture entries at both the 4-hour and 24-hour marks, assert
      `action == "none"` in every case (no re-notification, no
      re-archival, no state change) for entries that are no longer pending
- [X] T029 [US3] Implement `apply_stale_queue_guard(entry: dict, *,
      hours_since_queued: float) -> dict` in `tests/pipeline_sim.py`,
      covering FR-012/013 using T005's `STALE_REMINDER_HOURS`/
      `STALE_ARCHIVE_HOURS` constants: no-op on any entry that is
      `approved`, `rejected`, or already `auto_archived`; else archive at
      ≥24h (terminal), else re-notify once at ≥4h (`re_notified` gate),
      else no-op

**Checkpoint**: All 3 user stories independently functional — full feature
scope covered

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Regression safety and final validation

- [X] T030 [P] Run `pytest tests/ -v` (full suite) and confirm every
      feature 001 and 002 test still passes unmodified — the new
      `pipeline_sim.py` functions and fixtures must be pure additions with
      no shared mutable state
- [X] T031 [P] Run the exact command from `quickstart.md`'s "Automated test
      suite" section and confirm it passes:
      `pytest tests/integration/test_us1_email_draft_queued.py tests/integration/test_us2_email_approval_reply.py tests/integration/test_us3_stale_draft_guard.py -v`
- [X] T032 Run `/sp.analyze` across `spec.md`/`plan.md`/`tasks.md` to catch
      any cross-artifact drift (e.g., FR ↔ task coverage gaps) before
      implementation is considered complete, matching features 001 and
      002's pattern

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — T001 (skill-file backfill) can run
  alongside T002–T004 (fixtures, all different files)
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user
  stories; T005/T006 (pipeline_sim.py additions) are sequential (T006 will
  sit in the same file as T005 but doesn't call it, so no hard ordering
  beyond both landing before Phase 3); T007/T008 are `[P]`
- **User Stories (Phase 3-5)**: All depend on Foundational (Phase 2)
  completion
  - US1 (Phase 3) has no dependency on US2/US3
  - US2 (Phase 4) depends on US1's `queue_email_draft` (T017) only insofar
    as it needs a queue entry shape to resolve against — T008's fixture
    entries make US2 independently testable without calling US1's function
    directly
  - US3 (Phase 5) similarly depends only on the shared entry shape (T008),
    not on US1/US2's functions
- **Polish (Phase 6)**: Depends on all three user stories being complete

### Within Each User Story

- Tests are written first (T009-T016 before T017; T018-T024 before T025;
  T026-T028 before T029) and must FAIL until the corresponding
  implementation task lands
- Fixtures (Phase 1-2) before tests that consume them
- Story complete before moving to the next priority, per the MVP strategy
  below

### Parallel Opportunities

- T002, T003, T004 (Setup fixtures) — different files
- T007, T008 (Foundational) — different files, no dependency on each other
- T018 (US2 contract test) can be written in parallel with T009-T016 (US1
  tests), since both only depend on the Phase 2 foundation
- T030, T031 (Polish) — independent verification runs

---

## Parallel Example: Setup + Foundational

```bash
# Setup phase — launch together:
Task: "Create tests/fixtures/email_approval/leads_with_email.json"
Task: "Create tests/fixtures/email_approval/leads_without_email.json"
Task: "Create tests/fixtures/email_approval/tenant_auto_email_drafts.json"

# Foundational phase — launch together once Setup lands:
Task: "Create tests/contract/test_approval_queue_schema.py"
Task: "Create tests/fixtures/email_approval/queue_entries.json"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T008) — CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T009-T017)
4. **STOP and VALIDATE**: `pytest tests/integration/test_us1_email_draft_queued.py -v`
5. Demo: a dispatched lead with an email gets a queued draft and a WhatsApp
   alert — the core value proposition, independently provable

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add US1 → validate independently → MVP demonstrable
3. Add US2 → validate independently → full approve/reject loop demonstrable
4. Add US3 → validate independently → reliability guarantee demonstrable
5. Polish (T030-T032) → regression-safe, `/sp.analyze`-clean

---

## Notes

- No new agent-logic language or production `src/` code — every task here
  is a test function, fixture, or (T001) a one-time skill-file content fix,
  per `research.md` Decision 1
- `[P]` tasks touch different files with no dependency on an incomplete
  task
- `[Story]` label maps each task to its `spec.md` user story for
  traceability
- Verify tests fail before implementing the corresponding decision function
- Commit after each task or logical group
- Stop at any checkpoint to validate a story independently before moving on
