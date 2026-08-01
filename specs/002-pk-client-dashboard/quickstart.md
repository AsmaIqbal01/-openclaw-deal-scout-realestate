# Quickstart: PK Client Dashboard

## Prerequisites

1. At least one tenant configured under `workspace/tenants/{tenant_id}/`
   (see feature 001's `workspace/tenants/_template/USER.md`), with
   `active: true`.
2. Python 3.11+ available (no extra packages needed for the server itself
   — standard library only).

## Run the dashboard locally

```bash
python dashboard/server.py
# serves on http://127.0.0.1:18790
```

## Manual check — User Story 1 (pipeline status & quota)

1. Ensure `workspace/tenants/{tenant_id}/dashboard-state.json` exists (from
   a real or fixture pipeline run).
2. Open `http://127.0.0.1:18790/?tenant={tenant_id}`.
3. Confirm Pipeline Status shows the correct last-run badge/timestamp, Lead
   Counter shows `leads_today`/`leads_this_week`, and the Gemini Quota gauge
   shows `gemini_quota_used`/20.

## Manual check — User Story 2 (Score Radar)

1. With at least one entry in `recent_leads`, click that lead's row.
2. Confirm the Score Radar modal renders all 5 axes, the
   `lead_quality_reason` caption, and the `recommended_action` badge, with
   teal fill for score ≥ 0.9 or amber for 0.70–0.89.

## Manual check — User Story 3 (read-only approval queue)

1. With at least one entry in `approval_queue`, confirm it appears with
   contact name, source, score, and time remaining before the 2-hour
   timeout — and that no approve/reject button is rendered anywhere on the
   page.

## Edge cases to check manually

- Load `?tenant=some-unconfigured-id` → "Tenant not configured" state.
- Load with no `?tenant=` param at all → tenant selector list.
- Load for a tenant with no `dashboard-state.json` yet → "No runs yet"
  state, not an error page.

## Automated test suite

```bash
pytest tests/contract/test_dashboard_state_schema.py tests/integration/test_us1_pipeline_status.py tests/integration/test_us2_score_radar.py tests/integration/test_us3_approval_queue_visibility.py tests/integration/test_dashboard_tenant_isolation.py -v
```

Tests call `dashboard/server.py`'s request-handling functions directly
against fixture `dashboard-state.json` files (normal, missing,
unknown-tenant variants) — no live socket, no live pipeline run required.
