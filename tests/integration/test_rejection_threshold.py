"""FR-003/FR-006 boundary (/sp.analyze finding I1).

agents/intake/SOUL.md now rejects any classification_score < 0.7 (moved from
the old, contradictory < 0.5 threshold) so it agrees with
agents/delivery/SOUL.md's Tier 3 boundary. This test proves the merged
rejection band (including the former 0.5-0.69 "possible lead" band) is
enforced exactly at 0.70, with nothing in between falling through
unhandled.
"""

from tests.pipeline_sim import classify_tier, process_lead


def test_below_0_70_rejected_by_intake(load_fixture, tenant_context):
    boundary_scores = load_fixture("gemini/rejection_boundary_responses.json")
    by_score = {round(entry["classification_score"], 2): entry for entry in boundary_scores}

    assert classify_tier(by_score[0.65]["classification_score"]) == "reject"
    assert classify_tier(by_score[0.69]["classification_score"]) == "reject"
    assert classify_tier(by_score[0.70]["classification_score"]) == "review"

    for score in (0.65, 0.69):
        lead = {
            "lead_id": f"lead-{score}",
            "tenant_id": tenant_context["tenant_id"],
            "source": "whatsapp_forward",
            "market_mode": "PK",
            "classification_score": score,
            "raw_source_id": f"whatsapp-msg-{score}",
            "classified_at": "2026-08-01T09:00:00+00:00",
        }
        result = process_lead(lead, tenant_context["tenant_id"], processed_ids=[])
        assert result["status"] == "rejected"
        assert result["crm_write"] is False
        assert result["notification_sent"] is False

    lead_at_boundary = {
        "lead_id": "lead-0.70",
        "tenant_id": tenant_context["tenant_id"],
        "source": "whatsapp_forward",
        "market_mode": "PK",
        "classification_score": 0.70,
        "raw_source_id": "whatsapp-msg-0.70",
        "classified_at": "2026-08-01T09:00:00+00:00",
    }
    result = process_lead(lead_at_boundary, tenant_context["tenant_id"], processed_ids=[])
    assert result["status"] == "held_for_review"
    assert result["crm_write"] is False
