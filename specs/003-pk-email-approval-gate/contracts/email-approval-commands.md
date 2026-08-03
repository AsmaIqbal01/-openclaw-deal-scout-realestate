# Contract: Owner Email-Approval Commands

Applies to FR-007 through FR-011. Distinct from feature 001's
`/confirm`/`/discard` contract (`contracts/approval-commands.md`), which
governs Tier 2 *lead* review — this contract governs *drafted email*
approval, a separate decision made after a lead is already dispatched.

## Trigger message (Delivery → owner)

```
📧 New email draft awaiting your approval. Lead: {contact.name | lead_id}. Reply /approve {queue_id} or /reject {queue_id}
```

Sent once per draft (FR-007), and again exactly once more if unanswered
after 4 hours (FR-012, same message content).

## Owner reply commands

| Command | Format | Effect |
|---|---|---|
| Approve | `/approve {queue_id}` | `approved: true`, `approved_at` set, email sent, `sent_at` set on success (FR-009) |
| Reject | `/reject {queue_id}` | entry marked rejected; email never sent (FR-010) |

- `{queue_id}` MUST match a `pending` entry for the current tenant; a reply
  naming an unknown, already-resolved, or cross-tenant `queue_id` is
  ignored and logged as `unknown_queue_id_reply` (FR-011).
- Only a reply from the tenant's configured `agent_whatsapp` number is
  honored — consistent with feature 001's approval-commands contract.

## Timeout ladder (no reply)

| Elapsed since `queued_at` | Behavior |
|---|---|
| < 4 hours | entry stays `pending`, no action |
| ≥ 4 hours, < 24 hours, not yet re-notified | exactly one re-notification sent (FR-012) |
| ≥ 24 hours | `auto_archived: true`, permanent — a later `/approve` is treated as `unknown_queue_id_reply` (FR-013) |

## Response codes (logged, not HTTP)

| Code | Meaning |
|---|---|
| `queued` | draft appended to `approval-queue.json`, alert sent |
| `sent` | owner approved and the email send succeeded |
| `send_failed` | owner approved but the email send failed after one retry (`sent_at` stays null) |
| `rejected` | owner rejected the draft |
| `auto_archived` | 24-hour window elapsed with no reply |
| `unknown_queue_id_reply` | reply referenced a `queue_id` not `pending` for this tenant |
| `no_email_address` | lead had no `contact.email`; draft never created |
| `queue_full` | tenant's queue already had 50 entries; draft not created |
| `draft_generation_failed` | draft rendering itself failed; logged with `lead_id`, only that lead's email is skipped (FR-014) |
| `queue_write_failed` | `approval-queue.json` write failed; logged, owner alerted, draft not queued (FR-015) |
