# Quickstart: PK Dashboard Email Draft Queue Extension

## Prerequisites

1. A tenant (`workspace/tenants/{tenant_id}/USER.md`) already dashboard-
   configured per feature 002.
2. Feature 003's pipeline already queuing email drafts into
   `workspace/tenants/{tenant_id}/approval-queue.json` for at least one
   test lead.

## Manual check — User Story 1 (see pending drafts)

1. Ensure `approval-queue.json` has at least one entry with
   `approved: false`, `rejected: false`, `auto_archived: false`.
2. Load the dashboard with `?tenant={tenant_id}`.
3. Confirm the Email Draft Queue section shows that entry's exact
   `draft_subject` and `draft_body`, labeled "Pending," with reminder/
   archive countdowns, and no approve/reject control anywhere on the page.

## Manual check — User Story 2 (resolved history)

1. Set up one entry each with `sent_at` set (Sent), `rejected: true`
   (Rejected), `auto_archived: true` (Auto-Archived), and `approved: true`
   with `sent_at: null` (Send Failed).
2. Load the dashboard; confirm each entry shows its correct status label
   and none render any action control.

## Manual check — User Story 3 (isolation + resilience)

1. Load `?tenant=A` then `?tenant=B` back-to-back; confirm tenant A's
   drafts never appear under tenant B's Email Draft Queue section.
2. Replace a tenant's `approval-queue.json` with invalid JSON; reload the
   dashboard; confirm every other section still renders normally and the
   Email Draft Queue section alone shows "Unable to load email drafts."

## Automated test suite

```bash
pytest tests/contract/test_email_draft_queue_response.py tests/integration/test_us1_email_draft_queue_pending.py tests/integration/test_us2_email_draft_queue_history.py tests/integration/test_us3_email_draft_queue_isolation.py tests/integration/test_no_approval_actions_in_frontend.py -v
```

All tests call `dashboard/server.py`'s functions directly against fixture
`approval-queue.json` files — no live socket, no live WhatsApp/email calls.
