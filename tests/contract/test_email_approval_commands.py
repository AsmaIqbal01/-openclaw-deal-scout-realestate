"""Contract test for contracts/email-approval-commands.md (FR-009/010/011).

Validates the WhatsApp /approve and /reject command contract for drafted
emails: correct queue_id match, unknown queue_id, and a queue_id belonging
to a different tenant. Distinct from
tests/contract/test_approval_commands.py, which covers feature 001's
Tier 2 lead /confirm-/discard contract.
"""

from tests.pipeline_sim import resolve_email_approval_reply


def _pending_entry():
    return {
        "queue_id": "b7e2c2b0-1234-4a1a-9d3d-0000000000f1",
        "tenant_id": "pk-test-agency-001",
        "tenant_agent_whatsapp": "+923001234567",
        "approved": False,
        "rejected": False,
        "auto_archived": False,
    }


def test_approve_from_correct_tenant_and_queue_id():
    result = resolve_email_approval_reply(
        _pending_entry(),
        reply_command="/approve",
        reply_queue_id="b7e2c2b0-1234-4a1a-9d3d-0000000000f1",
        reply_tenant_id="pk-test-agency-001",
        reply_from_number="+923001234567",
    )
    assert result["status"] == "sent"
    assert result["entry"]["approved"] is True
    assert result["entry"]["sent_at"] is not None


def test_reject_from_correct_tenant_and_queue_id():
    result = resolve_email_approval_reply(
        _pending_entry(),
        reply_command="/reject",
        reply_queue_id="b7e2c2b0-1234-4a1a-9d3d-0000000000f1",
        reply_tenant_id="pk-test-agency-001",
        reply_from_number="+923001234567",
    )
    assert result["status"] == "rejected"
    assert result["entry"]["rejected"] is True


def test_unknown_queue_id_reply():
    result = resolve_email_approval_reply(
        _pending_entry(),
        reply_command="/approve",
        reply_queue_id="queue-id-does-not-exist",
        reply_tenant_id="pk-test-agency-001",
        reply_from_number="+923001234567",
    )
    assert result["status"] == "unknown_queue_id_reply"


def test_cross_tenant_queue_id_rejected():
    result = resolve_email_approval_reply(
        _pending_entry(),
        reply_command="/approve",
        reply_queue_id="b7e2c2b0-1234-4a1a-9d3d-0000000000f1",
        reply_tenant_id="pk-test-agency-999",
        reply_from_number="+923001234567",
    )
    assert result["status"] == "unknown_queue_id_reply"
