# DealClaw — Real Estate Edition

> The AI employee that never misses a property lead.

[![Tests](https://img.shields.io/badge/tests-74%20passing-brightgreen)](https://github.com/AsmaIqbal01/openclaw-deal-scout-realestate)
[![Phase](https://img.shields.io/badge/phase-1%20active-orange)](https://github.com/AsmaIqbal01/openclaw-deal-scout-realestate)
[![Spec Score](https://img.shields.io/badge/spec%20score-9.6%2F10%20min-blue)](https://github.com/AsmaIqbal01/openclaw-deal-scout-realestate)

▶️ [Watch live pipeline demo](https://youtube.com/shorts/ZtWuZAr5KUs?si=arSFTtL8kxe2W3Ac)

---

## The Problem

Pakistan and UK estate agents lose serious leads daily — not because leads don't come in, but because no one is watching all the time.

From 4 discovery interviews with Karachi agents (August 2026):

- **0 of 4** agents use any CRM or lead tracking software
- **30–65%** of inquiries are time-wasters — agents have no way to filter fast
- **100%** reply "whenever free" — no urgency system exists
- Average commission lost per missed deal: **Rs 50,000 to millions**

DealClaw fixes this with a always-on AI agent that watches Gmail and WhatsApp, scores every lead, and only surfaces the ones worth the agent's time.

---

## What It Does

Monitors a real estate agent's Gmail inbox, detects property leads using Gemini AI, scores them as serious or not, logs them to CRM, and notifies the agent instantly — zero manual effort required.

```
Gmail (input)
    ↓
Gemini 2.5 Flash (lead classifier + scorer)
    ↓
HubSpot CRM (deal logged automatically)
    ↓
WhatsApp / Discord (agent notified instantly)
    ↓
Email Queue (operator approval gate — HITL)
```

---

## Architecture

| Component | Technology |
|---|---|
| Orchestrator | OpenClaw 2026.7.1 |
| AI Classification | Gemini 2.5 Flash |
| Agent Pattern | Maker (Intake) + Checker (Delivery) |
| CRM | HubSpot Free |
| Channels | WhatsApp (PK) · Discord (UK) |
| Infrastructure cost | Zero |

Sub-agents: 2 active · Custom skills: 8 · ADR trail: complete from day one

---

## Build Progress

| Feature | Status | Tests |
|---|---|---|
| Agent + sub-agent architecture | ✅ Complete | — |
| 8 custom skills | ✅ Complete | — |
| Spec Kit Plus SDD workflow | ✅ Complete | — |
| F001: PK lead intake + notify | ✅ Complete | 28 passing |
| F002: PK client dashboard | ✅ Complete | — |
| F003: Operator approval gate (HITL) | ✅ Complete | 85 passing total |
| F004: Dashboard email draft queue | ✅ Complete | 11 passing |
| Customer discovery — PK + UK forms | ✅ Live | — |
| Phase 1 gate: 3 PK agencies onboarded | 🔨 In progress | — |

---

## Markets

**Phase 1 — Pakistan (validation)**
Karachi estate agencies. Discovery interviews complete. Pilot outreach active.

**Phase 2 — UK (revenue)**
Independent estate agents. Rightmove and Zoopla lead sources. WhatsApp replaced with email + SMS channel.

---

## Built With Discipline

- Spec-driven development — minimum **9.6/10 spec score** before every feature enters the build queue
- Maker/Checker agent pattern enforced on every pipeline step
- Constitution-gated merges — no exceptions
- Full ADR trail from day one
- Zero infrastructure cost constraint maintained throughout

---

## Origin

Built on lessons from [OpenClaw Deal Scout v1](https://github.com/AsmaIqbal01/openclaw-deal-scout) — 489 tests, 7 features shipped, full production pipeline live July 28 2026. Pivoted to real estate vertical after validating the pipeline model end-to-end.

---

## Customer Discovery

Validation-first. Forms built and live before Phase 2 build begins.

- 🇵🇰 [PK Agent Form — Urdu + English](https://docs.google.com/forms/d/e/1FAIpQLSeOkzaAonkDX9yJKmpmzxCa2cqMjCZKwm91oysY5bPxbo3S4w/viewform)
- 🇬🇧 [UK Agent Form — English](https://docs.google.com/forms/d/e/1FAIpQLSfmhtqwQ-fK11aZAItxd0RiEWG0yaOTt3cstR3Dqredpx8iaQ/viewform)
- Interview scripts and form IDs: `/discovery` folder

---

## Built By

**Asma Iqbal** — AI Systems Architect · Solo Founder  
[GitHub](https://github.com/AsmaIqbal01) · [LinkedIn](https://linkedin.com/in/asma-iqbal000/)
