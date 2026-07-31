# AGENTS.md — Sub-Agent Registry & Routing Rules

## Agent Registry

| Agent | File | Role | Pattern |
|---|---|---|---|
| Orchestrator | `agents/orchestrator/SOUL.md` | Master coordinator, heartbeat, routing | Always active |
| Intake Sub-Agent | `agents/intake/SOUL.md` | Inbox reader + Gemini classifier | Maker |
| Delivery Sub-Agent | `agents/delivery/SOUL.md` | CRM writer + notifier | Checker |
| Spec Scorer | `agents/spec-scorer/spec-scorer.md` | Score specs before build | Dev-time only |
| Constitution Checker | `agents/constitution-checker/constitution-checker.md` | Gate before merge | Dev-time only |

## Routing Rules

### Pipeline Routing (runtime)
```
Orchestrator
  → reads USER.md (multi-tenant-router skill)
  → reads Gmail + WhatsApp
  → Intake Sub-Agent (zameen-parser OR rightmove-parser + classifier)
  → [if score ≥ 0.7] → Delivery Sub-Agent (validate → CRM → notify → queue)
  → [if score < 0.7] → log rejection, skip Delivery
  → Orchestrator updates MEMORY.md + dashboard state
```

### Dev-Time Routing (not in production pipeline)
```
Developer writes spec
  → Spec Scorer (score ≥ 9.6 required)
  → [PASS] → /sp.plan → ADR → /sp.tasks → implementation
  → Constitution Checker (PASS required)
  → [PASS] → git merge
```

## Agent Communication Rules
1. Sub-agents communicate via structured JSON only — no natural language between agents
2. Orchestrator is the only agent that reads/writes MEMORY.md directly
3. Intake passes output to Delivery via Orchestrator — never directly
4. Spec Scorer and Constitution Checker are stateless — no MEMORY.md access
5. No sub-agent may invoke another sub-agent directly — all routing via Orchestrator

## Maker/Checker Contract
- Intake (Maker): produces lead JSON, never acts on it
- Delivery (Checker): validates Intake output, rejects if schema invalid, then acts
- If Delivery rejects: Orchestrator logs, notifies owner, does not retry automatically
