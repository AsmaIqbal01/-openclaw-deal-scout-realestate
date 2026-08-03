"""User Story 1 (P1): see every email draft awaiting a reply.

Covers Acceptance Scenarios 1-2 for FR-001, FR-002, FR-003, FR-004, FR-008.
"""

from datetime import datetime, timezone

from dashboard.server import handle_state_request

NOW = datetime(2026, 8, 3, 12, 0, 0, tzinfo=timezone.utc)


def test_pending_entry_shown_with_full_content(load_fixture, dashboard_workspace_factory):
    dashboard_state = load_fixture("dashboard/normal_state.json")
    pending_entries = load_fixture("dashboard/approval_queue_pending.json")
    workspace_root = dashboard_workspace_factory(
        {
            "pk-test-agency-001": {
                "state": dashboard_state,
                "approval_queue": pending_entries,
            }
        }
    )

    result = handle_state_request("pk-test-agency-001", workspace_root, now=NOW)

    queue = result["data"]["email_draft_queue"]
    assert queue["state"] == "entries"
    assert len(queue["entries"]) == 1

    entry = queue["entries"][0]
    fixture_entry = pending_entries[0]
    assert entry["draft_subject"] == fixture_entry["draft_subject"]
    assert entry["draft_body"] == fixture_entry["draft_body"]
    assert entry["recipient_email"] == fixture_entry["recipient_email"]
    assert entry["queued_at"] == fixture_entry["queued_at"]
    assert entry["status_label"] == "Pending"
    assert entry["reminder_seconds_remaining"] > 0
    assert entry["archive_seconds_remaining"] > 0


def test_no_email_drafts_yet_shows_empty_state(load_fixture, dashboard_workspace_factory):
    dashboard_state = load_fixture("dashboard/normal_state.json")
    workspace_root = dashboard_workspace_factory(
        {"pk-test-agency-001": {"state": dashboard_state}}
    )

    result = handle_state_request("pk-test-agency-001", workspace_root, now=NOW)

    queue = result["data"]["email_draft_queue"]
    assert queue["state"] == "empty"
    assert queue["entries"] == []
