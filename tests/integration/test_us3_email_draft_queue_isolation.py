"""User Story 3 (P3): queue data never leaks across tenants or breaks the
rest of the dashboard.

Covers Acceptance Scenarios 1-2 for FR-007, FR-009, FR-010.
"""

from datetime import datetime, timezone

from dashboard.server import handle_state_request

NOW = datetime(2026, 8, 3, 12, 0, 0, tzinfo=timezone.utc)


def test_cross_tenant_isolation(load_fixture, dashboard_workspace_factory):
    state_a = load_fixture("dashboard/normal_state.json")
    state_b = load_fixture("dashboard/tenant_b_state.json")
    queue_a = load_fixture("dashboard/approval_queue_pending.json")
    queue_b = load_fixture("dashboard/approval_queue_tenant_b.json")
    workspace_root = dashboard_workspace_factory(
        {
            "pk-test-agency-001": {"state": state_a, "approval_queue": queue_a},
            "pk-tenant-b-003": {"state": state_b, "approval_queue": queue_b},
        }
    )

    result_a = handle_state_request("pk-test-agency-001", workspace_root, now=NOW)
    result_b = handle_state_request("pk-tenant-b-003", workspace_root, now=NOW)

    entries_a = result_a["data"]["email_draft_queue"]["entries"]
    entries_b = result_b["data"]["email_draft_queue"]["entries"]

    queue_ids_a = {e["queue_id"] for e in entries_a}
    queue_ids_b = {e["queue_id"] for e in entries_b}
    lead_ids_a = {e["lead_id"] for e in entries_a}
    lead_ids_b = {e["lead_id"] for e in entries_b}

    assert queue_ids_a.isdisjoint(queue_ids_b)
    assert lead_ids_a.isdisjoint(lead_ids_b)
    assert all(e["tenant_id"] == "pk-test-agency-001" for e in entries_a)
    assert all(e["tenant_id"] == "pk-tenant-b-003" for e in entries_b)


def test_malformed_approval_queue_json_isolated_failure(load_fixture, dashboard_workspace_factory):
    dashboard_state = load_fixture("dashboard/normal_state.json")
    workspace_root = dashboard_workspace_factory(
        {
            "pk-test-agency-001": {
                "state": dashboard_state,
                "approval_queue_raw": "{this is not valid json",
            }
        }
    )

    result = handle_state_request("pk-test-agency-001", workspace_root, now=NOW)

    assert result["data"]["email_draft_queue"] == {"state": "unavailable", "entries": []}
    # Every other section is unaffected.
    assert result["data"]["last_run_status"] == dashboard_state["last_run_status"]
    assert result["data"]["leads_today"] == dashboard_state["leads_today"]
    assert len(result["data"]["recent_leads"]) == len(dashboard_state["recent_leads"])
    assert result["data"]["approval_queue"] is not None


def test_display_capped_at_ten_most_recent(load_fixture, dashboard_workspace_factory):
    dashboard_state = load_fixture("dashboard/normal_state.json")
    eleven_entries = load_fixture("dashboard/approval_queue_eleven_entries.json")
    workspace_root = dashboard_workspace_factory(
        {
            "pk-test-agency-001": {
                "state": dashboard_state,
                "approval_queue": eleven_entries,
            }
        }
    )

    result = handle_state_request("pk-test-agency-001", workspace_root, now=NOW)
    entries = result["data"]["email_draft_queue"]["entries"]

    assert len(entries) == 10
    queued_ats = [e["queued_at"] for e in entries]
    assert queued_ats == sorted(queued_ats, reverse=True)
    oldest_lead_id = min(eleven_entries, key=lambda e: e["queued_at"])["lead_id"]
    assert oldest_lead_id not in {e["lead_id"] for e in entries}
