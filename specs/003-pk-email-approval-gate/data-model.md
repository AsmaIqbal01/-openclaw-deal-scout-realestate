# Data Model: PK Email Draft & Operator Approval Gate

## Approval Queue Entry

One drafted email awaiting or past a decision, stored in
`workspace/tenants/{tenant_id}/approval-queue.json` (append-only array).

| Field | Type | Notes |
|---|---|---|
| `queue_id` | string (UUIDv4) | |
| `tenant_id` | string | must match the tenant that triggered the draft |
| `lead_id` | string | references the originating `Lead` (feature 001) |
| `draft_subject` | string | per FR-003's exact template |
| `draft_body` | string | per FR-003's exact template |
| `recipient_email` | string | copied from the lead's `contact.email` |
| `queued_at` | ISO8601 timestamp | starts both the 4-hour and 24-hour clocks |
| `approved` | boolean | `false` until an owner `/approve` reply |
| `approved_at` | ISO8601 timestamp \| null | set only on `/approve` |
| `sent_at` | ISO8601 timestamp \| null | set only once the email send succeeds (FR-009) |
| `re_notified` | boolean | internal — tracks whether the one-time 4-hour reminder has already fired (FR-012) |
| `auto_archived` | boolean | `true` once the 24-hour window elapses with no reply (FR-013) |
| `rejected` | boolean | `true` once the owner replies `/reject {queue_id}` (FR-010); not in the schema's `required` list (a `pending` entry omits it / defaults `false`), but is the field that records the `rejected` status named in this feature's Key Entities section |

**Validation rules**: `tenant_id` MUST match the tenant whose queue file
this entry lives in (FR-004). A new entry MUST NOT overwrite or remove any
existing entry (FR-005). The queue MUST NOT exceed 50 entries (FR-006).

**State transitions**:

```
pending → [owner /approve] → approved → sent (once send succeeds)
                                       → send_failed (retried once, then
                                         logged + owner alerted, sent_at
                                         stays null) [FR-009]
pending → [owner /reject]  → rejected (rejected: true)
pending → [4h elapsed, no reply]  → pending (re_notified: true) — one
                                     reminder only, stays pending
pending → [24h elapsed, no reply] → auto_archived (terminal — FR-013)
```

`auto_archived` and `rejected` are both terminal: no reply of any kind can
move an entry out of either state. A reply naming a `queue_id` already in
`sent`, `rejected`, or `auto_archived` state is treated identically to an
unknown `queue_id` (FR-011).

## Email Draft

The generated content itself — not persisted separately from the Approval
Queue Entry's `draft_subject`/`draft_body` fields, but conceptually
distinct: derived from a `Lead` (feature 001) and a `Tenant`'s `agent_name`
and agency name, per the exact PK template in FR-003.

## Relationships

- One **Tenant** (feature 001) has its own `approval-queue.json`, isolated
  from every other tenant's (FR-004, cross-tenant edge case).
- One **Approval Queue Entry** references exactly one **Lead** via
  `lead_id`, and is created only after that lead's CRM write already
  succeeded (FR-001) — it never exists for a lead that was rejected or
  still held at Tier 2.
