// Score Radar (skills/remote-dashboard.md Section 8) — Chart.js radar
// chart rendered in a modal when a Recent Leads row is clicked.

let radarChartInstance = null;

const RADAR_AXIS_LABELS = {
  contact_completeness: "Contact completeness",
  intent_clarity: "Intent clarity",
  budget_signal: "Budget signal",
  urgency: "Urgency",
  data_integrity: "Data integrity",
};

const TIER_FILL_COLOR = {
  teal: "rgba(20, 184, 166, 0.4)",
  amber: "rgba(245, 158, 11, 0.4)",
};

function renderScoreRadar(lead) {
  const modal = document.getElementById("radar-modal");
  const content = modal.querySelector(".modal-content");
  content.classList.remove("tier-teal", "tier-amber");
  content.classList.add("tier-" + lead.tier_color);

  const labels = Object.keys(RADAR_AXIS_LABELS).map((k) => RADAR_AXIS_LABELS[k]);
  const values = Object.keys(RADAR_AXIS_LABELS).map((k) => lead.radar[k]);

  const ctx = document.getElementById("radar-canvas").getContext("2d");
  if (radarChartInstance) {
    radarChartInstance.destroy();
  }
  radarChartInstance = new Chart(ctx, {
    type: "radar",
    data: {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor: TIER_FILL_COLOR[lead.tier_color] || "rgba(128,128,128,0.4)",
        },
      ],
    },
    options: { scales: { r: { min: 0, max: 1 } } },
  });

  document.getElementById("radar-caption").textContent = lead.lead_quality_reason;
  const actionBadge = document.getElementById("radar-action-badge");
  actionBadge.textContent = lead.recommended_action;

  modal.hidden = false;
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("radar-modal-close").addEventListener("click", () => {
    document.getElementById("radar-modal").hidden = true;
  });
});

window.renderScoreRadar = renderScoreRadar;
