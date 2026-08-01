import json
import copy
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_json(relative_path: str):
    with open(FIXTURES_DIR / relative_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def tenant_context():
    """The active tenant/session context (T006's fixture), per
    skills/multi-tenant-router.md. Returns a fresh copy so tests can't
    mutate a shared object across test runs."""
    return copy.deepcopy(_load_json("tenants/test_tenant.json"))


@pytest.fixture
def memory_state():
    """Factory for a fresh MEMORY.md-shaped state dict with configurable
    gemini_today_count and processed_ids, per data-model.md's Tenant entity."""

    def _make(gemini_today_count: int = 0, processed_ids=None):
        return {
            "gemini_today_count": gemini_today_count,
            "processed_ids": list(processed_ids or []),
        }

    return _make


@pytest.fixture
def load_fixture():
    """Generic loader for any JSON fixture under tests/fixtures/, by
    relative path, e.g. load_fixture('gemini/high_confidence_response.json')."""
    return _load_json


@pytest.fixture
def load_text_fixture():
    """Generic loader for any text fixture under tests/fixtures/."""

    def _load(relative_path: str) -> str:
        with open(FIXTURES_DIR / relative_path, encoding="utf-8") as f:
            return f.read()

    return _load
