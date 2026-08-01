---
id: 0016
title: ADR dashboard server architecture
stage: misc
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: 002-pk-client-dashboard
branch: 002-pk-client-dashboard
user: Asma
command: /sp.adr
labels: [adr, dashboard, server-architecture, constitution-checker-followup]
links:
  spec: specs/002-pk-client-dashboard/spec.md
  ticket: null
  adr: adrs/ADR-003-dashboard-server-architecture.md
  pr: null
files:
 - adrs/ADR-003-dashboard-server-architecture.md
tests:
 - none (documentation only)
---

## Prompt

Yes, run /sp.adr first

(follow-up to the Constitution Checker report flagging Q3 FAIL — no ADR existed for feature 002 — and the ADR-suggestion prompt for the dashboard server architecture)

## Response snapshot

Ran `check-prerequisites.ps1 -Json`, confirmed `plan.md` exists. Confirmed
`adrs/` (not `history/adr/`) remains the actual repo convention — ADR-001
and ADR-002 both live there; ADR-003 continues that numbering/location.

Identified 5 candidate decisions from `research.md` and the implementation:
(1) Python-stdlib server choice, (2) standalone-on-18790 rather than
blocking on the external MCP Gateway, (3) the read-only write/read split,
(4) server-side response enrichment (`tier_color`/`seconds_remaining`
computed in `server.py` rather than duplicated in JS — an implementation
choice made during coding, not pre-specified in `research.md`), and (5) the
`dashboard_workspace_factory` real-temp-directory testing pattern. Applied
the clustering rule: (1)-(4) are tightly coupled — the same "how the
server is built" question — and became one ADR. (5) was evaluated against
the anti-over-granularity check and folded into that same ADR's
Consequences as a corollary rather than a separate ADR, since on its own
it's a smaller methodological choice than warrants full separate treatment
(unlike ADR-002, which was substantial enough alone).

Created `adrs/ADR-003-dashboard-server-architecture.md` (Accepted): Decision
covers the stdlib server, read-only split, 127.0.0.1:18790 deployment
matching the tunnel setup, and server-side enrichment. Consequences
(positive: zero new dependencies, Principle IV made structurally
auditable — paired with the existing frontend guard test for a two-sided
enforced invariant, single source of truth for scoring/timeout formulas,
plus the testing-pattern corollary; negative: unrealized gateway-merge
assumption, basic static-file serving, served response diverges from
stored file). 4 Alternatives Considered (Node/Express, Flask/FastAPI,
blocking on external gateway code, client-side score/timeout computation),
each rejected with reasoning. Explicitly cross-referenced ADR-002 as this
ADR's counterpart — "how do we test this without live calls" for real
file-touching code, versus ADR-002's answer for LLM-agent behavior with no
callable code at all.

Verified against the Measure checklist: clusters multiple components (not
trivial) ✅, ≥1 alternative with rationale ✅ (4 listed), clear pros/cons
✅, concise but detailed ✅. No conflicts with ADR-001 or ADR-002.

## Outcome

- ✅ Impact: ADR-003 created, resolving the Constitution Checker's Q3 FAIL for feature 002-pk-client-dashboard.
- 🧪 Tests: none (documentation-only step).
- 📁 Files: `adrs/ADR-003-dashboard-server-architecture.md`.
- 🔁 Next prompts: re-run the Constitution Checker to confirm Q3 now passes; separately resolve the still-open B2 flag (README question) before the feature is fully clear to merge.
- 🧠 Reflection: explicitly cross-referencing ADR-002 in this ADR's References, and naming why the two are counterparts rather than duplicates, keeps the project's small but growing ADR set legible as a set rather than a pile of unrelated documents.

## Evaluation notes (flywheel)

- Failure modes observed: none.
- Graders run and results (PASS/FAIL): command's own Measure checklist — PASS (4/4 criteria met).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
