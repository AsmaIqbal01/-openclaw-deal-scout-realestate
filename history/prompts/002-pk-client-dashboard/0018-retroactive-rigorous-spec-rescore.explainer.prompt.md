---
id: 0018
title: Retroactive rigorous spec rescore
stage: explainer
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: 002-pk-client-dashboard
branch: 003-pk-email-approval-gate
user: Asma
command: /sp.specify (retroactive re-audit)
labels: [spec-scorer, audit, retroactive, self-scoring-correction]
links:
  spec: specs/002-pk-client-dashboard/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-pk-client-dashboard/spec.md
tests:
 - none (spec-level fixes only, no implementation changed)
---

## Prompt

Stop F003 work. First go back and run /sp:specify on F002 (pk-client-dashboard) retroactively. Score it against agents/spec-scorer/spec-scorer.md rubric. Show dimension breakdown. Iterate until ≥ 9.6/10. Once F002 scores 9.6, then return to F003 and do the same before any implementation.

## Response snapshot

The original F002 self-score (9.8/10, recorded in PHR 0011) was too
charitable — it applied the spec-template's "no implementation details"
convention as an excuse to skip rubric requirements the rubric doesn't
actually exempt. Re-scored `specs/002-pk-client-dashboard/spec.md`
literally and adversarially against `agents/spec-scorer/spec-scorer.md`:
**7.0/10 — BLOCKED**, with 4 real, quotable gaps:

1. Interface Precision (-0.5): no endpoint/request shape defined anywhere.
2. Error Path Coverage (-1.0): no authentication/access-control discussion
   at all for a multi-tenant data-exposing surface; "network timeout" (a
   rubric-named example) unaddressed.
3. Market Specificity (-1.0): exact lead `source` enum values never
   restated (unlike feature 001); no UI language/locale requirement stated.
4. Test Coverage Intent (-0.5): none of the 3 Independent Tests exercised a
   failure/rejection path — those cases lived only in the separate Edge
   Cases bullets.

Fixed all four directly in `spec.md`: added an "Interface Contract" section
(a table naming the single read request's 4 possible outcomes and their
exact triggers, at a behavior level — no HTTP verbs, staying inside the
spec-template's own constraints); added FR-015 (network-timeout fallback:
show stale data + retry) and FR-016 (explicit, accepted access-boundary
statement — tenant_id + private tunnel URL only, no auth, documented
limitation with a revisit trigger) plus matching edge cases; enumerated the
exact `source` values in FR-009 and added a top-level Language/Locale line;
extended US1's Independent Test with an explicit failure-path check
(unconfigured tenant → "Tenant not configured," zero data leaked).

Rescored after fixes: **10.0/10 — PASS**, all 7 dimensions at full marks.

## Outcome

- ✅ Impact: `specs/002-pk-client-dashboard/spec.md` now has a real, defensible ≥9.6 score, closing 4 gaps a charitable self-review missed (access-control policy, network-timeout handling, exact source enum, locale statement, an explicit failure-path test).
- 🧪 Tests: none run — spec-level correction only; the already-merged implementation (tests/dashboard/server.py) is unaffected, since none of the 4 gaps required changing shipped behavior, only documenting decisions that were already implicitly true in the code (e.g., server.py already has no auth, already has no source-enum ambiguity).
- 📁 Files: `specs/002-pk-client-dashboard/spec.md`.
- 🔁 Next prompts: decide whether/how to commit this retroactive spec correction (it touches a file from an already-merged, already-deleted branch); then repeat the same rigorous audit on F003 before any implementation, per the user's explicit sequencing.
- 🧠 Reflection: self-scoring a spec I just wrote is structurally biased toward charity — I'd unconsciously treat my own reasonable-sounding rationalizations (like "the spec-template forbids this, so partial credit is fine") as satisfying a rubric that doesn't actually grant that exception. An adversarial, literal re-read against the rubric's exact wording caught real gaps a friendlier pass rationalized away.

## Evaluation notes (flywheel)

- Failure modes observed: original self-scoring treated "the spec template says no implementation details" as license to skip Interface Precision requirements the rubric states unconditionally; also treated "this failure mode doesn't apply to my feature" as license to skip it without checking whether an *analogous* mode did apply (auth, network timeout) — both are examples of grading leniency disguised as contextual judgment.
- Graders run and results (PASS/FAIL): literal spec-scorer rubric application — first pass FAIL (7.0/10), second pass PASS (10.0/10) after 4 gaps closed.
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): when self-scoring a just-written spec against a rubric, do it as a genuinely separate pass — re-read the rubric's exact wording line by line and ask "does my spec literally satisfy this," not "can I explain why my spec is fine without this."
