# Contract: Dashboard Read Endpoint

Applies to FR-011 through FR-014. One local endpoint, served by
`dashboard/server.py` on port 18790.

## `GET /state?tenant={tenant_id}`

### Success response

Given `tenant_id` has a valid `workspace/tenants/{tenant_id}/dashboard-state.json`:

```json
{
  "status": "ok",
  "data": { /* Dashboard State document, see dashboard-state-schema.json */ }
}
```

### No tenant parameter (FR-012)

Given no `tenant` query parameter is present:

```json
{
  "status": "select_tenant",
  "tenants": ["pk-test-agency-001", "..."]
}
```

Lists only tenants with `active: true` in their `USER.md`.

### No runs yet (FR-013)

Given `tenant_id` is a valid, configured tenant but
`dashboard-state.json` does not yet exist:

```json
{
  "status": "no_runs_yet",
  "tenant_id": "pk-test-agency-001"
}
```

### Tenant not configured (FR-014)

Given `tenant_id` does not match any known tenant configuration:

```json
{
  "status": "tenant_not_configured",
  "tenant_id": "unknown-id"
}
```

### Isolation guarantee (FR-011)

The server MUST only ever read
`workspace/tenants/{tenant_id}/dashboard-state.json` for the exact
`tenant_id` supplied in the request — never another tenant's file, and
never a merged or aggregate view across tenants.
