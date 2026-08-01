"""Contract test for contracts/approval-commands.md (FR-006/007/008).

Validates the WhatsApp /confirm and /discard command contract: correct
lead_id match, unknown lead_id, and unauthorized reply source.
"""

from tests.pipeline_sim import resolve_approval_reply


def _entry():
    return {"lead_id": "lead-us2-001", "tenant_agent_whatsapp": "+923001234567"}


def test_confirm_from_correct_number_and_lead_id():
    result = resolve_approval_reply(
        _entry(),
        reply_command="/confirm",
        reply_lead_id="lead-us2-001",
        reply_from_number="+923001234567",
        hours_since_queued=0.5,
    )
    assert result == "confirmed"


def test_discard_from_correct_number_and_lead_id():
    result = resolve_approval_reply(
        _entry(),
        reply_command="/discard",
        reply_lead_id="lead-us2-001",
        reply_from_number="+923001234567",
        hours_since_queued=1.0,
    )
    assert result == "discarded"


def test_unknown_lead_id_reply():
    result = resolve_approval_reply(
        _entry(),
        reply_command="/confirm",
        reply_lead_id="lead-does-not-exist",
        reply_from_number="+923001234567",
        hours_since_queued=0.5,
    )
    assert result == "unknown_lead_id_reply"


def test_unauthorized_reply_source():
    result = resolve_approval_reply(
        _entry(),
        reply_command="/confirm",
        reply_lead_id="lead-us2-001",
        reply_from_number="+923009999999",
        hours_since_queued=0.5,
    )
    assert result == "unauthorized_reply_source"
