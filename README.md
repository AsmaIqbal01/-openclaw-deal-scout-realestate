# Deal Scout — Real Estate Edition

> The AI employee that never misses a property lead.

## Status: Active Development — Phase 1 🔨
Spec-driven build. Every feature scored ≥ 9.6/10 before implementation.

## What It Does
Monitors a real estate agent's Gmail and WhatsApp, detects property 
leads using Gemini AI, logs them to HubSpot CRM, and notifies the 
agent instantly via WhatsApp — zero manual effort.

## Markets
- **PK Real Estate** (Phase 1 — validating now): Karachi, Lahore, Islamabad agencies
- **UK Estate Agents** (Phase 2 — revenue): Independent agencies, Rightmove/Zoopla leads

## Architecture
- Orchestrator: OpenClaw 2026.7.1
- AI Classification: Gemini 2.5 Flash
- CRM: HubSpot Free
- Channels: WhatsApp (PK) + Discord (UK)
- Infrastructure cost: £0

## Progress
- [x] Agent/sub-agent architecture defined
- [x] 8 custom skills implemented  
- [x] F001: PK lead intake + notify (28 tests passing)
- [x] F002: PK client dashboard
- [ ] F003: Operator approval gate (in progress)
- [ ] Phase 1 gate: 3 PK agencies live

## Pilot
Outreach in progress — PK estate agencies in Karachi being onboarded.

## Built With Discipline
- Spec-driven development (min 9.6/10 spec score)
- Maker/Checker agent pattern
- Constitution-gated merges
- Full ADR trail

## Built By
Asma Iqbal — AI Systems Architect  
GitHub: [@AsmaIqbal01](https://github.com/AsmaIqbal01)  
Instagram: [@azeecreations000](https://instagram.com/azeecreations000)
