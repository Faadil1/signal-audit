"""
Flag engine — deterministic.
Six flags from DESIGN §8.
Every flag carries: id, name, severity, value, threshold, triggered, source, evidence_mode.
No probabilities. Thresholds are explicit and verifiable.
"""

from __future__ import annotations
from typing import List, Literal


def evaluate_flags(
    signals: dict,
    evidence_mode: Literal["LIVE_CMC", "SIMULATED", "ASSUMED"] = "SIMULATED",
) -> List[dict]:
    """
    Returns list of flag dicts — all six evaluated, triggered or not.
    Callers filter for triggered=True when computing verdict.
    """
    mkt = signals.get("market", {})
    der = signals.get("derivatives", {})
    onc = signals.get("onchain", {})
    sent = signals.get("sentiment", {})
    kol = signals.get("kol_news", {})

    flags = []

    # ── FLAG_001 — VOLUME_CONFIRM ────────────────────────────────────────────
    # Breakout strategy requires volume >= 1.5x avg. Below 1.2x = weak breakout.
    vol_ratio = mkt.get("volume_ratio", 1.0)
    f001_triggered = vol_ratio < 1.2
    flags.append({
        "id": "FLAG_001",
        "name": "VOLUME_CONFIRM",
        "severity": "HIGH",
        "value": f"{vol_ratio:.3f}x 20D avg volume",
        "threshold": "< 1.2x 20D avg volume",
        "triggered": f001_triggered,
        "source": "CMC market data" if evidence_mode == "LIVE_CMC" else evidence_mode,
        "evidence_mode": evidence_mode,
    })

    # ── FLAG_002 — PRICE_LEVEL ───────────────────────────────────────────────
    # Price within 0.5% of 20D high = potential stall at resistance.
    price = mkt.get("price_usd", 0.0)
    high_20d = mkt.get("high_20d_usd", 0.0)
    if high_20d > 0:
        gap_pct = abs(price - high_20d) / high_20d * 100
    else:
        gap_pct = 999.0
    f002_triggered = gap_pct <= 0.5
    flags.append({
        "id": "FLAG_002",
        "name": "PRICE_LEVEL",
        "severity": "MEDIUM",
        "value": f"{gap_pct:.2f}% from 20D high",
        "threshold": "<= 0.5% from 20D high (resistance proximity)",
        "triggered": f002_triggered,
        "source": "CMC market data" if evidence_mode == "LIVE_CMC" else evidence_mode,
        "evidence_mode": evidence_mode,
    })

    # ── FLAG_003 — FUNDING_RATE ──────────────────────────────────────────────
    # Perpetual funding > 0.10%/8h = longs overheated. CRITICAL override.
    funding = der.get("funding_rate_8h_pct", 0.0)
    f003_triggered = funding >= 0.10
    flags.append({
        "id": "FLAG_003",
        "name": "FUNDING_RATE",
        "severity": "CRITICAL",
        "value": f"+{funding:.3f}%/8h",
        "threshold": ">= 0.10%/8h (longs overheated)",
        "triggered": f003_triggered,
        "source": "CMC derivatives" if evidence_mode == "LIVE_CMC" else evidence_mode,
        "evidence_mode": evidence_mode,
    })

    # ── FLAG_004 — ONCHAIN_FLOW ──────────────────────────────────────────────
    # Exchange net inflow > 5,000 BTC/24h = sell pressure building.
    net_flow = onc.get("exchange_net_flow_btc_24h", 0)
    f004_triggered = net_flow > 5000
    flags.append({
        "id": "FLAG_004",
        "name": "ONCHAIN_FLOW",
        "severity": "HIGH",
        "value": f"+{net_flow:,} BTC net inflow/24h",
        "threshold": "> 5,000 BTC net inflow/24h (sell pressure)",
        "triggered": f004_triggered,
        "source": "CMC on-chain" if evidence_mode == "LIVE_CMC" else evidence_mode,
        "evidence_mode": evidence_mode,
    })

    # ── FLAG_005 — SENTIMENT_EXTREME ────────────────────────────────────────
    # Fear & Greed > 80 or < 20 = sentiment extreme preceding reversals.
    fg = sent.get("fear_greed_index", 50)
    f005_triggered = fg > 80 or fg < 20
    flags.append({
        "id": "FLAG_005",
        "name": "SENTIMENT_EXTREME",
        "severity": "HIGH",
        "value": f"Fear & Greed = {fg}",
        "threshold": "> 80 (Extreme Greed) or < 20 (Extreme Fear)",
        "triggered": f005_triggered,
        "source": "CMC sentiment" if evidence_mode == "LIVE_CMC" else evidence_mode,
        "evidence_mode": evidence_mode,
    })

    # ── FLAG_006 — NARRATIVE_SPIKE ───────────────────────────────────────────
    # KOL mention velocity > 3x 7D baseline without fundamental event = noise pump.
    vel_ratio = kol.get("mention_velocity_ratio", 1.0)
    f006_triggered = vel_ratio >= 3.0
    flags.append({
        "id": "FLAG_006",
        "name": "NARRATIVE_SPIKE",
        "severity": "MEDIUM",
        "value": f"{vel_ratio:.1f}x 7D baseline KOL mentions",
        "threshold": ">= 3.0x 7D baseline (manufactured momentum risk)",
        "triggered": f006_triggered,
        "source": "CMC KOL/news" if evidence_mode == "LIVE_CMC" else evidence_mode,
        "evidence_mode": evidence_mode,
    })

    return flags
