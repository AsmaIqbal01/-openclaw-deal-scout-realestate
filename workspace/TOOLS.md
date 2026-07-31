# TOOLS.md — MCP Tools & Skill Manifest

## ClawHub Skills (install before first run)
```bash
openclaw skills install agent-rate-limiter    # Gemini quota throttle
openclaw skills install agent-memory          # Cross-session lead memory
openclaw skills install honcho-setup          # Persistent MEMORY.md spine
openclaw skills install agent-task-tracker    # Pipeline task state
openclaw skills install agent-dashboard       # Dashboard base
openclaw skills install agentmail-integration # Gmail agent inbox
openclaw skills install action-suggester      # Follow-up actions from leads
openclaw skills install apollo                # UK lead enrichment (Phase 2 only)
openclaw skills install brevo                 # Email send fallback
openclaw skills install before-you-build      # Pre-spec risk check (dev-time)
```

## Custom Skills (in /skills/)
| Skill | Invoked By | Market |
|---|---|---|
| `zameen-parser.md` | Intake Sub-Agent | PK only |
| `pk-whatsapp-lead.md` | Intake Sub-Agent | PK only |
| `rightmove-parser.md` | Intake Sub-Agent | UK only |
| `lead-classifier-pk.md` | Intake Sub-Agent | PK only |
| `lead-classifier-uk.md` | Intake Sub-Agent | UK only |
| `multi-tenant-router.md` | Orchestrator | Both |
| `operator-approval-gate.md` | Delivery Sub-Agent | Both |
| `remote-dashboard.md` | Orchestrator | Both |

## External APIs
| API | Free Tier Limit | Used By | Key Storage |
|---|---|---|---|
| Gemini 2.5 Flash | 20 req/day | Intake Sub-Agent | `GEMINI_API_KEY` env var |
| HubSpot | Free CRM tier | Delivery Sub-Agent | `HUBSPOT_API_KEY` env var |
| Gmail OAuth | Unlimited | Intake Sub-Agent | OAuth token in `~/.openclaw/workspace/` |
| WhatsApp (OpenClaw) | Built-in | Orchestrator + Delivery | OpenClaw channel config |
| Discord (OpenClaw) | Built-in | Delivery Sub-Agent (UK) | OpenClaw channel config |
| Cloudflare Tunnel | Free | remote-dashboard skill | No key needed |

## MCP Gateway
Existing MCP Gateway from Deal Scout v1 (port 18790) — retain and extend.
6 existing tools remain active. New tools added per feature spec.

## Tool Priority Rule
Always use existing ClawHub skill before building custom.
Always use OpenClaw built-in channel before using external API.
Never add a paid tool without constitution gate I2 approval.
