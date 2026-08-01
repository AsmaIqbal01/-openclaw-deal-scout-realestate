"""User Story 1 (P1): instant notification for a high-confidence lead.

Covers Acceptance Scenarios 1-2, FR-005 ordering, FR-004 dedup, and FR-001
intake trigger/routing (/sp.analyze finding G1).
"""

from tests.pipeline_sim import process_lead, match_intake_source


def _parse_email_headers(raw_email: str) -> dict:
    headers = {}
    for line in raw_email.splitlines():
        if line.startswith("From: "):
            headers["from"] = line[len("From: "):].strip()
        elif line.startswith("Subject: "):
            headers["subject"] = line[len("Subject: "):].strip()
    return headers


def _sender_domain(from_header: str) -> str:
    return from_header.split("@")[-1].strip().rstrip(">")


def test_zameen_email_auto_dispatch(load_fixture, load_text_fixture, tenant_context):
    load_text_fixture("emails/zameen_alert_high_confidence.txt")  # confirms fixture is readable
    gemini = load_fixture("gemini/high_confidence_response.json")

    lead = {
        "lead_id": "lead-us1-001",
        "tenant_id": tenant_context["tenant_id"],
        "source": "zameen_alert",
        "market_mode": "PK",
        "classification_score": gemini["classification_score"],
        "raw_source_id": "gmail-msg-us1-001",
        "classified_at": "2026-08-01T09:00:00+00:00",
    }

    result = process_lead(lead, tenant_context["tenant_id"], processed_ids=[])

    assert result["status"] == "auto_dispatched"
    assert result["crm_write"] is True
    assert result["notification_sent"] is True
    assert result["notification_message"].startswith("🔴 URGENT — ")


def test_whatsapp_forward_auto_dispatch(load_fixture, load_text_fixture, tenant_context):
    load_text_fixture("whatsapp/whatsapp_forward_high_confidence.txt")
    gemini = load_fixture("gemini/high_confidence_response.json")

    lead = {
        "lead_id": "lead-us1-002",
        "tenant_id": tenant_context["tenant_id"],
        "source": "whatsapp_forward",
        "market_mode": "PK",
        "classification_score": gemini["classification_score"],
        "raw_source_id": "whatsapp-msg-us1-002",
        "classified_at": "2026-08-01T09:05:00+00:00",
    }

    result = process_lead(lead, tenant_context["tenant_id"], processed_ids=[])

    assert result["status"] == "auto_dispatched"
    assert result["crm_write"] is True
    assert result["notification_sent"] is True
    assert result["notification_message"].startswith("🔴 URGENT — ")


def test_auto_dispatch_order(tenant_context):
    """The CRM write must be confirmed before any notification is attempted.
    Simulated by forcing the HubSpot write to fail twice (initial + retry):
    the notification must never be attempted in that case."""
    lead = {
        "lead_id": "lead-us1-003",
        "tenant_id": tenant_context["tenant_id"],
        "source": "zameen_alert",
        "market_mode": "PK",
        "classification_score": 0.95,
        "raw_source_id": "gmail-msg-us1-003",
        "classified_at": "2026-08-01T09:10:00+00:00",
    }

    result = process_lead(
        lead, tenant_context["tenant_id"], processed_ids=[],
        hubspot_outcomes=(False, False),
    )

    assert result["status"] == "halted"
    assert result["crm_write"] is False
    assert result["notification_sent"] is False


def test_duplicate_raw_source_id_rejected(tenant_context):
    lead = {
        "lead_id": "lead-us1-004",
        "tenant_id": tenant_context["tenant_id"],
        "source": "zameen_alert",
        "market_mode": "PK",
        "classification_score": 0.95,
        "raw_source_id": "gmail-msg-us1-004-dup",
        "classified_at": "2026-08-01T09:15:00+00:00",
    }

    result = process_lead(
        lead, tenant_context["tenant_id"],
        processed_ids=["gmail-msg-us1-004-dup"],
    )

    assert result["status"] == "rejected"
    assert result["rejection_reason"] == "duplicate_raw_source_id"
    assert result["crm_write"] is False
    assert result["notification_sent"] is False


def test_intake_routing_by_source(load_text_fixture):
    zameen_email = load_text_fixture("emails/zameen_alert_high_confidence.txt")
    headers = _parse_email_headers(zameen_email)
    source = match_intake_source(
        is_whatsapp=False,
        sender_domain=_sender_domain(headers["from"]),
        subject=headers["subject"],
    )
    assert source == "zameen_alert"

    whatsapp_source = match_intake_source(is_whatsapp=True)
    assert whatsapp_source == "whatsapp_forward"

    non_pk_email = load_text_fixture("emails/non_pk_unrelated.txt")
    non_pk_headers = _parse_email_headers(non_pk_email)
    no_match = match_intake_source(
        is_whatsapp=False,
        sender_domain=_sender_domain(non_pk_headers["from"]),
        subject=non_pk_headers["subject"],
    )
    assert no_match is None
