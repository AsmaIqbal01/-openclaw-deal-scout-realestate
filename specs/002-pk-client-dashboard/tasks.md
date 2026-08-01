---
description: "Task list for PK Client Dashboard — Pipeline Visibility & Read-Only Approval Queue"
---

# Tasks: PK Client Dashboard — Pipeline Visibility & Read-Only Approval Queue

**Input**: Design documents from `/specs/002-pk-client-dashboard/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md (all present)

**Tests**: Included. Unlike feature 001, this feature also includes real
implementation tasks (`dashboard/server.py`, `dashboard/*.js`,
`dashboard/*.html`/`.css`) — per `research.md` Decision 1, the dashboard is
deterministic web tooling, not LLM-interpreted agent behavior, so it is
this project's first feature with genuine new production code. Frontend
interactivity (`dashboard.js`, `radar.js`) is verified manually per
`quickstart.md`, since browser-side rendering isn't practically unit-testable
without introducing a new browser-automation dependency not otherwise
needed; `dashboard/server.py`'s request-handling logic is plain Python and
gets full automated `pytest` coverage.

**Revision note**: Renumbered after `/sp.analyze` findings G1, G2, and G3.
G1 (FR-007 CRM Sync had zero task coverage) and G2 (FR-008 Market Toggle had
zero task coverage) added T011–T012. G3 (FR-009's "over 10 leads" and
"Unknown" contact-name edge cases were untested) was resolved more
precisely than first suggested: both are already guaranteed upstream —
`contracts/dashboard-state-schema.json`'s `recent_leads` has `maxItems: 10`
(the cap is a schema/contract concern, not display logic) and
`contact_name` is a required non-null string (so "Unknown" must already be
substituted before the file is written, not computed by this feature). The
real gap was that no test proved the schema actually *rejects* an
over-10-entry array — added T008 to close that. All later task IDs shifted
accordingly from the original set (23 → 26 tasks).

**Organization**: Tasks are grouped by user story (US1/US2/US3 from
`spec.md`) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an
  incomplete task)
- **[Story]**: Maps to `spec.md` user stories (US1, US2, US3)
- All file paths are relative to the repository root

## Path Conventions

Single project. Per `plan.md`'s Structure Decision: `dashboard/` holds the
new static frontend + minimal server; `tests/contract/`,
`tests/integration/`, `tests/fixtures/dashboard/` extend the existing
`tests/` suite from feature 001.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Directory scaffolding and static frontend shell

- [X] T001 Create directory structure: `dashboard/`, `tests/fixtures/dashboard/`
- [X] T002 [P] Create `dashboard/index.html`: page shell with placeholders for all 7 sections (Pipeline Status, Lead Counter, Gemini Quota, Approval Queue, CRM Sync, Market Toggle, Recent Leads) plus a tenant-selector view and a Score Radar modal container, with Chart.js loaded via `<script>` CDN tag per `skills/remote-dashboard.md` Section 8
- [X] T003 [P] Create `dashboard/dashboard.css`: vanilla styling for stat tiles, status badges, the approval-queue list, the recent-leads table, and the radar modal overlay — no framework, no build step

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The fixture set and server core every user story depends on

**⚠️ CRITICAL**: No user story test can be written until this phase is complete

- [X] T004 Create `tests/fixtures/dashboard/normal_state.json`: a fully populated Dashboard State document matching `contracts/dashboard-state-schema.json`, including `market_mode: "PK"`, `crm_last_write_at` set to a specific recent ISO timestamp with a successful-write status, one `recent_leads` entry with `classification_score` 0.95 and zero `parse_warning`s, one with `classification_score` 0.75 and radar `data_integrity` 0.6 (one warning), and one `approval_queue` entry with `queued_at` 1 hour 50 minutes before a fixed reference "now"
- [X] T005 [P] Create `tests/fixtures/dashboard/no_state_tenant/USER.md`: a valid, active tenant configuration with no corresponding `dashboard-state.json` present, for the "no runs yet" case
- [X] T006 Create `dashboard/server.py` with the core request-handling functions: `load_dashboard_state(tenant_id, workspace_root)`, and `handle_state_request(tenant_id, workspace_root, known_tenants)` implementing all 4 response shapes from `contracts/dashboard-api.md` (`ok`, `select_tenant`, `no_runs_yet`, `tenant_not_configured`), plus a thin `http.server.SimpleHTTPRequestHandler` subclass routing `GET /state` to `handle_state_request` and serving `dashboard/` static files otherwise
- [X] T007 Create `tests/contract/test_dashboard_state_schema.py`: validate `tests/fixtures/dashboard/normal_state.json` against `contracts/dashboard-state-schema.json` via `jsonschema`, and confirm `dashboard/server.py`'s `load_dashboard_state` returns that same fixture unmodified (FR-002)
- [X] T008 Add `test_recent_leads_over_ten_entries_rejected` to `tests/contract/test_dashboard_state_schema.py`: construct an otherwise-valid Dashboard State document with 11 `recent_leads` entries and assert `jsonschema.validate` raises, per the schema's `maxItems: 10` (`/sp.analyze` finding G3 — the 10-entry cap is a schema/contract concern, not display logic, so this is where it must be proven)

**Checkpoint**: Foundation ready — user story test-writing can now begin

---

## Phase 3: User Story 1 - See pipeline status and quota at a glance (Priority: P1) 🎯 MVP

**Goal**: Prove the dashboard reflects `dashboard-state.json`'s Pipeline
Status, Lead Counter, Gemini Quota gauge, CRM Sync status, and Market
Toggle exactly as written.

**Independent Test**: Run `pytest tests/integration/test_us1_pipeline_status.py -v`.

- [X] T009 [US1] `tests/integration/test_us1_pipeline_status.py::test_pipeline_status_reflects_state` — using T004's fixture, call `handle_state_request` and assert `last_run_status`, `last_run_at`, `leads_today`, and `leads_this_week` in the response match the fixture exactly (Acceptance Scenario 1, FR-003/FR-004)
- [X] T010 [US1] Add `test_gemini_quota_gauge_value` to `tests/integration/test_us1_pipeline_status.py` — assert `gemini_quota_used` is 12 and the fixed daily limit is 20, so the gauge value is derivable as "12/20 used" (Acceptance Scenario 2, FR-005)
- [X] T011 [US1] Add `test_crm_sync_status_reflects_state` to `tests/integration/test_us1_pipeline_status.py` — using T004's fixture, assert `crm_last_write_at` in the response matches the fixture's value exactly (FR-007, `/sp.analyze` finding G1)
- [X] T012 [US1] Add `test_market_toggle_reflects_mode` to `tests/integration/test_us1_pipeline_status.py` — using T004's fixture, assert `market_mode` in the response is `"PK"`, matching the fixture (FR-008, `/sp.analyze` finding G2); the "not an editable control" half of FR-008 is verified manually per `quickstart.md`, since it's a frontend-rendering property
- [X] T013 [US1] Wire `dashboard/dashboard.js`: on load and every 30 seconds thereafter, `fetch('/state?tenant=' + tenantId)` and render Pipeline Status (badge + timestamp + next-run estimate), the two Lead Counter tiles, the Gemini Quota gauge, the CRM Sync status, and the read-only Market Toggle indicator from the JSON response — verified manually per `quickstart.md` User Story 1 check

**Checkpoint**: User Story 1 is independently testable and deployable as the dashboard's MVP.

---

## Phase 4: User Story 2 - Understand why a lead scored what it scored (Priority: P2)

**Goal**: Prove the Score Radar renders all 5 axes, the plain-English
reason, and the recommended-action badge, with correct tier coloring.

**Independent Test**: Run `pytest tests/integration/test_us2_score_radar.py -v`.

- [X] T014 [US2] `tests/integration/test_us2_score_radar.py::test_high_score_lead_radar_teal` — using T004's 0.95-score `recent_leads` entry, assert all 5 `radar` axes are present within 0.0–1.0, `data_integrity` is 1.0, and the score's tier maps to "teal" per `skills/remote-dashboard.md` Section 8's coloring rule (Acceptance Scenario 1, FR-010)
- [X] T015 [US2] Add `test_medium_score_lead_with_warning_radar_amber` to `tests/integration/test_us2_score_radar.py` — using T004's 0.75-score entry, assert `data_integrity` is 0.6 (one `parse_warning`) and the tier maps to "amber" (Acceptance Scenario 2, FR-010)
- [X] T016 [US2] Wire `dashboard/radar.js`: on a Recent Leads row click, render a Chart.js radar chart from that lead's 5 `radar` axis values, the `lead_quality_reason` caption, and the `recommended_action` badge, with teal/amber fill matching T014/T015 — verified manually per `quickstart.md` User Story 2 check

**Checkpoint**: User Stories 1 AND 2 both independently functional.

---

## Phase 5: User Story 3 - See leads awaiting a WhatsApp reply (Priority: P3)

**Goal**: Prove the read-only Approval Queue section shows Tier 2 leads and
their time remaining, with no approve/reject action anywhere.

**Independent Test**: Run `pytest tests/integration/test_us3_approval_queue_visibility.py tests/integration/test_no_approval_actions_in_frontend.py -v`.

- [X] T017 [US3] `tests/integration/test_us3_approval_queue_visibility.py::test_approval_queue_entry_shown_with_time_remaining` — using T004's `approval_queue` entry (`queued_at` 1h50m before "now"), assert the computed time remaining is approximately 10 minutes and the entry is present in the response (Acceptance Scenario 1, FR-006)
- [X] T018 [US3] Add `test_leads_pending_approval_count_matches_queue_length` to `tests/integration/test_us3_approval_queue_visibility.py` — assert `leads_pending_approval` equals `len(approval_queue)` in T004's fixture (FR-006 data consistency)
- [X] T019 [US3] Wire `dashboard/dashboard.js`: render the Approval Queue section from the `approval_queue` array (`contact_name` or "Unknown", `lead_source`, `classification_score`, countdown from `queued_at`), with no approve/reject control anywhere in this section's markup — verified manually per `quickstart.md` User Story 3 check
- [X] T020 [P] [US3] Create `tests/integration/test_no_approval_actions_in_frontend.py`: read `dashboard/index.html` and `dashboard/dashboard.js` as text and assert neither contains the strings `"approve"` or `"reject"` (case-insensitive) — an automated guard against scope creep back into the deferred email-draft-approval action (spec.md Scope Decision)

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Multi-tenant isolation (FR-011/012/013/014) and final
validation, spanning all three stories' data.

- [X] T021 [P] Create `tests/fixtures/dashboard/tenant_b_state.json`: a second tenant's Dashboard State with distinct `tenant_id` and field values from T004's fixture, for isolation testing
- [X] T022 `tests/integration/test_dashboard_tenant_isolation.py::test_no_tenant_param_shows_selector` — call `handle_state_request` with no `tenant_id` and a `known_tenants` list; assert `status` is `"select_tenant"` and only active tenants are listed (FR-012)
- [X] T023 Add `test_unconfigured_tenant_returns_not_configured` to `tests/integration/test_dashboard_tenant_isolation.py` — assert `status` is `"tenant_not_configured"` for an unknown `tenant_id` (FR-014)
- [X] T024 Add `test_missing_state_file_returns_no_runs_yet` to `tests/integration/test_dashboard_tenant_isolation.py` — using T005's fixture tenant, assert `status` is `"no_runs_yet"` (FR-013)
- [X] T025 Add `test_cross_tenant_isolation_strict` to `tests/integration/test_dashboard_tenant_isolation.py` — using T004 and T021, assert a request for T004's tenant never contains any field value from T021's tenant, and vice versa (FR-011, SC-004)
- [X] T026 Run `pytest tests/contract tests/integration -v` per `quickstart.md` and confirm all tests pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies — start immediately
- **Foundational (Phase 2)**: depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–5)**: all depend only on Foundational; independent of each other (can proceed in parallel if staffed, or in priority order P1 → P2 → P3)
- **Polish (Phase 6)**: T021 depends only on Foundational; T022–T025 depend on T004/T005/T021 fixtures (Foundational + Polish's own T021), not on US1/US2/US3's test files themselves; T026 depends on everything

### User Story Dependencies

- **User Story 1 (P1)**: depends only on Foundational — no dependency on US2/US3
- **User Story 2 (P2)**: depends only on Foundational — no dependency on US1/US3
- **User Story 3 (P3)**: depends only on Foundational — no dependency on US1/US2

### Parallel Opportunities

- T002 and T003 (Setup) can run in parallel after T001
- T005 (Foundational) can run in parallel with T004; T006 and T007 depend on T004 existing; T008 depends on T007's file existing (same file, sequential)
- T013, T016, T019 (frontend-wiring tasks in US1/US2/US3) each touch different files (`dashboard.js` for T013/T019 is the same file — T019 must follow T013, not run parallel with it; `radar.js` for T016 is a separate file)
- T020 (Polish-adjacent, filed under US3) can run in parallel with T017/T018 — different file
- T021 can run in parallel with any US1/US2/US3 task — different file, no dependency beyond Foundational

---

## Parallel Example: Setup + Foundational

```bash
# Setup, after T001:
Task: "Create dashboard/index.html shell"
Task: "Create dashboard/dashboard.css"

# Foundational, after directories exist:
Task: "Create tests/fixtures/dashboard/normal_state.json"
Task: "Create tests/fixtures/dashboard/no_state_tenant/USER.md"
# Then, depending on the fixture:
Task: "Create dashboard/server.py"
Task: "Create tests/contract/test_dashboard_state_schema.py"
Task: "Add test_recent_leads_over_ten_entries_rejected"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run `pytest tests/integration/test_us1_pipeline_status.py -v`, then the manual check in `quickstart.md`
5. This is a deployable MVP — agents can see whether the pipeline is alive and how much quota remains, without asking the developer

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add User Story 1 → validate independently → MVP
3. Add User Story 2 → validate independently → Score Radar trust-building live
4. Add User Story 3 → validate independently → read-only Tier 2 visibility live
5. Polish → tenant isolation proven across all three stories' data

### Parallel Team Strategy

With multiple developers: complete Setup + Foundational together, then
split Phases 3/4/5 (US1/US2/US3) — US1/US3 share `dashboard.js` (T013 then
T019 must be sequential if the same person isn't doing both), while US2's
`radar.js` (T016) is fully independent.

---

## Notes

- `[P]` tasks = different files, no dependency on an incomplete task
- `[Story]` label maps each task to its user story for traceability back to `spec.md`
- This is the project's first feature with genuine new production code (`dashboard/server.py`, `dashboard/*.js`, `dashboard/*.html`/`.css`) — per `research.md` Decision 1, the write side of `dashboard-state.json` remains existing Orchestrator behavior, out of scope here
- Every test task cites the exact FR or Acceptance Scenario it proves, so a failing test names the exact requirement that regressed
- Commit after each phase checkpoint, not after each individual task
