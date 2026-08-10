"""Contract test for PILOTS.md (spec.md FR-001/002/003/004/005/006/007/
008/009/010/011/012/013).

Structural validation only, per research.md Decision 1/2 and
adrs/ADR-004-pilots-manual-tracking-boundary.md: PILOTS.md is manually
maintained, so this test parses it (or a fixture shaped like it) and
validates it -- it never invokes any runtime agent and never runs as part
of the pipeline heartbeat. FR-004's "traceable to a real MEMORY.md entry"
requirement remains unverifiable by design (ADR-004's accepted risk) --
this test can only confirm the fields are present and well-formed, not
that source_run_id corresponds to a real notification.
"""

import json
import re
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = (
    REPO_ROOT
    / "specs"
    / "005-pk-pilot-tracking"
    / "contracts"
    / "pilot-slot-schema.json"
)

SLOT_BLOCK_RE = re.compile(r"##\s*Slot\s+\d+\s*\n+```json\s*\n(.*?)\n```", re.DOTALL)


def _load_schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def schema():
    return _load_schema()


def parse_pilot_slots(markdown_text: str) -> list:
    """Extracts each fenced ```json block appearing under a '## Slot N'
    heading, in heading order, and returns the parsed list of slot dicts
    (data-model.md)."""
    return [json.loads(block) for block in SLOT_BLOCK_RE.findall(markdown_text)]


def parse_summary_line(markdown_text: str) -> str:
    """Returns the first non-blank content line, for comparison against
    the exact strings FR-009 requires."""
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _tenant_id_mismatches_real_user_md(tenant_id: str, workspace_root) -> bool:
    """FR-013: True if a real workspace/tenants/{tenant_id}/USER.md exists
    for this tenant but its own tenant_id field disagrees with the slot's.
    False (no mismatch) if the tenant doesn't exist yet -- FR-013 only
    applies "once that tenant exists" (data-model.md)."""
    user_md_path = Path(workspace_root) / "tenants" / tenant_id / "USER.md"
    if not user_md_path.exists():
        return False
    try:
        with open(user_md_path, encoding="utf-8") as f:
            real_config = json.load(f)
    except (OSError, json.JSONDecodeError):
        return False
    return real_config.get("tenant_id") != tenant_id


def count_valid_confirmed(slots: list, workspace_root=None) -> int:
    """Counts slots that are simultaneously (a) schema-valid against
    pilot-slot-schema.json, (b) not sharing a duplicate tenant_id with
    another slot (FR-006), (c) not mismatched against a real
    workspace/tenants/{tenant_id}/USER.md when workspace_root is given
    (FR-013), and (d) onboarding_status == "confirmed" -- implementing the
    FR-006/FR-007/FR-011/FR-013 exclusion rules together, since the gate
    count in FR-007 depends on all four. workspace_root is optional: when
    omitted, the FR-013 check is skipped (no real tenant data to compare
    against), matching this test suite's other structural-only checks."""
    schema_doc = _load_schema()

    seen_tenant_ids = set()
    duplicate_tenant_ids = set()
    for slot in slots:
        tenant_id = slot.get("tenant_id")
        if tenant_id is not None:
            if tenant_id in seen_tenant_ids:
                duplicate_tenant_ids.add(tenant_id)
            seen_tenant_ids.add(tenant_id)

    count = 0
    for slot in slots:
        tenant_id = slot.get("tenant_id")
        if tenant_id is not None and tenant_id in duplicate_tenant_ids:
            continue
        if (
            workspace_root is not None
            and tenant_id is not None
            and _tenant_id_mismatches_real_user_md(tenant_id, workspace_root)
        ):
            continue
        try:
            jsonschema.validate(slot, schema_doc)
        except jsonschema.ValidationError:
            continue
        if slot.get("onboarding_status") == "confirmed":
            count += 1
    return count


# --- User Story 1: see all 4 pilot slots' status at a glance ---


def test_summary_line_zero_confirmed(load_text_fixture):
    """Acceptance Scenario 1: a fresh scaffold reports 0 of 4 confirmed."""
    text = load_text_fixture("pilots/valid_four_slots.md")
    assert parse_summary_line(text) == "0 of 4 confirmed — Phase 1 gate not met"


def test_summary_line_two_confirmed(load_text_fixture):
    """Acceptance Scenario 2: 2 of 4 confirmed still reports gate not met."""
    text = load_text_fixture("pilots/two_confirmed.md")
    assert parse_summary_line(text) == "2 of 4 confirmed — Phase 1 gate not met"


def test_slot_count_is_always_exactly_four(load_text_fixture):
    """FR-001: PILOTS.md always contains exactly 4 slots."""
    text = load_text_fixture("pilots/valid_four_slots.md")
    assert len(parse_pilot_slots(text)) == 4


# --- User Story 2: record and update a slot's fields as onboarding advances ---


def test_all_slots_match_pilot_slot_schema(schema, load_text_fixture):
    """FR-002/FR-003: every field of every slot matches the schema."""
    text = load_text_fixture("pilots/valid_four_slots.md")
    for slot in parse_pilot_slots(text):
        jsonschema.validate(slot, schema)


def test_confirmed_slot_requires_source_run_id(load_text_fixture):
    """Acceptance Scenario 2 (FR-004): every confirmed slot has both
    first_notification_delivered_at and source_run_id non-null."""
    text = load_text_fixture("pilots/three_confirmed.md")
    confirmed_slots = [
        slot
        for slot in parse_pilot_slots(text)
        if slot["onboarding_status"] == "confirmed"
    ]
    assert len(confirmed_slots) == 3
    for slot in confirmed_slots:
        assert slot["first_notification_delivered_at"] is not None
        assert slot["source_run_id"] is not None


def test_confirmed_without_source_run_id_fails_schema(schema, load_text_fixture):
    """Acceptance Scenario 3 (FR-004/FR-011, the rejection/failure path):
    a slot claiming confirmed with source_run_id: null fails schema
    validation."""
    text = load_text_fixture("pilots/confirmed_without_source.md")
    confirmed_slots = [
        slot
        for slot in parse_pilot_slots(text)
        if slot["onboarding_status"] == "confirmed"
    ]
    assert len(confirmed_slots) == 1
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(confirmed_slots[0], schema)


# --- User Story 3: get an unambiguous signal the moment the gate is met ---


def test_gate_not_met_at_two_confirmed(load_text_fixture):
    """Acceptance Scenario 1: 2 of 4 confirmed is not the gate."""
    text = load_text_fixture("pilots/two_confirmed.md")
    slots = parse_pilot_slots(text)
    assert count_valid_confirmed(slots) == 2
    assert "not met" in parse_summary_line(text)


def test_gate_met_at_three_confirmed(load_text_fixture):
    """Acceptance Scenario 2: 3 of 4 confirmed (any 3) meets the gate."""
    text = load_text_fixture("pilots/three_confirmed.md")
    slots = parse_pilot_slots(text)
    assert count_valid_confirmed(slots) == 3
    assert parse_summary_line(text) == (
        "3 of 4 confirmed — Phase 1 gate met — UK-market work (Phase 2) "
        "is now authorized to begin"
    )


def test_duplicate_tenant_id_excluded_from_gate_count(load_text_fixture):
    """FR-006's fallback: two slots sharing a tenant_id are both excluded,
    even though each individually looks confirmed."""
    text = load_text_fixture("pilots/duplicate_tenant_id.md")
    slots = parse_pilot_slots(text)
    confirmed_by_status = [s for s in slots if s["onboarding_status"] == "confirmed"]
    assert len(confirmed_by_status) == 2  # naively looks confirmed...
    assert count_valid_confirmed(slots) == 0  # ...but both are excluded


def test_invalid_onboarding_status_excluded_from_gate_count(load_text_fixture):
    """FR-011's fallback: an out-of-enum onboarding_status is excluded from
    the gate count without raising an unhandled exception."""
    text = load_text_fixture("pilots/invalid_onboarding_status.md")
    slots = parse_pilot_slots(text)
    assert count_valid_confirmed(slots) == 0


# --- Remediation (from /sp.analyze findings C1/C2/C3/C4/U1) ---


def test_tenant_id_mismatch_with_real_user_md_excluded_from_gate_count(
    load_text_fixture, tmp_path
):
    """C1/FR-013's fallback: a slot's tenant_id must match the real
    USER.md's own tenant_id field once that tenant exists, else it is
    excluded from the gate count even though it otherwise looks
    confirmed."""
    text = load_text_fixture("pilots/three_confirmed.md")
    slots = parse_pilot_slots(text)
    mismatched_tenant_id = slots[0]["tenant_id"]

    tenant_dir = tmp_path / "tenants" / mismatched_tenant_id
    tenant_dir.mkdir(parents=True)
    (tenant_dir / "USER.md").write_text(
        json.dumps({"tenant_id": "pk-some-other-agency-999"}), encoding="utf-8"
    )

    assert count_valid_confirmed(slots) == 3  # unaffected without workspace_root
    assert count_valid_confirmed(slots, workspace_root=tmp_path) == 2  # excluded


def test_tenant_id_matching_real_user_md_still_counted(load_text_fixture, tmp_path):
    """FR-013 must not over-exclude: a slot whose tenant_id agrees with the
    real USER.md is still counted."""
    text = load_text_fixture("pilots/three_confirmed.md")
    slots = parse_pilot_slots(text)
    tenant_id = slots[0]["tenant_id"]

    tenant_dir = tmp_path / "tenants" / tenant_id
    tenant_dir.mkdir(parents=True)
    (tenant_dir / "USER.md").write_text(
        json.dumps({"tenant_id": tenant_id}), encoding="utf-8"
    )

    assert count_valid_confirmed(slots, workspace_root=tmp_path) == 3


def test_tenant_not_yet_onboarded_is_not_a_mismatch(load_text_fixture, tmp_path):
    """FR-013 only applies once the real tenant exists (data-model.md) --
    a slot referencing a tenant_id with no real USER.md yet is not
    penalized."""
    text = load_text_fixture("pilots/three_confirmed.md")
    slots = parse_pilot_slots(text)
    (tmp_path / "tenants").mkdir()  # no subdirectories -- no tenant exists yet

    assert count_valid_confirmed(slots, workspace_root=tmp_path) == 3


def load_pilots_document(path) -> dict:
    """C2/FR-010: reads a PILOTS.md-shaped file at `path`. Returns
    {"state": "missing"} if it does not exist; {"state": "malformed"} if it
    exists but does not contain exactly 4 well-formed fenced-JSON slots (a
    parse failure or the wrong slot count both count as malformed); else
    {"state": "ok", "summary_line": str, "slots": list[dict]}."""
    path = Path(path)
    if not path.exists():
        return {"state": "missing"}
    try:
        text = path.read_text(encoding="utf-8")
        slots = parse_pilot_slots(text)
    except (OSError, json.JSONDecodeError):
        return {"state": "malformed"}
    if len(slots) != 4:
        return {"state": "malformed"}
    return {"state": "ok", "summary_line": parse_summary_line(text), "slots": slots}


def gate_met(document: dict) -> bool:
    """C2/FR-010: the Phase 1 gate is unmet for any state other than "ok",
    regardless of any other record of agency onboarding that exists
    elsewhere -- the file's own presence and structural validity is
    required, not merely its claimed content."""
    if document["state"] != "ok":
        return False
    return count_valid_confirmed(document["slots"]) >= 3


def test_missing_pilots_file_treated_as_gate_unmet(tmp_path):
    document = load_pilots_document(tmp_path / "PILOTS.md")
    assert document["state"] == "missing"
    assert gate_met(document) is False


def test_malformed_pilots_file_treated_as_gate_unmet(tmp_path):
    bad_path = tmp_path / "PILOTS.md"
    bad_path.write_text("not a valid pilots document at all", encoding="utf-8")
    document = load_pilots_document(bad_path)
    assert document["state"] == "malformed"
    assert gate_met(document) is False


def test_wrong_slot_count_treated_as_malformed(load_text_fixture, tmp_path):
    text = load_text_fixture("pilots/valid_four_slots.md")
    truncated = text.split("## Slot 4")[0]  # only 3 slots remain
    bad_path = tmp_path / "PILOTS.md"
    bad_path.write_text(truncated, encoding="utf-8")
    document = load_pilots_document(bad_path)
    assert document["state"] == "malformed"
    assert gate_met(document) is False


def test_valid_pilots_file_reaches_ok_state_and_gate_met(load_text_fixture, tmp_path):
    text = load_text_fixture("pilots/three_confirmed.md")
    path = tmp_path / "PILOTS.md"
    path.write_text(text, encoding="utf-8")
    document = load_pilots_document(path)
    assert document["state"] == "ok"
    assert gate_met(document) is True


def test_real_pilots_md_reaches_ok_state():
    """Sanity check: the actual repository-root PILOTS.md (T020's
    deliverable) itself parses to state "ok"."""
    document = load_pilots_document(REPO_ROOT / "PILOTS.md")
    assert document["state"] == "ok"
    assert len(document["slots"]) == 4


def test_all_withdrawn_shows_zero_confirmed(load_text_fixture):
    """C3/FR-008 edge case: all 4 slots withdrawn still reports a correct,
    non-special-cased "0 of 4 confirmed"."""
    text = load_text_fixture("pilots/all_withdrawn.md")
    slots = parse_pilot_slots(text)
    assert count_valid_confirmed(slots) == 0
    assert parse_summary_line(text) == "0 of 4 confirmed — Phase 1 gate not met"


def test_non_pk_market_mode_fails_schema(schema, load_text_fixture):
    """C4/FR-012: market_mode is fixed to "PK" -- this feature never
    records a UK-market candidate, enforced at the schema level."""
    text = load_text_fixture("pilots/valid_four_slots.md")
    slot = parse_pilot_slots(text)[0]
    slot["market_mode"] = "UK"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(slot, schema)


def test_no_runtime_agent_file_references_pilots_md():
    """U1/FR-005: no agents/*/SOUL.md or skills/*.md file couples itself to
    PILOTS.md -- the manual-only boundary (adrs/ADR-004) must never be
    silently broken by a future edit to those runtime-facing files."""
    candidates = list((REPO_ROOT / "agents").rglob("SOUL.md")) + list(
        (REPO_ROOT / "skills").glob("*.md")
    )
    offenders = [
        p for p in candidates if "PILOTS.md" in p.read_text(encoding="utf-8")
    ]
    assert offenders == [], f"Runtime-agent coupling to PILOTS.md found in: {offenders}"
