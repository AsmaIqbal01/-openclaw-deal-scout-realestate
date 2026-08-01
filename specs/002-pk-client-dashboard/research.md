# Research: PK Client Dashboard — Pipeline Visibility & Read-Only Approval Queue

## Context

Unlike feature 001, where the Orchestrator/Intake/Delivery behavior is
entirely LLM-interpreted markdown with no callable production code, the
dashboard is described in `skills/remote-dashboard.md` as a "vanilla
HTML/JS dashboard (existing, port 18790)" — ordinary, deterministic web
tooling, not agent behavior. `backend/` and `dashboard/` are empty in this
repo (no prior implementation exists here), so this feature genuinely
requires new production code for the read/render side — a first for this
project, and a deliberate contrast with feature 001's "no new agent-logic
code" finding.

## Decision 1: What is new code vs. existing agent behavior?

**Decision**: The *write* side of `dashboard-state.json` (FR-001, FR-002)
is existing Orchestrator behavior, already described in
`skills/remote-dashboard.md`'s "Update Trigger" ("Called by Orchestrator...
Reads all sub-agent outputs for the run and writes the state file") and
`workspace/HEARTBEAT.md`'s execution order — no new code is needed for
this feature to write that file. This feature's actual scope is the *read
and render* side (FR-003 through FR-014): a static HTML/CSS/JS frontend
plus a minimal local server, since that has never been implemented as real
files in this repo before.

**Rationale**: writing `dashboard-state.json` is the same kind of file-write
action the Orchestrator already performs for `MEMORY.md` (feature 001) —
it's declarative agent behavior, not something requiring new production
code. Rendering an interactive, polling, per-tenant-scoped web page is not
something an LLM-interpreted SOUL.md file can do; it requires deterministic
code that runs the same way every time a browser requests it.

**Alternatives considered**:
- *Treat the whole dashboard as agent behavior and skip writing any HTML/JS/server code*: rejected — a dashboard is, by definition, something a browser renders; there's no way to "interpret" that requirement away.
- *Build the dashboard as part of a full frontend framework (React/Next.js)*: rejected — `skills/remote-dashboard.md` explicitly specifies "vanilla HTML/JS," and introducing a framework/build step for a small, mostly-static reporting page would be unjustified complexity (constitution's smallest-viable-change principle) and a new toolchain dependency with no corresponding need.

## Decision 2: Server technology for the read/render side

**Decision**: A minimal Python 3.11+ HTTP server using only the standard
library (`http.server`), serving the static `dashboard/index.html`,
`dashboard/dashboard.js`, `dashboard/dashboard.css`, and a `GET /state`
endpoint that reads the requested tenant's `dashboard-state.json` and
returns it as JSON (or a "no runs yet" / "tenant not configured" response
per FR-013/FR-014). The request-handling logic is written as plain,
directly callable functions (not only reachable via a live socket), so
`pytest` can test the handler logic without binding a port.

**Rationale**: Python is already this repo's only established language
(feature 001's test suite); the standard library's `http.server` needs zero
new dependencies (Constitution Principle II, zero infrastructure cost);
`skills/remote-dashboard.md` already mandates Chart.js for the Score Radar
(Section 8), so that choice is inherited, not newly introduced here.
Designing the handler as plain callable functions (rather than testing only
through a live HTTP round-trip) keeps the test suite fast and deterministic,
consistent with the test philosophy established by ADR-002.

**Alternatives considered**:
- *Node.js/Express server*: rejected — introduces a second language/runtime
  into a repo that has exactly one (Python), for a feature that doesn't
  need anything Express provides over the standard library.
- *A full REST framework (Flask/FastAPI)*: rejected — this endpoint set (one
  static-file server plus one JSON-returning route) doesn't need routing,
  middleware, or validation machinery a framework provides; the standard
  library is sufficient and adds no new dependency.
- *Testing only via a live bound socket end-to-end*: rejected as the primary
  test strategy — flakier and slower than calling the handler functions
  directly; a small number of true end-to-end tests may still be added
  later against a running server, but are not required to prove FR-003
  through FR-014.

## Decision 3: Where the dashboard server runs relative to the existing MCP Gateway

**Decision**: this feature ships `dashboard/server.py` as a standalone,
independently runnable server on port 18790, documented as intended to
eventually run alongside or be merged into the existing MCP Gateway
(`workspace/TOOLS.md`: "Existing MCP Gateway from Deal Scout v1 (port
18790)... 6 existing tools remain active"), which is not present in this
repo. Integrating the two servers is explicitly out of scope for this
feature — see `spec.md`'s Scope Decision.

**Rationale**: the MCP Gateway's actual implementation lives outside this
repo (a "Deal Scout v1" artifact referenced but not checked in here); making
this feature depend on code that doesn't exist here would block it
indefinitely. A standalone server keeps the feature independently
demoable and testable now, while remaining a straightforward later merge
(same port, same static-file-plus-one-JSON-route shape) once the gateway
code is available.

**Alternatives considered**:
- *Block this feature until the MCP Gateway code is added to the repo*:
  rejected — no timeline for that exists, and the dashboard's value (agent
  visibility) doesn't depend on gateway integration to be real and testable.

## Resolved Technical Context

- **Language/Version**: Python 3.11+ (standard library only) for the
  server; vanilla HTML/CSS/JavaScript (ES6, no framework, no build step)
  for the frontend, per `skills/remote-dashboard.md`.
- **Primary Dependencies**: Python standard library (`http.server`, `json`)
  only for the server; Chart.js (already mandated by
  `skills/remote-dashboard.md` Section 8) for the Score Radar chart.
- **Storage**: `workspace/tenants/{tenant_id}/dashboard-state.json`,
  written by existing Orchestrator behavior (no new writer code in this
  feature) — read-only from this feature's perspective.
- **Testing**: `pytest`, calling the server's request-handling functions
  directly with fixture `dashboard-state.json` files (normal, missing,
  unknown-tenant variants) — no live socket required for the primary suite.
- **Target Platform**: same Linux host as the pipeline, port 18790,
  exposed externally via the already-provisioned Cloudflare Tunnel
  (provisioning itself is out of scope, per `spec.md`).
- **Project Type**: single project — a new `dashboard/` static-file +
  minimal-server component; no framework/build split.
- **Performance Goals**: dashboard reflects state within one 30-second poll
  cycle (`skills/remote-dashboard.md`: "Dashboard HTML polls this file
  every 30 seconds via fetch").
- **Constraints**: zero paid infrastructure; read-only with respect to the
  pipeline (no writes, no notifications, no lead processing — this
  component must never become a second orchestrator, per Constitution
  Principle IV); WhatsApp remains the sole PK approval channel (Principle
  III) — the dashboard's Approval Queue section is view-only.
- **Scale/Scope**: single-tenant through the Phase 1 validation target of 3
  PK agencies, same as feature 001.
