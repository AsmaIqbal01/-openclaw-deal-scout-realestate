# Quickstart: PK Email Draft & Operator Approval Gate

## Prerequisites

1. A tenant (`workspace/tenants/{tenant_id}/USER.md`) with
   `auto_email_drafts: true` and the `brevo` ClawHub skill installed
   (`workspace/TOOLS.md`).
2. Feature 001's pipeline already dispatching leads (Tier 1 or confirmed
   Tier 2) with `contact.email` set for at least one test lead.

## Manual check — User Story 1 (draft queued automatically)

1. Run one heartbeat cycle with a dispatched lead that has a non-null
   `contact.email`.
2. Confirm a new entry appears in
   `workspace/tenants/{tenant_id}/approval-queue.json` with
   `approved: false`.
3. Confirm the tenant's `agent_whatsapp` received the
   "📧 New email draft awaiting your approval..." message referencing that
   `queue_id`.

## Manual check — User Story 2 (approve/reject)

1. Reply `/approve {queue_id}` from the tenant's `agent_whatsapp` number.
2. Confirm the email was sent to `recipient_email` and `sent_at` is set.
3. Repeat with a different pending entry and `/reject {queue_id}`; confirm
   no email is ever sent for it.

## Manual check — User Story 3 (stale-draft safety net)

1. Set a pending entry's `queued_at` to 4 hours 5 minutes in the past; run
   the pipeline; confirm exactly one re-notification WhatsApp message is
   sent, and running again does not send a second one.
2. Set another pending entry's `queued_at` to 24 hours 5 minutes in the
   past; run the pipeline; confirm `auto_archived: true` and that a
   subsequent `/approve` reply for it logs `unknown_queue_id_reply`.

## Automated test suite

```bash
pytest tests/integration/test_us1_email_draft_queued.py tests/integration/test_us2_email_approval_reply.py tests/integration/test_us3_stale_draft_guard.py -v
```

All tests extend `tests/pipeline_sim.py` (feature 001's pattern) with
draft/queue/approve/reject/stale-guard decision functions — fixture-based,
no live WhatsApp or email sends, no live Gemini/HubSpot calls.
