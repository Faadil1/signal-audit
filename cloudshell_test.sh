#!/usr/bin/env bash
# cloudshell_test.sh — SignalAudit reproducibility validation
#
# Status: LOCAL_VALIDATION_READY
# Run this in Google Cloud Shell to confirm CLOUDSHELL_VERIFIED.
#
# Usage:
#   bash cloudshell_test.sh
#
# Exits non-zero on any failure.

set -euo pipefail

cd "$(dirname "$0")"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SignalAudit — Reproducibility Validation"
echo "  Status: LOCAL_VALIDATION_READY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Step 1: Install requirements ─────────────────────────────────────────────
echo "[1/4] Installing requirements..."
# Try standard pip first (works in Cloud Shell and most venvs).
# Fall back to --break-system-packages for Debian-managed environments.
pip install -q -r requirements.txt 2>/dev/null \
  || pip install -q --break-system-packages -r requirements.txt
echo "      OK"

# ── Step 2: Run test suite ────────────────────────────────────────────────────
echo ""
echo "[2/4] Running test suite (28 tests expected)..."
python -m pytest tests/ -v
echo ""
echo "      Tests passed."

# ── Step 3: Smoke run — default SIMULATED output ─────────────────────────────
echo ""
echo "[3/4] Smoke run — python signal_audit.py..."
python signal_audit.py --evidence_mode SIMULATED
echo "      Smoke run OK."

# ── Step 4: Full demo script ──────────────────────────────────────────────────
echo ""
echo "[4/4] Running demo script..."
bash examples/demo_run.sh
echo "      Demo OK."

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ALL STEPS PASSED"
echo ""
echo "  If this ran in Google Cloud Shell, mark status:"
echo "  CLOUDSHELL_VERIFIED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
