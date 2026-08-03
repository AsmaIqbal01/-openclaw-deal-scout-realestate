# Data Model: PK Dashboard Email Draft Queue Extension

## Email Draft Queue (response wrapper)

A new key in the dashboard's existing `"ok"` response data (feature 002
`contracts/dashboard-api.md`), computed by `dashboard/server.py` at
request time from `workspace/tenants/{tenant_id}/approval-queue.json`. Not
persisted anywhere itself — purely a served-response shape, per Decision 2.

| Field | Type | Notes |
|---|---|---|
| `state` | string | one of `"entries"`, `"empty"`, `"unavailable"` — the 3 states from spec.md's Interface Contract |
| `entries` | array | populated only when `state == "entries"`; see Enriched Email Draft Queue Entry below; capped at the 10 most recently `queued_at` entries (FR-010) |

**Derivation**:
- `approval-queue.json` does not exist for the tenant → `state: "empty"`, `entries: []`
- `approval-queue.json` exists but fails to parse → `state: "unavailable"`, `entries: []`
- `approval-queue.json` exists and parses, with ≥ 1 entry → `state: "entries"`, `entries` sorted by `queued_at` descending, sliced to 10

## Enriched Email Draft Queue Entry

The base fields are feature 003's Approval Queue Entry
(`specs/003-pk-email-approval-gate/data-model.md`,
`contracts/approval-queue-schema.json`) — this feature adds two display-only
fields on top, exactly as `dashboard/server.py`'s existing `_enrich()`
already does for Recent Leads (`tier_color`) and the existing Approval
Queue (`seconds_remaining`).

| Field | Type | Notes |
|---|---|---|
| `queue_id`, `tenant_id`, `lead_id`, `draft_subject`, `draft_body`, `recipient_email`, `queued_at`, `approved`, `approved_at`, `sent_at`, `re_notified`, `auto_archived`, `rejected` | — | verbatim from feature 003's stored entry (FR-002) |
| `status_label` | string | derived, one of `"Pending"`, `"Sent"`, `"Send Failed"`, `"Rejected"`, `"Auto-Archived"` — see FR-003's exact derivation order |
| `reminder_seconds_remaining` | number \| null | only set when `status_label == "Pending"`; seconds until the 4-hour re-notification mark, floored at 0 (FR-004) |
| `archive_seconds_remaining` | number \| null | only set when `status_label == "Pending"`; seconds until the 24-hour auto-archive mark, floored at 0 (FR-004) |

**Validation rules**: `status_label` derivation is the single source of
truth for display state — never re-derived independently in
`dashboard.js` (Decision 2). `reminder_seconds_remaining` and
`archive_seconds_remaining` are `null` for every non-`"Pending"` entry —
a resolved entry has no meaningful countdown.

## Relationships

- One **Email Draft Queue** response belongs to exactly one tenant, scoped
  by the same `tenant_id` query parameter feature 002 already validates
  (FR-007).
- Each **Enriched Email Draft Queue Entry** wraps exactly one feature 003
  **Approval Queue Entry** — this feature never creates, mutates, or
  deletes the underlying file (FR-006).
