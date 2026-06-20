# SignalAudit — Submission

> Most Strategy Skills tell you what to trade. SignalAudit tells you whether the strategy is allowed to proceed.

**BNB Hack: AI Trading Agent Edition | Track 2: Strategy Skills**

---

## Project summary

SignalAudit is a **risk-audit Skill** for CMC Agent Hub. It checks whether
a strategy hypothesis is safe to run under current market conditions and
returns a structured verdict — PROCEED, REDUCE_RISK, or ABORT.

**The verdict is not the output. The output is a modified, backtestable
strategy spec, issued on every single run regardless of verdict.** That
spec — not the verdict label — is the artifact Track 2 asks a Strategy
Skill to produce, and it is what a reviewer should check for first.

It does not generate trade ideas. It checks whether a strategy that already
exists is safe to run under current conditions, and issues a written record
of that decision.

---

## Why Track 2

Track 2 (Strategy Skills) requires a CMC Skill that produces a backtestable
strategy specification, with no live execution. SignalAudit fits this
exactly: it has no wallet, no execution layer, and no on-chain transaction
of any kind. Its output is a specification document, not an order.

Track 1 (Autonomous Trading Agents) requires live wallet execution and
on-chain registration. SignalAudit deliberately does not implement this —
the product's entire premise is that execution authority should never be
granted by default.

---

## What the Skill does

1. Takes a strategy hypothesis as plain-language input (default: a BTC
   breakout rule).
2. Classifies the current market regime (TRENDING_UP, TRENDING_DOWN,
   RANGING, VOLATILE_BREAKDOWN) from five CMC signal categories: market
   data, derivatives, on-chain flow, sentiment, and KOL/narrative velocity.
3. Evaluates six named risk flags against explicit, stated thresholds.
4. Applies four no-trade conditions (NT-1 through NT-4) as absolute
   overrides.
5. Returns a deterministic verdict — PROCEED, REDUCE_RISK, or ABORT.
6. Issues a modified strategy spec on every run, regardless of verdict —
   this is the backtestable artifact, not the verdict alone.
7. Includes one historical reference case for illustration, labeled
   `ASSUMED`.

The verdict logic is rule-based, not probabilistic. Every threshold is
stated in `SKILL.md` and implemented in `skill/flag_engine.py` and
`skill/verdict_engine.py`. Nothing is a black box.

**Where each signal category is implemented:**

| Signal category | Code path |
|---|---|
| Market / regime signals | `skill/regime_classifier.py` |
| Derivatives / funding risk | `skill/flag_engine.py` |
| On-chain flow risk | `skill/flag_engine.py` |
| Verdict and no-trade conditions | `skill/verdict_engine.py` |
| Modified strategy spec | `skill/modified_spec.py` |

---

## What is simulated

The MVP runs entirely on `data/simulated_signals.json` and
`data/simulated_signals_clean.json` — deterministic, hand-set values used
to demonstrate both an ABORT path and a PROCEED path.

Every simulated value is labeled `evidence_mode: SIMULATED` in the output,
in the terminal display, and in the frontend. This is by design, not a
fallback hiding a failure: CMC MCP credentials were not provisioned in
time for this submission, and the team chose not to fabricate live API
responses rather than risk presenting invented data as real.

`skill/cmc_client.py` raises `NotImplementedError` if `LIVE_CMC` mode is
requested. It does not silently substitute simulated data for a live call.

---

## What is assumed

One historical reference case (`BTC_2024-03_BREAKOUT` in
`data/historical_examples.json`) is labeled `evidence_status: ASSUMED`.
Its values are consistent with publicly available March 2024 BTC price
action but were not independently re-verified against a primary source
for this submission, and no statistical backtest engine was run against
it. It is included only to illustrate how the flag logic would have
classified that period — not as a performance claim.

No part of this project makes a profit claim, return estimate, or
win-rate statement anywhere in its code, output, or copy.

---

## How to run

```bash
git clone https://github.com/Faadil1/signal-audit.git
cd signal-audit
pip install -r requirements.txt

# Run the Skill directly
python signal_audit.py

# Run the test suite
python -m pytest tests/ -v

# Run the terminal demo (both ABORT and PROCEED scenarios)
bash examples/demo_run.sh

# Reproduce the full install-test-demo cycle in a fresh environment
bash cloudshell_test.sh

# Open the static frontend (no server required)
open web/index.html
```

---

## Demo proof

- **28 of 28 tests passing** (`python -m pytest tests/ -v`)
- **Reproduced in a clean Google Cloud Shell environment** via
  `cloudshell_test.sh`
- Terminal demo (`examples/demo_run.sh`) runs both the ABORT and PROCEED
  paths end-to-end with no manual steps
- Static frontend (`web/index.html`) reproduces both scenarios with a
  Decision Receipt that can be copied as a plain-text audit record
- No wallet connection anywhere in the codebase
- No live trading anywhere in the codebase
- Every data-derived value carries an explicit `SIMULATED`, `ASSUMED`, or
  `LIVE_CMC` label

---

## Demo video checklist

These are recording/script notes, not product changes.

- **Lead with the proof, not the metaphor.** Open the video on the Judge
  Mode verification list (28/28 tests, Cloud Shell reproduced, no wallet,
  no live trading) before walking through the Standing Order interface.
  Judges deciding whether a submission is real engineering or a demo
  shell should see the proof in the first seconds, not after a metaphor
  they may not yet trust.
- **State the track explicitly, once, on camera.** Say plainly: "This is
  Track 2, not Track 1. No wallet, no live trading, no execution." Do not
  rely on the UI alone to make this distinction — say it.
- **Review the recorded video at compressed/upload resolution before
  finalizing.** The seal-crack visual on the standing order is the
  signature moment; confirm it still reads clearly after the video has
  been re-encoded for upload, not only in the original local recording.

---

## Why no wallet

A wallet implies execution authority. SignalAudit's entire thesis is that
execution authority should not exist by default — it should be granted
only after conditions written in advance are checked and confirmed. Adding
a wallet to this MVP would directly contradict the product's premise:
it would mean the audit layer could be bypassed by the same system that's
supposed to enforce it. The absence of a wallet is not a missing feature.
It is the point.

---

## Next step with real CMC MCP

`skill/cmc_client.py` is structured so that a `LIVE_CMC` evidence mode can
be added without changing any other module: `regime_classifier.py`,
`flag_engine.py`, `verdict_engine.py`, and `modified_spec.py` all consume
a plain signals dictionary regardless of where it came from.

The next step is:

1. Register for CMC MCP API access via the CMC Agent Hub.
2. Implement the five tool calls (market data, derivatives, on-chain,
   sentiment, KOL/news) in `cmc_client.py` under the `LIVE_CMC` branch.
3. Re-run the existing 28-test suite against live data with no other
   code changes required.
4. Only after that passes would `LIVE_CMC` move from stub to verified.

No part of this roadmap requires adding a wallet or an execution layer.
The Skill remains an audit, not an agent that acts on its own audit.
