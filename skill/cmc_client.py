"""
CMC client — stub for SIMULATED mode.

LIVE_CMC mode: requires CMC MCP endpoint credentials from DoraHacks registration.
  → Not implemented in MVP. Will be added when API access is confirmed.
  → Do NOT invent CMC API responses.

SIMULATED mode: loads from data/simulated_signals.json (deterministic).
ASSUMED mode: loads from data/simulated_signals.json with ASSUMED label.

Tool categories used (for SKILL.md registration):
  1. Market data    — price, volume, OHLCV, 20D high
  2. Derivatives    — perpetual funding rate, open interest
  3. On-chain       — exchange net flows (BTC 24h)
  4. Sentiment      — Fear & Greed index
  5. KOL/news       — mention velocity ratio (optional, stretch)
"""

from __future__ import annotations
import json
import os
from typing import Literal


_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def fetch_signals(
    asset: str = "BTC",
    timeframe: str = "1d",
    evidence_mode: Literal["LIVE_CMC", "SIMULATED", "ASSUMED"] = "SIMULATED",
    signal_file: str = "simulated_signals.json",
) -> dict:
    """
    Returns signals dict.

    evidence_mode=LIVE_CMC: raises NotImplementedError until API credentials confirmed.
    evidence_mode=SIMULATED|ASSUMED: loads from data/{signal_file}.
    """
    if evidence_mode == "LIVE_CMC":
        raise NotImplementedError(
            "LIVE_CMC mode requires CMC MCP credentials from DoraHacks registration. "
            "Run with --evidence_mode SIMULATED for MVP demo. "
            "Do not invent API responses."
        )

    path = os.path.join(_DATA_DIR, signal_file)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Signal file not found: {path}")

    with open(path) as f:
        signals = json.load(f)

    # Stamp evidence_mode onto every sub-dict for labeling discipline
    for section in ["market", "derivatives", "onchain", "sentiment", "kol_news"]:
        if section in signals:
            signals[section]["evidence_mode"] = evidence_mode

    return signals
