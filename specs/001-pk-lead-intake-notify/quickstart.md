# Quickstart: PK Lead Intake, Classification & WhatsApp Notification

## Prerequisites

1. OpenClaw installed and running, with the ClawHub skills from
   `workspace/TOOLS.md` installed: `agent-rate-limiter`, `agent-memory`,
   `honcho-setup`, `agentmail-integration`.
2. A tenant `USER.md` at `~/.openclaw/workspace/tenants/{tenant_id}/USER.md`
   matching the schema in `skills/multi-tenant-router.md`, with
   `market_mode: "PK"` and a non-null `agent_whatsapp`.
3. Environment variables set for the names referenced by `USER.md`'s
   `hubspot_api_key_env` and `gemini_api_key_env` (never the keys themselves
   in any tracked file).
4. Gmail OAuth token present at `~/.openclaw/workspace/` per
   `workspace/TOOLS.md`.

## Manual end-to-end check (User Story 1 — auto-dispatch)

1. Send a test email to the tenant's monitored Gmail account from an
   address that matches the Zameen/OLX sender pattern in
   `skills/zameen-parser.md`, with a phone number, property type, and PKR
   budget in the body.
2. Trigger one heartbeat cycle (wait for the 15-minute systemd timer, or run
   the pipeline manually per the Orchestrator's session-start checklist in
   `agents/orchestrator/SOUL.md`).
3. Confirm: a HubSpot contact and deal exist for the test lead, and the
   tenant's `agent_whatsapp` number received a message prefixed
   "🔴 URGENT — ".

## Manual check — User Story 2 (human review)

1. Send a test message with a contact but no budget mentioned.
2. Run one heartbeat cycle.
3. Confirm: no CRM write yet; the owner's WhatsApp received "Review needed —
   score {score}".
4. Reply `/confirm {lead_id}` (see `contracts/approval-commands.md`) and
   confirm the CRM write and standard agent notification now occur.

## Manual check — User Story 3 (quota guard)

1. Set the tenant's `gemini_today_count` to 18 in `MEMORY.md`.
2. Run one heartbeat cycle.
3. Confirm: no Gemini calls are made, `quota_exhausted: true` is logged, and
   exactly one WhatsApp alert reaches the owner.

## Automated test suite

```bash
# from repo root
pytest tests/contract tests/integration -v
```

- `tests/contract/` validates lead JSON against
  `contracts/lead-schema.json` and validates the approval-command contract
  in `contracts/approval-commands.md`, using static fixtures — no live
  Gmail/Gemini/HubSpot/WhatsApp calls.
- `tests/integration/` replays the three Independent Test scenarios from
  `spec.md` (auto-dispatch, human review, quota guard) against fixture data
  and asserts the resulting lead state transitions and `MEMORY.md`/queue
  writes match `data-model.md`.

No test in this suite consumes live Gemini quota or writes to a real
HubSpot portal — all external calls are replaced with recorded fixture
responses, consistent with `research.md` Decision 2.
