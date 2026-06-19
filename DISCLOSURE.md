# DISCLOSURE

## SignalAudit v1.0 — Evidence, Limitations, and Non-Advisory Statement

---

### 1. No Investment Advice

SignalAudit does not provide investment advice.

All output — verdicts, flags, regime labels, modified strategy specs,
and historical references — is produced for educational and research purposes only.

**Nothing in this Skill constitutes a recommendation to buy, sell, or hold any asset.**

---

### 2. No Profit Claims

SignalAudit makes no claims about future returns, profitability, or risk-adjusted performance.

- The phrase "backtestable strategy spec" means the output is formatted to be
  testable against historical data. It does not mean a backtest has been run or
  that the strategy has demonstrated positive returns.
- Historical reference examples are presented as illustrations of flag logic,
  not as evidence of strategy performance.
- No Sharpe ratio, expected return, drawdown curve, or win rate is implied or stated.

---

### 3. Evidence Modes

Every data-derived output field carries one of three evidence mode labels:

| Label | Meaning |
|---|---|
| `LIVE_CMC` | Data fetched from the CMC MCP API during this run. Requires valid credentials. |
| `SIMULATED` | Deterministic data loaded from `data/simulated_signals.json`. Values are illustrative. Not real market data. |
| `ASSUMED` | Data consistent with publicly available historical records but not independently verified. Used for historical reference examples only. |

**MVP operates entirely in SIMULATED mode.**
`LIVE_CMC` mode is stubbed and will raise `NotImplementedError` until CMC MCP
credentials are provisioned via the DoraHacks/CMC Agent Hub registration.

---

### 4. No Live Trading

SignalAudit does not:
- connect to any wallet
- submit any on-chain transaction
- interface with Trust Wallet Agent Kit
- execute any trade on PancakeSwap, BSC perps, or any other venue

The Skill is a read-only analysis tool.

---

### 5. Historical Reference Limitations

Historical reference examples (e.g., `BTC_2024-03_BREAKOUT`) carry
`evidence_status: ASSUMED`.

These examples are:
- consistent with publicly available market data
- not independently verified against a primary source
- not the result of a statistical backtest engine
- presented solely to illustrate how the flag system would have classified
  conditions at a given moment in time

**Past flag patterns do not predict future flag patterns or market outcomes.**

---

### 6. Thresholds and Rules

All flag thresholds and verdict rules are stated explicitly in `SKILL.md` and
in `skill/flag_engine.py` and `skill/verdict_engine.py`.

These thresholds were selected for illustrative clarity, not optimized through
backtesting. Users who deploy this Skill for real analysis should validate
and calibrate thresholds against their own historical data.

---

### 7. Third-Party Data

In LIVE_CMC mode (when provisioned), this Skill uses:
- CoinMarketCap AI Agent Hub
- CoinMarketCap MCP tools (market data, derivatives, on-chain, sentiment, KOL/news)

Use of CMC data is subject to CoinMarketCap's terms of service.
Any use of third-party AI agents, tools, or services is at the participant's own risk.

---

*This disclosure applies to all versions of SignalAudit produced for the
BNB Hack: AI Trading Agent Edition (June 2026).*
