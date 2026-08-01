"""FR-010, SC-006: multi-tenant data isolation.

A lead whose tenant_id doesn't match the active session's tenant is
rejected and logged, with no cross-tenant CRM write or notification —
regardless of how high its classification_score is.
"""

from tests.pipeline_sim import process_lead


def test_mismatched_tenant_id_rejected(tenant_context):
    lead = {
        "lead_id": "lead-cross-tenant-001",
        "tenant_id": "pk-some-other-agency-999",
        "source": "zameen_alert",
        "market_mode": "PK",
        "classification_score": 0.99,  # deliberately a slam-dunk auto-tier score
        "raw_source_id": "gmail-msg-cross-tenant-001",
        "classified_at": "2026-08-01T12:00:00+00:00",
    }

    result = process_lead(lead, tenant_context["tenant_id"], processed_ids=[])

    assert result["status"] == "rejected"
    assert result["rejection_reason"] == "tenant_mismatch"
    assert result["crm_write"] is False
    assert result["notification_sent"] is False
