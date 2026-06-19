"""T09, T10 — Schema validation tests."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from skill.schema import AuditInput, AuditOutput
from signal_audit import run_audit


def test_T09_default_inputs_validate():
    """T09: Default AuditInput loads without error."""
    inp = AuditInput()
    assert inp.asset == "BTC"
    assert inp.timeframe == "1d"
    assert inp.evidence_mode == "SIMULATED"


def test_T10_all_evidence_modes_accepted():
    """T10: All three evidence_mode values accepted by schema."""
    for mode in ("LIVE_CMC", "SIMULATED", "ASSUMED"):
        inp = AuditInput(evidence_mode=mode)
        assert inp.evidence_mode == mode


def test_T09b_custom_hypothesis_validates():
    """T09b: Custom hypothesis accepted."""
    inp = AuditInput(
        strategy_hypothesis="Short ETH when RSI > 75 on 4h.",
        asset="ETH",
        timeframe="4h",
        risk_tolerance="conservative",
    )
    assert inp.asset == "ETH"
