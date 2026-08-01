"""FR-011: run logging, including aborted runs."""

from tests.pipeline_sim import run_heartbeat_cycle

REQUIRED_RUN_LOG_FIELDS = (
    "run_id",
    "tenant_id",
    "started_at",
    "completed_at",
    "leads_found",
    "leads_classified",
    "leads_rejected",
    "crm_writes",
    "notifications_sent",
    "gemini_calls_this_run",
    "errors",
)


def test_run_log_written_for_successful_run(tenant_context):
    lead = {
        "lead_id": "lead-log-001",
        "tenant_id": tenant_context["tenant_id"],
        "source": "zameen_alert",
        "market_mode": "PK",
        "classification_score": 0.95,
        "raw_source_id": "gmail-msg-log-001",
        "classified_at": "2026-08-01T14:00:00+00:00",
    }
    memory_state = {"gemini_today_count": 0, "processed_ids": []}

    outcome = run_heartbeat_cycle(
        tenant_context, memory_state, gmail_leads=[lead], whatsapp_leads=[],
    )
    run_log = outcome["run_log"]

    for field in REQUIRED_RUN_LOG_FIELDS:
        assert field in run_log
    assert run_log["completed_at"] is not None
    assert run_log["leads_found"] == 1
    assert run_log["crm_writes"] == 1
    assert run_log["notifications_sent"] == 1


def test_run_log_written_even_when_aborted_on_quota(tenant_context):
    memory_state = {"gemini_today_count": 18, "processed_ids": []}

    outcome = run_heartbeat_cycle(
        tenant_context, memory_state, gmail_leads=[], whatsapp_leads=[],
    )
    run_log = outcome["run_log"]

    for field in REQUIRED_RUN_LOG_FIELDS:
        assert field in run_log
    assert run_log["completed_at"] is not None
    assert "quota_exhausted" in run_log["errors"]


def test_run_log_written_even_when_aborted_on_hubspot_auth(tenant_context):
    memory_state = {"gemini_today_count": 0, "processed_ids": []}

    outcome = run_heartbeat_cycle(
        tenant_context, memory_state, gmail_leads=[], whatsapp_leads=[],
        hubspot_auth_ok=False,
    )
    run_log = outcome["run_log"]

    for field in REQUIRED_RUN_LOG_FIELDS:
        assert field in run_log
    assert run_log["completed_at"] is not None
    assert "hubspot_auth_failed" in run_log["errors"]
