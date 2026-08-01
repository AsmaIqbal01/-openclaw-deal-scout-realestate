---
description: "Task list for PK Lead Intake, Classification & WhatsApp Notification"
---

# Tasks: PK Lead Intake, Classification & WhatsApp Notification

**Input**: Design documents from `/specs/001-pk-lead-intake-notify/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md (all present)

**Tests**: Included — per `research.md` Decision 1, no new agent-logic code
is being written (the Orchestrator/Intake/Delivery behavior already exists in
`agents/*/SOUL.md` and the PK skill files). This feature's deliverable *is*
the fixture-based `pytest` suite that proves those existing behaviors satisfy
every functional requirement in `spec.md`, per Constitution Checker gate Q2.

**Organization**: Tasks are grouped by user story (US1/US2/US3 from
`spec.md`) to enable independent implementation and testing of each story.

**Revision note**: Renumbered after `/sp.analyze` findings I1 and G1. I1
(the 0.5–0.69 score-band contradiction between `agents/intake/SOUL.md` and
`agents/delivery/SOUL.md`, now resolved by moving Intake's reject threshold
to < 0.7, matching `spec.md` FR-003/FR-006/`data-model.md`) added T009–T010.
G1 (FR-001's intake trigger/routing logic had no dedicated test) added
T019–T020. All later task IDs shifted accordingly from the original set.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an
  incomplete task)
- **[Story]**: Maps to `spec.md` user stories (US1, US2, US3)
- All file paths are relative to the repository root

## Path Conventions

Single project, no new `src/`. Per `plan.md`'s Structure Decision:
`tests/contract/`, `tests/integration/`, `tests/fixtures/` are new;
`agents/*/SOUL.md` and `skills/*.md` are existing and unchanged;
`workspace/tenants/{tenant_id}/` holds new per-tenant runtime config.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Test-suite scaffolding and tenant configuration templates

- [X] T001 Create directory structure: `tests/contract/`, `tests/integration/`, `tests/fixtures/emails/`, `tests/fixtures/whatsapp/`, `tests/fixtures/gemini/`, `tests/fixtures/hubspot/`, `tests/fixtures/tenants/`, `tests/fixtures/memory/`
- [X] T002 [P] Add `pytest.ini` at repo root with `testpaths = tests`
- [X] T003 [P] Add `tests/requirements.txt` listing `pytest` and `jsonschema`
- [X] T004 [P] Create `workspace/tenants/_template/USER.md` tenant config template matching the schema in `skills/multi-tenant-router.md` (market_mode, agent_whatsapp, gmail_account, hubspot_portal_id, hubspot_api_key_env, gemini_api_key_env, active)
- [X] T005 [P] Create `.env.example` at repo root listing `HUBSPOT_API_KEY_ENV` and `GEMINI_API_KEY_ENV` placeholder variable *names* only (never real keys), per `skills/multi-tenant-router.md` Step 3

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared fixtures and harness every user story's tests depend on

**⚠️ CRITICAL**: No user story test can be written until this phase is complete

- [X] T006 Create `tests/fixtures/tenants/test_tenant.json` (tenant_id: `pk-test-agency-001`, market_mode: `PK`, agent_whatsapp set) matching the Tenant entity in `data-model.md`
- [X] T007 Create `tests/conftest.py` with a `tenant_context` fixture (loads T006's fixture) and a `memory_state` fixture (configurable `gemini_today_count` and `processed_ids`, per `data-model.md`'s Tenant entity)
- [X] T008 [P] Create `tests/contract/test_lead_schema.py` validating inline example lead objects (one valid, one missing a required field, one with a duplicate-shaped `raw_source_id`) against `contracts/lead-schema.json` — this is the FR-004 baseline every story's leads must pass
- [X] T009 [P] Create `tests/fixtures/gemini/rejection_boundary_responses.json` with three example classification results at `classification_score` 0.65, 0.69, and 0.70 — covers the merged reject-below-0.7 band from FR-003 (`/sp.analyze` finding I1)
- [X] T010 Create `tests/integration/test_rejection_threshold.py::test_below_0_70_rejected_by_intake` — using T009, assert scores 0.65 and 0.69 are rejected by the Intake Sub-Agent (never forwarded to Delivery, `rejection_reason` logged) and 0.70 is forwarded to Delivery's Tier 2 hold path (FR-003/FR-006 boundary, `/sp.analyze` finding I1)

**Checkpoint**: Foundation ready — user story test-writing can now begin

---

## Phase 3: User Story 1 - Instant notification for a high-confidence lead (Priority: P1) 🎯 MVP

**Goal**: Prove the auto-dispatch path (score ≥ 0.9 → HubSpot write + WhatsApp
"🔴 URGENT —" notification) works end-to-end from both Gmail and WhatsApp
sources, and that the intake trigger/routing logic correctly selects each
source's parser.

**Independent Test**: Run `pytest tests/integration/test_us1_auto_dispatch.py -v` — all pass using only fixture data, no live external calls.

### Fixtures for User Story 1

- [X] T011 [P] [US1] Create `tests/fixtures/emails/zameen_alert_high_confidence.txt` (contact + budget present) per `skills/zameen-parser.md`'s field structure
- [X] T012 [P] [US1] Create `tests/fixtures/whatsapp/whatsapp_forward_high_confidence.txt` per `skills/pk-whatsapp-lead.md` Pattern A (forwarded listing, clear contact + price)
- [X] T013 [P] [US1] Create `tests/fixtures/gemini/high_confidence_response.json` (`classification_score: 0.95`) matching `skills/lead-classifier-pk.md`'s response JSON structure
- [X] T014 [P] [US1] Create `tests/fixtures/hubspot/contact_deal_success.json` mocking a successful contact + deal creation response
- [X] T015 [P] [US1] Create `tests/fixtures/emails/non_pk_unrelated.txt` — an email matching neither the Zameen/OLX sender domains nor any PK trigger keyword (`/sp.analyze` finding G1)

### Tests for User Story 1

- [X] T016 [US1] `tests/integration/test_us1_auto_dispatch.py::test_zameen_email_auto_dispatch` — using T011/T013/T014, assert `classification_score` ≥ 0.9 → HubSpot contact+deal created → WhatsApp message prefixed "🔴 URGENT — " sent, within one simulated run (Acceptance Scenario 1, FR-005)
- [X] T017 [US1] Add `test_whatsapp_forward_auto_dispatch` to `tests/integration/test_us1_auto_dispatch.py` — same outcome via the WhatsApp source path using T012 (Acceptance Scenario 2)
- [X] T018 [US1] Add `test_auto_dispatch_order` to `tests/integration/test_us1_auto_dispatch.py` — assert the CRM write is confirmed *before* the notification is sent, not concurrently or after (FR-005 ordering)
- [X] T019 [US1] Add `test_duplicate_raw_source_id_rejected` to `tests/integration/test_us1_auto_dispatch.py` — assert a second lead with the same `raw_source_id` as an already-`processed_ids` entry is rejected before any CRM write (FR-004 dedup edge case)
- [X] T020 [US1] Add `test_intake_routing_by_source` to `tests/integration/test_us1_auto_dispatch.py` — using T011/T012/T015, assert a Zameen-domain email routes via `skills/zameen-parser.md` with `source: zameen_alert`, a WhatsApp message routes via `skills/pk-whatsapp-lead.md` with `source: whatsapp_forward`, and the non-matching fixture (T015) produces no lead candidate at all (FR-001, `/sp.analyze` finding G1)

**Checkpoint**: User Story 1 is independently testable and deployable as the MVP.

---

## Phase 4: User Story 2 - Human review for a medium-confidence lead (Priority: P2)

**Goal**: Prove the 0.70–0.89 band holds the CRM write, asks the owner via
WhatsApp, and only proceeds on `/confirm` (or is dropped on `/discard`/timeout).

**Independent Test**: Run `pytest tests/integration/test_us2_human_review.py tests/contract/test_approval_commands.py -v`.

### Fixtures & Contract for User Story 2

- [X] T021 [P] [US2] Create `tests/fixtures/whatsapp/medium_confidence_no_budget.txt` (contact present, no budget) per `skills/pk-whatsapp-lead.md` Pattern B, budget line removed
- [X] T022 [P] [US2] Create `tests/fixtures/gemini/medium_confidence_response.json` (`classification_score: 0.80`)
- [X] T023 [P] [US2] Create `tests/contract/test_approval_commands.py` validating the `/confirm {lead_id}` / `/discard {lead_id}` contract in `contracts/approval-commands.md`: correct `lead_id` match, unknown `lead_id` → `unknown_lead_id_reply`, reply from a non-`agent_whatsapp` number → `unauthorized_reply_source`

### Tests for User Story 2

- [X] T024 [US2] `tests/integration/test_us2_human_review.py::test_medium_score_holds_for_review` — using T021/T022, assert no CRM write occurs and the owner receives "Review needed — score {score}" (Acceptance Scenario 1, FR-006)
- [X] T025 [US2] Add `test_confirm_within_window_dispatches` to `tests/integration/test_us2_human_review.py` — assert `/confirm {lead_id}` within 2 hours triggers the CRM write and standard agent notification (Acceptance Scenario 2, FR-007)
- [X] T026 [US2] Add `test_discard_or_timeout_blocks` to `tests/integration/test_us2_human_review.py` — assert both `/discard {lead_id}` and a 2-hour no-reply timeout result in `owner_no_response`/rejected logging with no CRM write and no agent notification (Acceptance Scenario 3, FR-008)

**Checkpoint**: User Stories 1 AND 2 both independently functional.

---

## Phase 5: User Story 3 - Reliable operation within the free Gemini quota (Priority: P3)

**Goal**: Prove the pipeline halts safely at the 18/day quota boundary and
warns (without halting) in the 15–17 band.

**Independent Test**: Run `pytest tests/integration/test_us3_quota_guard.py -v`.

### Fixtures for User Story 3

- [X] T027 [P] [US3] Create `tests/fixtures/memory/quota_at_18.json` (`gemini_today_count: 18`)
- [X] T028 [P] [US3] Create `tests/fixtures/memory/quota_at_16.json` (`gemini_today_count: 16`)

### Tests for User Story 3

- [X] T029 [US3] `tests/integration/test_us3_quota_guard.py::test_quota_boundary_halts_pipeline` — using T027, assert zero Gemini calls are made, `quota_exhausted: true` is logged, and exactly one owner WhatsApp alert is sent (Acceptance Scenario 1, FR-009)
- [X] T030 [US3] Add `test_quota_low_warning_only` to `tests/integration/test_us3_quota_guard.py` — using T028, assert classification proceeds normally with a "quota low: {count}/20 used" warning logged (Acceptance Scenario 2)

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Requirements that span all three stories — tenant isolation,
error paths, and run logging — plus final quickstart validation.

- [X] T031 [P] Create `tests/integration/test_tenant_isolation.py` — assert a lead whose `tenant_id` doesn't match the active `tenant_context` is rejected and logged, with no cross-tenant CRM write or notification (FR-010, SC-006)
- [X] T032 [P] Create `tests/integration/test_error_paths.py::test_hubspot_write_retry_then_halt` — assert a failing CRM write retries once after 30s, then halts that lead, logs the error, and sends no notification (FR-012)
- [X] T033 Add `test_whatsapp_send_retry_then_continue` to `tests/integration/test_error_paths.py` — assert a failing WhatsApp send retries once, then logs and continues the run without blocking remaining leads (FR-013)
- [X] T034 Add `test_gmail_oauth_failure_partial_degradation` to `tests/integration/test_error_paths.py` — assert an invalid/expired Gmail OAuth token logs an auth error and the run continues processing WhatsApp-sourced leads only (FR-014)
- [X] T035 Add `test_hubspot_auth_failure_aborts_run` to `tests/integration/test_error_paths.py` — assert an invalid HubSpot API key fails the pre-flight check and aborts the entire tenant run before any leads are processed (FR-015)
- [X] T036 [P] Create `tests/integration/test_run_logging.py` — assert `run_id`, `tenant_id`, `started_at`, `completed_at`, `leads_found`, `leads_classified`, `leads_rejected`, `crm_writes`, `notifications_sent`, `gemini_calls_this_run` are written to `MEMORY.md` after every run, including aborted runs (FR-011)
- [X] T037 Run `pytest tests/contract tests/integration -v` per `quickstart.md` and confirm all tests pass with zero live external calls

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies — start immediately
- **Foundational (Phase 2)**: depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–5)**: all depend only on Foundational; independent of each other (can proceed in parallel if staffed, or in priority order P1 → P2 → P3)
- **Polish (Phase 6)**: T031 (tenant isolation) depends only on Foundational and could run earlier if desired; T032–T036 depend on all three user stories being complete since the error-path and run-logging tests reference tier boundaries and scenarios from every story; T037 depends on everything

### User Story Dependencies

- **User Story 1 (P1)**: depends only on Foundational — no dependency on US2/US3
- **User Story 2 (P2)**: depends only on Foundational — no dependency on US1/US3
- **User Story 3 (P3)**: depends only on Foundational — no dependency on US1/US2

### Parallel Opportunities

- All Setup tasks marked `[P]` (T002–T005) can run in parallel after T001
- T008 and T009 (Foundational) can run in parallel with T006/T007 once directories exist; T010 depends on T007 (conftest) and T009 (fixture)
- All fixture-creation tasks within a story (`[P]` marked) can run in parallel; test-writing tasks within a story share one file and run sequentially
- Once Foundational is done, Phases 3, 4, and 5 (US1, US2, US3) can be staffed and run fully in parallel
- T031, T032, and T036 in Polish (different files) can run in parallel; T033–T035 are sequential (same file as T032)

---

## Parallel Example: User Story 1

```bash
# Launch all fixture tasks for User Story 1 together:
Task: "Create tests/fixtures/emails/zameen_alert_high_confidence.txt"
Task: "Create tests/fixtures/whatsapp/whatsapp_forward_high_confidence.txt"
Task: "Create tests/fixtures/gemini/high_confidence_response.json"
Task: "Create tests/fixtures/hubspot/contact_deal_success.json"
Task: "Create tests/fixtures/emails/non_pk_unrelated.txt"

# Then write tests sequentially (same file: test_us1_auto_dispatch.py):
Task: "test_zameen_email_auto_dispatch"
Task: "test_whatsapp_forward_auto_dispatch"
Task: "test_auto_dispatch_order"
Task: "test_duplicate_raw_source_id_rejected"
Task: "test_intake_routing_by_source"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run `pytest tests/integration/test_us1_auto_dispatch.py -v`, then the manual check in `quickstart.md`
5. This is a deployable MVP — the product's core promise ("never miss a lead") is proven for the auto-dispatch path

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add User Story 1 → validate independently → MVP
3. Add User Story 2 → validate independently → CRM data-quality protection live
4. Add User Story 3 → validate independently → zero-cost quota guarantee proven
5. Polish → tenant isolation, error paths, and run logging proven across all three stories

### Parallel Team Strategy

With multiple developers: complete Setup + Foundational together, then split
Phases 3/4/5 (US1/US2/US3) across developers — they touch entirely separate
fixture and test files with no shared dependencies — then converge on Polish.

---

## Notes

- `[P]` tasks = different files, no dependency on an incomplete task
- `[Story]` label maps each task to its user story for traceability back to `spec.md`
- No new files under `agents/*/SOUL.md` or `skills/*.md`, except the one-line
  threshold correction already applied to `agents/intake/SOUL.md` Hard Rule
  #1 (0.5 → 0.7) to resolve `/sp.analyze` finding I1 — no further changes to
  existing agent/skill content are needed; the rest of `research.md`
  Decision 1 still holds
- Every test task cites the exact FR or Acceptance Scenario it proves, so a failing test names the exact requirement that regressed
- Commit after each phase checkpoint, not after each individual task
