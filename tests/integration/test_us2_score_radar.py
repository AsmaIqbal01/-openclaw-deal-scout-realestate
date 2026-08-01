"""User Story 2 (P2): understand why a lead scored what it scored.

Covers Acceptance Scenarios 1-2 (FR-010).
"""

from dashboard.server import handle_state_request


def test_high_score_lead_radar_teal(load_fixture, dashboard_workspace_factory):
    normal_state = load_fixture("dashboard/normal_state.json")
    workspace_root = dashboard_workspace_factory(
        {"pk-test-agency-001": {"state": normal_state}}
    )

    result = handle_state_request("pk-test-agency-001", workspace_root)
    high_score_lead = next(
        lead for lead in result["data"]["recent_leads"] if lead["classification_score"] == 0.95
    )

    radar = high_score_lead["radar"]
    for axis in ("contact_completeness", "intent_clarity", "budget_signal", "urgency", "data_integrity"):
        assert 0.0 <= radar[axis] <= 1.0
    assert radar["data_integrity"] == 1.0
    assert high_score_lead["tier_color"] == "teal"
    assert high_score_lead["recommended_action"] == "call_now"


def test_medium_score_lead_with_warning_radar_amber(load_fixture, dashboard_workspace_factory):
    normal_state = load_fixture("dashboard/normal_state.json")
    workspace_root = dashboard_workspace_factory(
        {"pk-test-agency-001": {"state": normal_state}}
    )

    result = handle_state_request("pk-test-agency-001", workspace_root)
    medium_score_lead = next(
        lead for lead in result["data"]["recent_leads"] if lead["classification_score"] == 0.75
    )

    assert medium_score_lead["radar"]["data_integrity"] == 0.6
    assert medium_score_lead["tier_color"] == "amber"
