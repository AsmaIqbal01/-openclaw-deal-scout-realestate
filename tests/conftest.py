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


@pytest.fixture
def dashboard_workspace_factory(tmp_path):
    """Builds a temp workspace/tenants/ tree mimicking the real
    workspace/tenants/{tenant_id}/ layout, for dashboard/server.py tests.

    Usage: dashboard_workspace_factory({"tenant-id": {"active": True, "state": {...} or None}})
    Returns the temp workspace root (a Path) to pass as workspace_root."""

    def _make(tenants: dict) -> Path:
        tenants_dir = tmp_path / "tenants"
        tenants_dir.mkdir(exist_ok=True)
        for tenant_id, cfg in tenants.items():
            t_dir = tenants_dir / tenant_id
            t_dir.mkdir(exist_ok=True)
            (t_dir / "USER.md").write_text(
                json.dumps({"tenant_id": tenant_id, "active": cfg.get("active", True)}),
                encoding="utf-8",
            )
            if cfg.get("state") is not None:
                (t_dir / "dashboard-state.json").write_text(
                    json.dumps(cfg["state"]), encoding="utf-8"
                )
        return tmp_path

    return _make
