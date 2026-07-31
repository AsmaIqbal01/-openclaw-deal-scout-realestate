---
id: 0005
title: Fix create-new-feature PowerShell 5.1 compatibility
stage: general
date: 2026-08-01
surface: agent
model: claude-sonnet-5
feature: none
branch: 001-pk-lead-intake-notify
user: Asma
command: (follow-up fix)
labels: [tooling, powershell, bugfix, spec-kit]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/scripts/powershell/create-new-feature.ps1
tests:
 - Verified the fixed Join-Path chain in isolation under this environment's Windows PowerShell 5.1.19041, confirmed correct path output
---

## Prompt

Fix the PowerShell script compatibility issue

## Response snapshot

Grepped every `Join-Path` call across `.specify/scripts/powershell/*.ps1` to
confirm scope: only one call, line 267 of `create-new-feature.ps1`
(`Join-Path $repoRoot 'history' 'prompts' $branchName`), used more than two
arguments — a pwsh-7+-only form. All other calls in the script family already
use the 2-argument form Windows PowerShell 5.1 supports. Rewrote the one
offending line as nested 2-argument calls: `Join-Path (Join-Path (Join-Path
$repoRoot 'history') 'prompts') $branchName`. Verified in isolation (without
re-running the full script, to avoid creating another branch/spec scaffold)
that this produces the correct path under this environment's actual
PowerShell version (5.1.19041.6456).

## Outcome

- ✅ Impact: `/sp.specify` (and any other caller of `create-new-feature.ps1`) will now complete without a manual workaround on Windows PowerShell 5.1.
- 🧪 Tests: isolated Join-Path chain verified to produce the correct nested path under PS 5.1; full script not re-run to avoid a throwaway branch.
- 📁 Files: `.specify/scripts/powershell/create-new-feature.ps1` (1 line changed).
- 🔁 Next prompts: none pending from this fix.
- 🧠 Reflection: scoped the fix narrowly to the one actual incompatibility rather than rewriting the script defensively — the other ~20 Join-Path calls in the same script family were already 5.1-compatible.

## Evaluation notes (flywheel)

- Failure modes observed: original script authored assuming pwsh 7+ semantics for `Join-Path`, silently incompatible with the Windows PowerShell 5.1 actually present in this environment.
- Graders run and results (PASS/FAIL): manual verification — PASS (correct path produced).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
