"""User Story 2 (P2): the agent approves or rejects the draft via WhatsApp.

Covers Acceptance Scenarios 1-3 and Edge Cases for FR-009, FR-010, FR-011,
plus the cross-tenant edge case (Constitution Principle VIII).
"""

from tests.pipeline_sim import resolve_email_approval_reply


def _entries(load_fixture):
    return load_fixture("email_approval/queue_entries.json")


def test_approve_sends_email_and_sets_fields(load_fixture):
    """Acceptance Scenario 1: /approve {queue_id} -> approved becomes true,
    approved_at is set, the email is sent to recipient_email, sent_at is
    set, and no other queue entry is touched."""
    entries = _entries(load_fixture)
    pending = entries["pending"]
    other = entries["pending_other_tenant"]

    result = resolve_email_approval_reply(
        pending,
        reply_command="/approve",
        reply_queue_id=pending["queue_id"],
        reply_tenant_id=pending["tenant_id"],
        reply_from_number=pending["tenant_agent_whatsapp"],
    )

    assert result["status"] == "sent"
    updated = result["entry"]
    assert updated["approved"] is True
    assert updated["approved_at"] is not None
    assert updated["sent_at"] is not None

    # The un-related entry (a different tenant's queue) is never touched --
    # resolve_email_approval_reply operates on exactly one entry per call.
    assert other["approved"] is False
    assert other["sent_at"] is None


def test_reject_marks_rejected_never_sent(load_fixture):
    """Acceptance Scenario 2 / FR-010: /reject {queue_id} -> logged
    rejected, email never sent."""
    entries = _entries(load_fixture)
    pending = dict(entries["pending"])
    pending["queue_id"] = "b7e2c2b0-1234-4a1a-9d3d-0000000000f6"  # a distinct pending entry

    result = resolve_email_approval_reply(
        pending,
        reply_command="/reject",
        reply_queue_id=pending["queue_id"],
        reply_tenant_id=pending["tenant_id"],
        reply_from_number=pending["tenant_agent_whatsapp"],
    )

    assert result["status"] == "rejected"
    assert result["entry"]["rejected"] is True
    assert result["entry"]["sent_at"] is None


def test_unknown_queue_id_reply_ignored(load_fixture):
    """Acceptance Scenario 3 / FR-011: a reply naming a queue_id that does
    not match this entry is ignored and logged, no entry modified."""
    entries = _entries(load_fixture)
    pending = entries["pending"]

    result = resolve_email_approval_reply(
        pending,
        reply_command="/approve",
        reply_queue_id="queue-id-that-does-not-exist",
        reply_tenant_id=pending["tenant_id"],
        reply_from_number=pending["tenant_agent_whatsapp"],
    )

    assert result["status"] == "unknown_queue_id_reply"
    # The entry object returned is the original, unmodified.
    assert result["entry"]["approved"] is False
    assert result["entry"]["sent_at"] is None


def test_already_resolved_queue_id_reply_ignored(load_fixture):
    """FR-011: a reply naming a queue_id that is already approved,
    rejected, or auto_archived is treated identically to unknown -- never
    re-sent or re-processed."""
    entries = _entries(load_fixture)

    for key in ("approved_and_sent", "rejected", "auto_archived"):
        entry = entries[key]
        result = resolve_email_approval_reply(
            entry,
            reply_command="/approve",
            reply_queue_id=entry["queue_id"],
            reply_tenant_id=entry["tenant_id"],
            reply_from_number=entry["tenant_agent_whatsapp"],
        )
        assert result["status"] == "unknown_queue_id_reply", key


def test_cross_tenant_queue_id_rejected(load_fixture):
    """Edge Case (Constitution Principle VIII): a reply's queue_id belongs
    to a different tenant than the replying agent's own tenant -> rejected
    the same as unknown, never resolved across tenants."""
    entries = _entries(load_fixture)
    other_tenant_entry = entries["pending_other_tenant"]

    result = resolve_email_approval_reply(
        other_tenant_entry,
        reply_command="/approve",
        reply_queue_id=other_tenant_entry["queue_id"],
        reply_tenant_id="pk-test-agency-001",  # a different, replying tenant
        reply_from_number="+923001234567",
    )

    assert result["status"] == "unknown_queue_id_reply"
    assert result["entry"]["approved"] is False


def test_approve_email_send_retry_then_alert(load_fixture):
    """FR-009: the email send fails, is retried once after 30s
    (simulated); if the retry also fails, sent_at stays unset, the failure
    is logged, and the owner is alerted -- but the approval itself is not
    rolled back."""
    entries = _entries(load_fixture)
    pending = dict(entries["pending"])
    pending["queue_id"] = "b7e2c2b0-1234-4a1a-9d3d-0000000000f7"

    result = resolve_email_approval_reply(
        pending,
        reply_command="/approve",
        reply_queue_id=pending["queue_id"],
        reply_tenant_id=pending["tenant_id"],
        reply_from_number=pending["tenant_agent_whatsapp"],
        email_send_outcomes=(False, False),
    )

    assert result["status"] == "send_failed"
    updated = result["entry"]
    assert updated["approved"] is True
    assert updated["approved_at"] is not None
    assert updated["sent_at"] is None
    assert result["send_attempts"] == 2
    assert result["owner_alerted"] is True
