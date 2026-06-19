#!/usr/bin/env python3
"""
SignalAudit v1.0 — CMC Skill for Strategy Readiness Assessment
Track 2: Strategy Skills | BNB Hack: AI Trading Agent Edition

Usage:
  python signal_audit.py                                 # defaults
  python signal_audit.py --asset BTC --timeframe 1d
  python signal_audit.py --evidence_mode SIMULATED
  python signal_audit.py --signal_file simulated_signals_clean.json
  python signal_audit.py --output json

Evidence modes:
  SIMULATED — uses data/simulated_signals.json (default, always works)
  LIVE_CMC  — requires CMC MCP credentials (not yet provisioned)
  ASSUMED   — uses simulated data labeled ASSUMED

No profit claims. No live trading. No wallet execution.
"""

import argparse
import json
import sys
import os
from datetime import datetime, timezone

# Allow running from repo root
sys.path.insert(0, os.path.dirname(__file__))

from skill.schema import AuditInput, AuditOutput
from skill.cmc_client import fetch_signals
from skill.regime_classifier import classify_regime
from skill.flag_engine import evaluate_flags
from skill.verdict_engine import evaluate_no_trade_conditions, evaluate_verdict
from skill.modified_spec import generate_modified_spec
from skill.output_formatter import format_terminal, format_json


DEFAULT_HYPOTHESIS = (
    "Long BTC when the daily close prints above the 20-day high "
    "on volume at least 1.5x the 20-day average volume."
)

_HISTORICAL_EXAMPLE = {
    "included": True,
    "example_id": "BTC_2024-03_BREAKOUT",
    "description": (
        "BTC printed above its 20-day high on approximately March 5 2024 "
        "(daily close approx $65,800). Volume was approximately 1.8x the 20-day average."
    ),
    "audit_verdict": "ABORT",
    "active_flags": ["FLAG_003", "FLAG_004", "FLAG_005"],
    "actual_outcome": (
        "BTC peaked near $73,700 on approximately March 14 2024, "
        "then corrected to approximately $57,000 by mid-April 2024."
    ),
    "interpretation": (
        "SignalAudit's retrospective ABORT verdict was directionally consistent "
        "with the subsequent correction. Not a profit claim — presented as an "
        "illustration of flag logic only."
    ),
    "evidence_status": "ASSUMED",
}


def run_audit(
    hypothesis: str = DEFAULT_HYPOTHESIS,
    asset: str = "BTC",
    timeframe: str = "1d",
    risk_tolerance: str = "moderate",
    evidence_mode: str = "SIMULATED",
    signal_file: str = "simulated_signals.json",
) -> dict:
    """
    Core audit function.
    Returns a dict compatible with AuditOutput schema.
    Raises on invalid inputs; never invents CMC responses.
    """
    # Validate input
    audit_input = AuditInput(
        strategy_hypothesis=hypothesis,
        asset=asset,
        timeframe=timeframe,
        risk_tolerance=risk_tolerance,
        evidence_mode=evidence_mode,
    )

    # Fetch signals
    signals = fetch_signals(
        asset=asset,
        timeframe=timeframe,
        evidence_mode=evidence_mode,
        signal_file=signal_file,
    )

    # Classify regime
    regime = classify_regime(signals, evidence_mode=evidence_mode)

    # Evaluate flags
    flags = evaluate_flags(signals, evidence_mode=evidence_mode)

    # No-trade conditions
    no_trade_conditions = evaluate_no_trade_conditions(flags, regime)

    # Verdict
    verdict = evaluate_verdict(flags, regime, no_trade_conditions)

    # Triggered flags only (for spec generator)
    triggered = [f for f in flags if f["triggered"]]

    # Modified strategy spec — always present
    modified_spec = generate_modified_spec(
        verdict_status=verdict["status"],
        hypothesis=hypothesis,
        regime=regime,
        active_flags=triggered,
        no_trade_conditions=no_trade_conditions,
        evidence_mode=evidence_mode,
    )

    output = {
        "skill": "signal_audit",
        "version": "1.0",
        "asset": asset,
        "timeframe": timeframe,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evidence_mode": evidence_mode,
        "regime": regime,
        "verdict": verdict,
        "flags": flags,
        "no_trade_conditions_active": no_trade_conditions,
        "modified_strategy_spec": modified_spec,
        "historical_reference": _HISTORICAL_EXAMPLE,
    }

    # Validate against schema
    AuditOutput(**output)

    return output


def main():
    parser = argparse.ArgumentParser(description="SignalAudit — CMC Skill")
    parser.add_argument("--hypothesis", default=DEFAULT_HYPOTHESIS)
    parser.add_argument("--asset", default="BTC")
    parser.add_argument("--timeframe", default="1d", choices=["4h", "1d", "1w"])
    parser.add_argument("--risk_tolerance", default="moderate",
                        choices=["conservative", "moderate", "aggressive"])
    parser.add_argument("--evidence_mode", default="SIMULATED",
                        choices=["LIVE_CMC", "SIMULATED", "ASSUMED"])
    parser.add_argument("--signal_file", default="simulated_signals.json")
    parser.add_argument("--output", default="terminal", choices=["terminal", "json", "both"])
    args = parser.parse_args()

    result = run_audit(
        hypothesis=args.hypothesis,
        asset=args.asset,
        timeframe=args.timeframe,
        risk_tolerance=args.risk_tolerance,
        evidence_mode=args.evidence_mode,
        signal_file=args.signal_file,
    )

    if args.output in ("terminal", "both"):
        print(format_terminal(result))
    if args.output in ("json", "both"):
        print(format_json(result))


if __name__ == "__main__":
    main()
