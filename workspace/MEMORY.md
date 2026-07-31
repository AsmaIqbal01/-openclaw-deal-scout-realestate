# MEMORY.md — Pipeline State Spine

## Purpose
Persistent state that survives restarts. Written by Orchestrator after every run.
Never written by sub-agents directly — they return data to Orchestrator which writes here.

## Structure

### Quota Tracking (per tenant)
```json
{
  "tenant_id": "string",
  "gemini_today_count": 0,
  "gemini_quota_reset_at": "ISO8601 — today at 00:00 UTC",
  "last_updated": "ISO8601"
}
```

### Processed IDs (per tenant — deduplication spine)
```json
{
  "tenant_id": "string",
  "processed_ids": [
    "gmail_message_id_1",
    "gmail_message_id_2",
    "whatsapp_msg_id_1"
  ],
  "last_updated": "ISO8601"
}
```
Keep last 500 IDs per tenant. Prune oldest when limit exceeded.

### Run Log (last 50 runs per tenant)
```json
{
  "tenant_id": "string",
  "runs": [
    {
      "run_id": "uuid",
      "started_at": "ISO8601",
      "completed_at": "ISO8601",
      "leads_found": 0,
      "leads_classified": 0,
      "leads_rejected": 0,
      "crm_writes": 0,
      "notifications_sent": 0,
      "drafts_queued": 0,
      "gemini_calls_this_run": 0,
      "errors": []
    }
  ]
}
```

### Lead Audit Trail (last 100 leads per tenant)
```json
{
  "tenant_id": "string",
  "leads": [
    {
      "lead_id": "uuid",
      "raw_source_id": "string",
      "source": "string",
      "classification_score": 0.0,
      "lead_quality_reason": "string",
      "crm_deal_id": "string | null",
      "notification_sent_at": "ISO8601 | null",
      "email_queued": false,
      "classified_at": "ISO8601"
    }
  ]
}
```

## File Location
- Per tenant: `~/.openclaw/workspace/tenants/{tenant_id}/MEMORY.md`
- Format: JSON (despite .md extension — OpenClaw reads it as structured data)

## Integrity Rules
1. Never truncate MEMORY.md mid-write — use atomic write (write to temp, rename)
2. If MEMORY.md is corrupted on read: start fresh with empty state, log warning
3. processed_ids is the source of truth for deduplication — never bypass it
4. gemini_today_count must be incremented immediately after each Gemini call — not batched
