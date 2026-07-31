# SKILL.md — remote-dashboard

## Trigger
Use this skill when the Orchestrator needs to update the dashboard state after a pipeline run,
or when a client requests their dashboard URL.

## What This Skill Does
Manages the vanilla HTML/JS dashboard (existing, port 18790) and exposes it via
Cloudflare Tunnel so clients can access it remotely. Updates dashboard state file
after every pipeline run.

## Dashboard State File
Location: `~/.openclaw/workspace/tenants/{tenant_id}/dashboard-state.json`

Schema:
```json
{
  "tenant_id": "string",
  "market_mode": "PK | UK",
  "last_run_at": "ISO8601 timestamp",
  "last_run_status": "success | partial | failed",
  "leads_today": "integer",
  "leads_this_week": "integer",
  "leads_pending_approval": "integer",
  "gemini_quota_used": "integer",
  "gemini_quota_remaining": "integer",
  "crm_last_write_at": "ISO8601 timestamp",
  "pipeline_errors_today": "integer",
  "approval_queue": [
    {
      "queue_id": "string",
      "contact_name": "string | null",
      "lead_source": "string",
      "classification_score": "float",
      "queued_at": "ISO8601 timestamp"
    }
  ]
}
```

## Update Trigger
Called by Orchestrator at Step 7 of every pipeline run.
Reads all sub-agent outputs for the run and writes the state file.
Dashboard HTML polls this file every 30 seconds via fetch.

## Cloudflare Tunnel Setup
Run once on server setup. Do not re-run on every pipeline execution.

```bash
# Install
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Start tunnel (persists in background)
cloudflared tunnel --url http://127.0.0.1:18790 --no-autoupdate &

# Save the public URL returned (format: https://random-name.trycloudflare.com)
# Store in USER.md as: "dashboard_url": "https://random-name.trycloudflare.com"
```

## Per-Tenant Dashboard View
The dashboard reads `tenant_id` from a URL query param: `?tenant=pk-raza-properties-001`
If no tenant param: show selector of all active tenants.
Each tenant sees only their own data.

## Dashboard Sections (existing HTML, extend these)
1. Pipeline Status — last run time, status badge, next scheduled run
2. Lead Counter — today / this week (two stat tiles)
3. Gemini Quota — visual gauge (used / 20 daily limit)
4. Approval Queue — list of pending email drafts with approve/reject buttons
5. CRM Sync — last HubSpot write timestamp + status
6. Market Toggle — PK mode / UK mode indicator (read-only from USER.md)
7. Recent Leads — last 10 leads with score, source, contact name
8. Score Radar — per-lead breakdown showing WHY a lead scored what it scored

## Section 8 — Score Radar Spec

### Purpose
Agents see a score like 0.82 with no context. The radar shows exactly which
signals contributed to that score so the agent understands the AI's reasoning
and builds trust in the system over time.

### Radar Dimensions (5 axes, each 0–1)
| Axis | What it measures | Data source |
|---|---|---|
| Contact completeness | Name + phone + email present | Intake lead JSON |
| Intent clarity | How clearly buyer/seller intent is stated | Gemini `lead_quality_reason` |
| Budget signal | Budget explicitly mentioned | `property.budget_pkr` or `budget_gbp` not null |
| Urgency | Urgency signals detected | `urgency` field |
| Data integrity | No null critical fields, no parse warnings | `parse_warning` count |

### Axis Scoring
- Contact completeness: (fields present / 3) → 0.33 per field (name, phone, email)
- Intent clarity: derived from Gemini score — score ≥ 0.9 → 1.0, score 0.7–0.89 → 0.7, else 0.4
- Budget signal: budget present → 1.0, absent → 0.0
- Urgency: high → 1.0, medium → 0.6, low → 0.2
- Data integrity: 0 warnings → 1.0, 1 warning → 0.6, 2+ warnings → 0.2

### Rendering
- Use Chart.js radar chart (type: `radar`)
- Show on click of any lead row in Section 7 — renders as a modal overlay
- Display `lead_quality_reason` from Gemini as a one-line caption below the radar
- Colour: Tier 1 leads (≥0.9) → teal fill, Tier 2 leads (0.7–0.89) → amber fill
- Add `recommended_action` from Gemini as a badge: "Call now" / "WhatsApp follow-up" / "Email follow-up" / "Archive"

### State Addition
Add to `dashboard-state.json` per lead in the recent leads array:
```json
{
  "radar": {
    "contact_completeness": 0.67,
    "intent_clarity": 0.70,
    "budget_signal": 0.0,
    "urgency": 0.60,
    "data_integrity": 1.0
  },
  "lead_quality_reason": "Gemini's one-sentence reason",
  "recommended_action": "whatsapp_followup"
}
```

## Approve/Reject from Dashboard
Approve button → calls local endpoint `POST /approve/{queue_id}` → Orchestrator sends email
Reject button → calls local endpoint `POST /reject/{queue_id}` → removes from queue, logs

## Error Handling
- Dashboard state file missing: serve empty state with "No runs yet" message
- Cloudflare tunnel down: log warning, dashboard unavailable externally — local still works
- Tenant not found in state: return 404 with "Tenant not configured" message
