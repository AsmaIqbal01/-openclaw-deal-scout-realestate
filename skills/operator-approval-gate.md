# SKILL.md — operator-approval-gate

## Trigger
Use this skill when the Delivery Sub-Agent needs to queue a follow-up email draft
for operator approval before sending.
Never bypass this skill to send an email directly.

## What This Skill Does
Drafts a follow-up email for a classified lead, adds it to the approval queue,
and notifies the agent. Nothing is sent until the operator sets `approved: true`.

## Email Draft Template

### PK Mode (Roman Urdu + English)
```
Subject: Property Enquiry — {property.type} in {property.location}

Dear {contact.name | "Sir/Madam"},

Thank you for your interest in properties in {property.location}.

We have noted your requirement:
- Property Type: {property.type}
- Location: {property.location}
- Budget: PKR {property.budget_pkr | "to be discussed"}
- Size: {property.size | "flexible"}

We would like to arrange a time to discuss available options.
Please contact us at your convenience.

Regards,
{agent_name}
{agency_name}
```

### UK Mode (English)
```
Subject: Re: Your Property Enquiry — {property.location}

Dear {contact.name | "there"},

Thank you for your enquiry about {property.type | "the property"} in {property.location}.

We'd love to arrange a viewing at a time that suits you.
{property.preferred_viewing ? "You mentioned " + property.preferred_viewing + " — we'll do our best to accommodate." : ""}

Please reply to this email or call us directly.

Kind regards,
{agent_name}
{agency_name}
```

## Approval Queue Entry Schema
```json
{
  "queue_id": "uuid-v4",
  "tenant_id": "string",
  "lead_id": "string — from the originating lead",
  "draft_subject": "string",
  "draft_body": "string",
  "recipient_email": "string",
  "queued_at": "ISO8601 timestamp",
  "approved": false,
  "approved_at": null,
  "sent_at": null
}
```

## Queue Storage
- Write to `~/.openclaw/workspace/tenants/{tenant_id}/approval-queue.json`
- Append to existing array — never overwrite
- Max queue size: 50 entries — if exceeded, alert owner and halt new drafts

## Owner Notification
After queuing, send notification via the market-appropriate channel:
- PK: WhatsApp to `agent_whatsapp` — "📧 New email draft awaiting your approval. Lead: {contact.name | lead_id}. Reply /approve {queue_id} or /reject {queue_id}"
- UK: Discord to `agent_discord_channel` — same message format

## Approval Flow
The agent replies `/approve {queue_id}` or `/reject {queue_id}` via WhatsApp/Discord.
Orchestrator receives the reply, updates `approved: true` or removes from queue, triggers send.

## Stale Queue Guard
If any queue entry has `approved: false` and `queued_at` is older than 4 hours:
- Re-notify agent once
- If older than 24 hours: auto-archive (do not send), log `auto_archived: true`

## Error Handling
- contact.email is null: do not create draft, log "no email address for lead {lead_id}"
- Queue file write fails: log error, notify owner, do not proceed
- Draft generation fails: log error with lead_id, skip this lead's email
