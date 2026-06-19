"""
Verdict engine — deterministic.
Input: triggered flags list + regime dict.
Output: verdict dict + active no-trade conditions list.

No-trade conditions (NT) are absolute overrides:
  NT-1: Any CRITICAL flag triggered
  NT-2: Regime is VOLATILE_BREAKDOWN
  NT-3: FLAG_004 HIGH AND FLAG_005 HIGH both triggered simultaneously
  NT-4: FLAG_002 triggered AND funding_rate >= 0.08%
        (late-cycle breakout with squeeze risk — passed in via flags)
"""

from __future__ import annotations
from typing import List, Tuple


def _triggered(flags: List[dict], flag_id: str) -> bool:
    for f in flags:
        if f["id"] == flag_id and f["triggered"]:
            return True
    return False


def evaluate_no_trade_conditions(
    flags: List[dict],
    regime: dict,
) -> List[str]:
    """Returns list of active no-trade condition identifiers."""
    active = []

    # NT-1: Any CRITICAL flag
    if any(f["severity"] == "CRITICAL" and f["triggered"] for f in flags):
        critical_names = [
            f["name"] for f in flags if f["severity"] == "CRITICAL" and f["triggered"]
        ]
        active.append(f"NT-1: CRITICAL flag active — {', '.join(critical_names)}")

    # NT-2: Regime VOLATILE_BREAKDOWN
    if regime.get("label") == "VOLATILE_BREAKDOWN":
        active.append("NT-2: Regime VOLATILE_BREAKDOWN — breakout strategies have negative expected value")

    # NT-3: Distribution under elevated sentiment
    if _triggered(flags, "FLAG_004") and _triggered(flags, "FLAG_005"):
        active.append("NT-3: FLAG_004 (ONCHAIN_FLOW HIGH) + FLAG_005 (SENTIMENT_EXTREME HIGH) — distribution under euphoria pattern")

    # NT-4: Late-cycle breakout with squeeze risk
    # Requires FLAG_002 triggered AND FLAG_003 value >= 0.08%
    f003 = next((f for f in flags if f["id"] == "FLAG_003"), None)
    if _triggered(flags, "FLAG_002") and f003:
        # Parse funding value from string "+0.112%/8h"
        try:
            funding_val = float(f003["value"].lstrip("+").split("%")[0])
        except (ValueError, IndexError):
            funding_val = 0.0
        if funding_val >= 0.08:
            active.append("NT-4: Price near 20D high resistance AND funding >= 0.08% — late-cycle squeeze risk")

    return active


def evaluate_verdict(
    flags: List[dict],
    regime: dict,
    no_trade_conditions: List[str],
) -> dict:
    """
    Returns: {status, rationale}

    Priority:
      ABORT        if any NT active (covers CRITICAL flags and VOLATILE_BREAKDOWN)
      ABORT        if 2+ HIGH triggered flags
      REDUCE_RISK  if 1 HIGH triggered flag OR regime confidence MEDIUM
      PROCEED      all clear
    """
    triggered_flags = [f for f in flags if f["triggered"]]
    high_triggered = [f for f in triggered_flags if f["severity"] == "HIGH"]
    critical_triggered = [f for f in triggered_flags if f["severity"] == "CRITICAL"]

    # ABORT path — no-trade conditions active
    if no_trade_conditions:
        flag_refs = ", ".join(
            f["id"] for f in critical_triggered + high_triggered
        ) or "regime"
        rationale = (
            f"ABORT: {no_trade_conditions[0]}. "
            f"Active flags: {flag_refs}. "
            "Strategy entry not warranted under current conditions."
        )
        return {"status": "ABORT", "rationale": rationale}

    # ABORT path — 2+ HIGH flags even without NT
    if len(high_triggered) >= 2:
        flag_refs = ", ".join(f["id"] for f in high_triggered)
        rationale = (
            f"ABORT: {len(high_triggered)} HIGH-severity flags active ({flag_refs}). "
            "Multiple independent risk signals make strategy entry inadvisable."
        )
        return {"status": "ABORT", "rationale": rationale}

    # REDUCE_RISK path — 1 HIGH flag or MEDIUM regime confidence
    if len(high_triggered) == 1 or regime.get("confidence") == "MEDIUM":
        reasons = []
        if high_triggered:
            reasons.append(f"{high_triggered[0]['id']} ({high_triggered[0]['name']}) is HIGH")
        if regime.get("confidence") == "MEDIUM":
            reasons.append(f"Regime confidence is MEDIUM ({regime.get('label')})")
        rationale = (
            "REDUCE_RISK: " + "; ".join(reasons) + ". "
            "Strategy may be entered with reduced size and tighter stops per modified spec."
        )
        return {"status": "REDUCE_RISK", "rationale": rationale}

    # PROCEED — all clear
    rationale = (
        f"PROCEED: All flags clear. Regime {regime.get('label')} with "
        f"{regime.get('confidence')} confidence. Strategy conditions met."
    )
    return {"status": "PROCEED", "rationale": rationale}
