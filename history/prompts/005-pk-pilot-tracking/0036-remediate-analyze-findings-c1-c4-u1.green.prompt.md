---
id: 0036
title: Remediate analyze findings C1-C4 U1
stage: green
date: 2026-08-11
surface: agent
model: claude-sonnet-5
feature: 005-pk-pilot-tracking
branch: 005-pk-pilot-tracking
user: AsmaIqbal000
command: /sp.analyze remediation
labels: ["remediation", "pilot-tracking", "coverage-gap", "F012"]
links:
  spec: specs/005-pk-pilot-tracking/spec.md
  ticket: null
  adr: adrs/ADR-004-pilots-manual-tracking-boundary.md
  pr: null
files:
 - tests/contract/test_pilots_schema.py
 - tests/fixtures/pilots/all_withdrawn.md
 - specs/005-pk-pilot-tracking/tasks.md
tests:
 - tests/contract/test_pilots_schema.py (21 tests, all passing)
 - full suite: 106 passed
---

## Prompt

Apply direct remediation for C1 and C2 now. Add T009b for FR-013 tenant_id/USER.md mismatch check, add missing/malformed file handling for FR-010 (C2), add withdrawn fixture for FR-008 (C3), and add UK market_mode schema failure test for FR-012 (C4). Also add the boundary guard test for FR-005 (U1). Then re-run full test suite and confirm all pass before Phase 7 polish.

## Response snapshot

Closed all 5 findings from the `/sp.analyze` report in one pass:

- **C1 (CRITICAL, FR-013)**: added `_tenant_id_mismatches_real_user_md`
  helper and extended `count_valid_confirmed(slots, workspace_root=None)`
  with an optional parameter — when given, excludes any slot whose
  `tenant_id` disagrees with the real `workspace/tenants/{tenant_id}/USER.md`'s
  own `tenant_id` field. Kept the parameter optional and defaulted to
  `None` specifically so the 10 already-passing T010-T019 tests, which call
  `count_valid_confirmed(slots)` with one argument, needed zero changes.
  Added 3 tests: the mismatch actually excludes, a matching tenant is
  still counted (no over-exclusion), and a not-yet-onboarded tenant isn't
  penalized (per `data-model.md`'s "once that tenant exists" qualifier).
- **C2 (HIGH, FR-010)**: added `load_pilots_document(path)` (states
  `"missing"`/`"malformed"`/`"ok"`, mirroring `dashboard/server.py`'s
  established `load_email_draft_queue_raw` pattern from feature 004) and
  `gate_met(document)`. 5 tests: missing file, malformed content, wrong
  slot count, a valid file reaching `"ok"` with gate met, and a sanity
  check that the real repository-root `PILOTS.md` itself reaches `"ok"`.
- **C3 (MEDIUM, FR-008)**: new fixture `all_withdrawn.md` (4 slots, all
  `withdrawn`) plus a test proving the summary line still correctly reads
  "0 of 4 confirmed" rather than hitting a special case.
- **C4 (MEDIUM, FR-012)**: a test mutating a valid slot's `market_mode` to
  `"UK"` and asserting schema validation actually rejects it — proving the
  existing `const: "PK"` constraint works, not just that it's declared.
- **U1 (MEDIUM, FR-005)**: a regression guard scanning every
  `agents/*/SOUL.md` and `skills/*.md` file for the literal string
  `PILOTS.md`, asserting zero matches — the automated version of the
  manual-only boundary ADR-004 documents, matching feature 004's
  `test_no_approval_actions_in_frontend.py` precedent for hardening a
  negative/absence requirement.

Updated the module docstring's FR-coverage claim from
"FR-001/002/003/004/006/007/009/011" to the full 13-requirement list
(explicitly noting FR-004's MEMORY.md-traceability portion remains
unverifiable by design, per ADR-004's already-accepted risk — not a new
gap). Added a `tasks.md` Phase 8 documenting all 6 remediation tasks
(T009b, T024-T029) as `[X]` complete.

Ran `pytest tests/contract/test_pilots_schema.py -v`: 21/21 passing (up
from 10). Ran the full `pytest tests/ -v`: 106/106 passing (up from 95) —
zero regressions.

## Outcome

- ✅ Impact: FR coverage for feature 005 is now 13/13 (was 8 full + 2 partial + 3 zero); the one CRITICAL finding (FR-013 unimplemented despite being named in data-model.md) is closed
- 🧪 Tests: 21/21 in the pilot contract file (up from 10), 106/106 full suite (up from 95) — 11 new tests added, zero regressions
- 📁 Files: `tests/contract/test_pilots_schema.py` (extended), `tests/fixtures/pilots/all_withdrawn.md` (new), `specs/005-pk-pilot-tracking/tasks.md` (Phase 8 added)
- 🔁 Next prompts: Phase 7 polish is now fully re-verified post-remediation; feature 005 implementation is complete pending user review/commit
- 🧠 Reflection: making `workspace_root` an optional, defaulted parameter on `count_valid_confirmed` rather than a required one was the right call — it closed the CRITICAL gap without touching any of the 10 already-passing call sites, keeping the fix's diff scoped exactly to what was broken

## Evaluation notes (flywheel)

- Failure modes observed: none during remediation itself; the underlying failure mode (spec requirement added during self-audit not propagating to tasks.md's actual scope) was already identified in PHR 0035
- Graders run and results (PASS/FAIL): full test suite — PASS (106/106)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
