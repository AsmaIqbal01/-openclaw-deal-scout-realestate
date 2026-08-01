# ADR-003: Dashboard Server Architecture — Stdlib HTTP Server, Read-Only Split, Server-Side Enrichment

> **Scope**: Decision cluster covering how the client dashboard's backend is
> built and where it sits relative to the pipeline — not a single technology
> choice. Excludes the dashboard's file-I/O testing pattern
> (`dashboard_workspace_factory`), which is a minor corollary noted in
> Consequences rather than a separate decision, per the anti-over-granularity
> check in the `/sp.adr` workflow.

- **Status:** Accepted
- **Date:** 2026-08-01
- **Feature:** 002-pk-client-dashboard
- **Context:** `skills/remote-dashboard.md` describes a "vanilla HTML/JS
  dashboard (existing, port 18790)" exposed via Cloudflare Tunnel, backed by
  a per-tenant `dashboard-state.json`. Unlike feature 001, where the
  Orchestrator/Intake/Delivery agents are entirely LLM-interpreted markdown
  with no callable production code, the dashboard is ordinary deterministic
  web tooling — this project's first feature requiring genuine new
  production code (`specs/002-pk-client-dashboard/research.md` Decision 1).
  `backend/` and `dashboard/` were empty in this repo; the MCP Gateway code
  the dashboard is meant to eventually share a port with
  (`workspace/TOOLS.md`: "Existing MCP Gateway from Deal Scout v1... port
  18790") lives outside this repo and isn't available here. This ADR
  documents the architecture chosen to make the feature real and testable
  now, without blocking on that external code.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- **Server**: A minimal Python 3.11+ HTTP server using only the standard
  library (`http.server.ThreadingHTTPServer` + `SimpleHTTPRequestHandler`
  subclass) — zero new dependencies. Serves the static
  `dashboard/index.html`/`.css`/`.js` files and one JSON route,
  `GET /state?tenant={tenant_id}`.
- **Read-only split**: This server never writes `dashboard-state.json` (the
  Orchestrator already does, via existing agent behavior) and never
  processes leads, writes to CRM, or sends notifications — it is strictly a
  passive read/render layer, never a second orchestrator (Constitution
  Principle IV).
- **Deployment**: Binds `127.0.0.1:18790`, matching
  `skills/remote-dashboard.md`'s exact `cloudflared tunnel --url
  http://127.0.0.1:18790` command — external access comes through the
  already-provisioned Cloudflare Tunnel, not a direct `0.0.0.0` bind.
  Ships as a standalone, independently runnable server rather than waiting
  for the (not-present-in-this-repo) MCP Gateway code it may eventually
  share a port with.
- **Server-side response enrichment**: `handle_state_request` augments the
  raw stored document with derived, display-ready fields — `tier_color` per
  recent lead (from `classification_score`) and `seconds_remaining` per
  approval-queue entry (from `queued_at` and a fixed 2-hour window) —
  computed once in Python rather than duplicated in `dashboard.js`/
  `radar.js`. This keeps the frontend as thin rendering code with no scoring
  or timing logic of its own.

## Consequences

### Positive

- Zero new dependencies (Constitution Principle II) — the standard library
  is sufficient for one static-file server plus one JSON route; no
  framework, no build step, no `package.json`/`requirements.txt` growth
  beyond `jsonschema`/`pytest` already added for feature 001.
- The read-only split makes Constitution Principle IV trivially auditable:
  there is no write path in `dashboard/server.py` at all, so "never a second
  orchestrator" isn't just a convention, it's structurally true — a future
  contributor cannot accidentally wire in a write endpoint without it being
  a visible, reviewable addition to a currently read-only file.
  Test `test_no_approval_actions_in_frontend.py` gives this a symmetrical,
  automated guard on the frontend side (no "approve"/"reject" strings) —
  together they make the read-only boundary an enforced invariant, not just
  a documented intention.
- Server-side enrichment means `dashboard.js`/`radar.js` never reimplement
  the tier-coloring or timeout-countdown formulas — those live in one
  place (`server.py`), tested once, consumed twice (Score Radar coloring
  and Approval Queue countdown).
- A useful corollary, not a separate decision: because `server.py` does
  real file I/O (unlike feature 001's `agents/*/SOUL.md`-only behavior),
  its tests needed a different fixture pattern than feature 001's
  `pipeline_sim.py` (pure in-memory simulation). Added
  `dashboard_workspace_factory` to `tests/conftest.py` — builds a real temp
  `workspace/tenants/` tree per test via `tmp_path`, so the tests exercise
  actual file reads rather than mocking them away.

### Negative

- Standalone-on-18790 means there is, for now, a documented but unrealized
  assumption that this server and the eventual MCP Gateway will share a
  port cleanly — if the real gateway code (once available) has its own
  routing conventions, merging the two may require rework rather than a
  drop-in combination.
- `SimpleHTTPRequestHandler`'s static-file serving is intentionally basic
  (no caching headers, no compression) — acceptable for a small, mostly-text
  reporting page polled every 30 seconds, but would need revisiting if the
  dashboard grows heavier assets.
- Server-side enrichment means the *served* response is no longer
  byte-identical to the *stored* `dashboard-state.json` file — anyone
  debugging by diffing the two needs to know `tier_color`/
  `seconds_remaining` are computed, not stored. Documented in
  `_enrich()`'s docstring in `server.py`.

## Alternatives Considered

- **Node.js/Express server**: rejected — introduces a second
  language/runtime into a repo that has exactly one (Python, from feature
  001's test suite), for a feature that needs nothing Express provides over
  the standard library.
- **Flask/FastAPI**: rejected — one static-file server plus one
  JSON-returning route doesn't need routing/middleware/validation
  machinery a framework provides; adding one would be unjustified
  complexity for what this endpoint set actually does.
- **Block this feature until the real MCP Gateway code is added to the
  repo**: rejected — no timeline exists for that, and the dashboard's value
  (agent visibility) doesn't depend on gateway integration to be real and
  testable now.
- **Compute `tier_color`/`seconds_remaining` in `dashboard.js` instead of
  server-side**: rejected — would duplicate the exact scoring/timeout
  formulas already defined once in `skills/remote-dashboard.md` Section 8
  and feature 001's Tier 2 rules, across two languages, with no automated
  test coverage on the JS copy (per `tasks.md`, frontend JS is manually
  verified only) — keeping the logic in Python keeps it inside the
  automated test suite.

## References

- Feature Spec: `specs/002-pk-client-dashboard/spec.md`
- Implementation Plan: `specs/002-pk-client-dashboard/plan.md`,
  `specs/002-pk-client-dashboard/research.md` (Decisions 1–3)
- Related ADRs: `adrs/ADR-002-openclaw-agent-test-simulation-pattern.md`
  (the analogous "how do we test this without live calls" decision for
  feature 001's LLM-agent behavior — this ADR is its counterpart for real,
  file-touching production code); no conflicts.
- Evaluator Evidence / PHRs:
  `history/prompts/002-pk-client-dashboard/0012-pk-dashboard-plan.plan.prompt.md`,
  `history/prompts/002-pk-client-dashboard/0015-pk-dashboard-implementation.green.prompt.md`
  (45/45 tests passing, live-socket smoke test confirmed)
- Constitution: `.specify/memory/constitution.md` Principles II, IV;
  `CONSTITUTION.md` Section 7 gates I4/I5/A8/Q2
