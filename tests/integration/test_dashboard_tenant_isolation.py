"""Multi-tenant isolation (FR-011, FR-012, FR-013, FR-014, SC-004)."""

from dashboard.server import handle_state_request


def test_no_tenant_param_shows_selector(dashboard_workspace_factory):
    workspace_root = dashboard_workspace_factory(
        {
            "pk-test-agency-001": {"active": True, "state": None},
            "pk-tenant-b-003": {"active": True, "state": None},
            "pk-inactive-004": {"active": False, "state": None},
        }
    )

    result = handle_state_request(None, workspace_root)

    assert result["status"] == "select_tenant"
    assert set(result["tenants"]) == {"pk-test-agency-001", "pk-tenant-b-003"}


def test_unconfigured_tenant_returns_not_configured(dashboard_workspace_factory):
    workspace_root = dashboard_workspace_factory({"pk-test-agency-001": {"state": None}})

    result = handle_state_request("pk-does-not-exist", workspace_root)

    assert result["status"] == "tenant_not_configured"
    assert result["tenant_id"] == "pk-does-not-exist"


def test_missing_state_file_returns_no_runs_yet(dashboard_workspace_factory):
    workspace_root = dashboard_workspace_factory({"pk-new-agency-002": {"state": None}})

    result = handle_state_request("pk-new-agency-002", workspace_root)

    assert result["status"] == "no_runs_yet"
    assert result["tenant_id"] == "pk-new-agency-002"


def test_cross_tenant_isolation_strict(load_fixture, dashboard_workspace_factory):
    state_a = load_fixture("dashboard/normal_state.json")
    state_b = load_fixture("dashboard/tenant_b_state.json")
    workspace_root = dashboard_workspace_factory(
        {
            "pk-test-agency-001": {"state": state_a},
            "pk-tenant-b-003": {"state": state_b},
        }
    )

    result_a = handle_state_request("pk-test-agency-001", workspace_root)
    result_b = handle_state_request("pk-tenant-b-003", workspace_root)

    assert result_a["data"]["tenant_id"] == "pk-test-agency-001"
    assert result_b["data"]["tenant_id"] == "pk-tenant-b-003"

    # No cross-contamination of any field between the two responses
    assert result_a["data"]["leads_today"] != result_b["data"]["leads_today"]
    assert result_a["data"]["last_run_status"] != result_b["data"]["last_run_status"]
    a_contacts = {lead["contact_name"] for lead in result_a["data"]["recent_leads"]}
    b_contacts = {lead["contact_name"] for lead in result_b["data"]["recent_leads"]}
    assert a_contacts.isdisjoint(b_contacts)
