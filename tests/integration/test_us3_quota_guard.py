"""User Story 3 (P3): reliable operation within the free Gemini quota.

Covers Acceptance Scenarios 1-2 (FR-009).
"""

from tests.pipeline_sim import run_heartbeat_cycle, quota_guard


def test_quota_boundary_halts_pipeline(load_fixture, tenant_context):
    quota_fixture = load_fixture("memory/quota_at_18.json")
    memory_state = {
        "gemini_today_count": quota_fixture["gemini_today_count"],
        "processed_ids": quota_fixture["processed_ids"],
    }

    some_lead = {
        "lead_id": "lead-us3-001",
        "tenant_id": tenant_context["tenant_id"],
        "source": "whatsapp_forward",
        "market_mode": "PK",
        "classification_score": 0.95,
        "raw_source_id": "whatsapp-msg-us3-001",
        "classified_at": "2026-08-01T11:00:00+00:00",
    }

    outcome = run_heartbeat_cycle(
        tenant_context, memory_state, gmail_leads=[], whatsapp_leads=[some_lead],
    )

    assert outcome["aborted"] is True
    assert outcome["quota_exhausted"] is True
    assert outcome["owner_alerts"] == 1
    assert outcome["results"] == []
    assert outcome["run_log"]["gemini_calls_this_run"] == 0
    assert "quota_exhausted" in outcome["run_log"]["errors"]


def test_quota_low_warning_only(load_fixture):
    quota_fixture = load_fixture("memory/quota_at_16.json")
    result = quota_guard(quota_fixture["gemini_today_count"])

    assert result["halt"] is False
    assert result["quota_exhausted"] is False
    assert result["warning"] == "quota low: 16/20 used"
