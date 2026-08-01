"""User Story 2 (P2): human review for a medium-confidence lead.

Covers Acceptance Scenarios 1-3 (FR-006, FR-007, FR-008).
"""

from tests.pipeline_sim import (
    process_lead,
    dispatch_confirmed_review,
    resolve_approval_reply,
    check_timeout,
)


def _medium_lead(tenant_id: str, score: float) -> dict:
    return {
        "lead_id": "lead-us2-100",
        "tenant_id": tenant_id,
        "source": "whatsapp_forward",
        "market_mode": "PK",
        "classification_score": score,
        "raw_source_id": "whatsapp-msg-us2-100",
        "classified_at": "2026-08-01T10:00:00+00:00",
    }


def test_medium_score_holds_for_review(load_fixture, tenant_context):
    gemini = load_fixture("gemini/medium_confidence_response.json")
    lead = _medium_lead(tenant_context["tenant_id"], gemini["classification_score"])

    result = process_lead(lead, tenant_context["tenant_id"], processed_ids=[])

    assert result["status"] == "held_for_review"
    assert result["crm_write"] is False
    assert result["notification_sent"] is False
    assert result["owner_message"] == f"Review needed — score {gemini['classification_score']}"


def test_confirm_within_window_dispatches(tenant_context):
    entry = {"lead_id": "lead-us2-100", "tenant_agent_whatsapp": tenant_context["agent_whatsapp"]}

    reply_outcome = resolve_approval_reply(
        entry,
        reply_command="/confirm",
        reply_lead_id="lead-us2-100",
        reply_from_number=tenant_context["agent_whatsapp"],
        hours_since_queued=1.0,
    )
    assert reply_outcome == "confirmed"

    lead = _medium_lead(tenant_context["tenant_id"], 0.80)
    result = dispatch_confirmed_review(lead)

    assert result["status"] == "confirmed_dispatched"
    assert result["crm_write"] is True
    assert result["notification_sent"] is True
    # Standard notification, NOT the auto-tier's URGENT prefix
    assert "URGENT" not in result["notification_message"]


def test_discard_or_timeout_blocks(tenant_context):
    entry = {"lead_id": "lead-us2-100", "tenant_agent_whatsapp": tenant_context["agent_whatsapp"]}

    discard_outcome = resolve_approval_reply(
        entry,
        reply_command="/discard",
        reply_lead_id="lead-us2-100",
        reply_from_number=tenant_context["agent_whatsapp"],
        hours_since_queued=0.25,
    )
    assert discard_outcome == "discarded"

    timeout_outcome = check_timeout(hours_since_queued=2.5)
    assert timeout_outcome == "owner_no_response"

    timeout_not_yet = check_timeout(hours_since_queued=1.9)
    assert timeout_not_yet == "pending"
