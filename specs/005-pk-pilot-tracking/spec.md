# Feature Specification: PK Pilot Tracking — PILOTS.md

**Feature Branch**: `005-pk-pilot-tracking`
**Created**: 2026-08-11
**Status**: Draft
**Input**: User description: "PILOTS.md pilot tracking system — track 4 PK agency onboarding slots with fields matching the tenant template in workspace/tenants/_template/USER.md, plus onboarding status and delivered-notification confirmation, per Constitution Section 2's Phase 1 gate definition."
**Market**: PK Real Estate (Pakistan) only — this feature exclusively tracks the Phase 1 gate defined in `CONSTITUTION.md` Section 2 ("3 Pakistani agencies confirmed ... before UK-market work begins"). It introduces no UK-market (Phase 2) candidate tracking of any kind (FR-012). Candidate agencies enter this tracker via the existing PK discovery form (`discovery/create_form.py`), the same intake source already live per README's Customer Discovery section.
**Language/Locale**: English-only. `PILOTS.md` is an internal, founder-facing tracking document, not client-facing — unlike features 001-004's WhatsApp messages, email drafts, and dashboard UI, it carries no PK Roman Urdu or UK-locale requirement.
**Milestone**: F012 — continues progress toward the Phase 1 validation gate opened by F008 (lead intake), F009 (dashboard), F010 (email approval gate), and F011 (dashboard email queue). This is the first feature whose entire purpose is Phase 1 gate *visibility and tracking itself*, rather than pipeline capability that indirectly unlocks it.

## Scope Decision

This feature is exclusively a manually-maintained tracking document. Per an explicit
architectural decision (recorded in this feature's ADR), no runtime agent — Orchestrator,
Intake, or Delivery — ever reads or writes `PILOTS.md`; it is edited by hand by the founder
(Asma) as each candidate agency progresses. This feature introduces no new agent-logic
code, no new `pytest` runtime-behavior coverage, and no changes to
`agents/*/SOUL.md`.

This feature does not build the tenant onboarding process itself — creating a real
`workspace/tenants/{tenant_id}/USER.md`, connecting Gmail OAuth, or deploying the
heartbeat remain manual operator actions outside this spec's scope, exactly as they
were before this feature existed. `PILOTS.md`'s `onboarding_status: confirmed` value is
never authoritative for pipeline behavior: the only field the running pipeline itself
ever trusts is `workspace/tenants/{tenant_id}/USER.md`'s own `active` flag, per
`CONSTITUTION.md` Sections 3-4. `PILOTS.md` is a tracking mirror, not a second source of
truth.

This feature also does not modify `CONSTITUTION.md`'s Phase 1 gate definition — it only
makes that existing "3 of N confirmed" threshold visible, structured, and auditable
against `MEMORY.md` run logs. It does not track UK-market (Phase 2) candidate agencies
(FR-012); Phase 2 outreach tracking is explicitly out of scope until the Phase 1 gate
itself is met, per `CONSTITUTION.md` Section 2's strict phase sequencing.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See all 4 pilot slots' status at a glance (Priority: P1)

The founder opens `PILOTS.md` and, without cross-referencing any other file, immediately
sees how many of the 4 tracked agency slots are confirmed and whether the Phase 1 gate
has been met — replacing scattered notes, DMs, and memory with one authoritative
tracking document.

**Why this priority**: this is the entire value of the feature — a single, trustworthy
view of Phase 1 progress. Without it, the founder has no consolidated way to know how
close the pipeline is to unlocking UK-market work. Independently deployable and
demonstrable the moment the file exists, even with all 4 slots empty.

**Independent Test**: open `PILOTS.md` in isolation (no other file) and read its top
summary line; verify it correctly states the count of `confirmed` slots and whether the
Phase 1 gate is met, matching the actual `onboarding_status` values recorded in the 4
slots below it.

**Acceptance Scenarios**:

1. **Given** a freshly created `PILOTS.md` with all 4 slots at `onboarding_status:
   not_started`, **When** the founder opens the file, **Then** the summary line reads
   "0 of 4 confirmed — Phase 1 gate not met."
2. **Given** 2 of 4 slots at `onboarding_status: confirmed` and 2 at earlier stages,
   **When** the founder opens the file, **Then** the summary line reads "2 of 4 confirmed
   — Phase 1 gate not met."

---

### User Story 2 - Record and update a slot's fields as onboarding advances (Priority: P2)

As a candidate agency progresses from initial signup through a live, confirmed pilot,
the founder records that agency's tenant-template fields and onboarding stage directly
in its assigned slot — building the record that User Story 1 summarizes.

**Why this priority**: this is the data-entry mechanism that produces the state User
Story 1 displays; without it there is nothing to summarize, but it is independently
testable given an existing slot structure.

**Independent Test**: starting from a `not_started` slot, manually fill in its fields
through each `onboarding_status` stage in order and verify at each stage that the slot's
fields match the required set exactly (FR-002, FR-003) and that a `confirmed` status is
never reachable without a traceable notification record (FR-004).

**Acceptance Scenarios**:

1. **Given** a `not_started` slot, **When** the founder fills in `tenant_id`,
   `agent_name`, `agent_whatsapp`, and `gmail_account` and sets `onboarding_status` to
   `tenant_configured`, **Then** every field listed in FR-002 for that slot holds a
   real value, not a `REPLACE_*` placeholder.
2. **Given** a `live` slot whose tenant has a real delivered-notification entry in
   `workspace/tenants/{tenant_id}/MEMORY.md`, **When** the founder copies that entry's
   `run_id` into `source_run_id` and sets `first_notification_delivered_at` to its
   timestamp, **Then** FR-004's confirmation precondition is satisfied and
   `onboarding_status` can be set to `confirmed`.
3. **Given** a `live` slot with `source_run_id: null`, **When** the founder attempts to
   set `onboarding_status: confirmed` anyway, **Then** the entry is invalid per FR-004
   and FR-011 and MUST NOT be counted toward the Phase 1 gate in User Story 3 — the
   rejection/failure path for an unverified confirmation.

---

### User Story 3 - Get an unambiguous signal the moment the Phase 1 gate is met (Priority: P3)

The moment 3 of the 4 tracked slots reach `confirmed`, the founder sees a clear,
unmistakable statement that the Phase 1 gate is met and UK-market (Phase 2) work is
now authorized to begin — rather than having to re-derive this from `CONSTITUTION.md` Section 2 each time.

**Why this priority**: the entire reason this feature exists, tied to the F012
milestone — but it depends on User Stories 1 and 2 already existing (the summary
mechanism and the underlying data), so it is lower priority to build, though
independently testable once they exist.

**Independent Test**: set exactly 3 of the 4 slots to `onboarding_status: confirmed`
(any 3 of the 4 — the combination does not matter) and verify the summary line states
the gate is met; reduce to 2 confirmed and verify it reverts to stating the gate is not
met.

**Acceptance Scenarios**:

1. **Given** 2 of 4 slots `confirmed`, **When** the founder opens `PILOTS.md`, **Then**
   the summary line reads "2 of 4 confirmed — Phase 1 gate not met."
2. **Given** 3 of 4 slots `confirmed` (any 3), **When** the founder opens `PILOTS.md`,
   **Then** the summary line reads "3 of 4 confirmed — Phase 1 gate met — UK-market work
   (Phase 2) is now authorized to begin," per `CONSTITUTION.md` Section 2.

---

### Edge Cases

- A 4th slot reaches `confirmed` while a different combination of 3 slots is already
  confirmed: the gate is met the moment **any** 3 of the 4 are simultaneously
  `confirmed` — FR-007's threshold is combination-independent, not tied to slot order.
- A previously `confirmed` slot's real tenant is later deactivated (`active: false` in
  its actual `workspace/tenants/{tenant_id}/USER.md`, e.g. the agency churns):
  `PILOTS.md`'s `confirmed` status is **not** automatically revoked, since no runtime
  write path to `PILOTS.md` exists (FR-005). The Phase 1 gate's own definition
  ("having received at least one delivered lead notification") is a past-tense,
  permanent condition, not "is currently active" — reverting a churned agency's slot to
  `withdrawn` is a deliberate, separate manual decision the founder makes, not an
  automatic consequence of this feature.
- All 4 slots are simultaneously `withdrawn`: the summary line still correctly reads "0
  of 4 confirmed — Phase 1 gate not met," not a special or broken state.
- Two candidate agencies have near-identical details (same `agent_name`, different
  `agent_whatsapp` numbers): each still receives its own distinct `tenant_id` and slot —
  FR-006 forbids only duplicate `tenant_id` values, never duplicate `agent_name` values.
- A withdrawn slot is reassigned to a brand-new candidate agency: it restarts at
  `onboarding_status: not_started` with every field reset to its placeholder/`null`
  state (FR-008) and progresses through the same stages as any other slot — no
  special-cased handling.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `PILOTS.md` MUST exist at the repository root and contain exactly 4 named
  pilot slots (Slot 1 through Slot 4), each representing one candidate PK agency
  onboarding position toward the Phase 1 gate.
- **FR-002**: Each pilot slot MUST record the following 11 fields, matching
  `workspace/tenants/_template/USER.md`'s schema field-for-field: `tenant_id`,
  `market_mode` (fixed value `"PK"`), `agent_name`, `agent_whatsapp`,
  `agent_discord_channel` (fixed value `null`), `gmail_account`, `hubspot_portal_id`,
  `hubspot_api_key_env`, `gemini_api_key_env`, `auto_email_drafts`,
  `whatsapp_input_enabled`, `active`.
- **FR-003**: Each pilot slot MUST additionally record 4 pilot-tracking fields not
  present in `USER.md`: `onboarding_status` (exactly one of: `not_started`,
  `forms_confirmed`, `tenant_configured`, `oauth_pending`, `live`, `confirmed`,
  `withdrawn`), `signup_date` (ISO 8601 date, or `null`),
  `first_notification_delivered_at` (ISO 8601 timestamp, or `null`), and
  `source_run_id` (the `run_id` from that tenant's `MEMORY.md` run-log entry containing
  the delivered notification, or `null`).
- **FR-004**: A slot's `onboarding_status` MUST NOT be set to `confirmed` unless both
  `first_notification_delivered_at` and `source_run_id` are non-null and
  `source_run_id` corresponds to an actual `notifications_sent` entry in that tenant's
  `workspace/tenants/{tenant_id}/MEMORY.md` run log.
- **FR-005**: `PILOTS.md` MUST NOT be read or written by any runtime agent
  (Orchestrator, Intake Sub-Agent, or Delivery Sub-Agent) under any circumstance — it is
  exclusively maintained by direct manual edit. `CONSTITUTION.md` Section 3's "the
  Orchestrator is the only agent that reads/writes `MEMORY.md` directly" governs
  `MEMORY.md` specifically; `PILOTS.md` sits entirely outside runtime agent I/O.
- **FR-006**: Two slots MUST NOT share the same non-null `tenant_id` value — every
  `tenant_id` present across the 4 slots MUST be unique at any point in time. If a
  duplicate is found, both slots holding that `tenant_id` MUST be treated as invalid and
  excluded from the Phase 1 gate count in FR-007 until the duplication is corrected.
- **FR-007**: The Phase 1 gate is met the instant at least 3 of the 4 slots
  simultaneously hold `onboarding_status: confirmed`, matching `CONSTITUTION.md`
  Section 2's exact numeric threshold.
- **FR-008**: A slot whose candidate agency withdraws or is disqualified MUST be set to
  `onboarding_status: withdrawn` (never deleted, never left at its prior status). A
  `withdrawn` slot is eligible for reassignment to a new candidate agency by resetting
  every field to its `not_started`/placeholder/`null` state.
- **FR-009**: `PILOTS.md` MUST include, as the first content line of the file, a single
  running summary stating the current count of `confirmed` slots out of 4 and whether
  the Phase 1 gate has been met, in the exact form demonstrated in User Stories 1 and 3's
  acceptance scenarios.
- **FR-010**: If `PILOTS.md` is missing, deleted, or does not parse as valid Markdown
  containing exactly 4 well-formed slots, the Phase 1 gate MUST be treated as unmet
  regardless of any other record of agency onboarding that exists elsewhere — the
  file's own presence and structural validity is required, not merely its claimed
  content.
- **FR-011**: An `onboarding_status` value other than the 7 named in FR-003 MUST be
  treated as an invalid entry for that slot, and that slot MUST be excluded from the
  Phase 1 gate count in FR-007 until corrected to a valid value.
- **FR-012**: `PILOTS.md` MUST NOT record any UK-market (Phase 2) candidate agency —
  Phase 2 outreach tracking remains out of scope until the Phase 1 gate defined in
  FR-007 is met, per `CONSTITUTION.md` Section 2's strict phase sequencing.
- **FR-013**: If a slot's recorded `tenant_id` does not exactly match its corresponding
  `workspace/tenants/{tenant_id}/USER.md`'s own `tenant_id` field, that slot MUST be
  treated as invalid and excluded from the Phase 1 gate count in FR-007 until the
  mismatch is corrected.

### Key Entities

- **Pilot Slot**: one of exactly 4 tracked positions in `PILOTS.md`. Carries the 11
  tenant-template fields (FR-002) plus the 4 pilot-tracking fields (FR-003). A slot
  becomes a real `workspace/tenants/{tenant_id}/USER.md` once that tenant is actually
  onboarded and its `active: true` is set in the real file during the (out-of-scope,
  manual) onboarding process — but the slot's copy in `PILOTS.md` remains a historical
  tracking record, never the runtime source of truth for that tenant (FR-005).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The founder can determine exactly how many of the 4 slots are `confirmed`
  and whether the Phase 1 gate has been met within 10 seconds of opening `PILOTS.md`,
  without opening any other file.
- **SC-002**: Zero pilot slots are ever marked `confirmed` without a `source_run_id`
  traceable to a real delivered-notification entry in that tenant's `MEMORY.md`, across
  all slots, at all times.
- **SC-003**: Zero duplicate `tenant_id` values exist across the 4 slots at any point in
  time.
- **SC-004**: 100% of the 11 tenant-template fields recorded for any `live` or
  `confirmed` slot are identical to that tenant's actual
  `workspace/tenants/{tenant_id}/USER.md` — zero drift between the tracking copy and the
  real config.
- **SC-005**: A `withdrawn` slot can be reassigned to a new candidate agency and reach
  `confirmed` status by passing through the same 7-stage `onboarding_status`
  progression as any other slot, with no special-case handling required anywhere in the
  process.

## Assumptions

- Exactly 4 slots track toward a 3-agency gate (`CONSTITUTION.md` Section 2), giving one
  buffer slot in case a candidate agency withdraws or fails to convert mid-onboarding —
  a standard pipeline-sizing pattern for a small, fixed validation cohort. This is an
  explicit instruction from the feature description, not an inferred default.
- `PILOTS.md` lives at the repository root, alongside `README.md` and
  `CONSTITUTION.md`, rather than under `workspace/` — it is a founder-facing business
  tracking document, not tenant runtime state (which is what `workspace/` holds).
