"""FR-012, FR-013, FR-014, FR-015: failure-path handling."""

from tests.pipeline_sim import process_lead, run_heartbeat_cycle


def test_hubspot_write_retry_then_halt(tenant_context):
    lead = {
        "lead_id": "lead-err-001",
        "tenant_id": tenant_context["tenant_id"],
        "source": "zameen_alert",
        "market_mode": "PK",
        "classification_score": 0.95,
        "raw_source_id": "gmail-msg-err-001",
        "classified_at": "2026-08-01T13:00:00+00:00",
    }

    result = process_lead(
        lead, tenant_context["tenant_id"], processed_ids=[],
        hubspot_outcomes=(False, False),
    )

    assert result["status"] == "halted"
    assert result["hubspot_attempts"] == 2  # initial attempt + exactly one retry
    assert result["crm_write"] is False
    assert result["notification_sent"] is False
    assert result["error"] == "hubspot_write_failed"


def test_whatsapp_send_retry_then_continue(tenant_context):
    lead = {
        "lead_id": "lead-err-002",
        "tenant_id": tenant_context["tenant_id"],
        "source": "zameen_alert",
        "market_mode": "PK",
        "classification_score": 0.95,
        "raw_source_id": "gmail-msg-err-002",
        "classified_at": "2026-08-01T13:05:00+00:00",
    }

    result = process_lead(
        lead, tenant_context["tenant_id"], processed_ids=[],
        hubspot_outcomes=(True,),
        whatsapp_outcomes=(False, False),
    )

    # CRM write still succeeds; notification failure does not roll it back or
    # block the rest of the run — it just fails to notify for this lead.
    assert result["status"] == "auto_dispatched"
    assert result["crm_write"] is True
    assert result["notification_sent"] is False
    assert result["whatsapp_attempts"] == 2


def test_gmail_oauth_failure_partial_degradation(tenant_context):
    gmail_lead = {
        "lead_id": "lead-err-003",
        "tenant_id": tenant_context["tenant_id"],
        "source": "zameen_alert",
        "market_mode": "PK",
        "classification_score": 0.95,
        "raw_source_id": "gmail-msg-err-003",
        "classified_at": "2026-08-01T13:10:00+00:00",
    }
    whatsapp_lead = {
        "lead_id": "lead-err-004",
        "tenant_id": tenant_context["tenant_id"],
        "source": "whatsapp_forward",
        "market_mode": "PK",
        "classification_score": 0.95,
        "raw_source_id": "whatsapp-msg-err-004",
        "classified_at": "2026-08-01T13:11:00+00:00",
    }
    memory_state = {"gemini_today_count": 0, "processed_ids": []}

    outcome = run_heartbeat_cycle(
        tenant_context, memory_state,
        gmail_leads=[gmail_lead], whatsapp_leads=[whatsapp_lead],
        gmail_auth_ok=False,
    )

    assert outcome["aborted"] is False
    assert "gmail_auth_failed" in outcome["run_log"]["errors"]
    assert len(outcome["results"]) == 1
    assert outcome["results"][0]["status"] == "auto_dispatched"  # the WhatsApp lead only


def test_hubspot_auth_failure_aborts_run(tenant_context):
    some_lead = {
        "lead_id": "lead-err-005",
        "tenant_id": tenant_context["tenant_id"],
        "source": "zameen_alert",
        "market_mode": "PK",
        "classification_score": 0.95,
        "raw_source_id": "gmail-msg-err-005",
        "classified_at": "2026-08-01T13:15:00+00:00",
    }
    memory_state = {"gemini_today_count": 0, "processed_ids": []}

    outcome = run_heartbeat_cycle(
        tenant_context, memory_state,
        gmail_leads=[some_lead], whatsapp_leads=[],
        hubspot_auth_ok=False,
    )

    assert outcome["aborted"] is True
    assert outcome["results"] == []
    assert outcome["run_log"]["leads_found"] == 0
    assert "hubspot_auth_failed" in outcome["run_log"]["errors"]
