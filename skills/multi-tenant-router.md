# SKILL.md — multi-tenant-router

## Trigger
Use this skill at the start of every pipeline run, before any inbox reading or classification.
Invoked by the Orchestrator Agent.

## What This Skill Does
Loads the correct per-client configuration from USER.md and initialises the pipeline
with the right tenant context. Ensures zero data leakage between clients.

## USER.md Expected Schema
```json
{
  "tenant_id": "string — unique per client, e.g. pk-raza-properties-001",
  "market_mode": "PK | UK",
  "agent_name": "string",
  "agent_whatsapp": "string | null — required if market_mode = PK",
  "agent_discord_channel": "string | null — required if market_mode = UK",
  "gmail_account": "string — Gmail address to monitor",
  "hubspot_portal_id": "string",
  "hubspot_api_key_env": "string — env var name, never the key itself",
  "gemini_api_key_env": "string — env var name, never the key itself",
  "auto_email_drafts": "boolean",
  "whatsapp_input_enabled": "boolean — PK mode only",
  "active": "boolean — false = skip this tenant in pipeline run"
}
```

## Routing Logic

### Step 1 — Load tenant config
- Read USER.md from `~/.openclaw/workspace/USER.md`
- Validate all required fields present
- If `active: false` → log "tenant inactive, skipping" and exit

### Step 2 — Validate market mode
- If `market_mode = "PK"` and `agent_whatsapp` is null → FAIL: "PK mode requires agent_whatsapp"
- If `market_mode = "UK"` and `agent_discord_channel` is null → FAIL: "UK mode requires agent_discord_channel"

### Step 3 — Load API keys from environment
- Read `hubspot_api_key_env` value → look up `os.environ[value]` → fail if not set
- Read `gemini_api_key_env` value → look up `os.environ[value]` → fail if not set
- Never log or store API key values — only confirm they are present

### Step 4 — Load tenant state
- Read MEMORY.md → filter to entries where `tenant_id` matches
- Extract: `gemini_today_count`, `processed_ids` for this tenant only
- Set pipeline context: `{tenant_id, market_mode, gemini_today_count, processed_ids}`

### Step 5 — Return context to Orchestrator
Return routing context object. Orchestrator passes this to all sub-agents for the run.

## Multi-Tenant Isolation Rules
1. Each client has their own USER.md — stored at `~/.openclaw/workspace/tenants/{tenant_id}/USER.md`
2. Each client has their own MEMORY.md section — keyed by tenant_id
3. Never merge or share processed_ids between tenants
4. Never use one tenant's Gmail credentials for another tenant's inbox
5. If tenant_id mismatch detected at any point: halt pipeline, log security alert, notify owner

## Error Handling
- USER.md missing: FAIL — "tenant config not found for {tenant_id}"
- Required field missing from USER.md: FAIL — "missing required field: {field_name}"
- API key env var not set: FAIL — "env var {var_name} not set — check .env file"
- MEMORY.md unreadable: WARN — proceed with empty processed_ids, log warning
