// Deal Scout client dashboard — vanilla JS, no framework, no build step.
// Read-only: fetches /state and renders sections; sends no action requests
// of any kind (see spec.md Scope Decision) — the WhatsApp reply (/confirm
// or /discard) is the sole way a lead gets confirmed or dropped.

const POLL_INTERVAL_MS = 30000;

function getTenantIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get("tenant");
}

function showView(id) {
  document.querySelectorAll(".view").forEach((el) => {
    el.hidden = el.id !== id;
  });
}

function renderTenantSelector(tenants) {
  const list = document.getElementById("tenant-list");
  list.innerHTML = "";
  tenants.forEach((tenantId) => {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = "?tenant=" + encodeURIComponent(tenantId);
    a.textContent = tenantId;
    li.appendChild(a);
    list.appendChild(li);
  });
  showView("tenant-selector");
}

function renderPipelineStatus(data) {
  const badge = document.getElementById("status-badge");
  badge.textContent = data.last_run_status;
  badge.className = "badge " + data.last_run_status;
  document.getElementById("last-run-at").textContent =
    "Last run: " + data.last_run_at;
}

function renderLeadCounter(data) {
  document.getElementById("leads-today").textContent = data.leads_today;
  document.getElementById("leads-this-week").textContent = data.leads_this_week;
}

function renderQuotaGauge(data) {
  document.getElementById("quota-gauge").textContent =
    data.gemini_quota_used + "/20 used";
}

function renderCrmSync(data) {
  document.getElementById("crm-last-write-at").textContent =
    data.crm_last_write_at ? "Last write: " + data.crm_last_write_at : "No writes yet";
}

function renderMarketToggle(data) {
  // Read-only indicator only — see .market-toggle's pointer-events: none
  // in dashboard.css. Never bind an input/select here.
  document.getElementById("market-toggle").textContent = data.market_mode;
}

function formatTimeRemaining(seconds) {
  const mins = Math.floor(seconds / 60);
  const hrs = Math.floor(mins / 60);
  const remMins = mins % 60;
  if (hrs > 0) return hrs + "h " + remMins + "m remaining";
  return remMins + "m remaining";
}

// Read-only: displays contact/source/score/time-remaining only. No action
// control is ever rendered here — the agent's WhatsApp reply
// (per contracts/approval-commands.md) is the sole channel, per spec.md's
// Scope Decision and Constitution Principle III.
function renderApprovalQueue(queue) {
  const list = document.getElementById("approval-queue-list");
  list.innerHTML = "";
  queue.forEach((entry) => {
    const li = document.createElement("li");
    li.textContent =
      (entry.contact_name || "Unknown") +
      " — " + entry.lead_source +
      " — score " + entry.classification_score.toFixed(2) +
      " — " + formatTimeRemaining(entry.seconds_remaining);
    list.appendChild(li);
  });
}

// Read-only display of feature 003's approval-queue.json (004). Purely
// data-driven: status text/class always come from entry.status_label,
// received from the server response — this function never hardcodes any
// command-verb text of its own (research.md Decision 3). No action
// control of any kind is ever rendered here; WhatsApp remains the sole
// resolution channel, per spec.md FR-005.
function renderEmailDraftQueue(queue) {
  const list = document.getElementById("email-draft-queue-list");
  list.innerHTML = "";

  if (queue.state === "empty") {
    const li = document.createElement("li");
    li.textContent = "No email drafts yet";
    list.appendChild(li);
    return;
  }

  if (queue.state === "unavailable") {
    const li = document.createElement("li");
    li.textContent = "Unable to load email drafts";
    list.appendChild(li);
    return;
  }

  queue.entries.forEach((entry) => {
    const li = document.createElement("li");

    const badge = document.createElement("span");
    badge.className = "badge " + entry.status_label.toLowerCase().replace(/\s+/g, "-");
    badge.textContent = entry.status_label;
    li.appendChild(badge);

    li.appendChild(document.createTextNode(
      " " + entry.draft_subject + " → " + entry.recipient_email
    ));

    if (entry.reminder_seconds_remaining !== null) {
      li.appendChild(document.createTextNode(
        " (reminder in " + formatTimeRemaining(entry.reminder_seconds_remaining) + ")"
      ));
    }

    if (entry.archive_seconds_remaining !== null) {
      li.appendChild(document.createTextNode(
        " (auto-archives in " + formatTimeRemaining(entry.archive_seconds_remaining) + ")"
      ));
    }

    list.appendChild(li);
  });
}

function renderRecentLeads(data) {
  const body = document.getElementById("recent-leads-body");
  body.innerHTML = "";
  (data.recent_leads || []).forEach((lead) => {
    const row = document.createElement("tr");
    row.innerHTML =
      "<td>" + lead.classification_score.toFixed(2) + "</td>" +
      "<td>" + lead.source + "</td>" +
      "<td>" + (lead.contact_name || "Unknown") + "</td>";
    row.addEventListener("click", () => {
      if (window.renderScoreRadar) {
        window.renderScoreRadar(lead);
      }
    });
    body.appendChild(row);
  });
}

function renderDashboard(data) {
  renderPipelineStatus(data);
  renderLeadCounter(data);
  renderQuotaGauge(data);
  renderCrmSync(data);
  renderMarketToggle(data);
  renderRecentLeads(data);
  if (window.renderApprovalQueue) {
    window.renderApprovalQueue(data.approval_queue || []);
  }
  if (window.renderEmailDraftQueue) {
    window.renderEmailDraftQueue(data.email_draft_queue || { state: "empty", entries: [] });
  }
  showView("dashboard-view");
}

async function loadState() {
  const tenantId = getTenantIdFromUrl();
  const url = tenantId
    ? "/state?tenant=" + encodeURIComponent(tenantId)
    : "/state";
  const response = await fetch(url);
  const body = await response.json();

  if (body.status === "select_tenant") {
    renderTenantSelector(body.tenants);
    return;
  }
  if (body.status === "tenant_not_configured") {
    showView("tenant-not-configured");
    return;
  }
  if (body.status === "no_runs_yet") {
    showView("no-runs-yet");
    return;
  }
  renderDashboard(body.data);
}

document.addEventListener("DOMContentLoaded", () => {
  loadState();
  setInterval(loadState, POLL_INTERVAL_MS);
});

window.renderApprovalQueue = renderApprovalQueue;
window.renderEmailDraftQueue = renderEmailDraftQueue;
