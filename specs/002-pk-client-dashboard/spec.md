# Feature Specification: PK Client Dashboard — Pipeline Visibility & Read-Only Approval Queue

**Feature Branch**: `002-pk-client-dashboard`
**Created**: 2026-08-01
**Status**: Draft
**Input**: User description: "Second PK feature: client-accessible dashboard showing pipeline status, lead counter, Gemini quota gauge, approval queue, HubSpot CRM sync status, and recent leads with score breakdown, per skills/remote-dashboard.md"
**Market**: PK Real Estate (Pakistan) only — the dashboard schema is market-agnostic, but this feature verifies PK-tenant data only, consistent with the Phase 1 validation sequencing
**Milestone**: F009 — unlocks further progress toward the Phase 1 validation gate (agencies must be able to see their own pipeline activity, quota, and leads before confident onboarding of the 3 target PK agencies) and satisfies Constitution Checker gate I4 ("Dashboard remains client-accessible")

## Scope Decision

`skills/remote-dashboard.md`'s Approval Queue section describes "email drafts
with approve/reject buttons." Email drafting (`skills/operator-approval-gate.md`)
is a separate, not-yet-built feature. This spec instead makes the Approval
Queue section **read-only**, displaying Tier 2 leads currently
held-for-review (from feature 001) and their time remaining before the
2-hour timeout — the agent still confirms or discards exclusively via
WhatsApp, per Constitution Principle III (WhatsApp-only PK notifications)
and `contracts/approval-commands.md`. Adding a dashboard-based approve/reject
*action* is deferred to a future email-draft-approval feature, once
`operator-approval-gate.md`'s flow is actually built. Initial Cloudflare
Tunnel provisioning (one-time server setup) is also out of scope — this
feature assumes the tunnel already exists and focuses on the dashboard state
data and rendered sections.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See pipeline status and quota at a glance (Priority: P1)

A Pakistani real estate agent opens their dashboard URL and immediately sees
whether the last pipeline run succeeded, how many leads came in today and
this week, and how much of today's Gemini quota has been used — without
messaging the developer to ask "is it working?"

**Why this priority**: this is the minimum that makes the pipeline's
operation visible and trustworthy to a non-technical agent; without it,
feature 001's pipeline runs invisibly. Independently deployable as the
dashboard's MVP.

**Independent Test**: after a pipeline run, load the dashboard with
`?tenant={tenant_id}`; verify Pipeline Status shows the correct
`last_run_at`/`last_run_status`, Lead Counter shows correct `leads_today`/
`leads_this_week`, and the Gemini Quota gauge shows `gemini_quota_used` out
of 20. Edge case tested: the dashboard reflects state written by the
Orchestrator, not a live recomputation — it must match `dashboard-state.json`
exactly.

**Acceptance Scenarios**:

1. **Given** a pipeline run completed successfully 5 minutes ago with 3
   leads found, **When** the agent loads `?tenant={tenant_id}`, **Then**
   Pipeline Status shows a "success" badge with that timestamp, and Lead
   Counter reflects the updated `leads_today` count.
2. **Given** `gemini_today_count` is 12 for the tenant, **When** the agent
   loads the dashboard, **Then** the Gemini Quota gauge shows "12/20 used."

---

### User Story 2 - Understand why a lead scored what it scored (Priority: P2)

An agent sees a lead in the Recent Leads list with a score of 0.82 and,
without knowing anything about Gemini or AI, clicks it and sees a Score
Radar breaking the score into five understandable signals (contact info
completeness, intent clarity, budget mention, urgency, data integrity),
plus a one-line plain-English reason and a recommended next action.

**Why this priority**: builds agent trust in the AI's classification over
time — depends on User Story 1's dashboard shell existing, but is
independently testable and valuable on its own.

**Independent Test**: load the dashboard for a tenant with at least one
recent lead; click that lead's row; verify the Score Radar modal renders all
5 axis values (each 0.0–1.0), the `lead_quality_reason` caption, and the
`recommended_action` badge, colored teal for score ≥ 0.9 or amber for
0.70–0.89. Edge case tested: the radar renders correctly for a lead with one
or more `parse_warning`s (lower data-integrity axis), not just the clean
happy-path lead.

**Acceptance Scenarios**:

1. **Given** a recent lead with `classification_score` 0.95 and no parse
   warnings, **When** the agent clicks its row, **Then** the Score Radar
   shows a teal-filled radar with `data_integrity` at 1.0 and the correct
   `recommended_action` badge.
2. **Given** a recent lead with `classification_score` 0.75 and one
   `parse_warning`, **When** the agent clicks its row, **Then** the radar
   shows an amber fill and `data_integrity` at 0.6, per the documented axis
   scoring formula.

---

### User Story 3 - See leads awaiting a WhatsApp reply (Priority: P3)

An agent who missed or lost track of a "Review needed" WhatsApp message can
open the dashboard and see every Tier 2 lead currently awaiting their
`/confirm` or `/discard` reply, along with how much time is left before it
auto-discards.

**Why this priority**: a safety net for the WhatsApp-only approval flow from
feature 001 — lower priority than seeing the pipeline is alive at all (US1)
or trusting the scores (US2), but independently valuable and testable.

**Independent Test**: hold a lead at Tier 2 (0.70–0.89, per feature 001);
load the dashboard; verify the Approval Queue section lists it with
`contact_name` (or "Unknown"), `lead_source`, `classification_score`,
`queued_at`, and time remaining, with no approve/reject button rendered.
Edge case tested: an entry within 10 minutes of its 2-hour timeout is still
listed (not silently dropped) — the countdown must reach zero before it
disappears from the queue, not before.

**Acceptance Scenarios**:

1. **Given** a lead has been held-for-review for 1 hour 50 minutes,
   **When** the agent loads the dashboard, **Then** the Approval Queue
   shows that entry with "10 minutes remaining," and no approve/reject
   control is present anywhere in the section.
2. **Given** a held lead's 2-hour window has elapsed and it was logged
   `owner_no_response` by the pipeline, **When** the agent loads the
   dashboard on the next run, **Then** that entry no longer appears in the
   Approval Queue.

---

### Edge Cases

- `dashboard-state.json` does not yet exist for a tenant (no pipeline runs
  yet): the dashboard renders an empty state reading "No runs yet" rather
  than an error.
- No `tenant` query parameter is present in the URL: the dashboard shows a
  selector of active tenants rather than defaulting to any one tenant's
  data.
- The `tenant` query parameter references a `tenant_id` with no matching
  configuration: the dashboard returns a "Tenant not configured" state
  (404-equivalent).
- The Cloudflare Tunnel is down: the dashboard is unavailable externally,
  but continues to work when accessed locally on the host.
- Two tenants' dashboards are viewed back-to-back in the same browser
  session (e.g., `?tenant=A` then `?tenant=B`): no data from tenant A must
  remain visible or cached into tenant B's view.
- A tenant has more than 10 leads in the current period: only the 10 most
  recent appear in Recent Leads; older ones are not shown but remain counted
  in `leads_today`/`leads_this_week`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Orchestrator MUST write or update `dashboard-state.json`
  for the tenant after every pipeline run, regardless of whether the run
  succeeded, partially completed, or failed (including runs aborted by the
  quota guard or a HubSpot pre-flight failure).
- **FR-002**: `dashboard-state.json` MUST include `tenant_id`,
  `market_mode`, `last_run_at`, `last_run_status`
  (`success | partial | failed`), `leads_today`, `leads_this_week`,
  `leads_pending_approval`, `gemini_quota_used`, `gemini_quota_remaining`,
  `crm_last_write_at`, and `pipeline_errors_today`.
- **FR-003**: The dashboard MUST display Pipeline Status: last run time,
  status badge, and the next scheduled run time (computed from
  `last_run_at` plus the fixed 15-minute heartbeat cadence).
- **FR-004**: The dashboard MUST display a Lead Counter with two stat
  tiles: `leads_today` and `leads_this_week`.
- **FR-005**: The dashboard MUST display a Gemini Quota gauge showing
  `gemini_quota_used` out of the fixed daily limit of 20.
- **FR-006**: The dashboard MUST display the Approval Queue as a read-only
  list of Tier 2 held-for-review leads, each showing `contact_name` (or
  "Unknown"), `lead_source`, `classification_score`, `queued_at`, and time
  remaining before the 2-hour timeout. No approve/reject control MUST be
  rendered anywhere in this section.
- **FR-007**: The dashboard MUST display CRM Sync status:
  `crm_last_write_at` and whether that write succeeded or failed.
- **FR-008**: The dashboard MUST display a read-only Market Toggle
  indicator reflecting the tenant's `market_mode` from `USER.md` — it MUST
  NOT be an editable control.
- **FR-009**: The dashboard MUST display the 10 most recent leads, each
  showing `classification_score`, `source`, and contact name (or
  "Unknown").
- **FR-010**: Clicking a lead row in Recent Leads MUST open a Score Radar
  showing all 5 axes (`contact_completeness`, `intent_clarity`,
  `budget_signal`, `urgency`, `data_integrity`, each 0.0–1.0), the
  `lead_quality_reason` caption, and the `recommended_action` badge, per the
  axis-scoring formulas in `skills/remote-dashboard.md` Section 8.
- **FR-011**: The dashboard MUST scope every displayed field to the
  `tenant_id` present in the URL query parameter and MUST NOT display any
  other tenant's data under any circumstance.
- **FR-012**: If no `tenant` query parameter is present, the dashboard MUST
  show a selector of active tenants rather than defaulting to any one
  tenant's data.
- **FR-013**: If `dashboard-state.json` does not yet exist for the
  requested tenant, the dashboard MUST render an empty state reading "No
  runs yet" rather than an error.
- **FR-014**: If the requested `tenant_id` has no corresponding
  configuration, the dashboard MUST return a "Tenant not configured" state.

### Key Entities

- **Dashboard State**: one JSON document per tenant
  (`dashboard-state.json`), written by the Orchestrator after every
  pipeline run; the sole data source for every dashboard section (no
  section computes its own values independently).
- **Approval Queue Entry** (display-only here): a Tier 2 lead awaiting an
  owner WhatsApp reply, as defined in feature 001's `data-model.md`; this
  feature only reads and displays it, never mutates it.
- **Recent Lead Entry**: a lightweight projection of a `Lead` (feature 001)
  carrying `classification_score`, `source`, `contact_name`, and the 5-axis
  `radar` breakdown plus `lead_quality_reason` and `recommended_action`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An agent can determine whether the pipeline ran successfully
  within the last 15 minutes by viewing the dashboard alone, with no
  message to the developer required.
- **SC-002**: An agent can see their current Gemini quota usage (X/20) in
  under 5 seconds of loading the dashboard.
- **SC-003**: An agent can identify why a specific lead received its score
  by viewing its Score Radar, without an external explanation.
- **SC-004**: Zero instances of one tenant's dashboard view showing
  another tenant's leads, quota, queue, or CRM data across all test runs.
- **SC-005**: A newly onboarded tenant with zero pipeline runs sees a
  usable "No runs yet" state, not an error page, on their first dashboard
  visit.
