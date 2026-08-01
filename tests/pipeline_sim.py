"""Test-only simulation of the Deal Scout PK pipeline decision rules.

This module is NOT production agent logic — per specs/001-pk-lead-intake-notify/
research.md Decision 1, the Orchestrator/Intake/Delivery agents are OpenClaw
agents whose real behavior lives in agents/*/SOUL.md and skills/*.md,
interpreted by the OpenClaw runtime. There is no way to exercise that runtime
from a `pytest` process without a live OpenClaw session, Gemini call, or
HubSpot/WhatsApp API call — which this test suite must not make (zero-cost
constraint, quota guard).

So this module re-implements the exact thresholds and control flow already
documented in agents/intake/SOUL.md, agents/delivery/SOUL.md,
workspace/HEARTBEAT.md, and skills/*.md, purely so those documented rules are
machine-checked against fixtures. If a threshold changes in the SOUL.md/skill
files, it MUST change here too, and vice versa — this is exactly the kind of
drift /sp.analyze finding I1 caught between intake/SOUL.md and
delivery/SOUL.md before this module existed.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

# --- Thresholds (must mirror agents/intake/SOUL.md, agents/delivery/SOUL.md) ---

GEMINI_DAILY_LIMIT = 20
GEMINI_QUOTA_HALT_THRESHOLD = 18  # workspace/HEARTBEAT.md, constitution Principle VI
GEMINI_QUOTA_LOW_THRESHOLD = 15  # workspace/HEARTBEAT.md "quota low" warning band

TIER_AUTO_MIN = 0.9  # FR-005
TIER_REVIEW_MIN = 0.7  # FR-003/FR-006 boundary (corrected, /sp.analyze finding I1)

APPROVAL_TIMEOUT_HOURS = 2  # FR-008

REQUIRED_LEAD_FIELDS = (
    "lead_id",
    "tenant_id",
    "source",
    "market_mode",
    "classification_score",
    "raw_source_id",
    "classified_at",
)

ZAMEEN_SENDER_DOMAINS = {"zameen.com", "alerts.zameen.com"}
OLX_SENDER_DOMAINS = {"olx.com.pk", "alerts.olx.com.pk"}
ZAMEEN_SUBJECT_MARKERS = ("New listing", "Property Alert", "New property", "نئی جائیداد")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --- FR-003/FR-005/FR-006: tier classification ---

def classify_tier(score: float) -> str:
    """Returns 'auto' (>=0.9), 'review' (0.70-0.89), or 'reject' (<0.70)."""
    if score >= TIER_AUTO_MIN:
        return "auto"
    if score >= TIER_REVIEW_MIN:
        return "review"
    return "reject"


# --- FR-009: Gemini quota guard ---

def quota_guard(gemini_today_count: int) -> dict:
    if gemini_today_count >= GEMINI_QUOTA_HALT_THRESHOLD:
        return {"halt": True, "quota_exhausted": True, "warning": None}
    if gemini_today_count >= GEMINI_QUOTA_LOW_THRESHOLD:
        return {
            "halt": False,
            "quota_exhausted": False,
            "warning": f"quota low: {gemini_today_count}/{GEMINI_DAILY_LIMIT} used",
        }
    return {"halt": False, "quota_exhausted": False, "warning": None}


# --- FR-004: schema + dedup + FR-010: tenant isolation ---

def missing_required_fields(lead: dict) -> list:
    return [f for f in REQUIRED_LEAD_FIELDS if lead.get(f) is None]


def is_duplicate(raw_source_id: str, processed_ids: list) -> bool:
    return raw_source_id in processed_ids


def tenant_matches(lead_tenant_id: str, session_tenant_id: str) -> bool:
    return lead_tenant_id == session_tenant_id


# --- FR-001: intake trigger/routing ---

def match_intake_source(*, is_whatsapp: bool, sender_domain: str | None = None,
                         subject: str = "") -> str | None:
    """Mirrors skills/zameen-parser.md and skills/pk-whatsapp-lead.md triggers.
    Returns the lead 'source' value, or None if no PK skill would trigger."""
    if is_whatsapp:
        return "whatsapp_forward"
    if sender_domain in OLX_SENDER_DOMAINS:
        return "olx_alert"
    if sender_domain in ZAMEEN_SENDER_DOMAINS or any(m in subject for m in ZAMEEN_SUBJECT_MARKERS):
        return "zameen_alert"
    return None


# --- FR-012/FR-013: retry-once-then-give-up helper ---

def _attempt_with_one_retry(outcomes) -> tuple:
    """outcomes: sequence of booleans for attempt 1, attempt 2 (retry).
    Returns (final_ok, attempts_made). Never makes more than 2 attempts."""
    outcomes = list(outcomes)
    if outcomes and outcomes[0]:
        return True, 1
    if len(outcomes) > 1 and outcomes[1]:
        return True, 2
    return False, min(len(outcomes), 2)


# --- FR-005/006/007/008: Delivery Sub-Agent decision + action ---

def process_lead(
    lead: dict,
    session_tenant_id: str,
    processed_ids: list,
    *,
    hubspot_outcomes=(True,),
    whatsapp_outcomes=(True,),
) -> dict:
    """Full Delivery Sub-Agent decision for one lead: validate, dedup, tenant
    check, then tier-dispatch. Returns a result dict with at least 'status',
    'crm_write', 'notification_sent'."""
    missing = missing_required_fields(lead)
    if missing:
        return {
            "status": "rejected",
            "rejection_reason": f"missing_required_field:{missing[0]}",
            "crm_write": False,
            "notification_sent": False,
        }
    if not tenant_matches(lead["tenant_id"], session_tenant_id):
        return {
            "status": "rejected",
            "rejection_reason": "tenant_mismatch",
            "crm_write": False,
            "notification_sent": False,
        }
    if is_duplicate(lead["raw_source_id"], processed_ids):
        return {
            "status": "rejected",
            "rejection_reason": "duplicate_raw_source_id",
            "crm_write": False,
            "notification_sent": False,
        }

    tier = classify_tier(lead["classification_score"])

    if tier == "reject":
        return {
            "status": "rejected",
            "rejection_reason": lead.get("rejection_reason") or "low_score",
            "crm_write": False,
            "notification_sent": False,
        }

    if tier == "review":
        return {
            "status": "held_for_review",
            "crm_write": False,
            "notification_sent": False,
            "owner_message": f"Review needed — score {lead['classification_score']}",
        }

    # tier == "auto"
    crm_ok, hubspot_attempts = _attempt_with_one_retry(hubspot_outcomes)
    if not crm_ok:
        return {
            "status": "halted",
            "crm_write": False,
            "notification_sent": False,
            "hubspot_attempts": hubspot_attempts,
            "error": "hubspot_write_failed",
        }
    wa_ok, wa_attempts = _attempt_with_one_retry(whatsapp_outcomes)
    return {
        "status": "auto_dispatched",
        "crm_write": True,
        "notification_sent": wa_ok,
        "hubspot_attempts": hubspot_attempts,
        "whatsapp_attempts": wa_attempts,
        "notification_message": (f"🔴 URGENT — lead {lead.get('lead_id')}" if wa_ok else None),
    }


def dispatch_confirmed_review(lead: dict, *, hubspot_outcomes=(True,), whatsapp_outcomes=(True,)) -> dict:
    """FR-007: after an owner /confirm on a held-for-review lead, write CRM and
    send the STANDARD (non-URGENT) notification."""
    crm_ok, hubspot_attempts = _attempt_with_one_retry(hubspot_outcomes)
    if not crm_ok:
        return {"status": "halted", "crm_write": False, "notification_sent": False,
                "hubspot_attempts": hubspot_attempts, "error": "hubspot_write_failed"}
    wa_ok, wa_attempts = _attempt_with_one_retry(whatsapp_outcomes)
    return {
        "status": "confirmed_dispatched",
        "crm_write": True,
        "notification_sent": wa_ok,
        "hubspot_attempts": hubspot_attempts,
        "whatsapp_attempts": wa_attempts,
        "notification_message": (f"lead {lead.get('lead_id')}" if wa_ok else None),
    }


# --- contracts/approval-commands.md: Tier 2 owner reply contract ---

def resolve_approval_reply(
    entry: dict,
    *,
    reply_command: str,
    reply_lead_id: str,
    reply_from_number: str,
    hours_since_queued: float,
) -> str:
    """entry: {'lead_id', 'tenant_agent_whatsapp'}. Returns one of:
    'confirmed', 'discarded', 'owner_no_response', 'unknown_lead_id_reply',
    'unauthorized_reply_source', 'pending'."""
    if reply_from_number != entry["tenant_agent_whatsapp"]:
        return "unauthorized_reply_source"
    if reply_lead_id != entry["lead_id"]:
        return "unknown_lead_id_reply"
    if reply_command == "/confirm":
        return "confirmed"
    if reply_command == "/discard":
        return "discarded"
    if hours_since_queued >= APPROVAL_TIMEOUT_HOURS:
        return "owner_no_response"
    return "pending"


def check_timeout(hours_since_queued: float) -> str:
    return "owner_no_response" if hours_since_queued >= APPROVAL_TIMEOUT_HOURS else "pending"


# --- FR-011: run logging ---

def new_run_log(tenant_id: str) -> dict:
    return {
        "run_id": str(uuid.uuid4()),
        "tenant_id": tenant_id,
        "started_at": now_iso(),
        "completed_at": None,
        "leads_found": 0,
        "leads_classified": 0,
        "leads_rejected": 0,
        "crm_writes": 0,
        "notifications_sent": 0,
        "gemini_calls_this_run": 0,
        "errors": [],
    }


def close_run_log(run_log: dict) -> dict:
    run_log["completed_at"] = now_iso()
    return run_log


# --- FR-014/FR-015: auth failure handling at the heartbeat level ---

def run_heartbeat_cycle(
    tenant: dict,
    memory_state: dict,
    gmail_leads: list,
    whatsapp_leads: list,
    *,
    gmail_auth_ok: bool = True,
    hubspot_auth_ok: bool = True,
    hubspot_outcomes=(True,),
    whatsapp_outcomes=(True,),
) -> dict:
    """Simulates one full heartbeat run's Gmail/WhatsApp intake + Delivery
    dispatch for a tenant, honoring the quota guard and auth-failure edge
    cases (FR-014, FR-015) at the run level."""
    run_log = new_run_log(tenant["tenant_id"])

    if not hubspot_auth_ok:
        # FR-015: pre-flight reachability check fails -> abort before any leads
        run_log["errors"].append("hubspot_auth_failed")
        close_run_log(run_log)
        return {"aborted": True, "results": [], "owner_alerts": 0, "run_log": run_log}

    quota = quota_guard(memory_state["gemini_today_count"])
    if quota["halt"]:
        run_log["errors"].append("quota_exhausted")
        close_run_log(run_log)
        return {"aborted": True, "quota_exhausted": True, "owner_alerts": 1, "run_log": run_log, "results": []}

    sources = []
    if gmail_auth_ok:
        sources.extend(gmail_leads)
    else:
        # FR-014: skip Gmail source only, continue with WhatsApp-sourced leads
        run_log["errors"].append("gmail_auth_failed")
    sources.extend(whatsapp_leads)

    results = []
    for lead in sources:
        run_log["leads_found"] += 1
        run_log["gemini_calls_this_run"] += 1
        result = process_lead(
            lead,
            tenant["tenant_id"],
            memory_state["processed_ids"],
            hubspot_outcomes=hubspot_outcomes,
            whatsapp_outcomes=whatsapp_outcomes,
        )
        run_log["leads_classified"] += 1
        if result["status"] == "rejected":
            run_log["leads_rejected"] += 1
        if result.get("crm_write"):
            run_log["crm_writes"] += 1
        if result.get("notification_sent"):
            run_log["notifications_sent"] += 1
        results.append(result)

    close_run_log(run_log)
    return {"aborted": False, "quota_warning": quota["warning"], "results": results, "run_log": run_log}
