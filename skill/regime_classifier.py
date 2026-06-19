"""
Regime classifier — deterministic.
Input: raw signals dict.
Output: Regime dataclass values (label, confidence, basis).
No ML. No probabilities. Verifiable threshold logic.
"""

from __future__ import annotations
from typing import Literal


def classify_regime(
    signals: dict,
    evidence_mode: Literal["LIVE_CMC", "SIMULATED", "ASSUMED"] = "SIMULATED",
) -> dict:
    """
    Returns:
        {label, confidence, basis, evidence_mode}

    Regime priority (highest wins):
        1. VOLATILE_BREAKDOWN — funding CRITICAL and inflow HIGH
        2. TRENDING_UP        — price above 20D high, volume confirms, funding neutral
        3. TRENDING_DOWN      — inflow high but funding low (distribution without leverage)
        4. RANGING            — default
    """
    basis = []
    label = "RANGING"
    confidence = "MEDIUM"

    mkt = signals.get("market", {})
    der = signals.get("derivatives", {})
    onc = signals.get("onchain", {})

    funding = der.get("funding_rate_8h_pct", 0.0)
    net_flow = onc.get("exchange_net_flow_btc_24h", 0)
    volume_ratio = mkt.get("volume_ratio", 1.0)
    above_20d = mkt.get("close_above_20d_high", False)

    # Rule 1 — VOLATILE_BREAKDOWN: overheated leverage + distribution
    if funding >= 0.10 and net_flow > 5000:
        label = "VOLATILE_BREAKDOWN"
        confidence = "HIGH"
        basis.append(f"Funding rate {funding:.3f}%/8h >= 0.10% (leverage overheated)")
        basis.append(f"Exchange net inflow {net_flow:,} BTC > 5,000 BTC (distribution)")
        return {
            "label": label,
            "confidence": confidence,
            "basis": basis,
            "evidence_mode": evidence_mode,
        }

    # Rule 2 — TRENDING_UP: breakout above 20D high with volume
    if above_20d and volume_ratio >= 1.5 and funding < 0.08 and net_flow < 0:
        label = "TRENDING_UP"
        confidence = "HIGH" if volume_ratio >= 1.8 else "MEDIUM"
        basis.append(f"Close above 20D high, volume ratio {volume_ratio:.2f}x")
        if net_flow < 0:
            basis.append("Exchange net outflow — accumulation signal")
        return {
            "label": label,
            "confidence": confidence,
            "basis": basis,
            "evidence_mode": evidence_mode,
        }

    # Rule 3 — TRENDING_UP with moderate signals
    if above_20d and volume_ratio >= 1.5:
        label = "TRENDING_UP"
        confidence = "MEDIUM"
        basis.append(f"Close above 20D high, volume ratio {volume_ratio:.2f}x")
        basis.append("Confidence MEDIUM — funding or flow mixed")
        return {
            "label": label,
            "confidence": confidence,
            "basis": basis,
            "evidence_mode": evidence_mode,
        }

    # Rule 4 — TRENDING_DOWN: inflow without leverage
    if net_flow > 5000 and funding < 0.05:
        label = "TRENDING_DOWN"
        confidence = "MEDIUM"
        basis.append(f"Exchange net inflow {net_flow:,} BTC — sell pressure")
        basis.append("Low funding: distribution without leverage bubble")
        return {
            "label": label,
            "confidence": confidence,
            "basis": basis,
            "evidence_mode": evidence_mode,
        }

    # Default — RANGING
    basis.append("No dominant regime signal detected")
    return {
        "label": label,
        "confidence": confidence,
        "basis": basis,
        "evidence_mode": evidence_mode,
    }
