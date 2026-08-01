---
id: 0014
title: Dashboard analyze remediation applied
stage: misc
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: 002-pk-client-dashboard
branch: 002-pk-client-dashboard
user: Asma
command: /sp.analyze (remediation follow-up)
labels: [analyze, remediation, coverage-gap, tasks-renumber]
links:
  spec: specs/002-pk-client-dashboard/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-pk-client-dashboard/tasks.md
tests:
 - tasks.md T008 (new, schema negative-case), T011/T012 (new, US1) will close the coverage gaps — not yet executed, planning-stage only
---

## Prompt

Yes, apply the edits now

## Response snapshot

Applied remediation for `/sp.analyze` findings G1, G2, and G3 against
`tasks.md`. G1 (FR-007 CRM Sync, zero coverage) and G2 (FR-008 Market
Toggle, zero coverage) were closed as offered: extended T004's fixture
description to explicitly include `crm_last_write_at` and `market_mode`,
and added two new US1 tests (`test_crm_sync_status_reflects_state`,
`test_market_toggle_reflects_mode`).

G3 was resolved more precisely than originally framed, rather than applied
literally as first suggested. Re-examining the architecture during
remediation: the "over 10 leads" cap is already enforced by
`contracts/dashboard-state-schema.json`'s `recent_leads` `maxItems: 10` —
it's a schema/contract concern belonging to whatever writes
`dashboard-state.json` (out of this feature's scope per `research.md`
Decision 1), not something this feature's display code computes. Likewise
`contact_name`'s "Unknown" fallback is already guaranteed by the schema
requiring a non-null string — the upstream writer must substitute it before
the file exists, so there's no fallback logic for this feature to test
either. The actual gap was narrower than first stated: no test proved the
schema *rejects* an over-10-entry array. Added one negative-case test
(T008) to `test_dashboard_state_schema.py` instead of inventing new
display-layer capping/fallback logic that would have duplicated a
constraint already enforced elsewhere — a more architecturally correct fix
than the original offer.

Renumbered `tasks.md` from 23 to 26 tasks (Foundational gained T008;
US1 gained T011–T012 inserted before its frontend-wiring task, which shifted
to T013). Verified via grep that final IDs T001–T026 are contiguous, unique,
and appear in strictly increasing order matching file position, and that no
stale task-ID references remain elsewhere in the feature directory.

`/sp.analyze` finding I1 (a pre-existing "Step 7" vs "Step 10" documentation
mismatch between `skills/remote-dashboard.md` and `workspace/HEARTBEAT.md`)
was not addressed — it was flagged as lower-priority and not included in
the user's edit approval, and touches files outside this feature's scope.

## Outcome

- ✅ Impact: `tasks.md` now has test coverage for all 12 in-scope FRs (FR-001 remains correctly N/A by design); the 10-leads-cap and Unknown-fallback "gaps" were shown to be non-issues once traced to the schema layer, avoiding unnecessary duplicate logic.
- 🧪 Tests: 3 new tasks (T008, T011, T012) planned; not yet executed.
- 📁 Files: `specs/002-pk-client-dashboard/tasks.md` (renumbered 23 → 26 tasks).
- 🔁 Next prompts: `/sp.implement`; optionally revisit I1 (doc inconsistency) separately since it wasn't part of this remediation's scope.
- 🧠 Reflection: re-deriving the correct fix during remediation rather than mechanically applying the originally-offered wording caught that two of the three "gaps" were actually already closed by the schema — worth re-checking architecture before implementing a suggested fix verbatim, even one's own.

## Evaluation notes (flywheel)

- Failure modes observed: the initial `/sp.analyze` report's G3 wording (implying new display-layer logic was needed) was imprecise — corrected during remediation by re-tracing where the cap/fallback guarantees actually live.
- Graders run and results (PASS/FAIL): format/ID-contiguity check via grep — PASS (26/26 unique, contiguous, monotonic); stale-reference check via grep — PASS.
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
