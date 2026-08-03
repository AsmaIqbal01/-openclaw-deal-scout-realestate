"""User Story 3 (P3): stale drafts never linger or self-send.

Covers Acceptance Scenarios 1-2 and the permanence edge case for FR-012,
FR-013.
"""

from tests.pipeline_sim import apply_stale_queue_guard, resolve_email_approval_reply


def _entries(load_fixture):
    return load_fixture("email_approval/queue_entries.json")


def test_four_hour_reminder_sent_exactly_once(load_fixture):
    """Acceptance Scenario 1 / FR-012: a pending entry queued 4h5m ago with
    no reply gets exactly one re-notification; running again at the same
    age does not send a second one."""
    pending = dict(_entries(load_fixture)["pending"])
    assert pending["re_notified"] is False

    first = apply_stale_queue_guard(pending, hours_since_queued=4 + 5 / 60)

    assert first["action"] == "re_notified"
    assert first["entry"]["re_notified"] is True
    assert first["notification_message"] is not None
    assert pending["queue_id"] in first["notification_message"]

    second = apply_stale_queue_guard(first["entry"], hours_since_queued=4 + 5 / 60)

    assert second["action"] == "none"
    assert second["notification_message"] is None


def test_twenty_four_hour_auto_archive_permanent(load_fixture):
    """Acceptance Scenario 2 / FR-013: a pending entry queued 24h5m ago
    with no reply is marked auto_archived: true, never sent, and a later
    /approve reply for that queue_id is treated as unknown_queue_id_reply
    -- the archival is permanent."""
    pending = dict(_entries(load_fixture)["pending"])

    result = apply_stale_queue_guard(pending, hours_since_queued=24 + 5 / 60)

    assert result["action"] == "auto_archived"
    archived = result["entry"]
    assert archived["auto_archived"] is True
    assert archived["sent_at"] is None

    late_approve = resolve_email_approval_reply(
        archived,
        reply_command="/approve",
        reply_queue_id=archived["queue_id"],
        reply_tenant_id=archived["tenant_id"],
        reply_from_number=archived["tenant_agent_whatsapp"],
    )
    assert late_approve["status"] == "unknown_queue_id_reply"
    assert late_approve["entry"]["sent_at"] is None


def test_stale_guard_skips_already_resolved_entries(load_fixture):
    """An approved, rejected, or already-archived entry is left untouched
    by the stale guard at both the 4-hour and 24-hour marks -- no
    re-notification, no re-archival."""
    entries = _entries(load_fixture)

    for key in ("approved_and_sent", "rejected", "auto_archived"):
        entry = entries[key]
        for hours in (4 + 5 / 60, 24 + 5 / 60):
            result = apply_stale_queue_guard(entry, hours_since_queued=hours)
            assert result["action"] == "none", (key, hours)
            assert result["entry"] == entry, (key, hours)
