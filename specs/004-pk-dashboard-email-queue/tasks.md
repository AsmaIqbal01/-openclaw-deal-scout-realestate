---
description: "Task list for PK Dashboard Email Draft Queue Extension"
---

# Tasks: PK Dashboard Email Draft Queue Extension

**Input**: Design documents from `/specs/004-pk-dashboard-email-queue/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md (all present)

**Tests**: Included. Like feature 002 and unlike features 001/003, this
feature touches genuine production code (`dashboard/server.py` and the
vanilla frontend) — `pytest` covers `server.py`'s request-handling
functions directly against fixtures (no live socket), matching feature
002's established pattern; frontend rendering is verified manually per
`quickstart.md`.

**Note on research.md Decision 3**: planning initially flagged a need to
refine feature 002's `test_no_approval_actions_in_frontend.py` guard test
to allow a "Rejected" status label — on closer inspection this doesn't
apply, since Decision 2 (server-side status derivation, purely data-driven
frontend rendering) means `dashboard.js` never hardcodes that word. No task
below touches that test file.

**Organization**: Tasks are grouped by user story (US1/US2/US3 from
`spec.md`) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an
  incomplete task)
- **[Story]**: Maps to `spec.md` user stories (US1, US2, US3)
- All file paths are relative to the repository root

## Path Conventions

Single project. Extends the existing `dashboard/` component in place
(`server.py`, `index.html`, `dashboard.css`, `dashboard.js`) — no new
component or directory, per `plan.md`'s Structure Decision.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Fixture-factory extension and new fixture data

- [X] T001 [P] Extend `dashboard_workspace_factory` in `tests/conftest.py`
      to optionally write `approval-queue.json` per tenant: a new
      `approval_queue` config key (a list) writes valid JSON; a new
      `approval_queue_raw` key (a string) writes that string verbatim,
      unparsed, for malformed-JSON testing. Absent either key, no
      `approval-queue.json` file is created for that tenant (the existing
      "no drafts yet" case).
- [X] T002 [P] Create `tests/fixtures/dashboard/approval_queue_pending.json`:
      one entry for `pk-test-agency-001`, matching
      `specs/003-pk-email-approval-gate/contracts/approval-queue-schema.json`,
      with `approved: false`, `rejected: false`, `auto_archived: false`,
      `queued_at` 20 minutes before a fixed reference "now"
- [X] T003 [P] Create `tests/fixtures/dashboard/approval_queue_mixed_status.json`:
      5 entries for `pk-test-agency-001`, one of each resolvable state —
      pending, sent (`approved: true`, `sent_at` set), send-failed
      (`approved: true`, `sent_at: null`), rejected (`rejected: true`),
      auto-archived (`auto_archived: true`)
- [X] T004 [P] Create `tests/fixtures/dashboard/approval_queue_tenant_b.json`:
      one entry for `pk-tenant-b-003` (a different `tenant_id`), for the
      cross-tenant isolation test
- [X] T005 [P] Create `tests/fixtures/dashboard/approval_queue_eleven_entries.json`:
      11 pending entries for `pk-test-agency-001` with distinct `queued_at`
      timestamps spanning several hours, for the 10-entry display-cap test

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The read/derive/enrich functions every user story depends on

**⚠️ CRITICAL**: No user story test can be written until this phase is
complete

- [X] T006 Add constants to `dashboard/server.py`:
      `EMAIL_QUEUE_REMINDER_HOURS = 4`, `EMAIL_QUEUE_ARCHIVE_HOURS = 24`,
      `EMAIL_QUEUE_DISPLAY_CAP = 10` — mirroring
      `tests/pipeline_sim.py`'s `STALE_REMINDER_HOURS`/
      `STALE_ARCHIVE_HOURS` (feature 003) so the two independently-computed
      countdowns (WhatsApp re-notification vs. dashboard display) cannot
      silently drift apart (`research.md` Decision 2)
- [X] T007 Add `load_email_draft_queue_raw(tenant_id: str, workspace_root: Path) -> tuple[str, list]`
      to `dashboard/server.py`: reads
      `workspace_root/tenants/{tenant_id}/approval-queue.json`. Returns
      `("empty", [])` if the file does not exist **or** parses to an empty
      list (both mean "nothing to review" — FR-008); returns
      `("unavailable", [])` if the file exists but `json.load` raises
      (FR-009); returns `("entries", raw_list)` otherwise
- [X] T008 Add `derive_status_label(entry: dict) -> str` to
      `dashboard/server.py`, implementing FR-003's exact 5-way order:
      `auto_archived` → `"Auto-Archived"`; else `rejected` →
      `"Rejected"`; else `approved` and non-null `sent_at` → `"Sent"`;
      else `approved` and null `sent_at` → `"Send Failed"`; else
      `"Pending"`
- [X] T009 Add `enrich_email_draft_queue_entry(entry: dict, now: datetime) -> dict`
      to `dashboard/server.py`: returns a copy of `entry` with
      `status_label` (T008) added, plus `reminder_seconds_remaining` and
      `archive_seconds_remaining` — both `null` unless `status_label ==
      "Pending"`, in which case each is
      `max(0, HOURS * 3600 - elapsed_since(queued_at, now))` using T006's
      constants (mirrors `server.py`'s existing `seconds_remaining()`
      pattern for the Tier-2 Approval Queue)
- [X] T010 Add `build_email_draft_queue_response(tenant_id: str, workspace_root: Path, now: datetime) -> dict`
      to `dashboard/server.py`: calls T007; if state is `"entries"`, sorts
      by `queued_at` descending and slices to `EMAIL_QUEUE_DISPLAY_CAP`
      (T006), then enriches each surviving entry via T009 (T008 is called
      internally by T009); returns `{"state": ..., "entries": [...]}`
      matching `contracts/email-draft-queue-response.md`
- [X] T011 [P] Create `tests/contract/test_email_draft_queue_response.py`:
      validate an enriched entry's base fields (everything except
      `status_label`/`reminder_seconds_remaining`/
      `archive_seconds_remaining`) against
      `specs/003-pk-email-approval-gate/contracts/approval-queue-schema.json`
      via `jsonschema` (reusing that schema directly — not duplicated, per
      `research.md` Decision 1), and assert the 3 enrichment fields are
      present with correct types for a `"Pending"` entry and all-`null`
      for a `"Sent"` entry

**Checkpoint**: Foundation ready — user story test-writing can now begin

---

## Phase 3: User Story 1 - See every email draft awaiting a reply (Priority: P1) 🎯 MVP

**Goal**: Prove a tenant's pending drafts are shown in full, with correct
countdowns, and that "no drafts" renders a clean empty state.

**Independent Test**: `pytest tests/integration/test_us1_email_draft_queue_pending.py -v`

- [X] T012 [US1] `tests/integration/test_us1_email_draft_queue_pending.py::test_pending_entry_shown_with_full_content`
      — Acceptance Scenario 1: using T001's extended factory with T002's
      fixture, call `handle_state_request`; assert
      `data["email_draft_queue"]["state"] == "entries"`, the entry's
      `draft_subject`/`draft_body`/`recipient_email`/`queued_at` match the
      fixture exactly, `status_label == "Pending"`, and both
      `reminder_seconds_remaining` and `archive_seconds_remaining` are
      positive numbers
- [X] T013 [US1] Add `test_no_email_drafts_yet_shows_empty_state` —
      Acceptance Scenario 2 (FR-008): a tenant configured with no
      `approval_queue`/`approval_queue_raw` key at all (no file created);
      assert `state == "empty"` and `entries == []`
- [X] T014 [US1] Wire T010's `build_email_draft_queue_response` into
      `handle_state_request`'s `"ok"` response in `dashboard/server.py`:
      after `state = load_dashboard_state(...)` succeeds, merge
      `enriched["email_draft_queue"] = build_email_draft_queue_response(tenant_id, workspace_root, now)`
      into the dict `_enrich()` already returns, before returning
      `{"status": "ok", "data": enriched}` (FR-001, FR-011 — no new
      request type, same response)

**Checkpoint**: US1 fully functional and independently testable — MVP

---

## Phase 4: User Story 2 - See the outcome of a resolved draft (Priority: P2)

**Goal**: Prove every resolvable status (Sent, Send Failed, Rejected,
Auto-Archived) is labeled correctly and carries no stale countdown.

**Independent Test**: `pytest tests/integration/test_us2_email_draft_queue_history.py -v`

- [X] T015 [US2] `tests/integration/test_us2_email_draft_queue_history.py::test_status_labels_for_each_resolved_state`
      — Acceptance Scenarios 1-4: using T003's fixture, assert each of the
      5 entries' `status_label` matches its expected value (Pending, Sent,
      Send Failed, Rejected, Auto-Archived) per FR-003's derivation order
- [X] T016 [US2] Add `test_resolved_entries_have_null_time_remaining_fields`
      — FR-004: for every entry in T003's fixture whose `status_label !=
      "Pending"`, assert `reminder_seconds_remaining is None` and
      `archive_seconds_remaining is None`
- [X] T017 [US2] Add `test_auto_archived_takes_precedence_over_rejected` —
      the Edge Case from spec.md: construct an entry with both
      `rejected: true` and `auto_archived: true` set; assert
      `status_label == "Auto-Archived"` (T008's order checks
      `auto_archived` first) and that `derive_status_label` does not raise
      on this otherwise-impossible-in-practice combination

**Checkpoint**: US1 and US2 both work independently — the queue is now a
complete, correctly-labeled record

---

## Phase 5: User Story 3 - Queue data never leaks across tenants or breaks the rest of the dashboard (Priority: P3)

**Goal**: Prove tenant isolation holds and a malformed queue file degrades
gracefully without affecting the rest of the dashboard.

**Independent Test**: `pytest tests/integration/test_us3_email_draft_queue_isolation.py -v`

- [X] T018 [US3] `tests/integration/test_us3_email_draft_queue_isolation.py::test_cross_tenant_isolation`
      — Acceptance Scenario 1: configure tenant A (T002's fixture) and
      tenant B (T004's fixture) in the same workspace; assert tenant A's
      response `email_draft_queue.entries` contains none of tenant B's
      `queue_id`/`lead_id` values, and vice versa
- [X] T019 [US3] Add `test_malformed_approval_queue_json_isolated_failure`
      — Acceptance Scenario 2 (FR-009): use T001's `approval_queue_raw`
      key with invalid JSON text for a tenant that also has a valid
      `dashboard-state.json`; assert `email_draft_queue == {"state":
      "unavailable", "entries": []}` while every other top-level field in
      the response (`last_run_status`, `leads_today`, `recent_leads`, the
      existing `approval_queue`, etc.) still matches the
      `dashboard-state.json` fixture exactly, unaffected
- [X] T020 [US3] Add `test_display_capped_at_ten_most_recent` — FR-010:
      using T005's 11-entry fixture, assert exactly 10 entries are
      returned, sorted by `queued_at` descending, and the single oldest
      entry is excluded

**Checkpoint**: All 3 user stories independently functional — backend
scope complete

---

## Phase 6: Frontend

**Purpose**: Render the Email Draft Queue section — verified manually per
`quickstart.md`, matching feature 002's precedent for frontend JS

- [X] T021 [P] Add a new "Email Draft Queue" section to
      `dashboard/index.html`: `<section id="email-draft-queue" class="card"><h2>Email Draft Queue</h2><ul id="email-draft-queue-list"></ul></section>`,
      placed inside `#dashboard-view`, after the existing Approval Queue
      section
- [X] T022 [P] Add status-badge styles to `dashboard/dashboard.css`: reuse
      the existing `.badge` base class with 5 new modifier classes
      (`.badge.pending`, `.badge.sent`, `.badge.send-failed`,
      `.badge.rejected`, `.badge.auto-archived`) — class names are derived
      from `status_label.toLowerCase().replace(" ", "-")` at render time,
      not hardcoded per-entry markup
- [X] T023 Implement `renderEmailDraftQueue(queueData)` in
      `dashboard/dashboard.js`: purely data-driven (no hardcoded status
      text anywhere in this function, per `research.md` Decision 3) —
      renders `"No email drafts yet"` for `state == "empty"`,
      `"Unable to load email drafts"` for `state == "unavailable"`, and
      for `state == "entries"` one list item per entry showing
      `draft_subject`, `recipient_email`, a badge whose class and text
      both come from `entry.status_label`, and — only when
      `entry.reminder_seconds_remaining` is not `null` — the reminder/
      archive countdown via the existing `formatTimeRemaining` helper.
      Wire into `renderDashboard()` via the existing conditional-call
      pattern: `if (window.renderEmailDraftQueue) { window.renderEmailDraftQueue(data.email_draft_queue) }`,
      matching `renderApprovalQueue`'s wiring; export
      `window.renderEmailDraftQueue = renderEmailDraftQueue;`

**Checkpoint**: Full feature scope covered — backend and frontend

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Regression safety and final validation

- [X] T024 [P] Run `pytest tests/ -v` (full suite) and confirm every
      feature 001, 002, and 003 test still passes unmodified
- [X] T025 [P] Run the exact command from `quickstart.md`'s "Automated
      test suite" section and confirm it passes
- [X] T026 Manual quickstart checks (`specs/004-pk-dashboard-email-queue/quickstart.md`
      User Stories 1-3) against a live `dashboard/server.py` instance with
      fixture data — frontend rendering is not unit-tested, matching
      feature 002's precedent
- [X] T027 Run `/sp.analyze` across `spec.md`/`plan.md`/`tasks.md` to catch
      any cross-artifact drift before implementation is considered
      complete, matching features 001-003's pattern

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — T001-T005 are all `[P]`,
  different files
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories;
  T006-T010 are sequential (each builds on the previous function in the
  same file); T011 is `[P]` with T006-T010 only in the sense that it can
  be drafted in parallel but needs T009's output shape to assert against
  meaningfully
- **User Stories (Phase 3-5)**: All depend on Foundational (Phase 2)
  completion
  - US1 (Phase 3) has no dependency on US2/US3
  - US2 (Phase 4) and US3 (Phase 5) both depend only on the shared
    Foundational functions (T006-T010), not on US1's specific tests —
    independently testable per spec.md
- **Frontend (Phase 6)**: Depends on Phase 3's T014 (the response shape
  must be finalized and wired in `server.py` before the frontend renders
  it) — can start once T014 lands, does not need US2/US3 complete
- **Polish (Phase 7)**: Depends on all of the above being complete

### Within Each User Story

- Tests are written first (T012-T013 before T014 lands the wiring;
  T015-T017 and T018-T020 exercise Foundational functions already
  implemented in Phase 2, so they can be written and run immediately after
  Phase 2 completes)
- Fixtures (Phase 1) before tests that consume them

### Parallel Opportunities

- T001-T005 (Setup) — different files
- T021, T022 (frontend markup/CSS) — different files, no dependency on
  each other; T023 (JS) depends on both existing since it targets the DOM
  IDs T021 defines and the classes T022 defines
- T024, T025 (Polish verification runs) — independent

---

## Parallel Example: Setup

```bash
# Launch together:
Task: "Extend dashboard_workspace_factory in tests/conftest.py"
Task: "Create tests/fixtures/dashboard/approval_queue_pending.json"
Task: "Create tests/fixtures/dashboard/approval_queue_mixed_status.json"
Task: "Create tests/fixtures/dashboard/approval_queue_tenant_b.json"
Task: "Create tests/fixtures/dashboard/approval_queue_eleven_entries.json"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T011) — CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T012-T014)
4. **STOP and VALIDATE**: `pytest tests/integration/test_us1_email_draft_queue_pending.py -v`
5. Demo: a tenant's pending email drafts appear on the dashboard with full
   content and countdowns — the core value proposition

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add US1 → validate independently → MVP demonstrable (backend only)
3. Add US2 → validate independently → resolved-history view complete
4. Add US3 → validate independently → isolation/resilience proven
5. Add Frontend (Phase 6) → the section is actually visible in a browser
6. Polish (Phase 7) → regression-safe, `/sp.analyze`-clean

---

## Notes

- No guard-test modification appears anywhere above — `research.md`
  Decision 3 concluded none is needed
- `[P]` tasks touch different files with no dependency on an incomplete
  task
- `[Story]` label maps each task to its `spec.md` user story for
  traceability
- Verify tests fail before implementing the corresponding function
- Commit after each task or logical group
- Stop at any checkpoint to validate a story independently before moving on
