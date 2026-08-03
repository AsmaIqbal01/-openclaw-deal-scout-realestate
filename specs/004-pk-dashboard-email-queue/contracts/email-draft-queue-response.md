# Contract: Email Draft Queue Response

Applies to spec.md FR-001 through FR-005, FR-008 through FR-011. Extends
feature 002's existing `contracts/dashboard-api.md` — no new endpoint. The
`"ok"` response's `data` object gains one new key, `email_draft_queue`,
alongside everything feature 002 already returns there.

## `GET /state?tenant={tenant_id}` — `"ok"` response, extended

```json
{
  "status": "ok",
  "data": {
    "...": "everything feature 002 already returns, unchanged",
    "email_draft_queue": {
      "state": "entries",
      "entries": [
        {
          "queue_id": "b7e2c2b0-1234-4a1a-9d3d-0000000000f1",
          "tenant_id": "pk-test-agency-001",
          "lead_id": "b7e2c2b0-1234-4a1a-9d3d-0000000000e1",
          "draft_subject": "Property Enquiry — residential in DHA Phase 6",
          "draft_body": "Dear Ali Raza, ...",
          "recipient_email": "ali.raza@example.com",
          "queued_at": "2026-08-03T09:05:00+00:00",
          "approved": false,
          "approved_at": null,
          "sent_at": null,
          "re_notified": false,
          "auto_archived": false,
          "rejected": false,
          "status_label": "Pending",
          "reminder_seconds_remaining": 12000,
          "archive_seconds_remaining": 84000
        }
      ]
    }
  }
}
```

## `email_draft_queue.state` values

| Value | Trigger | Requirement |
|---|---|---|
| `"entries"` | `approval-queue.json` exists for the tenant with ≥ 1 entry | FR-001–FR-005, FR-010 |
| `"empty"` | `approval-queue.json` does not exist for the tenant | FR-008 |
| `"unavailable"` | `approval-queue.json` exists but fails to parse or read | FR-009 |

No other value exists. `entries` is always `[]` except when
`state == "entries"`.

## `status_label` derivation (FR-003)

Evaluated in this exact order — first match wins:

1. `auto_archived: true` → `"Auto-Archived"`
2. `rejected: true` → `"Rejected"`
3. `approved: true` and `sent_at` non-null → `"Sent"`
4. `approved: true` and `sent_at` null → `"Send Failed"`
5. otherwise → `"Pending"`

## Isolation and no-action guarantees

- This response's `email_draft_queue` key MUST only ever reflect the exact
  `tenant_id` supplied in the request — never another tenant's entries
  (FR-007), extending feature 002's existing isolation guarantee
  (`contracts/dashboard-api.md`'s "Isolation guarantee" section).
- No field in this response, and no markup or script that renders it,
  exposes an `/approve` or `/reject` action of any kind (FR-005) — WhatsApp
  remains the sole resolution channel.
