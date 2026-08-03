"""Contract test for contracts/email-draft-queue-response.md (004).

Validates that an enriched Email Draft Queue Entry's base fields still
match feature 003's approval-queue-schema.json exactly (reused directly,
not duplicated), and that the enrichment fields (status_label,
reminder_seconds_remaining, archive_seconds_remaining) are present with
correct values.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import jsonschema
import pytest

from dashboard.server import enrich_email_draft_queue_entry

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


def _base_entry(**overrides):
    entry = {
        "queue_id": "d1e2f3a0-0000-4000-8000-000000000099",
        "tenant_id": "pk-test-agency-001",
        "lead_id": "b7e2c2b0-1234-4a1a-9d3d-0000000000e1",
        "draft_subject": "Property Enquiry — residential in DHA Phase 6",
        "draft_body": "Dear Ali Raza, ...",
        "recipient_email": "ali.raza@example.com",
        "queued_at": "2026-08-03T11:40:00+00:00",
        "approved": False,
        "approved_at": None,
        "sent_at": None,
        "re_notified": False,
        "auto_archived": False,
        "rejected": False,
    }
    entry.update(overrides)
    return entry


def _strip_enrichment(entry: dict) -> dict:
    return {
        k: v
        for k, v in entry.items()
        if k not in ("status_label", "reminder_seconds_remaining", "archive_seconds_remaining")
    }


def test_enriched_pending_entry_base_fields_still_match_schema(schema):
    now = datetime(2026, 8, 3, 12, 0, 0, tzinfo=timezone.utc)
    entry = enrich_email_draft_queue_entry(_base_entry(), now)
    jsonschema.validate(_strip_enrichment(entry), schema)


def test_pending_entry_has_positive_countdowns():
    now = datetime(2026, 8, 3, 12, 0, 0, tzinfo=timezone.utc)
    entry = enrich_email_draft_queue_entry(_base_entry(), now)

    assert entry["status_label"] == "Pending"
    assert entry["reminder_seconds_remaining"] > 0
    assert entry["archive_seconds_remaining"] > 0


def test_sent_entry_has_null_countdowns_and_still_matches_schema(schema):
    now = datetime(2026, 8, 3, 12, 0, 0, tzinfo=timezone.utc)
    entry = enrich_email_draft_queue_entry(
        _base_entry(
            approved=True,
            approved_at="2026-08-03T08:30:00+00:00",
            sent_at="2026-08-03T08:30:05+00:00",
        ),
        now,
    )

    assert entry["status_label"] == "Sent"
    assert entry["reminder_seconds_remaining"] is None
    assert entry["archive_seconds_remaining"] is None
    jsonschema.validate(_strip_enrichment(entry), schema)
