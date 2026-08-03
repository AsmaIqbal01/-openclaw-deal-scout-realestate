"""Contract test for contracts/approval-queue-schema.json (FR-004).

Validates the shape of an Approval Queue Entry as written to
workspace/tenants/{tenant_id}/approval-queue.json, mirroring
tests/contract/test_lead_schema.py's pattern.
"""

import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = (
    REPO_ROOT
    / "specs"
    / "003-pk-email-approval-gate"
    / "contracts"
    / "approval-queue-schema.json"
)


@pytest.fixture(scope="module")
def schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _valid_entry(**overrides):
    entry = {
        "queue_id": "b7e2c2b0-1234-4a1a-9d3d-0000000000f1",
        "tenant_id": "pk-test-agency-001",
        "lead_id": "b7e2c2b0-1234-4a1a-9d3d-0000000000e1",
        "draft_subject": "Property Enquiry — residential in DHA Phase 6",
        "draft_body": "Dear Ali Raza,\n\nThank you for your interest...",
        "recipient_email": "ali.raza@example.com",
        "queued_at": "2026-08-01T09:05:00+00:00",
        "approved": False,
        "approved_at": None,
        "sent_at": None,
        "re_notified": False,
        "auto_archived": False,
    }
    entry.update(overrides)
    return entry


def test_valid_entry_passes_schema(schema):
    jsonschema.validate(_valid_entry(), schema)


def test_entry_missing_sent_at_fails_schema(schema):
    entry = _valid_entry()
    del entry["sent_at"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(entry, schema)


def test_entry_with_non_string_recipient_email_fails_schema(schema):
    """The schema's plain jsonschema.validate() (no FormatChecker attached,
    matching this suite's other contract tests) does not enforce the
    'format: email' keyword, only 'type: string' -- so this proves the type
    constraint is enforced, without asserting format behavior this suite
    doesn't actually turn on."""
    entry = _valid_entry(recipient_email=12345)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(entry, schema)


def test_approved_and_sent_entry_still_matches_schema(schema):
    entry = _valid_entry(
        approved=True,
        approved_at="2026-08-01T10:00:00+00:00",
        sent_at="2026-08-01T10:00:05+00:00",
    )
    jsonschema.validate(entry, schema)


def test_auto_archived_entry_still_matches_schema(schema):
    entry = _valid_entry(auto_archived=True, re_notified=True)
    jsonschema.validate(entry, schema)


def test_extra_test_only_field_allowed_by_additional_properties(schema):
    """The schema's additionalProperties: true permits the test-only
    'rejected' field pipeline_sim.py uses to derive terminal state,
    consistent with spec.md's Key Entities section naming a 'rejected'
    status the required-fields list doesn't itself enumerate."""
    entry = _valid_entry(rejected=True)
    jsonschema.validate(entry, schema)
