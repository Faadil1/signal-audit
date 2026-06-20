/* ==========================================================================
   SignalAudit — Standing Order Registry
   Presentation layer only. Scenario facts below are unchanged and copied
   verbatim from validated backend runs:
     python signal_audit.py --signal_file simulated_signals.json --output json
     python signal_audit.py --signal_file simulated_signals_clean.json --output json
   No live computation. No network calls. No CDN. No dependencies.
   Motion is deliberately slow (250-900ms) — restraint is the message.
   ========================================================================== */

(function () {
  "use strict";

  // ---------------------------------------------------------------------
  // Scenario data — facts unchanged from validated backend output.
  // ---------------------------------------------------------------------

  var SCENARIOS = {
    abort: {
      verdict: "ABORT",
      statusText: "ORDER HOLDS",
      rationale: "Order holds. Execution authority remains none. FLAG_003 is CRITICAL and NT conditions are active \u2014 the conditions written in advance were not met.",
      authority: "NONE \u2014 order holds",
      flags: [
        "FLAG_003  FUNDING_RATE  CRITICAL \u2014 +0.112%/8h  (threshold \u2265 0.10%/8h, longs overheated)",
        "FLAG_004  ONCHAIN_FLOW  HIGH \u2014 +6,800 BTC net inflow/24h  (threshold > 5,000 BTC, sell pressure)"
      ],
      noTradeConditions: [
        "NT-1: CRITICAL flag active \u2014 FUNDING_RATE",
        "NT-2: Regime VOLATILE_BREAKDOWN \u2014 breakout strategies have negative expected value"
      ],
      terms: [
        ["Entry", "DO NOT ENTER. No-trade condition active."],
        ["Position size", "0% \u2014 no position."],
        ["Stop loss", "N/A \u2014 no position."],
        ["Re-evaluate when", "Funding rate drops below +0.05%/8h, exchange net flows shift to outflow, and regime shifts away from VOLATILE_BREAKDOWN."]
      ]
    },

    proceed: {
      verdict: "PROCEED",
      statusText: "ORDER OPENS",
      rationale: "Order opens. Original terms apply. All signals cited in the order are clear \u2014 nothing was improvised, nothing was decided in the moment.",
      authority: "GRANTED \u2014 order opens",
      flags: [],
      noTradeConditions: [],
      terms: [
        ["Entry", "Original entry conditions apply \u2014 no modification required."],
        ["Exit", "Original exit conditions apply \u2014 no modification required."],
        ["Position size", "Full position size per original risk rules."],
        ["Stop loss", "Original stop distance applies."]
      ]
    }
  };

  // ---------------------------------------------------------------------
  // DOM references
  // ---------------------------------------------------------------------

  var btnAbort = document.getElementById("btn-abort");
  var btnProceed = document.getElementById("btn-proceed");

  var seal = document.getElementById("seal");
  var orderAuthority = document.getElementById("order-authority");
  var orderFold = document.getElementById("order-fold");
  var orderStatus = document.getElementById("order-status");
  var orderRationale = document.getElementById("order-rationale");

  var flagsSection = document.getElementById("flags-section");
  var orderFlags = document.getElementById("order-flags");

  var ntSection = document.getElementById("nt-section");
  var orderNt = document.getElementById("order-nt");

  var orderTerms = document.getElementById("order-terms");
  var badgeEvidence = document.getElementById("badge-evidence");

  var isAnimating = false;

  // ---------------------------------------------------------------------
  // Render helpers
  // ---------------------------------------------------------------------

  function clearChildren(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function renderFlags(flags) {
    clearChildren(orderFlags);
    if (!flags.length) {
      flagsSection.hidden = true;
      return;
    }
    flagsSection.hidden = false;
    flags.forEach(function (text) {
      var li = document.createElement("li");
      li.textContent = text;
      orderFlags.appendChild(li);
    });
  }

  function renderNoTrade(conditions) {
    clearChildren(orderNt);
    if (!conditions.length) {
      ntSection.hidden = true;
      return;
    }
    ntSection.hidden = false;
    conditions.forEach(function (text) {
      var li = document.createElement("li");
      li.textContent = text;
      orderNt.appendChild(li);
    });
  }

  function renderTerms(terms) {
    clearChildren(orderTerms);
    terms.forEach(function (pair) {
      var dt = document.createElement("dt");
      dt.textContent = pair[0];
      var dd = document.createElement("dd");
      dd.textContent = pair[1];
      orderTerms.appendChild(dt);
      orderTerms.appendChild(dd);
    });
  }

  // ---------------------------------------------------------------------
  // Sequencing — slow, deliberate. Two beats: seal reacts, then fold opens.
  // ---------------------------------------------------------------------

  function runScenario(key) {
    if (isAnimating) return;
    isAnimating = true;

    btnAbort.disabled = true;
    btnProceed.disabled = true;

    var data = SCENARIOS[key];

    seal.setAttribute("data-state", "idle");
    orderFold.classList.remove("open");
    orderAuthority.textContent = "NONE \u2014 reviewing";

    // Beat 1: the seal reacts.
    window.setTimeout(function () {
      seal.setAttribute("data-state", key);
      orderAuthority.textContent = data.authority;
    }, 250);

    // Beat 2: the fold opens, content renders within it.
    window.setTimeout(function () {
      orderStatus.textContent = data.statusText;
      orderStatus.className = "order-status " + (key === "abort" ? "status-abort" : "status-proceed");
      orderRationale.textContent = data.rationale;

      renderFlags(data.flags);
      renderNoTrade(data.noTradeConditions);
      renderTerms(data.terms);

      badgeEvidence.textContent = "Evidence seal: ASSUMED";

      orderFold.classList.add("open");

      window.setTimeout(function () {
        orderFold.scrollIntoView({ behavior: "smooth", block: "center" });
      }, 250);

      btnAbort.disabled = false;
      btnProceed.disabled = false;
      isAnimating = false;
    }, 700);
  }

  // ---------------------------------------------------------------------
  // Wire up
  // ---------------------------------------------------------------------

  btnAbort.addEventListener("click", function () { runScenario("abort"); });
  btnProceed.addEventListener("click", function () { runScenario("proceed"); });

})();
