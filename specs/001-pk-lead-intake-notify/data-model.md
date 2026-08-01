# Data Model: PK Lead Intake, Classification & WhatsApp Notification

Entities extracted from `spec.md`'s Key Entities section, with fields,
relationships, validation rules, and state transitions. No database is
introduced (Constitution Principle II); these entities are represented as
JSON within `MEMORY.md`, per-tenant `USER.md` files, and in-flight lead JSON
passed between Intake and Delivery, per `agents/intake/SOUL.md` and
`agents/delivery/SOUL.md`.

## Lead

A candidate property inquiry extracted from Gmail or WhatsApp.

| Field | Type | Notes |
|---|---|---|
| `lead_id` | string (UUIDv4) | assigned by Intake |
| `tenant_id` | string | must match the active session's `USER.md` |
| `source` | enum | `zameen_alert \| olx_alert \| whatsapp_forward` (PK-scoped subset of the full schema in `agents/intake/SOUL.md`) |
| `market_mode` | enum | fixed `"PK"` for this feature |
| `contact.name` | string \| null | |
| `contact.phone` | string \| null | Pakistani format |
| `contact.whatsapp` | string \| null | |
| `property.type` | enum | `residential \| commercial \| plot \| rental \| unknown` |
| `property.location` | string \| null | |
| `property.budget_pkr` | number \| null | |
| `property.size` | string \| null | |
| `urgency` | enum | `high \| medium \| low` |
| `classification_score` | float 0.0–1.0 | from `skills/lead-classifier-pk.md` |
| `rejection_reason` | string \| null | populated only if rejected |
| `raw_source_id` | string | Gmail message ID or WhatsApp message ID |
| `classified_at` | ISO8601 timestamp | |

**Validation rules** (FR-004): `lead_id`, `tenant_id`, `source`,
`market_mode`, `classification_score`, `raw_source_id`, `classified_at` are
required; a lead missing any of these is rejected by Delivery before any
action. `raw_source_id` MUST NOT already exist in the tenant's
`processed_ids` (FR-004, dedup).

**State transitions**:

```
pending → [score < 0.70]   → rejected (Intake, never reaches Delivery —
                                        includes the former 0.5–0.69 band,
                                        now merged into rejection per FR-003)
pending → [score 0.70–0.89] → held-for-review → confirmed → auto-dispatched
                                              → discarded (owner /discard or
                                                2h timeout)
pending → [score ≥ 0.9]     → auto-dispatched
```

`auto-dispatched` and `confirmed`-then-dispatched both terminate in a CRM
write + WhatsApp notification. `rejected` and `discarded` terminate with no
CRM write and no agent notification (owner-facing messages only, where
applicable).

## Tenant (Agency)

A PK real estate agency using Deal Scout.

| Field | Type | Notes |
|---|---|---|
| `tenant_id` | string | unique, e.g. `pk-raza-properties-001` |
| `market_mode` | const | `"PK"` for this feature |
| `agent_whatsapp` | string | required in PK mode, per `skills/multi-tenant-router.md` |
| `gmail_account` | string | monitored inbox |
| `hubspot_portal_id` | string | |
| `hubspot_api_key_env` | string | env var name, never the key |
| `gemini_api_key_env` | string | env var name, never the key |
| `active` | boolean | `false` skips the tenant in a pipeline run |
| `gemini_today_count` | integer | per-tenant, in `MEMORY.md`, resets 00:00 UTC |
| `processed_ids` | string[] | per-tenant, in `MEMORY.md`, never merged across tenants |

**Validation rules**: PK mode requires `agent_whatsapp` non-null (FR from
`skills/multi-tenant-router.md`, Step 2). A mismatch between a lead's
`tenant_id` and the active session's `tenant_id` is rejected everywhere
(FR-010).

## Pipeline Run

One heartbeat execution instance.

| Field | Type | Notes |
|---|---|---|
| `run_id` | string (UUIDv4) | |
| `tenant_id` | string | |
| `started_at` / `completed_at` | ISO8601 | |
| `leads_found` / `leads_classified` / `leads_rejected` | integer | |
| `crm_writes` / `notifications_sent` | integer | |
| `gemini_calls_this_run` | integer | must not push `gemini_today_count` past 18 |
| `errors` | array | |

**Validation rules**: written to `MEMORY.md` at the end of every run
regardless of outcome (FR-011) — including runs that abort early on the
quota guard or a HubSpot pre-flight failure.

## Approval Queue Entry

A Tier 2 (0.70–0.89) lead awaiting an owner decision.

| Field | Type | Notes |
|---|---|---|
| `lead_id` | string | references the held Lead |
| `tenant_id` | string | |
| `classification_score` | float | 0.70–0.89 |
| `queued_at` | ISO8601 timestamp | starts the 2-hour timeout clock |
| `status` | enum | `pending \| confirmed \| discarded \| timed_out` |

**State transitions**: `pending` → `confirmed` (owner `/confirm {lead_id}`
within 2 hours) → CRM write + notification; `pending` → `discarded` (owner
`/discard {lead_id}`) → no further action; `pending` → `timed_out` (no reply
within 2 hours) → logged as `owner_no_response`, no further action (FR-007,
FR-008).

## Relationships

- A **Tenant** has many **Lead**s and many **Pipeline Run**s; a **Lead**
  belongs to exactly one **Tenant** (enforced by `tenant_id` matching,
  FR-010).
- A **Pipeline Run** produces zero or more **Lead**s and zero or more
  **Approval Queue Entry** records (one per Tier 2 lead surfaced in that
  run).
- An **Approval Queue Entry** references exactly one **Lead** via `lead_id`.
