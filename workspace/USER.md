# USER.md — Tenant Configuration Template

## How This File Works
Each client (tenant) gets their own copy of this file at:
`~/.openclaw/workspace/tenants/{tenant_id}/USER.md`

Copy this template, fill in client details, save to their tenant folder.
The Orchestrator reads this file at session start via the multi-tenant-router skill.

## Template
```json
{
  "tenant_id": "pk-AGENCYNAME-001",
  "market_mode": "PK",
  "agent_name": "Agent Full Name",
  "agency_name": "Agency Name",
  "agent_whatsapp": "+923001234567",
  "agent_discord_channel": null,
  "gmail_account": "agent@gmail.com",
  "hubspot_portal_id": "12345678",
  "hubspot_api_key_env": "HUBSPOT_API_KEY_AGENCYNAME",
  "gemini_api_key_env": "GEMINI_API_KEY",
  "auto_email_drafts": true,
  "whatsapp_input_enabled": true,
  "dashboard_url": "https://random-name.trycloudflare.com",
  "active": true
}
```

## Field Reference
- `tenant_id`: Unique ID. Format: `{market}-{agencyslug}-{seq}`. e.g. `pk-raza-properties-001`
- `market_mode`: `"PK"` or `"UK"` — determines which parsers and classifiers load
- `agent_whatsapp`: Required for PK mode. Pakistani format: `+923XXXXXXXXX`
- `agent_discord_channel`: Required for UK mode. Discord channel ID (not name)
- `hubspot_api_key_env`: Name of the env var holding this client's HubSpot key — never the key itself
- `gemini_api_key_env`: Name of the env var for Gemini — typically shared across tenants
- `auto_email_drafts`: If true, Delivery queues email drafts for approval. If false, notify only.
- `whatsapp_input_enabled`: If true, Intake monitors WhatsApp forwards in addition to Gmail
- `dashboard_url`: Set after Cloudflare Tunnel is running. Share this URL with the client.
- `active`: Set to false to pause a tenant without deleting their config

## PK Example (Phase 1)
```json
{
  "tenant_id": "pk-raza-properties-001",
  "market_mode": "PK",
  "agent_name": "Raza Ahmed",
  "agency_name": "Raza Properties",
  "agent_whatsapp": "+923451234567",
  "agent_discord_channel": null,
  "gmail_account": "razaproperties@gmail.com",
  "hubspot_portal_id": "98765432",
  "hubspot_api_key_env": "HUBSPOT_API_KEY_RAZA",
  "gemini_api_key_env": "GEMINI_API_KEY",
  "auto_email_drafts": true,
  "whatsapp_input_enabled": true,
  "dashboard_url": null,
  "active": true
}
```

## UK Example (Phase 2)
```json
{
  "tenant_id": "uk-northfield-estates-001",
  "market_mode": "UK",
  "agent_name": "James Northfield",
  "agency_name": "Northfield Estates",
  "agent_whatsapp": null,
  "agent_discord_channel": "1234567890123456789",
  "gmail_account": "james@northfieldestates.co.uk",
  "hubspot_portal_id": "11223344",
  "hubspot_api_key_env": "HUBSPOT_API_KEY_NORTHFIELD",
  "gemini_api_key_env": "GEMINI_API_KEY",
  "auto_email_drafts": true,
  "whatsapp_input_enabled": false,
  "dashboard_url": "https://another-name.trycloudflare.com",
  "active": true
}
```
