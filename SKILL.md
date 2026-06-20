# SKILL: signal_audit

**Version:** 1.0
**Track:** BNB Hack — Strategy Skills (Track 2)
**Author:** SignalAudit / BNB Hack 2026

---

## What This Skill Does

SignalAudit takes a trader's existing strategy hypothesis and cross-tests it against
current market signals to return a structured, evidence-backed verdict:

- **PROCEED** — conditions support the strategy
- **REDUCE_RISK** — enter with reduced size and tighter stops (modified spec included)
- **ABORT** — no-trade condition active; do not enter

Every output includes a **modified backtestable strategy spec** — not just a verdict.
This is the Skill's core Track 2 deliverable.

---

## CMC Tool Categories Used

| # | Category | Signals Extracted |
|---|---|---|
| 1 | Market data | Price, OHLCV, 20D high, volume ratio |
| 2 | Derivatives | Perpetual funding rate / 8h, open interest |
| 3 | On-chain | Exchange net BTC flow / 24h |
| 4 | Sentiment | Fear & Greed index |
| 5 | KOL / news | Mention velocity ratio vs 7D baseline |

---

## Input Schema

```json
{
  "strategy_hypothesis": "string (plain-language strategy to audit)",
  "asset": "string (default: BTC)",
  "timeframe": "4h | 1d | 1w (default: 1d)",
  "risk_tolerance": "conservative | moderate | aggressive (default: moderate)",
  "evidence_mode": "LIVE_CMC | SIMULATED | ASSUMED (default: SIMULATED)"
}
```

**All fields have defaults. The Skill runs with zero required input.**

---

## Output Schema (summary)

```json
{
  "evidence_mode": "LIVE_CMC | SIMULATED | ASSUMED",
  "regime": {
    "label": "TRENDING_UP | TRENDING_DOWN | RANGING | VOLATILE_BREAKDOWN",
    "confidence": "HIGH | MEDIUM | LOW",
    "basis": ["...signals that drove the label"]
  },
  "verdict": {
    "status": "PROCEED | REDUCE_RISK | ABORT",
    "rationale": "Plain-language explanation referencing specific flags."
  },
  "flags": [
    {
      "id": "FLAG_XXX",
      "name": "...",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW",
      "value": "observed value",
      "threshold": "threshold crossed",
      "triggered": true,
      "source": "CMC tool name | SIMULATED",
      "evidence_mode": "..."
    }
  ],
  "no_trade_conditions_active": ["NT-1: ...", "NT-2: ..."],
  "modified_strategy_spec": {
    "hypothesis": "...",
    "regime_gate": "...",
    "entry_condition": "...",
    "exit_condition": "...",
    "position_size_rule": "...",
    "stop_loss": "...",
    "no_trade_condition": "...",
    "backtest_hypothesis": "Fully specified testable strategy string",
    "re_evaluate_when": "...",
    "monitor_condition": "...",
    "evidence_status": "..."
  },
  "historical_reference": {
    "example_id": "...",
    "audit_verdict": "...",
    "actual_outcome": "...",
    "evidence_status": "ASSUMED"
  }
}
```

---

## Flag Definitions

| Flag | Name | Severity | Trigger Condition |
|---|---|---|---|
| FLAG_001 | VOLUME_CONFIRM | HIGH | Volume ratio < 1.2× 20D average |
| FLAG_002 | PRICE_LEVEL | MEDIUM | Price within 0.5% of 20D high |
| FLAG_003 | FUNDING_RATE | **CRITICAL** | Perpetual funding ≥ +0.10%/8h |
| FLAG_004 | ONCHAIN_FLOW | HIGH | Exchange net BTC inflow > 5,000/24h |
| FLAG_005 | SENTIMENT_EXTREME | HIGH | Fear & Greed > 80 or < 20 |
| FLAG_006 | NARRATIVE_SPIKE | MEDIUM | KOL mention velocity ≥ 3× 7D baseline |

---

## No-Trade Conditions

| ID | Condition |
|---|---|
| NT-1 | Any CRITICAL flag active |
| NT-2 | Regime is VOLATILE_BREAKDOWN |
| NT-3 | FLAG_004 HIGH AND FLAG_005 HIGH simultaneously (distribution under euphoria) |
| NT-4 | FLAG_002 triggered AND funding rate ≥ 0.08%/8h (late-cycle squeeze risk) |

---

## Evidence Modes

All data-derived output is labeled with one of:

| Mode | Meaning |
|---|---|
| `LIVE_CMC` | Fetched from CMC MCP API (requires credentials) |
| `SIMULATED` | Deterministic data from `data/simulated_signals.json` |
| `ASSUMED` | Historically consistent reference data; not verified |

**MVP uses SIMULATED mode.** LIVE_CMC mode is stubbed pending API provisioning.

---

## Verdict Logic

```
ABORT        if any NT active (covers CRITICAL flags, VOLATILE_BREAKDOWN, NT-3, NT-4)
ABORT        if 2+ HIGH triggered flags (without NT)
REDUCE_RISK  if 1 HIGH flag OR regime confidence = MEDIUM
PROCEED      all flags clear AND regime HIGH confidence
```

Verdict is **deterministic from flags**. No ML. No probabilistic scoring.
All thresholds are explicit and verifiable.

---

## Disclaimer

This Skill does not provide investment advice.
It does not execute trades.
It does not make profit claims.
Evidence mode is always labeled.
See `DISCLOSURE.md`.
