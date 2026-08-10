# Quickstart: PK Pilot Tracking — PILOTS.md

## Prerequisites

None beyond a working checkout of this repository — `PILOTS.md` has no
runtime dependency on a live pipeline, tenant, or API key.

## Manual check — User Story 1 (see all 4 slots at a glance)

1. Open `PILOTS.md` at the repository root.
2. Confirm the first content line states the current count of `confirmed`
   slots out of 4 and whether the Phase 1 gate is met, matching the
   `onboarding_status` values in the 4 slots below it.
3. On a fresh scaffold (all 4 slots `not_started`), confirm it reads
   "0 of 4 confirmed — Phase 1 gate not met."

## Manual check — User Story 2 (record and update a slot)

1. Pick any `not_started` slot. Fill in `tenant_id`, `agent_name`,
   `agent_whatsapp`, and `gmail_account`; set `onboarding_status` to
   `tenant_configured`.
2. Once that tenant is actually live and has a real delivered-notification
   entry in `workspace/tenants/{tenant_id}/MEMORY.md`, copy that entry's
   `run_id` into `source_run_id` and its timestamp into
   `first_notification_delivered_at`; only then set `onboarding_status` to
   `confirmed`.
3. Attempt to set a different slot's `onboarding_status` to `confirmed`
   while its `source_run_id` is still `null` — confirm this is recognized
   as an invalid entry (FR-004/FR-011) and is not counted in the summary
   line.

## Manual check — User Story 3 (Phase 1 gate signal)

1. With 2 of 4 slots `confirmed`, confirm the summary line reads "2 of 4
   confirmed — Phase 1 gate not met."
2. Set a 3rd slot to `confirmed` (any 3 of the 4). Confirm the summary line
   updates to "3 of 4 confirmed — Phase 1 gate met — UK-market work
   (Phase 2) is now authorized to begin."

## Automated test suite

```bash
pytest tests/contract/test_pilots_schema.py -v
```

Parses `PILOTS.md`'s 4 fenced JSON blocks and validates each against
`contracts/pilot-slot-schema.json` — checks exact slot count, required
fields, the `onboarding_status` enum, the `confirmed`-requires-traceable-
source rule, and `tenant_id` uniqueness across slots. No live socket, no
runtime agent invocation, no tenant data beyond what is already committed
in `PILOTS.md` and `tests/fixtures/pilots/`.
