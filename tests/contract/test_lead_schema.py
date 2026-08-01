"""Contract test for contracts/lead-schema.json (FR-004).

Validates that Delivery's schema check — every required field present,
enum values respected, score in range — is enforced exactly as the contract
states, using inline example lead objects (not the story-specific fixtures,
which don't need to exist for this baseline check).
"""

import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "specs" / "001-pk-lead-intake-notify" / "contracts" / "lead-schema.json"


@pytest.fixture(scope="module")
def schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _valid_lead(**overrides):
    lead = {
        "lead_id": "b7e2c2b0-1234-4a1a-9d3d-000000000001",
        "tenant_id": "pk-test-agency-001",
        "source": "zameen_alert",
        "market_mode": "PK",
        "contact": {"name": "Ali Raza", "phone": "03001234567", "whatsapp": None, "email": None},
        "property": {"type": "residential", "location": "DHA Phase 6", "budget_pkr": 45000000, "size": "10 Marla"},
        "urgency": "high",
        "classification_score": 0.95,
        "rejection_reason": None,
        "raw_source_id": "gmail-msg-0001",
        "classified_at": "2026-08-01T09:00:00+00:00",
    }
    lead.update(overrides)
    return lead


def test_valid_lead_passes_schema(schema):
    jsonschema.validate(_valid_lead(), schema)


def test_lead_missing_required_field_fails_schema(schema):
    lead = _valid_lead()
    del lead["classification_score"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(lead, schema)


def test_lead_with_duplicate_shaped_raw_source_id_still_matches_schema_shape(schema):
    """The schema only constrains shape, not dedup — dedup is a Delivery
    runtime check (FR-004), covered separately by pipeline_sim.is_duplicate
    in the integration suite. This test documents that two leads sharing a
    raw_source_id are each independently schema-valid; it's Delivery's
    processed_ids check, not the schema, that rejects the second one."""
    lead_a = _valid_lead(lead_id="b7e2c2b0-1234-4a1a-9d3d-000000000001", raw_source_id="gmail-msg-dup")
    lead_b = _valid_lead(lead_id="b7e2c2b0-1234-4a1a-9d3d-000000000002", raw_source_id="gmail-msg-dup")
    jsonschema.validate(lead_a, schema)
    jsonschema.validate(lead_b, schema)


def test_invalid_market_mode_fails_schema(schema):
    lead = _valid_lead(market_mode="UK")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(lead, schema)


def test_score_out_of_range_fails_schema(schema):
    lead = _valid_lead(classification_score=1.5)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(lead, schema)
