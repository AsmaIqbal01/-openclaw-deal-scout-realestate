"""User Story 3 (P3): see leads awaiting a WhatsApp reply.

Covers Acceptance Scenarios 1-2 (FR-006).
"""

from datetime import datetime, timezone

from dashboard.server import handle_state_request

FIXED_NOW = datetime(2026, 8, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_approval_queue_entry_shown_with_time_remaining(load_fixture, dashboard_workspace_factory):
    normal_state = load_fixture("dashboard/normal_state.json")
    workspace_root = dashboard_workspace_factory(
        {"pk-test-agency-001": {"state": normal_state}}
    )

    result = handle_state_request("pk-test-agency-001", workspace_root, now=FIXED_NOW)

    queue = result["data"]["approval_queue"]
    assert len(queue) == 1
    entry = queue[0]
    # queued_at is 1h50m before FIXED_NOW -> 10 minutes (600s) remaining
    assert 590 <= entry["seconds_remaining"] <= 610


def test_leads_pending_approval_count_matches_queue_length(load_fixture, dashboard_workspace_factory):
    normal_state = load_fixture("dashboard/normal_state.json")
    workspace_root = dashboard_workspace_factory(
        {"pk-test-agency-001": {"state": normal_state}}
    )

    result = handle_state_request("pk-test-agency-001", workspace_root, now=FIXED_NOW)

    data = result["data"]
    assert data["leads_pending_approval"] == len(data["approval_queue"])
