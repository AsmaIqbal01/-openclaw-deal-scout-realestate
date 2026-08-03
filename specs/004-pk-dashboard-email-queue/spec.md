# Feature Specification: PK Dashboard Email Draft Queue Extension

**Feature Branch**: `004-pk-dashboard-email-queue`
**Created**: 2026-08-03
**Status**: Draft
**Input**: User description: "Fourth PK feature: extend the client dashboard (feature 002, F009) to display the email-draft approval queue introduced by feature 003 (F010) — showing each tenant's queued/pending/approved/rejected/auto-archived email drafts read-only, alongside the existing Tier 2 lead Approval Queue section, per skills/remote-dashboard.md and skills/operator-approval-gate.md. This was explicitly deferred by feature 002's Scope Decision (dashboard originally scoped to Tier 2 lead review only) and feature 003's Scope Decision (the draft/approve loop stays WhatsApp-only, no dashboard extension) until now. Strictly read-only, matching feature 002's design: never writes approval-queue.json, never processes drafts, never exposes an approve/reject action in the UI — WhatsApp remains the sole /approve or /reject channel, per Constitution Principle VII."
**Market**: PK Real Estate (Pakistan) only — consistent with features 002 and 003, this feature verifies PK-tenant `approval-queue.json` data only, per the Phase 1 validation sequencing.
**Language/Locale**: All new dashboard UI text (section title, status labels) is English-only, matching feature 002's established precedent. The displayed `draft_subject`/`draft_body` are shown verbatim in whatever language feature 003 generated them (English-only PK template, per feature 003's spec) — this feature does not translate or reformat that content.
**Milestone**: F011 — extends F009's (dashboard) and F010's (email approval gate) client-visibility surface ahead of the Phase 1 validation gate; satisfies Constitution Checker gate I4 ("Dashboard remains client-accessible") for the email-draft capability specifically, since F010 shipped with WhatsApp-only visibility.

## Scope Decision

`skills/remote-dashboard.md`'s existing "Approval Queue" section (dashboard
section 4) and `dashboard-state.json`'s `approval_queue` field refer to
**Tier 2 leads** awaiting a `/confirm`/`/discard` reply (feature 001/002) —
a different queue than feature 003's `approval-queue.json`, which holds
**email drafts** awaiting a `/approve`/`/reject` reply. This feature adds a
distinctly named **"Email Draft Queue"** section so the two queues are never
confused in the UI or in test names; it does not rename or alter feature
002's existing Approval Queue section in any way.

This feature is, and remains, **strictly read-only** — this is not a
temporary deferral like feature 002's original Scope Decision, but a
permanent design constraint carried forward from feature 003: WhatsApp is
the sole `/approve`/`/reject` channel (Constitution Principle VII), and
`skills/remote-dashboard.md`'s "Approve/Reject from Dashboard" section
(describing `POST /approve/{queue_id}` / `POST /reject/{queue_id}`
endpoints) is explicitly **not** implemented by this feature or any
currently planned feature. Feature 002's automated guard test (asserting no
"approve"/"reject" strings appear in the frontend) is extended by this
feature to also cover the new Email Draft Queue section, not replaced.

This feature does not introduce a new client-facing request type. It
extends the existing single per-tenant data request from feature 002
(`contracts/dashboard-api.md`'s `GET /state?tenant={tenant_id}`) so its
`"ok"` response also carries the tenant's current email draft queue,
alongside everything feature 002 already returns. The other 3 existing
response outcomes (`select_tenant`, `no_runs_yet`, `tenant_not_configured`)
are unchanged by this feature.

## Interface Contract

No new endpoint, request type, or polling cycle is introduced. Within the
existing `"ok"` response's data, the Email Draft Queue sub-section resolves
to exactly one of 3 named states, each fully specified by the Requirements
below:

| State | Trigger | Requirement |
|---|---|---|
| Entries present | `approval-queue.json` exists for the tenant with ≥ 1 entry | FR-001 through FR-005, FR-010 |
| "No email drafts yet" | `approval-queue.json` does not exist for the tenant | FR-008 |
| "Unable to load email drafts" | `approval-queue.json` exists but fails to parse or read | FR-009 |

No other state exists for this sub-section, and it never affects the other
3 top-level response outcomes (`select_tenant`, `no_runs_yet`,
`tenant_not_configured`) inherited unchanged from feature 002 — see FR-011.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See every email draft awaiting a reply (Priority: P1)

An agent who enabled `auto_email_drafts` opens their dashboard and sees
every one of their currently pending email drafts — the full subject and
body text, the intended recipient, and how long until the automatic
4-hour reminder or 24-hour auto-archive — without having to scroll back
through WhatsApp history to find the original alert.

**Why this priority**: this is the entire value of the feature — turning a
one-time WhatsApp alert into a durable, reviewable view of what's actually
waiting for a decision. Independently deployable and demonstrable on its
own; feature 003 already guarantees the underlying data exists.

**Independent Test**: with a tenant that has one pending entry in
`approval-queue.json`, load the dashboard with `?tenant={tenant_id}`;
verify the Email Draft Queue section lists that entry with its exact
`draft_subject`, `draft_body`, `recipient_email`, `queued_at`, and a
"Pending" status label, and that no approve/reject control of any kind is
rendered anywhere in the section. Edge case tested: an entry within 10
minutes of its 4-hour reminder mark is still shown as "Pending" (the
reminder is a WhatsApp side-effect owned by feature 003, not a dashboard
state change).

**Acceptance Scenarios**:

1. **Given** a tenant has one pending email draft queued 20 minutes ago,
   **When** the agent loads `?tenant={tenant_id}`, **Then** the Email
   Draft Queue section shows that entry's exact `draft_subject`,
   `draft_body`, and `recipient_email`, labeled "Pending," with no
   approve/reject button anywhere on the page.
2. **Given** a tenant has `auto_email_drafts` disabled and zero entries in
   `approval-queue.json`, **When** the agent loads the dashboard, **Then**
   the Email Draft Queue section shows "No email drafts yet" rather than
   an empty list or an error.

---

### User Story 2 - See the outcome of a resolved draft (Priority: P2)

An agent who replied `/approve` or `/reject` to a draft days ago — or who
never replied and it auto-archived — can see that resolution reflected on
the dashboard: sent, rejected, or auto-archived, alongside the still-pending
ones, so the dashboard is a complete record, not just a to-do list.

**Why this priority**: builds on User Story 1's queue view to make the
dashboard a trustworthy audit trail — valuable for an agent who wants to
confirm "did that email actually go out?" without re-checking WhatsApp, but
not required for the MVP value of seeing what's pending right now.

**Independent Test**: with a tenant whose `approval-queue.json` has one
entry of each status (sent, rejected, auto_archived), load the dashboard;
verify each is labeled correctly ("Sent," "Rejected," "Auto-Archived") and
none render an approve/reject control. Edge case tested: an approved entry
whose send failed (`approved: true`, `sent_at: null`) is labeled distinctly
("Send Failed") rather than merged into "Pending" or "Sent."

**Acceptance Scenarios**:

1. **Given** an entry has `approved: true` and a non-null `sent_at`,
   **When** the agent loads the dashboard, **Then** it is labeled "Sent."
2. **Given** an entry has `rejected: true`, **When** the agent loads the
   dashboard, **Then** it is labeled "Rejected."
3. **Given** an entry has `auto_archived: true`, **When** the agent loads
   the dashboard, **Then** it is labeled "Auto-Archived."
4. **Given** an entry has `approved: true` and `sent_at: null` (the
   approved-but-send-failed state from feature 003 FR-009), **When** the
   agent loads the dashboard, **Then** it is labeled "Send Failed," not
   "Pending" or "Sent."

---

### User Story 3 - Queue data never leaks across tenants or breaks the rest of the dashboard (Priority: P3)

An agent viewing their own dashboard never sees another tenant's drafts,
even by mistake; and if their own `approval-queue.json` is unreadable for
any reason, the rest of the dashboard (Pipeline Status, Lead Counter, etc.)
keeps working instead of failing entirely.

**Why this priority**: a reliability and isolation guarantee rather than a
new capability — lower priority to build than seeing the data at all (US1)
or its history (US2), but non-negotiable per Constitution Principle VIII
and independently testable.

**Independent Test**: load `?tenant=A` then `?tenant=B` back-to-back in the
same session; verify tenant A's drafts never appear under tenant B's Email
Draft Queue section. Separately, simulate a malformed `approval-queue.json`
for a tenant and verify the rest of the dashboard still renders correctly
with the Email Draft Queue section showing a load-failure state instead of
crashing the whole page.

**Acceptance Scenarios**:

1. **Given** tenant A has 2 pending drafts and tenant B has 1, **When**
   `?tenant=B` is loaded, **Then** exactly 1 entry appears in the Email
   Draft Queue section, and none of tenant A's data is present anywhere in
   the response.
2. **Given** a tenant's `approval-queue.json` exists but fails to parse,
   **When** the agent loads the dashboard, **Then** every other section
   (Pipeline Status, Lead Counter, Gemini Quota, existing Approval Queue,
   CRM Sync, Market Toggle, Recent Leads) renders normally, and the Email
   Draft Queue section alone shows "Unable to load email drafts" instead of
   blanking or erroring the whole page.

---

### Edge Cases

- A tenant has more than 10 entries across all statuses in
  `approval-queue.json`: only the 10 most recently `queued_at` entries are
  shown, matching the existing Recent Leads display cap (feature 002
  FR-009) — older ones are not shown but are not deleted or otherwise
  affected.
- `approval-queue.json` does not exist yet for a tenant (no drafts have
  ever been queued, or `auto_email_drafts` has never been enabled): the
  Email Draft Queue section shows "No email drafts yet" rather than an
  error, matching feature 002's "No runs yet" pattern (FR-013).
- An entry is both `rejected: true` and `auto_archived: true` at once
  (feature 003's terminal-state design treats each as independently
  permanent, so the write path never produces both together, but the
  display logic MUST NOT crash if it occurs): `rejected` takes display
  precedence, since a reply-driven outcome is more specific than a
  timeout-driven one.
- The dashboard's periodic 30-second refresh (feature 002 FR-003) is
  already in flight when a WhatsApp `/approve` reply resolves an entry
  mid-poll: the next successful poll reflects the new status; no partial or
  torn state is ever displayed, matching feature 002's existing
  poll-and-replace behavior.
- Two tenants' dashboards are viewed back-to-back in the same browser
  session: no email draft data from the first tenant remains visible or
  cached into the second tenant's Email Draft Queue view (extends feature
  002 FR-011's isolation guarantee to this new data source).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The dashboard MUST display a new "Email Draft Queue" section,
  distinct from the existing Approval Queue section (Tier 2 leads), listing
  entries from the tenant's `approval-queue.json` (feature 003
  `data-model.md`).
- **FR-002**: Each Email Draft Queue entry MUST display `draft_subject`,
  `draft_body`, `recipient_email`, and `queued_at`, exactly as stored — no
  truncation, translation, or reformatting of the drafted content.
- **FR-003**: Each Email Draft Queue entry MUST display exactly one status
  label, derived as follows: `auto_archived: true` → "Auto-Archived";
  else `rejected: true` → "Rejected"; else `approved: true` and non-null
  `sent_at` → "Sent"; else `approved: true` and null `sent_at` → "Send
  Failed"; else → "Pending."
- **FR-004**: A "Pending" entry MUST additionally display time remaining
  until its 4-hour re-notification and its 24-hour auto-archive deadline
  (both computed from `queued_at`, per feature 003 FR-012/FR-013).
- **FR-005**: The Email Draft Queue section MUST NOT render any
  approve/reject control, button, link, or form of any kind, for any entry
  in any status — WhatsApp `/approve {queue_id}` / `/reject {queue_id}`
  remains the sole resolution channel (Constitution Principle VII).
- **FR-006**: This feature MUST NOT write to any tenant's
  `approval-queue.json` under any circumstance — read-only, matching
  feature 002's design for the existing Approval Queue section.
- **FR-007**: The Email Draft Queue section MUST scope every displayed
  entry to the `tenant_id` present in the dashboard's URL query parameter
  and MUST NOT display any other tenant's entries under any circumstance
  (Constitution Principle VIII).
- **FR-008**: If a tenant's `approval-queue.json` does not exist yet, the
  Email Draft Queue section MUST show "No email drafts yet" rather than an
  error or an indistinguishable empty list.
- **FR-009**: If a tenant's `approval-queue.json` exists but fails to parse
  or read, the Email Draft Queue section alone MUST show "Unable to load
  email drafts," and every other dashboard section MUST continue to render
  normally from its own data source, unaffected.
- **FR-010**: If a tenant has more than 10 entries in `approval-queue.json`,
  the Email Draft Queue section MUST display only the 10 most recently
  `queued_at` entries, matching the existing Recent Leads display cap
  (feature 002 FR-009).
- **FR-011**: The dashboard's existing single per-tenant data request
  (`GET /state?tenant={tenant_id}`, feature 002 `contracts/dashboard-api.md`)
  MUST be the sole request that carries Email Draft Queue data — this
  feature MUST NOT introduce a second request type, endpoint, or polling
  cycle.

### Key Entities

- **Email Draft Queue Entry** (display-only here): one entry from feature
  003's `approval-queue.json` / `data-model.md` — this feature only reads
  and displays it, exactly as feature 002 already does for Tier 2 leads in
  the existing Approval Queue section. Never mutated by this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An agent can see the full subject and body of every currently
  pending email draft for their tenant by loading the dashboard alone, with
  no need to locate the original WhatsApp alert message.
- **SC-002**: An agent can distinguish a draft's exact status (Pending,
  Sent, Send Failed, Rejected, or Auto-Archived) at a glance, for every
  entry, without asking the developer or re-checking WhatsApp.
- **SC-003**: Zero instances of one tenant's Email Draft Queue section
  showing another tenant's drafts, across all test runs.
- **SC-004**: Zero approve/reject action of any kind — button, link, form,
  or otherwise — is present anywhere in the dashboard UI, across all test
  runs, verified by an automated guard identical in spirit to feature 002's
  existing frontend-action guard.
- **SC-005**: A tenant with no queued email drafts (or `auto_email_drafts`
  disabled) sees a clear "No email drafts yet" state, not an error or a
  blank section, on every dashboard visit.
