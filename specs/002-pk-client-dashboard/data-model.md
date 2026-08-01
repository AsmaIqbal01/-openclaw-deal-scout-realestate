# Data Model: PK Client Dashboard — Pipeline Visibility & Read-Only Approval Queue

Entities extracted from `spec.md`'s Key Entities section and
`skills/remote-dashboard.md`'s existing schema. This feature only *reads*
these structures (per `research.md` Decision 1) — the Dashboard State
document is written by existing Orchestrator behavior, not by this
feature's code.

## Dashboard State

One JSON document per tenant, at
`workspace/tenants/{tenant_id}/dashboard-state.json`.

| Field | Type | Notes |
|---|---|---|
| `tenant_id` | string | must match the tenant requested via the `?tenant=` query param |
| `market_mode` | enum | `PK \| UK` — displayed read-only (FR-008) |
| `last_run_at` | ISO8601 timestamp | drives Pipeline Status (FR-003) |
| `last_run_status` | enum | `success \| partial \| failed` |
| `leads_today` | integer | Lead Counter tile (FR-004) |
| `leads_this_week` | integer | Lead Counter tile (FR-004) |
| `leads_pending_approval` | integer | count shown alongside the Approval Queue list |
| `gemini_quota_used` | integer | Gemini Quota gauge numerator (FR-005), out of the fixed 20/day limit |
| `gemini_quota_remaining` | integer | derived/cross-check against `gemini_quota_used` |
| `crm_last_write_at` | ISO8601 timestamp \| null | CRM Sync section (FR-007) |
| `pipeline_errors_today` | integer | surfaced in Pipeline Status |
| `approval_queue` | array of Approval Queue Entry (display) | FR-006 |
| `recent_leads` | array of Recent Lead Entry | FR-009/FR-010, max 10 entries |

**Validation rules**: if the file does not exist for the requested tenant,
the server MUST return the FR-013 "no runs yet" response instead of an
error. If `tenant_id` inside the file (once read) does not match the
requested tenant, this is a configuration error — the entry MUST NOT be
displayed (defense in depth for FR-011, alongside the primary check of
which tenant's file was opened in the first place).

## Recent Lead Entry

A lightweight projection of a `Lead` (feature 001's `data-model.md`), plus
the Score Radar breakdown.

| Field | Type | Notes |
|---|---|---|
| `classification_score` | float 0.0–1.0 | drives the teal/amber tier coloring (FR-010) |
| `source` | string | e.g. `zameen_alert`, `whatsapp_forward` |
| `contact_name` | string \| "Unknown" | never blank — falls back to the literal string "Unknown" |
| `radar.contact_completeness` | float 0.0–1.0 | axis scoring per `skills/remote-dashboard.md` Section 8 |
| `radar.intent_clarity` | float 0.0–1.0 | derived from the Gemini score band |
| `radar.budget_signal` | float 0.0–1.0 | 1.0 if budget present, else 0.0 |
| `radar.urgency` | float 0.0–1.0 | 1.0 high / 0.6 medium / 0.2 low |
| `radar.data_integrity` | float 0.0–1.0 | 1.0 / 0.6 / 0.2 by `parse_warning` count (0 / 1 / 2+) |
| `lead_quality_reason` | string | Gemini's one-sentence explanation, shown as the radar caption |
| `recommended_action` | enum | `call_now \| whatsapp_followup \| email_followup \| archive` — shown as a badge |

**Validation rules**: all 5 `radar` axis values MUST be present and within
0.0–1.0 for the Score Radar (FR-010) to render; a `recent_leads` array is
capped at 10 entries (FR-009) — the Dashboard State document is the
authority on which 10, this feature does no additional filtering or
sorting of its own.

## Approval Queue Entry (display-only)

Reuses feature 001's Approval Queue Entry entity
(`specs/001-pk-lead-intake-notify/data-model.md`) — this feature adds no
new fields and never mutates it.

| Field | Type | Notes |
|---|---|---|
| `lead_id` | string | |
| `contact_name` | string \| "Unknown" | |
| `lead_source` | string | |
| `classification_score` | float | 0.70–0.89 (Tier 2 band) |
| `queued_at` | ISO8601 timestamp | used to compute time remaining before the 2-hour timeout (FR-006) |

**Validation rules**: no approve/reject control may be associated with this
entity anywhere in this feature (FR-006) — display only.

## Relationships

- One **Dashboard State** document belongs to exactly one tenant and
  contains zero or more **Recent Lead Entry** and **Approval Queue Entry**
  (display) records.
- A **Recent Lead Entry** and an **Approval Queue Entry** (display) each
  correspond to exactly one `Lead` from feature 001's data model, but
  neither is the authoritative record — the Dashboard State document is a
  read-only projection, never a source of truth for pipeline decisions.
