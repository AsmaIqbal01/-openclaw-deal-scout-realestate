"""User Story 2 (P2): see the outcome of a resolved draft.

Covers Acceptance Scenarios 1-4 and the auto_archived/rejected precedence
edge case, for FR-003, FR-004.
"""

from datetime import datetime, timezone

from dashboard.server import derive_status_label, handle_state_request

NOW = datetime(2026, 8, 3, 12, 0, 0, tzinfo=timezone.utc)


def test_status_labels_for_each_resolved_state(load_fixture, dashboard_workspace_factory):
    dashboard_state = load_fixture("dashboard/normal_state.json")
    mixed_entries = load_fixture("dashboard/approval_queue_mixed_status.json")
    workspace_root = dashboard_workspace_factory(
        {
            "pk-test-agency-001": {
                "state": dashboard_state,
                "approval_queue": mixed_entries,
            }
        }
    )

    result = handle_state_request("pk-test-agency-001", workspace_root, now=NOW)
    entries = result["data"]["email_draft_queue"]["entries"]
    labels_by_queue_id = {e["queue_id"]: e["status_label"] for e in entries}

    assert labels_by_queue_id["d1e2f3a0-0000-4000-8000-000000000010"] == "Pending"
    assert labels_by_queue_id["d1e2f3a0-0000-4000-8000-000000000011"] == "Sent"
    assert labels_by_queue_id["d1e2f3a0-0000-4000-8000-000000000012"] == "Send Failed"
    assert labels_by_queue_id["d1e2f3a0-0000-4000-8000-000000000013"] == "Rejected"
    assert labels_by_queue_id["d1e2f3a0-0000-4000-8000-000000000014"] == "Auto-Archived"


def test_resolved_entries_have_null_time_remaining_fields(load_fixture, dashboard_workspace_factory):
    dashboard_state = load_fixture("dashboard/normal_state.json")
    mixed_entries = load_fixture("dashboard/approval_queue_mixed_status.json")
    workspace_root = dashboard_workspace_factory(
        {
            "pk-test-agency-001": {
                "state": dashboard_state,
                "approval_queue": mixed_entries,
            }
        }
    )

    result = handle_state_request("pk-test-agency-001", workspace_root, now=NOW)
    entries = result["data"]["email_draft_queue"]["entries"]

    for entry in entries:
        if entry["status_label"] != "Pending":
            assert entry["reminder_seconds_remaining"] is None
            assert entry["archive_seconds_remaining"] is None


def test_auto_archived_takes_precedence_over_rejected():
    entry = {
        "queue_id": "d1e2f3a0-0000-4000-8000-0000000000ff",
        "tenant_id": "pk-test-agency-001",
        "approved": False,
        "sent_at": None,
        "rejected": True,
        "auto_archived": True,
    }

    assert derive_status_label(entry) == "Auto-Archived"
