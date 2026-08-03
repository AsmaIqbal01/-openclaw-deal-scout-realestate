# Research: PK Dashboard Email Draft Queue Extension

## Context

Like feature 002 and unlike features 001/003, this feature touches genuine
production code — `dashboard/server.py` and the vanilla HTML/CSS/JS
frontend — not LLM-interpreted agent markdown. It extends an existing,
already-shipped component rather than building a new one.

## Decision 1: Extend the existing dashboard component, not a new one

**Decision**: All new code lives inside the existing `dashboard/` directory
(`server.py`, `index.html`, `dashboard.js`, `dashboard.css`), extended in
place. No new directory, service, or process is introduced.

**Rationale**: this feature's entire scope is "show one more read-only data
source on the page that already exists." Feature 002 already solved
per-tenant scoping, the 30-second poll cycle, the 4-outcome response
contract, and the static-file-plus-`/state`-endpoint server shape — none of
that needs to be re-solved or duplicated.

**Alternatives considered**:
- *A separate mini-page or endpoint just for email drafts*: rejected — it
  would duplicate the tenant-scoping and polling logic feature 002 already
  has correct and tested, for no benefit; spec.md FR-011 explicitly
  requires reusing the single existing request.

## Decision 2: Server-side enrichment, not client-side computation

**Decision**: Status-label derivation (Pending / Sent / Send Failed /
Rejected / Auto-Archived) and the two countdown values (seconds to the
4-hour reminder, seconds to the 24-hour auto-archive) are computed in
`dashboard/server.py`, inside the same enrichment step that already adds
`tier_color` (Recent Leads) and `seconds_remaining` (existing Approval
Queue) to the served response — not in `dashboard.js`.

**Rationale**: ADR-003 (feature 002) already established the principle
that scoring/timeout formulas belong in one tested place, keeping the
frontend thin. `tests/pipeline_sim.py`'s `apply_stale_queue_guard` (feature
003) already implements the identical 4h/24h logic for the WhatsApp
re-notification path — `dashboard/server.py`'s enrichment mirrors those
same constants (`STALE_REMINDER_HOURS = 4`, `STALE_ARCHIVE_HOURS = 24`) so
the two independently-computed countdowns (one driving a WhatsApp message,
one driving a dashboard display) can never silently drift apart.

**Alternatives considered**:
- *Compute status/countdowns in `dashboard.js`*: rejected — duplicates
  logic across two languages (Python enrichment already exists for two
  other sections; JS would be a third, untested-by-`pytest` copy of the
  same 4h/24h arithmetic), against the precedent ADR-003 set.

## Decision 3 (reconsidered): no guard-test change needed

**Original concern**: feature 002's
`tests/integration/test_no_approval_actions_in_frontend.py` bans the bare
substrings `"approve"` and `"reject"` (case-insensitive) anywhere in
`dashboard/index.html` or `dashboard.js`. Feature 003's `/reject
{queue_id}` command produces a `"rejected"` outcome this feature needs to
*display* (spec.md FR-003's "Rejected" status label) — an apparent
collision with the literal-substring ban.

**Correction**: this concern assumed `dashboard.js` would need to hardcode
the literal string `"Rejected"` to render the label. It doesn't, given
Decision 2 above: status-label text is computed once, server-side, in
`dashboard/server.py`'s enrichment step, and served as plain data
(`status_label: "Rejected"`) in the JSON response. `dashboard.js` only ever
needs to render that received value directly (e.g.
`element.textContent = entry.status_label`, or derive a CSS class via
`entry.status_label.toLowerCase()`) — it never needs to write, compare
against, or branch on the literal word "reject" in its own source code.
Neither `index.html` (structural markup only) nor `dashboard.js` (purely
data-driven rendering) needs to contain the word at all.

**Conclusion**: the existing guard test requires **no change**. This was
caught by writing out the concrete `renderEmailDraftQueue` implementation
before committing to "the test needs refining" as a decision — a case of
verifying an assumption against a decision (Decision 2) already made in the
same planning pass, rather than treating a first impression as settled. An
ADR was drafted for a test-refinement approach and then retracted once this
was caught, before any code changed (see PHR 0028) — no guard-test task
appears in `tasks.md` as a result.

## Resolved Technical Context

- **Language/Version**: Python 3.11+ (stdlib only) for `server.py`; vanilla
  HTML/CSS/ES6 JS for the frontend — unchanged stack from feature 002.
- **Primary Dependencies**: none new.
- **Storage**: `workspace/tenants/{tenant_id}/approval-queue.json`
  (feature 003), read-only; `dashboard-state.json` (feature 002) unchanged.
- **Testing**: `pytest` against `dashboard/server.py`'s functions directly,
  fixture-based, no live socket required for the primary suite (feature
  002's Decision 2 pattern); frontend rendering verified manually per
  `quickstart.md`.
- **Target Platform**: same Linux host, port 18790, existing Cloudflare
  Tunnel.
- **Project Type**: single project, extends `dashboard/` in place.
- **Performance Goals**: reflected within the existing 30-second poll
  cycle — no new cadence introduced.
- **Constraints**: zero paid infrastructure; read-only re: `approval-queue.json`;
  WhatsApp remains the sole `/approve`/`/reject` channel; zero cross-tenant
  reads; no new endpoint/request type.
- **Scale/Scope**: Phase 1 target of 3 PK agencies; 10-entry display cap.
