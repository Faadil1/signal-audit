/* ==========================================================================
   SignalAudit — The Trading Gate
   Presentation layer only. All values below are hardcoded from the
   already-validated backend output (signal_audit.py, SIMULATED mode).
   No live computation. No network calls. No CDN. No dependencies.
   ========================================================================== */

(function () {
  "use strict";

  // ---------------------------------------------------------------------
  // Hardcoded scenario data — copied verbatim from validated backend runs:
  //   python signal_audit.py --signal_file simulated_signals.json --output json
  //   python signal_audit.py --signal_file simulated_signals_clean.json --output json
  // ---------------------------------------------------------------------

  var SCENARIOS = {
    abort: {
      verdict: "ABORT",
      regime: "VOLATILE_BREAKDOWN (HIGH confidence)",
      flags: [
        { id: "FLAG_003", name: "FUNDING_RATE", severity: "CRITICAL", value: "+0.112%/8h  (threshold \u2265 0.10%)" },
        { id: "FLAG_004", name: "ONCHAIN_FLOW", severity: "HIGH", value: "+6,800 BTC net inflow/24h  (threshold > 5,000 BTC)" }
      ],
      noTradeConditions: [
        "NT-1: CRITICAL flag active \u2014 FUNDING_RATE",
        "NT-2: Regime VOLATILE_BREAKDOWN \u2014 breakout strategies have negative expected value"
      ],
      spec: [
        ["Entry", "DO NOT ENTER. No-trade condition active."],
        ["Position size", "0% \u2014 no position."],
        ["Stop loss", "N/A \u2014 no position."],
        ["Re-evaluate when", "Funding rate drops below +0.05%/8h, exchange net flows shift to outflow, and regime shifts away from VOLATILE_BREAKDOWN."],
        ["Monitor condition", "Re-run SignalAudit when funding cools and exchange outflows resume."]
      ],
      evidenceMode: "SIMULATED",
      historical: "ASSUMED"
    },

    proceed: {
      verdict: "PROCEED",
      regime: "TRENDING_UP (HIGH confidence)",
      flags: [],
      noTradeConditions: [],
      spec: [
        ["Entry", "Original entry conditions apply \u2014 no modification required."],
        ["Exit", "Original exit conditions apply \u2014 no modification required."],
        ["Position size", "Full position size per original risk rules."],
        ["Stop loss", "Original stop distance applies."],
        ["Monitor condition", "Re-run SignalAudit if funding rate rises above 0.08%/8h or exchange inflows exceed 5,000 BTC/24h."]
      ],
      evidenceMode: "SIMULATED",
      historical: "ASSUMED"
    }
  };

  // ---------------------------------------------------------------------
  // DOM references
  // ---------------------------------------------------------------------

  var btnAbort = document.getElementById("btn-abort");
  var btnProceed = document.getElementById("btn-proceed");
  var gateRig = document.getElementById("gate-rig");
  var gateStatusValue = document.getElementById("gate-status-value");
  var resultPanel = document.getElementById("result-panel");
  var resultVerdict = document.getElementById("result-verdict");
  var resultRegime = document.getElementById("result-regime");
  var flagList = document.getElementById("flag-list");
  var ntSection = document.getElementById("nt-section");
  var ntList = document.getElementById("nt-list");
  var specGrid = document.getElementById("spec-grid");
  var pillEvidenceMode = document.getElementById("pill-evidence-mode");
  var pillHistorical = document.getElementById("pill-historical");

  var isAnimating = false;

  // ---------------------------------------------------------------------
  // Render helpers
  // ---------------------------------------------------------------------

  function clearChildren(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function renderFlags(flags) {
    clearChildren(flagList);
    if (!flags.length) {
      var none = document.createElement("p");
      none.className = "flag-none";
      none.textContent = "All flags clear. No risk signals triggered.";
      flagList.appendChild(none);
      return;
    }
    flags.forEach(function (flag) {
      var row = document.createElement("div");
      row.className = "flag-row";

      var sev = document.createElement("span");
      sev.className = "flag-sev " + (flag.severity === "CRITICAL" ? "sev-critical" : "sev-high");
      sev.textContent = flag.severity;

      var id = document.createElement("span");
      id.className = "flag-id";
      id.textContent = flag.id + " " + flag.name;

      var val = document.createElement("span");
      val.className = "flag-value";
      val.textContent = flag.value;

      row.appendChild(sev);
      row.appendChild(id);
      row.appendChild(val);
      flagList.appendChild(row);
    });
  }

  function renderNoTrade(conditions) {
    clearChildren(ntList);
    if (!conditions.length) {
      ntSection.hidden = true;
      return;
    }
    ntSection.hidden = false;
    conditions.forEach(function (c) {
      var li = document.createElement("li");
      li.textContent = c;
      ntList.appendChild(li);
    });
  }

  function renderSpec(spec) {
    clearChildren(specGrid);
    spec.forEach(function (pair) {
      var dt = document.createElement("dt");
      dt.textContent = pair[0];
      var dd = document.createElement("dd");
      dd.textContent = pair[1];
      specGrid.appendChild(dt);
      specGrid.appendChild(dd);
    });
  }

  function renderScenario(key) {
    var data = SCENARIOS[key];

    resultVerdict.textContent = data.verdict;
    resultVerdict.className = "result-verdict " + (key === "abort" ? "v-abort" : "v-proceed");
    resultRegime.textContent = data.regime;

    renderFlags(data.flags);
    renderNoTrade(data.noTradeConditions);
    renderSpec(data.spec);

    pillEvidenceMode.textContent = "Evidence mode: " + data.evidenceMode;
    pillHistorical.textContent = "Historical reference: " + data.historical;

    resultPanel.hidden = false;
  }

  // ---------------------------------------------------------------------
  // Gate animation sequencing
  // ---------------------------------------------------------------------

  function runScenario(key) {
    if (isAnimating) return;
    isAnimating = true;

    btnAbort.disabled = true;
    btnProceed.disabled = true;

    // Reset to idle, trigger scan sweep
    gateRig.setAttribute("data-state", "idle");
    gateStatusValue.textContent = "SCANNING\u2026";
    gateStatusValue.className = "gate-status-value";
    gateRig.classList.remove("scanning");

    // Force reflow so the scan animation can re-trigger
    void gateRig.offsetWidth;
    gateRig.classList.add("scanning");

    window.setTimeout(function () {
      gateRig.setAttribute("data-state", key);

      if (key === "abort") {
        gateStatusValue.textContent = "GATE CLOSED";
        gateStatusValue.className = "gate-status-value state-abort";
      } else {
        gateStatusValue.textContent = "GATE OPEN";
        gateStatusValue.className = "gate-status-value state-proceed";
      }

      renderScenario(key);

      window.setTimeout(function () {
        resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 150);

      btnAbort.disabled = false;
      btnProceed.disabled = false;
      isAnimating = false;
    }, 950);
  }

  // ---------------------------------------------------------------------
  // Wire up
  // ---------------------------------------------------------------------

  btnAbort.addEventListener("click", function () { runScenario("abort"); });
  btnProceed.addEventListener("click", function () { runScenario("proceed"); });

})();
