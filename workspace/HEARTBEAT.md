# HEARTBEAT.md — Deal Scout Pipeline Schedule

## Schedule
Every 15 minutes via systemd timer (existing from Deal Scout v1).
Unit file: `/etc/systemd/system/deal-scout.timer`

## Pre-Flight Checks (abort entire run if any fail)
1. `gemini_today_count < 18` — read from MEMORY.md for this tenant
2. HubSpot API reachable — `GET /crm/v3/objects/contacts?limit=1` returns 200
3. Tenant USER.md exists and `active: true`
4. No unresolved approval queue entry older than 4 hours — alert owner if found

## Pipeline Execution Order
```
Step 1: multi-tenant-router → load tenant context
Step 2: Intake Sub-Agent → read Gmail (+ WhatsApp if enabled)
Step 3: Intake Sub-Agent → parse (zameen-parser OR rightmove-parser)
Step 4: Intake Sub-Agent → classify (lead-classifier-pk OR lead-classifier-uk)
Step 5: [if score ≥ 0.7] Delivery Sub-Agent → validate schema
Step 6: Delivery Sub-Agent → write HubSpot CRM
Step 7: Delivery Sub-Agent → send WhatsApp/Discord notification
Step 8: [if auto_email_drafts] Delivery → queue draft via operator-approval-gate
Step 9: Orchestrator → update MEMORY.md spine
Step 10: Orchestrator → update dashboard state via remote-dashboard skill
```

## Quota Guard
- Before Step 4: read `gemini_today_count` from MEMORY.md
- If count ≥ 18: skip Steps 3–4, log `quota_exhausted`, send single owner alert, jump to Step 9
- If count = 15–17: proceed with warning logged — "quota low: {count}/20 used"
- Reset: `gemini_today_count = 0` at 00:00 UTC daily (handled by Orchestrator, not cron)

## Scope Limits (per run, per tenant)
- Max Gmail messages processed: 20
- Max WhatsApp messages processed: 10
- Max Gemini calls: 5 (conservative — leaves buffer across runs)
- Max HubSpot API calls: 50
- Max Discord/WhatsApp notifications: 10
- Max email drafts queued: 5

## Run Logging
After every run write to MEMORY.md:
```json
{
  "run_id": "uuid",
  "tenant_id": "string",
  "started_at": "ISO8601",
  "completed_at": "ISO8601",
  "leads_found": "integer",
  "leads_classified": "integer",
  "leads_rejected": "integer",
  "crm_writes": "integer",
  "notifications_sent": "integer",
  "drafts_queued": "integer",
  "gemini_calls_this_run": "integer",
  "errors": []
}
```
