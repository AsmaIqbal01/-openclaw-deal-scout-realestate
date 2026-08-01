"""Contract test for contracts/dashboard-state-schema.json (FR-002).

Validates the Dashboard State document shape, and confirms
dashboard/server.py reads it back unmodified.
"""

import copy
import json
import sys
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "specs" / "002-pk-client-dashboard" / "contracts" / "dashboard-state-schema.json"

sys.path.insert(0, str(REPO_ROOT))
from dashboard.server import load_dashboard_state  # noqa: E402


@pytest.fixture(scope="module")
def schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_normal_state_fixture_passes_schema(load_fixture, schema):
    state = load_fixture("dashboard/normal_state.json")
    jsonschema.validate(state, schema)


def test_load_dashboard_state_returns_fixture_unmodified(
    load_fixture, dashboard_workspace_factory
):
    normal_state = load_fixture("dashboard/normal_state.json")
    workspace_root = dashboard_workspace_factory(
        {"pk-test-agency-001": {"state": normal_state}}
    )

    loaded = load_dashboard_state("pk-test-agency-001", workspace_root)

    assert loaded == normal_state


def test_recent_leads_over_ten_entries_rejected(load_fixture, schema):
    """/sp.analyze finding G3: the 10-entry cap on recent_leads is a
    schema/contract concern (maxItems: 10), not display logic — prove the
    schema actually rejects an over-10-entry array."""
    state = copy.deepcopy(load_fixture("dashboard/normal_state.json"))
    one_lead = state["recent_leads"][0]
    state["recent_leads"] = [one_lead] * 11

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(state, schema)
