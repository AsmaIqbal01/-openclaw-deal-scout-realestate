# Feature Specification: PK Lead Intake, Classification & WhatsApp Notification

**Feature Branch**: `001-pk-lead-intake-notify`
**Created**: 2026-08-01
**Status**: Draft
**Input**: User description: "First PK feature: intake Zameen and OLX Gmail alerts plus WhatsApp forwarded leads, classify with Gemini, validate and write to HubSpot CRM, and notify the agent via WhatsApp"
**Market**: PK Real Estate (Pakistan) only — Karachi, Lahore, Islamabad agents and small agencies
**Milestone**: F008 — unlocks progress toward the Phase 1 validation gate (3 PK agencies confirmed active, defined as having received at least one delivered lead notification, before UK launch)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Instant notification for a high-confidence lead (Priority: P1)

A Pakistani real estate agent receives a Zameen.com or OLX alert email, or a
WhatsApp-forwarded property enquiry, that clearly names a contact and a
budget. The agent gets a WhatsApp message with the lead details within the
same pipeline cycle, and the lead is already logged in HubSpot — no manual
copy-paste, no missed lead.

**Why this priority**: this is the entire value proposition of Deal Scout —
"the AI employee that never misses a property lead." Without this story
there is no product; it is independently deployable as the complete MVP.

**Independent Test**: send a test Zameen.com alert email containing a phone
number, property type, and budget to a connected Gmail inbox; run one
heartbeat cycle; verify a HubSpot contact and deal exist and the agent's
WhatsApp number receives a "🔴 URGENT —" message with the lead's contact,
property type, location, and score. Edge case tested: the auto-dispatch path
runs end-to-end (classify → CRM write → notify) with no human step in
between.

**Acceptance Scenarios**:

1. **Given** a new Zameen.com alert email containing a phone number, property
   type, and budget arrives in the tenant's Gmail inbox, **When** the
   heartbeat pipeline runs, **Then** Gemini classifies it with
   `classification_score` ≥ 0.9, a HubSpot contact and deal are created, and
   the agent receives a WhatsApp notification prefixed "🔴 URGENT — " within
   that same run.
2. **Given** a WhatsApp message forwarded to the agent's connected number
   containing clear buyer intent and a phone number, **When** the heartbeat
   pipeline runs, **Then** the same auto-dispatch outcome as Scenario 1
   occurs via the WhatsApp source path.

---

### User Story 2 - Human review for a medium-confidence lead (Priority: P2)

When Gemini is only moderately confident a message is a real lead (contact
present but no budget mentioned, or similarly partial signal), the system
does not clutter the agent's CRM automatically. Instead, the owner is asked
to confirm or discard it via WhatsApp before anything is written or sent to
the agent.

**Why this priority**: protects CRM data quality and the agent's trust in
notifications without losing potentially real leads. Depends on User Story 1
existing but adds no new intake or classification logic — a pure "what to do
with an uncertain score" layer.

**Independent Test**: submit a message with a contact present but no budget
mentioned; run one heartbeat cycle; verify no CRM write occurs, the owner
receives a "Review needed — score {score}" WhatsApp message, and the lead
remains held until `/confirm` or `/discard` is received. Edge case tested:
the rejection/hold path — a lead that must NOT be auto-written despite being
a plausible lead.

**Acceptance Scenarios**:

1. **Given** a lead classified with `classification_score` between 0.70 and
   0.89 inclusive, **When** the Delivery Sub-Agent receives it, **Then** no
   CRM write occurs immediately, the owner receives a WhatsApp message
   reading "Review needed — score {score}", and the lead is held in the
   approval queue.
2. **Given** the owner replies `/confirm {lead_id}` within 2 hours of the
   review request, **When** Delivery processes the reply, **Then** the CRM
   contact and deal are written and the agent receives the standard lead
   WhatsApp notification.
3. **Given** the owner replies `/discard {lead_id}`, or does not reply within
   2 hours, **When** the reply or the 2-hour timeout occurs, **Then** the
   lead is logged as rejected (`owner_no_response` if timed out) and no CRM
   write or agent notification occurs.

---

### User Story 3 - Reliable operation within the free Gemini quota (Priority: P3)

The product's entire business model depends on zero paid infrastructure.
Gemini's free tier allows 20 classification requests per day; the pipeline
must stop itself safely before that limit is reached rather than fail loudly
or silently exceed it.

**Why this priority**: this is a cross-cutting reliability guarantee rather
than a new user-facing capability, so it is lowest priority to build but
independently testable and independently valuable — it protects the zero-cost
constraint that both Story 1 and 2 depend on operationally.

**Independent Test**: set the tenant's `gemini_today_count` to 18 before a
heartbeat run; verify the run skips parsing and classification entirely,
makes zero Gemini calls, logs `quota_exhausted: true`, and sends exactly one
WhatsApp alert to the owner. Edge case tested: the guard fires at the
threshold itself (18), not only once the limit is exceeded.

**Acceptance Scenarios**:

1. **Given** `gemini_today_count` is 18 for the tenant, **When** the
   heartbeat pre-flight check runs, **Then** the pipeline aborts before the
   parse and classify steps, makes zero Gemini calls that run, logs
   `quota_exhausted: true`, and sends exactly one WhatsApp alert to the owner.
2. **Given** `gemini_today_count` is between 15 and 17 for the tenant,
   **When** the heartbeat pipeline runs, **Then** classification proceeds
   normally and a "quota low: {count}/20 used" warning is logged.

---

### Edge Cases

- A lead's `classification_score` is below 0.7 (including scores in the
  0.5–0.69 "partial contact/ambiguous intent" range): the Intake Sub-Agent
  rejects it before it reaches Delivery, logging a `rejection_reason`; no CRM
  write or notification occurs.
- The same `raw_source_id` appears twice across separate heartbeat runs (a
  duplicate Gmail message or repeated WhatsApp forward): Delivery rejects the
  second occurrence before any CRM write, using the tenant's `processed_ids`.
- The HubSpot CRM write fails: Delivery retries exactly once after 30
  seconds; if the retry also fails, Delivery halts that lead, logs the
  error, and sends no notification for it.
- A Gemini classification call times out: the lead is marked
  `unclassified`, logged, and not passed to Delivery.
- A lead JSON is missing a required field: Delivery rejects it, logs the
  missing field, and takes no further action.
- A lead's `tenant_id` does not match the active session's `USER.md`
  `tenant_id`: Delivery rejects it immediately and logs the mismatch; no
  cross-tenant CRM write or notification occurs.
- The WhatsApp notification send fails: Delivery retries exactly once; if
  the retry also fails, it logs the failure and continues the pipeline run
  without blocking remaining leads.
- Gmail OAuth authorization is invalid or expired: the Gmail read step for
  that tenant fails immediately, is logged as an authentication error, and
  the run continues processing WhatsApp-sourced leads rather than aborting
  entirely.
- The HubSpot API key is invalid or unauthorized: this fails the heartbeat
  pre-flight reachability check, so the entire run for that tenant aborts
  before any leads are processed, and the failure is logged.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Intake Sub-Agent MUST read new Gmail messages from
  Zameen.com and OLX Pakistan property-alert senders, plus new WhatsApp
  messages forwarded to the tenant's connected number, once per heartbeat run
  (every 15 minutes).
- **FR-002**: The Intake Sub-Agent MUST classify each candidate message with
  Gemini 2.5 Flash against the PK trigger-keyword set (Roman Urdu/English:
  "plot", "ghar", "kanal", "marla", "property", "kiraya", "sale", "purchase",
  "DHA", "Bahria", "gulshan", "nazimabad", "budget hai", "dekhna hai") and
  produce a `classification_score` between 0.0 and 1.0.
- **FR-003**: The Intake Sub-Agent MUST reject (not forward to Delivery) any
  candidate with `classification_score` < 0.7, logging a `rejection_reason`.
  This threshold aligns exactly with the lower bound of the held-for-review
  band in FR-006, so every score is unambiguously either rejected (< 0.7),
  held for review (0.70–0.89), or auto-dispatched (≥ 0.9) — no unassigned band.
- **FR-004**: The Delivery Sub-Agent MUST validate every required field of
  the Intake output (`lead_id`, `tenant_id`, `source`, `market_mode`,
  `classification_score`, `raw_source_id`, `classified_at`) before taking any
  action, and MUST reject the lead if any required field is missing or if
  `raw_source_id` already exists in the tenant's `processed_ids`.
- **FR-005**: For a lead with `classification_score` ≥ 0.9, the Delivery
  Sub-Agent MUST create a HubSpot CRM contact and deal, then send a WhatsApp
  notification prefixed "🔴 URGENT — " to the agent's WhatsApp number from
  `USER.md`, in that order, within the same pipeline run.
- **FR-006**: For a lead with `classification_score` between 0.70 and 0.89
  inclusive, the Delivery Sub-Agent MUST hold the CRM write, send the owner a
  WhatsApp message reading "Review needed — score {score}", and wait for a
  reply of `/confirm {lead_id}` or `/discard {lead_id}`.
- **FR-007**: If the owner sends `/confirm {lead_id}` within 2 hours of the
  review request, the Delivery Sub-Agent MUST write the CRM contact and deal
  and send the standard WhatsApp lead notification to the agent.
- **FR-008**: If the owner sends `/discard {lead_id}`, or sends no reply
  within 2 hours, the Delivery Sub-Agent MUST log the lead as rejected
  (`owner_no_response` if timed out) and MUST NOT write to CRM or notify the
  agent.
- **FR-009**: The Orchestrator MUST read `gemini_today_count` from
  `MEMORY.md` before every heartbeat run's classification step, and MUST
  skip parsing and classification entirely (zero Gemini calls) when
  `gemini_today_count` ≥ 18, logging `quota_exhausted: true` and sending
  exactly one WhatsApp alert to the owner.
- **FR-010**: The Orchestrator MUST verify that every lead's `tenant_id`
  matches the `tenant_id` declared in the active session's `USER.md` before
  any CRM write, notification, or `MEMORY.md` update, and MUST reject and log
  any mismatch without taking further action on that lead.
- **FR-011**: The Orchestrator MUST write `run_id`, `tenant_id`,
  `started_at`, `completed_at`, `leads_found`, `leads_classified`,
  `leads_rejected`, `crm_writes`, `notifications_sent`, and
  `gemini_calls_this_run` to `MEMORY.md` at the end of every heartbeat run,
  regardless of outcome.
- **FR-012**: If the HubSpot CRM write fails, the Delivery Sub-Agent MUST
  retry exactly once after 30 seconds; if the retry also fails, it MUST halt
  processing of that lead, log the error, and MUST NOT send any notification
  for that lead.
- **FR-013**: If the WhatsApp notification send fails, the Delivery
  Sub-Agent MUST retry exactly once; if the retry also fails, it MUST log the
  failure and continue the pipeline run without blocking remaining leads.
- **FR-014**: If Gmail OAuth authorization is invalid or expired, the
  Orchestrator MUST log an authentication error for the Gmail source only and
  MUST continue processing WhatsApp-sourced leads for that run rather than
  aborting the entire pipeline.
- **FR-015**: If the HubSpot API key is invalid or unauthorized, the
  heartbeat pre-flight reachability check MUST fail, and the Orchestrator
  MUST abort the entire run for that tenant before processing any leads,
  logging the failure.

### Key Entities

- **Lead**: a candidate property inquiry extracted from Gmail or WhatsApp,
  carrying contact info, property details, urgency, `classification_score`,
  `source`, and a processing status (pending, auto-dispatched, held-for-review,
  rejected, or discarded).
- **Tenant (Agency)**: a PK real estate agency using Deal Scout, identified by
  `tenant_id`, with its own `USER.md` configuration (WhatsApp number, active
  status) and its own `gemini_today_count` and `processed_ids` in `MEMORY.md`.
- **Pipeline Run**: one heartbeat execution instance, with `run_id`,
  timestamps, and counts of leads found, classified, rejected, and delivered.
- **Approval Queue Entry**: a Tier 2 (0.70–0.89) lead awaiting an owner
  `/confirm` or `/discard` reply, subject to a 2-hour timeout.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An agent with a clear, high-confidence lead (contact and budget
  present) receives a WhatsApp notification within one heartbeat cycle (15
  minutes) of the source email or WhatsApp message arriving.
- **SC-002**: At least 95% of leads scoring 0.9 or above result in both a CRM
  entry and an agent WhatsApp notification with no manual intervention.
- **SC-003**: Zero client-facing emails are sent without explicit owner
  approval, across all test runs (this feature has no email-send path; the
  criterion confirms none is introduced).
- **SC-004**: Zero duplicate CRM entries are created for the same source
  message across repeated heartbeat runs.
- **SC-005**: The pipeline never issues more than 18 Gemini classification
  calls in a single UTC day for a single tenant.
- **SC-006**: Zero cross-tenant data appears in another tenant's CRM,
  notifications, or logs across all test runs.
