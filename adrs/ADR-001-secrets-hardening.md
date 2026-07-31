# ADR-001: Secrets Hardening Deferred

## Status
OPEN — known issue, not a blocker

## Context
OpenClaw 2026.6.33 stores gateway.auth.token, discord.token, and Google API key
as plaintext in openclaw.json and SQLite. SecretRef migration attempted but
OpenClaw config schema rejected the format.

## Decision
Defer to Phase 2 (UK onboarding). Mitigations in place:
- ~/.openclaw permissions set to 700 (done via doctor)
- Secrets not committed to git
- Discord token to be regenerated (exposed in chat session)

## Action Items
- [ ] Regenerate Discord token in Discord Developer Portal
- [ ] Revisit openclaw secrets apply command (different from secrets configure)
- [ ] Add .openclaw to .gitignore

## Date
2026-08-01
