# Contract: Owner Approval Commands (Tier 2 Review)

Applies to FR-006, FR-007, FR-008. This is the WhatsApp-side contract between
the owner and the Delivery Sub-Agent for a held (0.70–0.89) lead — not an
HTTP API, since the channel is WhatsApp itself (Constitution Principle III:
PK notifications MUST use WhatsApp only).

## Trigger message (Delivery → owner)

```
Review needed — score {classification_score}
```

Sent once, when a lead lands in the 0.70–0.89 band. Starts a 2-hour timeout
clock from `queued_at`.

## Owner reply commands

| Command | Format | Effect |
|---|---|---|
| Confirm | `/confirm {lead_id}` | CRM contact + deal written; agent receives the standard lead WhatsApp notification (FR-007) |
| Discard | `/discard {lead_id}` | Lead logged as rejected; no CRM write, no agent notification (FR-008) |

- `{lead_id}` MUST match the `lead_id` of a `pending` Approval Queue Entry
  for the current tenant; a reply referencing an unknown or already-resolved
  `lead_id` is ignored and logged as `unknown_lead_id_reply`.
- Only a reply from the tenant's configured `agent_whatsapp` number is
  honored; replies from any other number are ignored and logged as
  `unauthorized_reply_source` (enforces Constitution Principle VIII —
  multi-tenant isolation extends to who may act on a tenant's queue).

## Timeout (no reply)

If no `/confirm` or `/discard` is received within 2 hours of `queued_at`:
the entry transitions to `timed_out`, is logged as `owner_no_response`
(FR-008), and no CRM write or notification occurs.

## Response codes (logged, not HTTP)

| Code | Meaning |
|---|---|
| `confirmed` | owner replied `/confirm`, CRM write + notification completed |
| `discarded` | owner replied `/discard` |
| `owner_no_response` | 2-hour timeout elapsed with no reply |
| `unknown_lead_id_reply` | reply referenced a `lead_id` not in this tenant's pending queue |
| `unauthorized_reply_source` | reply came from a number other than `agent_whatsapp` |
