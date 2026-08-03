# Feature Specification: PK Email Draft & Operator Approval Gate

**Feature Branch**: `003-pk-email-approval-gate`
**Created**: 2026-08-01
**Status**: Draft
**Input**: User description: "Third PK feature: draft follow-up emails for dispatched leads when auto_email_drafts is enabled, queue them for operator approval, notify the agent via WhatsApp, and only send after an explicit /approve reply, per skills/operator-approval-gate.md"
**Market**: PK Real Estate (Pakistan) only — the PK-mode email template from `skills/operator-approval-gate.md` is used exclusively; the UK-mode template is out of scope until the UK launch phase
**Language/Locale**: The drafted email itself is English-only. `skills/operator-approval-gate.md` labels its PK template section "PK Mode (Roman Urdu + English)," but the template body it defines is entirely English — this spec resolves that heading/content mismatch by fixing the actual drafted output as English-only, matching every other PK client-facing artifact already built (feature 001's WhatsApp templates, feature 002's dashboard UI). The WhatsApp draft-alert and re-notification messages (FR-007, FR-012) are likewise English-only.
**Milestone**: F010 — this is the first feature to actually exercise Constitution Principle VII (Human Approval Gate for Client-Facing Communication), which was explicitly marked N/A in both F008 (no email path) and F009 (dashboard, read-only). Unlocks the "auto follow-up email" capability as an offerable feature ahead of the Phase 1 gate.

## Scope Decision

This feature covers the WhatsApp-based draft/queue/notify/approve/reject/
stale-guard flow only. It does **not** extend the dashboard (feature 002)
to display the email-draft queue — `dashboard-state.json`'s
`leads_pending_approval`/Approval Queue section remains scoped to Tier 2
lead review only, per feature 002's own Scope Decision. Showing email
drafts on the dashboard is deferred to a future dashboard-extension
feature. This feature also does not change feature 001's Tier 1/Tier 2
CRM-write-and-notify behavior — it adds a new step that runs *after* a
successful CRM write, per `agents/delivery/SOUL.md`'s existing Step 4
("Email Queue (if applicable)").

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A follow-up email is drafted and queued automatically (Priority: P1)

An agent who has enabled automatic email drafts gets a ready-to-review
follow-up email queued the moment one of their leads is dispatched (Tier 1
auto-dispatch or a Tier 2 lead the owner just confirmed) — with a WhatsApp
alert telling them a draft is waiting. They never have to write the email
themselves, and nothing is sent without their say-so.

**Why this priority**: this is the entire value proposition of the
feature — saving the agent the work of writing a follow-up, without
compromising the "never send without a human" guarantee. Without it there
is no feature; independently deployable and demonstrable on its own.

**Independent Test**: dispatch a lead with a non-null `contact.email` for a
tenant with `auto_email_drafts: true`; verify a new entry appears in
`approval-queue.json` with `approved: false`, and the owner's WhatsApp
number receives "📧 New email draft awaiting your approval..." within the
same pipeline run. Edge case tested: the draft is queued, not sent — no
email leaves the system at this point.

**Acceptance Scenarios**:

1. **Given** a Tier 1 auto-dispatched lead with `contact.email` set and the
   tenant's `auto_email_drafts` is `true`, **When** the CRM write completes,
   **Then** a new `approval-queue.json` entry is appended with
   `approved: false`, `sent_at: null`, and the owner receives the WhatsApp
   draft-alert message referencing that `queue_id`.
2. **Given** the same lead but `contact.email` is `null`, **When** the CRM
   write completes, **Then** no draft is created and
   `"no email address for lead {lead_id}"` is logged instead.

---

### User Story 2 - The agent approves or rejects the draft via WhatsApp (Priority: P2)

The agent reads the drafted email, and either replies `/approve {queue_id}`
to send it as-is, or `/reject {queue_id}` to discard it — completing the
approval loop that Constitution Principle VII requires for every
client-facing email.

**Why this priority**: closes the loop opened by User Story 1; depends on a
queued draft existing but is independently testable given one.

**Independent Test**: with a pending queue entry, reply `/approve
{queue_id}`; verify the email is sent, `approved`/`approved_at`/`sent_at`
are all set, and no other queue entries are touched. Separately, reply
`/reject {queue_id}` to a different pending entry and verify it is never
sent. Edge case tested: a reply naming a `queue_id` that doesn't exist (or
is already resolved) is ignored and logged, not silently accepted or
misapplied to another entry.

**Acceptance Scenarios**:

1. **Given** a pending queue entry, **When** the owner replies `/approve
   {queue_id}`, **Then** `approved` becomes `true`, `approved_at` is set,
   the email is sent to `recipient_email`, and `sent_at` is set.
2. **Given** a pending queue entry, **When** the owner replies `/reject
   {queue_id}`, **Then** the entry is logged as rejected and the email is
   never sent.
3. **Given** no queue entry matches the `queue_id` in a reply (or it was
   already approved/rejected), **When** that reply is processed, **Then**
   it is logged as `unknown_queue_id_reply` and no queue entry is modified.

---

### User Story 3 - Stale drafts never linger or self-send (Priority: P3)

A draft the agent hasn't responded to gets exactly one reminder after 4
hours, and is safely auto-archived (never sent) after 24 hours — so an
unanswered draft can never accidentally go out, and never sits forgotten
forever either.

**Why this priority**: a reliability guarantee protecting Constitution
Principle VII over time, not a new user-facing capability — lower priority
to build than the core draft/approve loop, but independently testable and
important for a real multi-week deployment.

**Independent Test**: hold a pending entry at `queued_at` + 4 hours; verify
exactly one re-notification is sent (not on every subsequent run). Hold
another at `queued_at` + 24 hours with no reply; verify it is marked
`auto_archived: true` and is never sent, even if a late `/approve` for it
arrives afterward. Edge case tested: the 24-hour archival is permanent —
approval cannot revive an archived draft.

**Acceptance Scenarios**:

1. **Given** a pending entry queued 4 hours and 5 minutes ago with no
   reply, **When** the pipeline runs, **Then** exactly one re-notification
   WhatsApp message is sent for that entry, and running the pipeline again
   before any reply does not send a second reminder.
2. **Given** a pending entry queued 24 hours and 5 minutes ago with no
   reply, **When** the pipeline runs, **Then** the entry is marked
   `auto_archived: true`, is never sent, and a subsequent `/approve` reply
   for that `queue_id` is treated as `unknown_queue_id_reply`.

---

### Edge Cases

- `contact.email` is `null`: no draft is created; logged as "no email
  address for lead {lead_id}" (FR-002).
- The tenant's `approval-queue.json` already has 50 entries: no new draft
  is added, the owner is alerted, and the halt is logged (FR-006).
- Queue file write fails: logged, the owner is alerted, and the draft is
  not queued (FR-015).
- Draft generation itself fails (e.g., template rendering error): logged
  with the `lead_id`; only that lead's email is skipped — the CRM write
  and agent notification that already happened for that lead are
  unaffected (FR-014).
- `auto_email_drafts` is `false` (the default) for a tenant: no draft is
  ever attempted for that tenant's leads.
- A reply's `queue_id` belongs to a different tenant than the replying
  agent's own tenant: rejected the same as an unknown `queue_id` — never
  resolved across tenants (ties to Constitution Principle VIII).
- Two different agents' approval queues are processed in the same
  heartbeat run: no cross-tenant reads or writes occur to either queue
  file.
- The draft-alert or re-notification WhatsApp message fails to send
  (network/API failure): retried exactly once, then logged; the draft
  remains queued and awaiting reply regardless (FR-007).
- The email itself fails to send after an `/approve` reply (e.g., SMTP
  error): retried exactly once after 30 seconds; if still failing,
  `sent_at` remains unset, the failure is logged, and the owner is alerted
  so an approved-but-unsent draft is never silently lost (FR-009).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: After a lead's CRM write succeeds (Tier 1 auto-dispatch, or
  Tier 2 following an owner `/confirm`), the Delivery Sub-Agent MUST draft
  a follow-up email using the PK-mode template from
  `skills/operator-approval-gate.md`, if and only if the tenant's
  `auto_email_drafts` is `true` and the lead's `contact.email` is non-null.
- **FR-002**: If `contact.email` is `null`, the Delivery Sub-Agent MUST NOT
  attempt to draft an email, and MUST log
  `"no email address for lead {lead_id}"`.
- **FR-003**: The PK email draft MUST use the subject
  `"Property Enquiry — {property.type} in {property.location}"`, address
  `contact.name` (or `"Sir/Madam"` if null), state `property.type`,
  `property.location`, `property.budget_pkr` (or `"to be discussed"` if
  null), and `property.size` (or `"flexible"` if null), and be signed with
  the tenant's `agent_name` and agency name.
- **FR-004**: The Delivery Sub-Agent MUST append a new entry to the
  tenant's `approval-queue.json` with `queue_id`, `tenant_id`, `lead_id`,
  `draft_subject`, `draft_body`, `recipient_email`, `queued_at`,
  `approved: false`, `approved_at: null`, and `sent_at: null`.
- **FR-005**: Appending to `approval-queue.json` MUST NOT overwrite or
  remove any existing entry in that tenant's queue.
- **FR-006**: If the tenant's `approval-queue.json` already contains 50
  entries, the Delivery Sub-Agent MUST NOT add a new draft, MUST alert the
  owner, and MUST log the halt.
- **FR-007**: After queuing, the Delivery Sub-Agent MUST send exactly one
  WhatsApp message to `agent_whatsapp` reading
  `"📧 New email draft awaiting your approval. Lead: {contact.name |
  lead_id}. Reply /approve {queue_id} or /reject {queue_id}"`. If this send
  fails, the Delivery Sub-Agent MUST retry exactly once, then log the
  failure and continue the pipeline run without blocking other drafts —
  matching feature 001 FR-013's WhatsApp-send retry semantics. The draft
  remains queued and awaiting reply regardless of notification delivery.
- **FR-008**: The drafted email MUST NOT be sent under any circumstance
  while `approved` is `false`.
- **FR-009**: When the owner replies `/approve {queue_id}` for a `pending`
  entry belonging to their own tenant, the Delivery Sub-Agent MUST set
  `approved: true`, set `approved_at` to the current timestamp, then send
  the email to `recipient_email`, and set `sent_at` only once that send
  succeeds. If the send fails, the Delivery Sub-Agent MUST retry exactly
  once after 30 seconds (matching feature 001 FR-012's HubSpot-write retry
  semantics); if the retry also fails, `sent_at` MUST remain unset, the
  failure MUST be logged, and the owner MUST be alerted so the approved
  draft is not silently lost.
- **FR-010**: When the owner replies `/reject {queue_id}` for a `pending`
  entry belonging to their own tenant, the Delivery Sub-Agent MUST mark it
  rejected and MUST NOT send it.
- **FR-011**: A reply naming a `queue_id` that does not exist for that
  tenant, or that is already resolved (approved, rejected, or
  auto-archived), MUST be ignored and logged as `unknown_queue_id_reply` —
  no queue entry MUST be modified by that reply.
- **FR-012**: If a `pending` entry's `queued_at` is more than 4 hours in
  the past and it has not yet been re-notified, the Delivery Sub-Agent
  MUST send exactly one re-notification WhatsApp message for it; it MUST
  NOT send a second reminder for the same entry.
- **FR-013**: If a `pending` entry's `queued_at` is more than 24 hours in
  the past, the Delivery Sub-Agent MUST mark it `auto_archived: true`,
  MUST NOT send it, and this state MUST be permanent — a subsequent
  `/approve` reply for that `queue_id` MUST be treated as
  `unknown_queue_id_reply` (FR-011).
- **FR-014**: If draft generation itself fails, the Delivery Sub-Agent
  MUST log the failure with the `lead_id` and MUST skip only that lead's
  email — it MUST NOT roll back or block the CRM write or agent
  notification already completed for that lead.
- **FR-015**: If writing to `approval-queue.json` fails, the Delivery
  Sub-Agent MUST log the error, alert the owner, and MUST NOT proceed with
  queuing that draft.

### Key Entities

- **Approval Queue Entry**: one drafted email awaiting or past a decision,
  identified by `queue_id`, scoped to exactly one `tenant_id`, with status
  implied by its fields (`pending` when `approved: false` and not yet
  archived; `approved`/`sent` once `sent_at` is set; `rejected`; or
  `auto_archived`).
- **Email Draft**: the `draft_subject`/`draft_body` content generated from
  the PK template and a specific `Lead` (feature 001's data model) and
  `Tenant` (`agent_name`, agency name, `agent_whatsapp`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero client-facing emails are sent without a prior explicit
  `/approve` reply, across all test runs.
- **SC-002**: An agent with `auto_email_drafts` enabled receives a WhatsApp
  draft-alert within the same pipeline run a qualifying lead is dispatched.
- **SC-003**: A draft that receives no reply is never sent, and is marked
  `auto_archived: true` within 24 hours of being queued.
- **SC-004**: Zero drafts are created for leads whose `contact.email` is
  null.
- **SC-005**: Zero cross-tenant approval-queue reads, writes, or resolved
  replies across all test runs.
