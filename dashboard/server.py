"""Minimal Python-stdlib server for the Deal Scout client dashboard.

Read-only, per specs/002-pk-client-dashboard/research.md Decision 1/2: this
server never writes dashboard-state.json (the Orchestrator does, via
existing agent behavior) and never processes leads or sends notifications —
it only reads and serves. See Constitution Principle IV: this must never
become a second orchestrator.

Standard library only (http.server, json) — zero new dependencies, per
Constitution Principle II.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

TIMEOUT_HOURS = 2  # matches feature 001's Tier 2 approval window (FR-006/007/008)
TIER_AUTO_MIN = 0.9
TIER_REVIEW_MIN = 0.7
PORT = 18790

# 004-pk-dashboard-email-queue: mirrors tests/pipeline_sim.py's
# STALE_REMINDER_HOURS/STALE_ARCHIVE_HOURS (feature 003) so the WhatsApp
# re-notification clock and this dashboard countdown can't silently drift
# apart (research.md Decision 2).
EMAIL_QUEUE_REMINDER_HOURS = 4
EMAIL_QUEUE_ARCHIVE_HOURS = 24
EMAIL_QUEUE_DISPLAY_CAP = 10


def load_dashboard_state(tenant_id: str, workspace_root: Path) -> dict | None:
    """Reads workspace_root/tenants/{tenant_id}/dashboard-state.json.
    Returns None if it does not exist (FR-013 "no runs yet")."""
    path = Path(workspace_root) / "tenants" / tenant_id / "dashboard-state.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def is_known_tenant(tenant_id: str, workspace_root: Path) -> bool:
    """A tenant is 'configured' if its USER.md exists, per
    skills/multi-tenant-router.md (FR-014)."""
    return (Path(workspace_root) / "tenants" / tenant_id / "USER.md").exists()


def list_active_tenants(workspace_root: Path) -> list:
    """FR-012: only tenants with active: true in USER.md."""
    tenants_dir = Path(workspace_root) / "tenants"
    if not tenants_dir.exists():
        return []
    active = []
    for entry in sorted(tenants_dir.iterdir()):
        user_md = entry / "USER.md"
        if not user_md.exists():
            continue
        with open(user_md, encoding="utf-8") as f:
            config = json.load(f)
        if config.get("active"):
            active.append(entry.name)
    return active


def classify_tier_color(score: float) -> str:
    """Maps a classification_score to the tier coloring from
    skills/remote-dashboard.md Section 8 (FR-010)."""
    if score >= TIER_AUTO_MIN:
        return "teal"
    if score >= TIER_REVIEW_MIN:
        return "amber"
    return "none"


def seconds_remaining(queued_at_iso: str, now: datetime) -> float:
    """FR-006: time remaining before the 2-hour Tier 2 timeout. Never
    negative — floors at 0 once the window has elapsed."""
    queued_at = datetime.fromisoformat(queued_at_iso)
    elapsed = (now - queued_at).total_seconds()
    remaining = TIMEOUT_HOURS * 3600 - elapsed
    return max(remaining, 0.0)


# --- 004-pk-dashboard-email-queue: Email Draft Queue (read-only display of
#     feature 003's approval-queue.json) ---

def load_email_draft_queue_raw(tenant_id: str, workspace_root: Path) -> tuple[str, list]:
    """Reads workspace_root/tenants/{tenant_id}/approval-queue.json.

    Returns ("empty", []) if the file does not exist, or exists but parses
    to an empty list (both mean "nothing to review" -- FR-008). Returns
    ("unavailable", []) if the file exists but fails to parse (FR-009).
    Returns ("entries", raw_list) otherwise."""
    path = Path(workspace_root) / "tenants" / tenant_id / "approval-queue.json"
    if not path.exists():
        return "empty", []
    try:
        with open(path, encoding="utf-8") as f:
            raw_list = json.load(f)
    except (json.JSONDecodeError, OSError):
        return "unavailable", []
    if not raw_list:
        return "empty", []
    return "entries", raw_list


def derive_status_label(entry: dict) -> str:
    """FR-003's exact 5-way derivation order -- first match wins."""
    if entry.get("auto_archived"):
        return "Auto-Archived"
    if entry.get("rejected"):
        return "Rejected"
    if entry.get("approved"):
        return "Sent" if entry.get("sent_at") else "Send Failed"
    return "Pending"


def enrich_email_draft_queue_entry(entry: dict, now: datetime) -> dict:
    """Adds status_label plus (only when Pending) reminder/archive
    countdowns to a copy of entry, mirroring _enrich()'s existing
    tier_color/seconds_remaining pattern for the other two sections."""
    enriched = dict(entry)
    status_label = derive_status_label(entry)
    enriched["status_label"] = status_label

    if status_label != "Pending":
        enriched["reminder_seconds_remaining"] = None
        enriched["archive_seconds_remaining"] = None
        return enriched

    queued_at = datetime.fromisoformat(entry["queued_at"])
    elapsed = (now - queued_at).total_seconds()
    enriched["reminder_seconds_remaining"] = max(
        EMAIL_QUEUE_REMINDER_HOURS * 3600 - elapsed, 0.0
    )
    enriched["archive_seconds_remaining"] = max(
        EMAIL_QUEUE_ARCHIVE_HOURS * 3600 - elapsed, 0.0
    )
    return enriched


def build_email_draft_queue_response(tenant_id: str, workspace_root: Path, now: datetime) -> dict:
    """Assembles the email_draft_queue key per
    contracts/email-draft-queue-response.md: reads the raw queue (FR-008/
    FR-009), sorts and caps to the 10 most recently queued entries
    (FR-010), then enriches each survivor."""
    state, raw_entries = load_email_draft_queue_raw(tenant_id, workspace_root)
    if state != "entries":
        return {"state": state, "entries": []}

    sorted_entries = sorted(raw_entries, key=lambda e: e["queued_at"], reverse=True)
    capped = sorted_entries[:EMAIL_QUEUE_DISPLAY_CAP]
    return {
        "state": "entries",
        "entries": [enrich_email_draft_queue_entry(e, now) for e in capped],
    }


def _enrich(state: dict, now: datetime) -> dict:
    """Adds derived, display-ready fields to a raw Dashboard State document
    without mutating the stored file's own shape — the schema in
    contracts/dashboard-state-schema.json describes the file on disk; this
    enrichment happens only in the served response."""
    enriched = dict(state)
    enriched["recent_leads"] = [
        {**lead, "tier_color": classify_tier_color(lead["classification_score"])}
        for lead in state.get("recent_leads", [])
    ]
    enriched["approval_queue"] = [
        {**entry, "seconds_remaining": seconds_remaining(entry["queued_at"], now)}
        for entry in state.get("approval_queue", [])
    ]
    return enriched


def handle_state_request(
    tenant_id: str | None,
    workspace_root: Path,
    known_tenants: list | None = None,
    now: datetime | None = None,
) -> dict:
    """Implements all 4 response shapes from contracts/dashboard-api.md.
    `known_tenants` and `now` are injectable for deterministic tests;
    production use leaves both None (real tenant scan / real current time)."""
    now = now or datetime.now(timezone.utc)

    if not tenant_id:
        return {
            "status": "select_tenant",
            "tenants": known_tenants if known_tenants is not None else list_active_tenants(workspace_root),
        }

    if not is_known_tenant(tenant_id, workspace_root):
        return {"status": "tenant_not_configured", "tenant_id": tenant_id}

    state = load_dashboard_state(tenant_id, workspace_root)
    if state is None:
        return {"status": "no_runs_yet", "tenant_id": tenant_id}

    # Defense in depth for FR-011: never serve a document whose own
    # tenant_id doesn't match the tenant actually requested.
    if state.get("tenant_id") != tenant_id:
        return {"status": "tenant_not_configured", "tenant_id": tenant_id}

    enriched = _enrich(state, now)
    enriched["email_draft_queue"] = build_email_draft_queue_response(tenant_id, workspace_root, now)
    return {"status": "ok", "data": enriched}


class DashboardRequestHandler(SimpleHTTPRequestHandler):
    """Serves dashboard/ static files, plus GET /state?tenant={tenant_id}."""

    workspace_root: Path = Path.home() / ".openclaw" / "workspace"

    def do_GET(self):  # noqa: N802 (stdlib method name)
        parsed = urlparse(self.path)
        if parsed.path == "/state":
            query = parse_qs(parsed.query)
            tenant_id = (query.get("tenant") or [None])[0]
            response = handle_state_request(tenant_id, self.workspace_root)
            body = json.dumps(response).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


def run(workspace_root: Path | None = None, port: int = PORT) -> None:
    if workspace_root is not None:
        DashboardRequestHandler.workspace_root = Path(workspace_root)
    server = ThreadingHTTPServer(("127.0.0.1", port), DashboardRequestHandler)
    print(f"Dashboard serving on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    import os

    os.chdir(Path(__file__).parent)
    run()
