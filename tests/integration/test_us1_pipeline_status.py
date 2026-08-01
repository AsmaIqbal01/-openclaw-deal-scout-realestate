"""User Story 1 (P1): see pipeline status and quota at a glance.

Covers Acceptance Scenarios 1-2 (FR-003/004/005), plus FR-007 (CRM Sync)
and FR-008 (Market Toggle) — closed by /sp.analyze findings G1/G2.
"""

from dashboard.server import handle_state_request


def test_pipeline_status_reflects_state(load_fixture, dashboard_workspace_factory):
    normal_state = load_fixture("dashboard/normal_state.json")
    workspace_root = dashboard_workspace_factory(
        {"pk-test-agency-001": {"state": normal_state}}
    )

    result = handle_state_request("pk-test-agency-001", workspace_root)

    assert result["status"] == "ok"
    data = result["data"]
    assert data["last_run_status"] == "success"
    assert data["last_run_at"] == normal_state["last_run_at"]
    assert data["leads_today"] == 3
    assert data["leads_this_week"] == 11


def test_gemini_quota_gauge_value(load_fixture, dashboard_workspace_factory):
    normal_state = load_fixture("dashboard/normal_state.json")
    workspace_root = dashboard_workspace_factory(
        {"pk-test-agency-001": {"state": normal_state}}
    )

    result = handle_state_request("pk-test-agency-001", workspace_root)

    data = result["data"]
    assert data["gemini_quota_used"] == 12
    daily_limit = 20
    assert f"{data['gemini_quota_used']}/{daily_limit} used" == "12/20 used"


def test_crm_sync_status_reflects_state(load_fixture, dashboard_workspace_factory):
    normal_state = load_fixture("dashboard/normal_state.json")
    workspace_root = dashboard_workspace_factory(
        {"pk-test-agency-001": {"state": normal_state}}
    )

    result = handle_state_request("pk-test-agency-001", workspace_root)

    assert result["data"]["crm_last_write_at"] == normal_state["crm_last_write_at"]


def test_market_toggle_reflects_mode(load_fixture, dashboard_workspace_factory):
    normal_state = load_fixture("dashboard/normal_state.json")
    workspace_root = dashboard_workspace_factory(
        {"pk-test-agency-001": {"state": normal_state}}
    )

    result = handle_state_request("pk-test-agency-001", workspace_root)

    assert result["data"]["market_mode"] == "PK"
