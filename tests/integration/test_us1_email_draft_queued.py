"""User Story 1 (P1): a follow-up email is drafted and queued automatically.

Covers Acceptance Scenarios 1-2 and Edge Cases for FR-001, FR-002, FR-005,
FR-006, FR-007, FR-014, FR-015.
"""

from tests.pipeline_sim import process_lead, queue_email_draft


def _tenant(load_fixture):
    return load_fixture("email_approval/tenant_auto_email_drafts.json")


def _lead_with_email(load_fixture, index=0):
    return load_fixture("email_approval/leads_with_email.json")[index]


def _lead_without_email(load_fixture):
    return load_fixture("email_approval/leads_without_email.json")[0]


def test_draft_queued_for_dispatched_lead_with_email(load_fixture):
    """Acceptance Scenario 1: a Tier 1 auto-dispatched lead with
    contact.email set and auto_email_drafts true gets a new
    approval-queue.json entry with approved: false, sent_at: null, and the
    owner receives the WhatsApp draft-alert referencing that queue_id."""
    tenant = _tenant(load_fixture)
    lead = _lead_with_email(load_fixture, 0)

    result = queue_email_draft(lead, tenant, existing_queue=[])

    assert result["status"] == "queued"
    entry = result["entry"]
    assert entry["approved"] is False
    assert entry["sent_at"] is None
    assert entry["lead_id"] == lead["lead_id"]
    assert entry["recipient_email"] == lead["contact"]["email"]
    assert entry in result["queue"]

    assert result["notification_sent"] is True
    assert entry["queue_id"] in result["notification_message"]
    assert result["notification_message"].startswith(
        "📧 New email draft awaiting your approval."
    )

    # The draft is queued, not sent -- no email leaves the system here.
    assert entry["sent_at"] is None


def test_draft_content_matches_pk_template(load_fixture):
    """FR-003: subject and body follow the exact PK-mode template, with
    non-null property fields substituted directly."""
    tenant = _tenant(load_fixture)
    lead = _lead_with_email(load_fixture, 0)  # DHA Phase 6, budget/size set

    result = queue_email_draft(lead, tenant, existing_queue=[])
    entry = result["entry"]

    assert entry["draft_subject"] == "Property Enquiry — residential in DHA Phase 6"
    assert "Dear Ali Raza," in entry["draft_body"]
    assert "- Property Type: residential" in entry["draft_body"]
    assert "- Location: DHA Phase 6" in entry["draft_body"]
    assert "- Budget: PKR 45000000" in entry["draft_body"]
    assert "- Size: 10 Marla" in entry["draft_body"]
    assert entry["draft_body"].endswith(f"{tenant['agent_name']}\n{tenant['agency_name']}")


def test_draft_content_uses_fallbacks_for_missing_fields(load_fixture):
    """FR-003: null contact.name, budget_pkr, size fall back to
    'Sir/Madam', 'to be discussed', 'flexible' respectively."""
    tenant = _tenant(load_fixture)
    lead = _lead_with_email(load_fixture, 1)  # Gulberg III, budget/size null
    lead = dict(lead)
    lead["contact"] = dict(lead["contact"])
    lead["contact"]["name"] = None

    result = queue_email_draft(lead, tenant, existing_queue=[])
    entry = result["entry"]

    assert "Dear Sir/Madam," in entry["draft_body"]
    assert "- Budget: PKR to be discussed" in entry["draft_body"]
    assert "- Size: flexible" in entry["draft_body"]


def test_no_draft_for_null_email(load_fixture):
    """Acceptance Scenario 2 / FR-002: contact.email is null -> no draft is
    created, logged as 'no email address for lead {lead_id}'."""
    tenant = _tenant(load_fixture)
    lead = _lead_without_email(load_fixture)

    result = queue_email_draft(lead, tenant, existing_queue=[])

    assert result["status"] == "no_email_address"
    assert result["entry"] is None
    assert result["queue"] == []
    assert result["log"] == f"no email address for lead {lead['lead_id']}"


def test_no_draft_when_auto_email_drafts_disabled(load_fixture, tenant_context):
    """Edge Case: auto_email_drafts is false (the default) -> no draft is
    ever attempted for that tenant's leads, regardless of contact.email."""
    lead = _lead_with_email(load_fixture, 0)
    assert tenant_context["auto_email_drafts"] is False

    result = queue_email_draft(lead, tenant_context, existing_queue=[])

    assert result["status"] == "auto_email_drafts_disabled"
    assert result["entry"] is None
    assert result["queue"] == []


def test_queue_append_only_never_overwrites(load_fixture):
    """FR-005: appending a second draft must not overwrite or remove the
    first entry."""
    tenant = _tenant(load_fixture)
    lead_a = _lead_with_email(load_fixture, 0)
    lead_b = _lead_with_email(load_fixture, 1)

    first = queue_email_draft(lead_a, tenant, existing_queue=[])
    second = queue_email_draft(lead_b, tenant, existing_queue=first["queue"])

    assert len(second["queue"]) == 2
    assert first["entry"] in second["queue"]
    assert first["entry"]["queue_id"] != second["entry"]["queue_id"]
    # The original list returned to the first caller is untouched.
    assert len(first["queue"]) == 1


def test_queue_full_halts_new_drafts(load_fixture):
    """FR-006: a tenant queue already at 50 entries gets no new draft; the
    owner is alerted and the halt is logged."""
    tenant = _tenant(load_fixture)
    lead = _lead_with_email(load_fixture, 0)
    full_queue = [{"queue_id": f"existing-{i}"} for i in range(50)]

    result = queue_email_draft(lead, tenant, existing_queue=full_queue)

    assert result["status"] == "queue_full"
    assert result["entry"] is None
    assert result["queue"] == full_queue
    assert len(result["queue"]) == 50
    assert result["owner_alerted"] is True
    assert result["log"] is not None


def test_draft_generation_failure_skips_only_that_lead(load_fixture):
    """FR-014: draft generation itself fails -> logged with lead_id, only
    that lead's email is skipped; an already-completed CRM write/
    notification for the same lead (simulated via process_lead) is
    unaffected -- proven by the two calls being fully independent."""
    tenant = _tenant(load_fixture)
    lead = _lead_with_email(load_fixture, 0)

    dispatch_result = process_lead(lead, tenant["tenant_id"], processed_ids=[])
    assert dispatch_result["status"] == "auto_dispatched"
    assert dispatch_result["crm_write"] is True

    draft_result = queue_email_draft(
        lead, tenant, existing_queue=[], draft_render_outcome=False,
    )

    assert draft_result["status"] == "draft_generation_failed"
    assert draft_result["entry"] is None
    assert draft_result["log"] == f"draft generation failed for lead {lead['lead_id']}"
    # The earlier CRM write/notification result is untouched by the failure.
    assert dispatch_result["crm_write"] is True
    assert dispatch_result["notification_sent"] is True


def test_queue_write_failure_not_queued(load_fixture):
    """FR-015: writing approval-queue.json fails -> logged, owner alerted,
    draft not queued."""
    tenant = _tenant(load_fixture)
    lead = _lead_with_email(load_fixture, 0)

    result = queue_email_draft(lead, tenant, existing_queue=[], queue_write_ok=False)

    assert result["status"] == "queue_write_failed"
    assert result["entry"] is None
    assert result["queue"] == []
    assert result["owner_alerted"] is True


def test_draft_alert_retry_then_continue(load_fixture):
    """FR-007: the draft-alert WhatsApp send fails once, is retried
    exactly once, then logged -- the draft remains queued regardless of
    notification delivery."""
    tenant = _tenant(load_fixture)
    lead = _lead_with_email(load_fixture, 0)

    result = queue_email_draft(
        lead, tenant, existing_queue=[], whatsapp_outcomes=(False, False),
    )

    assert result["status"] == "queued"
    assert result["notification_sent"] is False
    assert result["whatsapp_attempts"] == 2
    assert result["entry"] is not None
    assert result["entry"] in result["queue"]
