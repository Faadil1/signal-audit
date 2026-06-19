#!/usr/bin/env bash
# SignalAudit — 5-minute demo script
# Matches DESIGN §12 exactly.
# Run from repo root: bash examples/demo_run.sh

set -e
cd "$(dirname "$0")/.."

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SignalAudit — CMC Skill Demo"
echo "  BNB Hack: AI Trading Agent Edition | Track 2: Strategy Skills"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "[0:00] STRATEGY HYPOTHESIS"
echo "  Long BTC when the daily close prints above the 20-day high"
echo "  on volume at least 1.5x the 20-day average volume."
echo ""
echo "[0:30] FETCHING CMC SIGNALS  [evidence_mode: SIMULATED]"
echo "  → market data:   price, volume, 20D high"
echo "  → derivatives:   perpetual funding rate"
echo "  → on-chain:      exchange net BTC flow"
echo "  → sentiment:     Fear & Greed index"
echo ""

# ── ABORT scenario (default signals) ─────────────────────────────────────────
echo "[1:00] AUDIT RESULT — ABORT SCENARIO"
python signal_audit.py \
  --hypothesis "Long BTC when the daily close prints above the 20-day high on volume at least 1.5x the 20-day average volume." \
  --asset BTC \
  --timeframe 1d \
  --risk_tolerance moderate \
  --evidence_mode SIMULATED \
  --signal_file simulated_signals.json \
  --output terminal

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[3:30] NOW — SAME STRATEGY, CONDITIONS CLEARED"
echo "       Showing PROCEED scenario (conditions improved)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python signal_audit.py \
  --hypothesis "Long BTC when the daily close prints above the 20-day high on volume at least 1.5x the 20-day average volume." \
  --asset BTC \
  --timeframe 1d \
  --risk_tolerance moderate \
  --evidence_mode SIMULATED \
  --signal_file simulated_signals_clean.json \
  --output terminal

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[4:30] SUMMARY"
echo "  • Same strategy hypothesis"
echo "  • Different market regime → different verdict"
echo "  • Modified backtestable spec in every output path"
echo "  • All evidence labeled: SIMULATED or ASSUMED"
echo "  • 5 CMC signal categories used"
echo "  • No wallet. No live trading. No profit claims."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
