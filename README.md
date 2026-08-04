# Deal Scout — Real Estate Edition

> The AI employee that never misses a property lead.

## Demo
▶️ [Watch live pipeline demo](https://youtube.com/shorts/ZtWuZAr5KUs?si=arSFTtL8kxe2W3Ac)

## Status: Active Development — Phase 1 🔨

Spec-driven build. Every feature scored minimum 9.6/10 before implementation.

## What It Does

Monitors a real estate agent's Gmail and WhatsApp, detects property
leads using Gemini AI, logs them to HubSpot CRM, and notifies the
agent instantly via WhatsApp — zero manual effort required.

## Markets

- PK Real Estate (Phase 1 — validating now): Karachi, Lahore, Islamabad agencies
- UK Estate Agents (Phase 2 — revenue): Independent agencies, Rightmove and Zoopla leads

## PipelineGmail + WhatsApp (input)
↓
Gemini AI (lead classifier)
↓
HubSpot Free CRM (deal logged)
↓
WhatsApp/Discord (agent notified)
↓
Email Queue (operator approval gate)


## Architecture

- Orchestrator: OpenClaw 2026.7.1
- AI Classification: Gemini 2.5 Flash
- Sub-agents: Intake (Maker) + Delivery (Checker)
- CRM: HubSpot Free
- Channels: WhatsApp (PK) + Discord (UK)
- Infrastructure cost: zero

## Progress

- [x] Agent and sub-agent architecture defined
- [x] 8 custom skills implemented
- [x] Spec Kit Plus SDD workflow configured
- [x] F001: PK lead intake and notify (28 tests passing)
- [x] F002: PK client dashboard
- [x] F003: Operator email draft and approval gate (74 tests passing total)
- [x] Customer discovery forms live — PK and UK markets
- [ ] Phase 1 gate: 3 PK agencies live

## Built With Discipline

- Spec-driven development — minimum 9.6/10 spec score before every build
- Maker/Checker agent pattern enforced
- Constitution-gated merges — no exceptions
- Full ADR trail from day one
- Zero infrastructure cost constraint maintained throughout

## Origin

Built on lessons from OpenClaw Deal Scout v1 (489 tests, 7 features shipped).
Pivoted to real estate after validating the pipeline model with UK micro-businesses.

Origin project: https://github.com/AsmaIqbal01/openclaw-deal-scout

## Pilot

Outreach in progress — PK estate agencies in Karachi being onboarded.

## Customer Discovery
Validation forms built and live before Phase 2 build begins.

- PK Agent Form (Urdu + English): https://docs.google.com/forms/d/e/1FAIpQLSe.../viewform
- UK Agent Form (English): https://docs.google.com/forms/d/e/1FAIpQLSfmhtqwQ-fK11aZAItxd0RiEWG0yaOTt3cstR3Dqredpx8iaQ/viewform
- Scripts and form IDs: /discovery folder

## Built By

Asma Iqbal — AI Systems Architect
GitHub: https://github.com/AsmaIqbal01

