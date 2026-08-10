# Data Model: PK Pilot Tracking — PILOTS.md

## Pilot Slot

One of exactly 4 tracked positions in `PILOTS.md` (spec.md FR-001), stored
as a fenced JSON block under an `## Slot N` heading. Field-for-field
identical, for its first 11 fields, to
`workspace/tenants/_template/USER.md`.

| Field | Type | Notes |
|---|---|---|
| `tenant_id` | string \| null | matches `workspace/tenants/{tenant_id}/USER.md`'s own `tenant_id` once live (FR-013); `null` while `not_started` |
| `market_mode` | string | fixed `"PK"` (FR-002) — this feature tracks no other value |
| `agent_name` | string \| null | |
| `agent_whatsapp` | string \| null | PK WhatsApp number once assigned |
| `agent_discord_channel` | null | fixed `null` (FR-002) — PK mode never uses Discord |
| `gmail_account` | string \| null | |
| `hubspot_portal_id` | string \| null | |
| `hubspot_api_key_env` | string \| null | env var name, never the key itself |
| `gemini_api_key_env` | string \| null | env var name, never the key itself |
| `auto_email_drafts` | boolean | mirrors the real `USER.md` value once live |
| `whatsapp_input_enabled` | boolean | mirrors the real `USER.md` value once live |
| `active` | boolean | mirrors the real `USER.md` value once live — `PILOTS.md`'s copy is never authoritative (FR-005) |
| `onboarding_status` | string | one of `not_started`, `forms_confirmed`, `tenant_configured`, `oauth_pending`, `live`, `confirmed`, `withdrawn` (FR-003) |
| `signup_date` | string (ISO 8601 date) \| null | |
| `first_notification_delivered_at` | string (ISO 8601 timestamp) \| null | required non-null for `confirmed` (FR-004) |
| `source_run_id` | string \| null | the `MEMORY.md` `run_id` proving delivery; required non-null for `confirmed` (FR-004) |

**Validation rules**:
- Exactly 4 slots exist at all times (FR-001).
- `onboarding_status: confirmed` requires both `first_notification_delivered_at`
  and `source_run_id` non-null, and `source_run_id` must correspond to a real
  `notifications_sent` entry in that tenant's `MEMORY.md` (FR-004).
- No two slots share the same non-null `tenant_id` (FR-006); a violation
  invalidates both slots for gate-counting purposes.
- A slot's `tenant_id` must exactly match its real
  `workspace/tenants/{tenant_id}/USER.md`'s own `tenant_id` once that tenant
  exists (FR-013); a mismatch invalidates the slot for gate-counting
  purposes.
- `onboarding_status` values outside the named 7-value set are invalid and
  excluded from the gate count (FR-011).

**State transitions**:

```
not_started → forms_confirmed → tenant_configured → oauth_pending → live
  → confirmed  (requires first_notification_delivered_at + source_run_id, FR-004)
  → withdrawn  (from any non-confirmed state; also reachable from confirmed
                if the founder makes a deliberate manual decision — see
                spec.md's churned-agency edge case)
withdrawn → not_started (full field reset, reassigned to a new candidate agency, FR-008)
```

`confirmed` has no automatic exit — per spec.md's edge case on tenant
deactivation, only a deliberate manual edit can move a `confirmed` slot to
`withdrawn`; nothing in this feature does so automatically (FR-005).

## PILOTS.md (document-level)

| Element | Notes |
|---|---|
| Summary line | first content line of the file; states `"{n} of 4 confirmed — Phase 1 gate {not met \| met — UK-market work (Phase 2) is now authorized to begin}"` (FR-009) |
| 4 × `## Slot N` sections | each containing one Pilot Slot fenced JSON block, in order Slot 1-4 (FR-001) |

## Relationships

- Each **Pilot Slot** optionally corresponds to exactly one real
  `workspace/tenants/{tenant_id}/USER.md` (feature 001's tenant config),
  once `onboarding_status` reaches `tenant_configured` or later — but the
  slot's copy of the shared 11 fields is a tracking mirror, never the
  runtime source of truth (FR-005, Key Entities in spec.md).
- Each **Pilot Slot** that reaches `confirmed` references exactly one
  `MEMORY.md` run-log entry via `source_run_id`, proving the Phase 1 gate's
  literal definition ("received at least one delivered lead notification")
  for that tenant (FR-004).
