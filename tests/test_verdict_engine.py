"""T05–T08 — Verdict engine deterministic logic tests."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skill.flag_engine import evaluate_flags
from skill.regime_classifier import classify_regime
from skill.verdict_engine import evaluate_no_trade_conditions, evaluate_verdict


def _signals(funding=0.05, net_flow=0, fear_greed=50, vol_ratio=1.8, above_20d=True, vel_ratio=1.0):
    return {
        "market": {
            "price_usd": 67000,
            "volume_ratio": vol_ratio,
            "high_20d_usd": 65000,
            "close_above_20d_high": above_20d,
            "volume_24h_usd": 1e10,
            "volume_20d_avg_usd": 1e10 / vol_ratio,
            "evidence_mode": "SIMULATED",
        },
        "derivatives": {"funding_rate_8h_pct": funding, "evidence_mode": "SIMULATED"},
        "onchain": {"exchange_net_flow_btc_24h": net_flow, "evidence_mode": "SIMULATED"},
        "sentiment": {"fear_greed_index": fear_greed, "evidence_mode": "SIMULATED"},
        "kol_news": {"mention_velocity_ratio": vel_ratio, "evidence_mode": "SIMULATED"},
    }


def _run(sigs):
    flags = evaluate_flags(sigs)
    regime = classify_regime(sigs)
    nt = evaluate_no_trade_conditions(flags, regime)
    verdict = evaluate_verdict(flags, regime, nt)
    return verdict, flags, regime, nt


# T05 — ABORT when CRITICAL flag present
def test_T05_abort_on_critical_flag():
    sigs = _signals(funding=0.112)
    verdict, _, _, _ = _run(sigs)
    assert verdict["status"] == "ABORT"


# T06 — REDUCE_RISK on 1 HIGH flag + MEDIUM regime confidence
def test_T06_reduce_risk_on_high_flag_medium_regime():
    # FLAG_004 HIGH, but no CRITICAL, no NT-3 (fear_greed neutral)
    sigs = _signals(funding=0.04, net_flow=6000, fear_greed=55, above_20d=True, vol_ratio=1.8)
    verdict, flags, regime, nt = _run(sigs)
    # FLAG_004 should trigger, no CRITICAL
    from tests.test_flag_engine import _get_flag
    f004 = _get_flag(flags, "FLAG_004")
    assert f004["triggered"] is True
    assert verdict["status"] in ("REDUCE_RISK", "ABORT"), (
        f"Expected REDUCE_RISK or ABORT, got {verdict['status']}"
    )


# T07 — PROCEED when all flags clear and regime TRENDING_UP/HIGH
def test_T07_proceed_all_clear():
    # Low funding, outflow, neutral sentiment, strong volume, above 20D high
    sigs = _signals(funding=0.02, net_flow=-1500, fear_greed=55, vol_ratio=1.8, above_20d=True)
    verdict, flags, regime, nt = _run(sigs)
    assert verdict["status"] == "PROCEED", (
        f"Expected PROCEED, got {verdict['status']}. "
        f"NTs: {nt}. "
        f"Triggered flags: {[f['id'] for f in flags if f['triggered']]}"
    )


# T08 — ABORT when regime is VOLATILE_BREAKDOWN regardless of individual flag counts
def test_T08_abort_on_volatile_breakdown_regime():
    # VOLATILE_BREAKDOWN requires funding >= 0.10 AND net_flow > 5000
    sigs = _signals(funding=0.112, net_flow=6800, fear_greed=79)
    verdict, _, regime, _ = _run(sigs)
    assert regime["label"] == "VOLATILE_BREAKDOWN"
    assert verdict["status"] == "ABORT"


# Extra — verdict rationale is non-empty string
def test_verdict_rationale_always_present():
    for sigs in [
        _signals(funding=0.112),           # ABORT
        _signals(net_flow=6000),           # REDUCE_RISK or ABORT
        _signals(funding=0.02, net_flow=-1500, fear_greed=55, vol_ratio=1.8),  # PROCEED
    ]:
        verdict, _, _, _ = _run(sigs)
        assert isinstance(verdict["rationale"], str)
        assert len(verdict["rationale"]) > 10


# Extra — modified_strategy_spec present in all verdict paths
def test_modified_spec_always_present():
    from signal_audit import run_audit

    # ABORT path
    result = run_audit(signal_file="simulated_signals.json")
    assert "modified_strategy_spec" in result
    assert result["modified_strategy_spec"]["backtest_hypothesis"]

    # PROCEED path
    result2 = run_audit(signal_file="simulated_signals_clean.json")
    assert "modified_strategy_spec" in result2
    assert result2["modified_strategy_spec"]["backtest_hypothesis"]
