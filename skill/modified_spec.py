"""
Modified strategy spec generator.
Always returns a complete ModifiedStrategySpec dict regardless of verdict.
Three templates: PROCEED | REDUCE_RISK | ABORT
Evidence mode propagated from caller.
"""

from __future__ import annotations
from typing import List, Literal


def generate_modified_spec(
    verdict_status: Literal["PROCEED", "REDUCE_RISK", "ABORT"],
    hypothesis: str,
    regime: dict,
    active_flags: List[dict],
    no_trade_conditions: List[str],
    evidence_mode: Literal["LIVE_CMC", "SIMULATED", "ASSUMED"] = "SIMULATED",
) -> dict:
    """
    Returns a ModifiedStrategySpec-compatible dict.
    modified_strategy_spec is present in every output path — AC-3.
    """
    regime_label = regime.get("label", "UNKNOWN")
    regime_conf = regime.get("confidence", "UNKNOWN")

    active_flag_ids = ", ".join(f["id"] for f in active_flags if f["triggered"]) or "None"

    if verdict_status == "PROCEED":
        return _proceed_template(
            hypothesis, regime_label, regime_conf, active_flag_ids, evidence_mode
        )
    elif verdict_status == "REDUCE_RISK":
        return _reduce_risk_template(
            hypothesis, regime_label, regime_conf, active_flags, evidence_mode
        )
    else:  # ABORT
        return _abort_template(
            hypothesis, regime_label, no_trade_conditions, active_flag_ids, evidence_mode
        )


# ── PROCEED ───────────────────────────────────────────────────────────────────

def _proceed_template(hypothesis, regime_label, regime_conf, active_flag_ids, evidence_mode):
    return {
        "hypothesis": hypothesis,
        "regime_gate": f"Only enter when regime is {regime_label} with {regime_conf} confidence.",
        "entry_condition": "Original entry conditions apply — no modification required.",
        "exit_condition": "Original exit conditions apply — no modification required.",
        "position_size_rule": "Full position size per original risk rules.",
        "stop_loss": "Original stop distance applies.",
        "no_trade_condition": "None active. Continue monitoring FLAG_003 and FLAG_004.",
        "backtest_hypothesis": (
            f"{hypothesis} "
            f"[Regime gate: {regime_label}, confidence {regime_conf}, all flags clear.]"
        ),
        "re_evaluate_when": None,
        "monitor_condition": "Re-run SignalAudit if funding rate rises above 0.08%/8h or exchange inflows exceed 5,000 BTC/24h.",
        "evidence_status": evidence_mode,
    }


# ── REDUCE_RISK ───────────────────────────────────────────────────────────────

def _reduce_risk_template(hypothesis, regime_label, regime_conf, active_flags, evidence_mode):
    triggered_high = [f for f in active_flags if f["triggered"] and f["severity"] == "HIGH"]
    flag_ids = ", ".join(f["id"] for f in triggered_high) or "None"

    return {
        "hypothesis": hypothesis,
        "regime_gate": (
            f"Only enter when regime is {regime_label} — wait for HIGH confidence before adding to position."
        ),
        "entry_condition": (
            "Original entry signal required PLUS one additional confirmation candle "
            "closing above the breakout level before entering."
        ),
        "exit_condition": (
            "Reduce target to 50% of original. "
            "Add time-stop: exit if target not reached within 3 bars."
        ),
        "position_size_rule": "50% of normal position size.",
        "stop_loss": "Tighten to 60% of original stop distance.",
        "no_trade_condition": f"Abort if {flag_ids} escalates to CRITICAL or NT-3 activates.",
        "backtest_hypothesis": (
            f"{hypothesis} "
            f"[Regime: {regime_label} {regime_conf} confidence. "
            f"Active HIGH flags: {flag_ids}. "
            "Position size 0.5x, stop 0.6x, confirmation candle required, "
            "time-stop 3 bars.]"
        ),
        "re_evaluate_when": (
            f"Re-evaluate for full size when {flag_ids} clears AND regime confidence is HIGH."
        ),
        "monitor_condition": "Re-run SignalAudit after each daily close until flags clear.",
        "evidence_status": evidence_mode,
    }


# ── ABORT ─────────────────────────────────────────────────────────────────────

def _abort_template(hypothesis, regime_label, no_trade_conditions, active_flag_ids, evidence_mode):
    # Build clear-condition string from no-trade condition names
    nt_labels = "; ".join(no_trade_conditions) if no_trade_conditions else "Active critical flags"

    return {
        "hypothesis": hypothesis,
        "regime_gate": f"Regime {regime_label} — breakout entry not supported.",
        "entry_condition": "DO NOT ENTER. No-trade condition active.",
        "exit_condition": "N/A — no position.",
        "position_size_rule": "0% — no position.",
        "stop_loss": "N/A — no position.",
        "no_trade_condition": nt_labels,
        "backtest_hypothesis": (
            "N/A — strategy not executable under current conditions. "
            f"Active no-trade conditions: {nt_labels}."
        ),
        "re_evaluate_when": (
            "Re-evaluate when: (1) FLAG_003 funding rate drops below +0.05%/8h, "
            "(2) exchange net flows shift to outflow, "
            f"(3) regime shifts away from {regime_label}."
        ),
        "monitor_condition": (
            "Re-run SignalAudit when funding rate drops below 0.05%/8h "
            "AND exchange daily net flow turns negative (outflow)."
        ),
        "evidence_status": evidence_mode,
    }
