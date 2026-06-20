# SignalAudit

> Most Strategy Skills tell you what to trade. SignalAudit tells you whether the strategy is allowed to proceed.

**CMC Skill — Strategy Readiness Assessment**
BNB Hack: AI Trading Agent Edition | Track 2: Strategy Skills

SignalAudit is a **risk-audit Skill**, not a trading bot and not a strategy
generator. It does not trade, hold a wallet, or execute anything.

---

## What It Does

Most strategy tools tell you *what* to trade.
SignalAudit asks a different question: **is now a good time to run your strategy at all?**

You provide a strategy hypothesis in plain language.
SignalAudit cross-tests it against five CMC signal categories,
classifies the current market regime, identifies active risk flags,
and returns a structured verdict — **PROCEED**, **REDUCE_RISK**, or **ABORT**.

**Every run issues a modified, backtestable strategy spec** — this is the
core Track 2 artifact this Skill produces. The verdict alone is not the
output; the spec is. See [Modified Strategy Spec](#modified-strategy-spec--the-core-track-2-artifact) below.

---

## Quick Start

```bash
pip install -r requirements.txt

# Default demo (SIMULATED mode — always works, no API key needed)
python signal_audit.py

# With custom hypothesis
python signal_audit.py --hypothesis "Long ETH when RSI crosses above 50 on 4h."

# JSON output
python signal_audit.py --output json

# One-command demo (matches 5-minute demo script)
bash examples/demo_run.sh
```

---

## Example Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SignalAudit v1.0 — Strategy Readiness Assessment
  Asset: BTC | Timeframe: 1d | Evidence mode: SIMULATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REGIME  [SIMULATED]
  Label:      VOLATILE_BREAKDOWN  |  Confidence: HIGH
  Basis:      Funding rate 0.112%/8h >= 0.10% (leverage overheated)
  Basis:      Exchange net inflow 6,800 BTC > 5,000 BTC (distribution)

FLAGS
  ✗ FLAG_003  FUNDING_RATE    🔴 CRITICAL  +0.112%/8h  [SIMULATED]
  ✗ FLAG_004  ONCHAIN_FLOW    🟠 HIGH      +6,800 BTC  [SIMULATED]

NO-TRADE CONDITIONS ACTIVE
  ⛔ NT-1: CRITICAL flag active — FUNDING_RATE
  ⛔ NT-2: Regime VOLATILE_BREAKDOWN

VERDICT  🛑 ABORT
  FLAG_003 is CRITICAL. NT-3 active: distribution under elevated sentiment.

MODIFIED STRATEGY SPEC  [SIMULATED]
  Entry:            DO NOT ENTER — NT conditions active
  Re-evaluate when: Funding rate < 0.05%/8h AND exchange outflows resume
  Backtest spec:    N/A under current conditions
```

---

## Modified Strategy Spec — the core Track 2 artifact

The verdict (PROCEED / REDUCE_RISK / ABORT) is not the Skill's output.
**The modified strategy spec is.** Track 2 requires a CMC Skill that
produces a backtestable strategy specification — SignalAudit satisfies
this on every single run, regardless of verdict:

| Verdict | What the spec contains |
|---|---|
| PROCEED | Original entry/exit/size/stop terms, unmodified, with a monitor condition |
| REDUCE_RISK | Adjusted entry confirmation, reduced position size, tightened stop, re-evaluation trigger |
| ABORT | "Do not enter," 0% position size, and an explicit re-evaluate-when condition |

This is the artifact a judge should check for: not "does it give a
verdict," but "does it issue a complete, testable strategy specification
every time." It always does. See `skill/modified_spec.py` for the three
templates and `tests/test_verdict_engine.py::test_modified_spec_always_present`
for the test enforcing this.

---

## Architecture

```
signal_audit.py          ← entry point (CLI args → run_audit())
├── skill/cmc_client.py  ← fetch signals (LIVE_CMC stub | SIMULATED from JSON)
├── skill/regime_classifier.py  ← deterministic regime label from signals
├── skill/flag_engine.py        ← six flags with explicit thresholds
├── skill/verdict_engine.py     ← PROCEED / REDUCE_RISK / ABORT
├── skill/modified_spec.py      ← three modified strategy spec templates
├── skill/output_formatter.py   ← terminal + JSON output
└── skill/schema.py             ← Pydantic input/output models
data/
├── simulated_signals.json       ← ABORT scenario (BTC overheated)
├── simulated_signals_clean.json ← PROCEED scenario (all clear)
└── historical_examples.json     ← BTC_2024-03 reference [ASSUMED]
```

---

## CMC Signal Categories Used — and where each one is implemented

| Signal category | Flags | Code path |
|---|---|---|
| Market / regime signals | FLAG_001, FLAG_002 | `skill/regime_classifier.py` |
| Derivatives / funding risk | FLAG_003 | `skill/flag_engine.py` |
| On-chain flow risk | FLAG_004 | `skill/flag_engine.py` |
| Sentiment | FLAG_005 | `skill/flag_engine.py` |
| KOL / narrative velocity | FLAG_006 | `skill/flag_engine.py` |
| Verdict and no-trade conditions | — | `skill/verdict_engine.py` |
| Modified strategy spec | — | `skill/modified_spec.py` |

Every threshold is explicit and stated in `SKILL.md`. Nothing here is a
black box — the mapping above is the fastest way to verify the claim.

---

## Flag System

| Flag | Severity | Threshold |
|---|---|---|
| FLAG_001 VOLUME_CONFIRM | HIGH | Volume < 1.2× 20D avg |
| FLAG_002 PRICE_LEVEL | MEDIUM | Price within 0.5% of 20D high |
| FLAG_003 FUNDING_RATE | **CRITICAL** | Funding ≥ +0.10%/8h |
| FLAG_004 ONCHAIN_FLOW | HIGH | Net inflow > 5,000 BTC/24h |
| FLAG_005 SENTIMENT_EXTREME | HIGH | Fear & Greed > 80 or < 20 |
| FLAG_006 NARRATIVE_SPIKE | MEDIUM | Mentions ≥ 3× 7D baseline |

No-trade conditions (NT-1 through NT-4) are absolute ABORT overrides.
See `SKILL.md` for full definitions.

---

## Evidence Modes

All output is labeled:

- `LIVE_CMC` — from CMC MCP API (requires credentials)
- `SIMULATED` — deterministic fallback from `data/simulated_signals.json`
- `ASSUMED` — historical reference data; not independently verified

MVP uses `SIMULATED` mode throughout.
`LIVE_CMC` is stubbed; raises `NotImplementedError` until API is provisioned.

---

## Judging Alignment — Track 2

| Criterion | How SignalAudit addresses it |
|---|---|
| Technical execution | Pydantic schema, deterministic flag engine, six CMC tool categories, 28 passing tests |
| Originality | Inverted question: "is now safe to run?" vs "what should I trade?" — explicit no-trade conditions and NT-3 conjunction rule |
| Real-world value | Modified backtestable strategy spec in every output; REDUCE_RISK path gives actionable position sizing and stop adjustments |
| Presentation | Terminal demo in < 5 minutes; fallback to SIMULATED if LIVE_CMC unavailable; all evidence labeled |

---

## Tests

**28 of 28 tests passing.** Verify it yourself:

```bash
python -m pytest tests/ -v
# 28 passed
```

Tests cover: T01–T13 from design spec + T14 (no-profit-claim assertion on all output).

---

## Non-Goals

- No wallet, no execution, no live trading
- No Trust Wallet Agent Kit integration
- No BNB Chain transactions
- No frontend UI
- No ML-based signal generation
- No profit claims

---

## Disclosure

This Skill does not provide investment advice.
No live trading. No profit claims. All evidence labeled.
See `DISCLOSURE.md` for full statement.

---

## Reproducibility Test in Google Cloud Shell

Status: **LOCAL_VALIDATION_READY** — not yet CLOUDSHELL_VERIFIED.

Run this in a fresh [Google Cloud Shell](https://shell.cloud.google.com) to confirm clean reproduction:

```bash
git clone <YOUR_REPO_URL> signal-audit
cd signal-audit
bash cloudshell_test.sh
```

Expected output:
- `[1/4]` pip install completes without error
- `[2/4]` `28 passed` in pytest
- `[3/4]` smoke run prints ABORT verdict with SIMULATED label
- `[4/4]` demo script prints both ABORT and PROCEED scenarios

`cloudshell_test.sh` exits non-zero on any failure.

Once confirmed in Cloud Shell, update `cloudshell_test.sh` status line to `CLOUDSHELL_VERIFIED`.

---

## Optional Static Frontend Demo

A static, presentation-only frontend lives in `web/` — **"The Trading Gate."**

It visualizes the audit as a checkpoint gate that opens (PROCEED) or closes (ABORT)
based on the same flag and verdict logic the CLI produces. All scenario data shown
is hardcoded from already-validated backend runs — the frontend does not call,
import, or recompute anything from `skill/`. The Python backend remains the
source of truth.

**To open it:**

```bash
open web/index.html
# or just double-click web/index.html in your file browser
```

No server, no build step, no internet connection, and no external dependencies
are required. Pure HTML/CSS/JS.

