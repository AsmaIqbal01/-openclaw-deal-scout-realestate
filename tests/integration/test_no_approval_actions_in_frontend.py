"""Automated guard against scope creep back into the deferred email-draft
approve/reject action (spec.md Scope Decision). The Approval Queue section
must remain read-only; WhatsApp /confirm or /discard is the sole channel.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_TERMS = ("approve", "reject")


def _assert_no_forbidden_terms(file_path: Path):
    text = file_path.read_text(encoding="utf-8").lower()
    for term in FORBIDDEN_TERMS:
        assert term not in text, f"'{term}' found in {file_path} — Approval Queue must stay read-only"


def test_index_html_has_no_approval_action_strings():
    _assert_no_forbidden_terms(REPO_ROOT / "dashboard" / "index.html")


def test_dashboard_js_has_no_approval_action_strings():
    _assert_no_forbidden_terms(REPO_ROOT / "dashboard" / "dashboard.js")
