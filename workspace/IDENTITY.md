# IDENTITY.md — Deal Scout Real Estate

## Product Name
Deal Scout — Real Estate Edition

## Tagline
The AI employee that never misses a property lead.

## What This Product Is
An autonomous AI pipeline that monitors a real estate agent's Gmail and WhatsApp,
identifies property leads using Gemini 2.5 Flash, logs them to HubSpot CRM,
and notifies the agent instantly — with zero manual effort.

## What This Product Is Not
- Not a property portal or listing aggregator
- Not a CRM replacement — it feeds the CRM
- Not a chatbot — agents do not interact with it conversationally
- Not a scraper — all data comes from authorised inboxes

## Primary Market (Phase 1 — Validate)
Pakistani real estate agents and small agencies in Karachi, Lahore, Islamabad.
Pain: Zameen/OLX alert emails and WhatsApp forwards get buried. Leads go cold.
Price point: Free during validation. Target: 3 agencies confirmed before UK launch.

## Secondary Market (Phase 2 — Revenue)
UK independent estate agents (sub-5-staff agencies).
Pain: Rightmove/Zoopla lead emails missed during busy periods. Commission lost.
Price point: £X/month/client (TBD after PK validation).

## Zero Cost Constraint
No paid APIs. No paid hosting. No paid infrastructure. This is a hard constraint, not a preference.
Gemini free tier: 20 requests/day — treat as a fixed limit, build around it.
HubSpot free tier: pipeline + contacts — sufficient for validation stage.
Cloudflare Tunnel: free — sufficient for remote dashboard access.

## Engineering Rigor & Delivery Discipline
Every ADR, every spec, every commit is evidence of rigorous, auditable process —
required because this pipeline handles real client data for paying agencies,
not because it is being showcased.
Maintain clean commit history. Write ADRs for every architectural decision.
This repo is a client-delivery codebase held to production-quality standards.
