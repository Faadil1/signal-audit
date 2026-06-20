/* ==========================================================================
   SignalAudit — Mission Control
   Presentation layer only. Scenario facts below are unchanged and copied
   verbatim from validated backend runs:
     python signal_audit.py --signal_file simulated_signals.json --output json
     python signal_audit.py --signal_file simulated_signals_clean.json --output json
   No live computation. No network calls. No CDN. No dependencies.
   ========================================================================== */

(function () {
  "use strict";

  // ---------------------------------------------------------------------
  // Scenario data — facts unchanged from validated backend output.
  // checklistRows maps the 5 displayed categories to the 6 underlying
  // flags. Each row is GO unless any of its mapped flags is triggered.
  // ---------------------------------------------------------------------

  var SCENARIOS = {
    abort: {
      verdict: "ABORT",
      statusLabel: "RUN HOLD",
      clock: "T-00:17",
      checklist: {
        market:      { state: "go",   detail: "1.668x 20D avg volume" },
        derivatives: { state: "nogo", detail: "+0.112%/8h \u2265 0.10% threshold" },
        onchain:     { state: "nogo", detail: "+6,800 BTC inflow > 5,000 threshold" },
        sentiment:   { state: "go",   detail: "Fear & Greed = 79" },
        narrative:   { state: "go",   detail: "2.1x 7D baseline" }
      },
      noTradeConditions: [
        "NT-1: CRITICAL flag active \u2014 FUNDING_RATE",
        "NT-2: Regime VOLATILE_BREAKDOWN \u2014 breakout strategies have negative expected value"
      ],
      plan: [
        ["Entry", "DO NOT ENTER. No-trade condition active."],
        ["Position size", "0% \u2014 no execution authority."],
        ["Stop loss", "N/A \u2014 no position."],
        ["Re-evaluate when", "Funding rate drops below +0.05%/8h, exchange net flows shift to outflow, and regime shifts away from VOLATILE_BREAKDOWN."],
        ["Status", "No execution authority \u2014 no position."]
      ]
    },

    proceed: {
      verdict: "PROCEED",
      statusLabel: "CLEAR TO RUN",
      clock: "T-00:00",
      checklist: {
        market:      { state: "go", detail: "1.85x 20D avg volume" },
        derivatives: { state: "go", detail: "+0.03%/8h, well below threshold" },
        onchain:     { state: "go", detail: "-1,200 BTC net outflow" },
        sentiment:   { state: "go", detail: "Fear & Greed = 58" },
        narrative:   { state: "go", detail: "1.1x 7D baseline" }
      },
      noTradeConditions: [],
      plan: [
        ["Entry", "Original entry conditions apply \u2014 no modification required."],
        ["Exit", "Original exit conditions apply \u2014 no modification required."],
        ["Position size", "Full position size per original risk rules."],
        ["Stop loss", "Original stop distance applies."],
        ["Status", "Original terms apply."]
      ]
    }
  };

  var ROW_ORDER = ["market", "derivatives", "onchain", "sentiment", "narrative"];

  // ---------------------------------------------------------------------
  // DOM references
  // ---------------------------------------------------------------------

  var btnAbort = document.getElementById("btn-abort");
  var btnProceed = document.getElementById("btn-proceed");

  var statusPanel = document.getElementById("status-panel");
  var statusClock = document.getElementById("status-clock");
  var statusVerdict = document.getElementById("status-verdict");
  var statusAuthority = document.getElementById("status-authority");

  var ntPanel = document.getElementById("nt-panel");
  var ntList = document.getElementById("nt-list");

  var planPanel = document.getElementById("plan-panel");
  var planGrid = document.getElementById("plan-grid");

  var evidencePanel = document.getElementById("evidence-panel");
  var pillSignalChannel = document.getElementById("pill-signal-channel");
  var pillEvidenceSeal = document.getElementById("pill-evidence-seal");

  var isAnimating = false;
  var pendingTimers = [];

  // ---------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------

  function clearChildren(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function clearPendingTimers() {
    pendingTimers.forEach(function (t) { window.clearTimeout(t); });
    pendingTimers = [];
  }

  function resetChecklist() {
    ROW_ORDER.forEach(function (key) {
      var row = document.querySelector('.check-row[data-row="' + key + '"]');
      var stateEl = document.getElementById("state-" + key);
      var detailEl = document.getElementById("detail-" + key);
      row.classList.remove("resolved");
      stateEl.textContent = "STANDBY";
      stateEl.className = "check-state";
      detailEl.textContent = "\u2014";
    });
  }

  function renderNoTrade(conditions) {
    clearChildren(ntList);
    if (!conditions.length) {
      ntPanel.hidden = true;
      return;
    }
    ntPanel.hidden = false;
    conditions.forEach(function (c) {
      var li = document.createElement("li");
      li.textContent = c;
      ntList.appendChild(li);
    });
  }

  function renderPlan(plan) {
    clearChildren(planGrid);
    plan.forEach(function (pair) {
      var dt = document.createElement("dt");
      dt.textContent = pair[0];
      var dd = document.createElement("dd");
      dd.textContent = pair[1];
      planGrid.appendChild(dt);
      planGrid.appendChild(dd);
    });
    planPanel.hidden = false;
  }

  // ---------------------------------------------------------------------
  // Sequencing
  // ---------------------------------------------------------------------

  function runScenario(key) {
    if (isAnimating) return;
    isAnimating = true;
    clearPendingTimers();

    btnAbort.disabled = true;
    btnProceed.disabled = true;

    var data = SCENARIOS[key];

    // Reset to standby
    statusPanel.setAttribute("data-state", "idle");
    statusClock.textContent = "T-00:00";
    statusVerdict.textContent = "CHECKING\u2026";
    statusAuthority.textContent = "PENDING";
    resetChecklist();
    ntPanel.hidden = true;
    planPanel.hidden = true;
    evidencePanel.hidden = true;

    // Staggered GO/NO-GO reveal — one row at a time, ~220ms apart
    ROW_ORDER.forEach(function (rowKey, i) {
      var t = window.setTimeout(function () {
        var rowData = data.checklist[rowKey];
        var row = document.querySelector('.check-row[data-row="' + rowKey + '"]');
        var stateEl = document.getElementById("state-" + rowKey);
        var detailEl = document.getElementById("detail-" + rowKey);

        detailEl.textContent = rowData.detail;
        stateEl.textContent = rowData.state === "go" ? "GO" : "NO-GO";
        stateEl.className = "check-state " + (rowData.state === "go" ? "go" : "nogo");
        row.classList.add("resolved");
      }, 180 + i * 220);
      pendingTimers.push(t);
    });

    // After checklist finishes, resolve status panel + plan + evidence
    var resolveDelay = 180 + ROW_ORDER.length * 220 + 200;
    var t2 = window.setTimeout(function () {
      statusPanel.setAttribute("data-state", key);
      statusClock.textContent = data.clock;
      statusVerdict.textContent = data.statusLabel;
      statusAuthority.textContent = key === "abort" ? "NONE" : "GRANTED";

      renderNoTrade(data.noTradeConditions);
      renderPlan(data.plan);

      pillSignalChannel.textContent = "Signal channel: SIMULATED";
      pillEvidenceSeal.textContent = "Evidence seal: ASSUMED";
      evidencePanel.hidden = false;

      var t3 = window.setTimeout(function () {
        statusPanel.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
      pendingTimers.push(t3);

      btnAbort.disabled = false;
      btnProceed.disabled = false;
      isAnimating = false;
    }, resolveDelay);
    pendingTimers.push(t2);
  }

  // ---------------------------------------------------------------------
  // Wire up
  // ---------------------------------------------------------------------

  btnAbort.addEventListener("click", function () { runScenario("abort"); });
  btnProceed.addEventListener("click", function () { runScenario("proceed"); });

})();
