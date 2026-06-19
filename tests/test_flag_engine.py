"""T01–T04 — Flag engine deterministic threshold tests."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skill.flag_engine import evaluate_flags


def _signals(funding=0.05, net_flow=0, fear_greed=50, vol_ratio=1.8, vel_ratio=1.0, above_20d=True, price=67000, high_20d=65000):
    return {
        "market": {
            "price_usd": price,
            "volume_ratio": vol_ratio,
            "high_20d_usd": high_20d,
            "close_above_20d_high": above_20d,
            "volume_24h_usd": 1e10,
            "volume_20d_avg_usd": 1e10 / vol_ratio,
            "evidence_mode": "SIMULATED",
        },
        "derivatives": {
            "funding_rate_8h_pct": funding,
            "evidence_mode": "SIMULATED",
        },
        "onchain": {
            "exchange_net_flow_btc_24h": net_flow,
            "evidence_mode": "SIMULATED",
        },
        "sentiment": {
            "fear_greed_index": fear_greed,
            "evidence_mode": "SIMULATED",
        },
        "kol_news": {
            "mention_velocity_ratio": vel_ratio,
            "evidence_mode": "SIMULATED",
        },
    }


def _get_flag(flags, flag_id):
    return next((f for f in flags if f["id"] == flag_id), None)


# T01 — FLAG_003 triggers at >= 0.10%
def test_T01_flag003_triggers_at_critical_threshold():
    flags = evaluate_flags(_signals(funding=0.112))
    f = _get_flag(flags, "FLAG_003")
    assert f is not None
    assert f["triggered"] is True
    assert f["severity"] == "CRITICAL"


# T02 — FLAG_003 does not trigger at 0.08%
def test_T02_flag003_clear_below_threshold():
    flags = evaluate_flags(_signals(funding=0.08))
    f = _get_flag(flags, "FLAG_003")
    assert f is not None
    assert f["triggered"] is False


# T03 — NT-3 fires when FLAG_004 HIGH AND FLAG_005 HIGH both triggered
def test_T03_nt3_fires_on_conjunction():
    from skill.verdict_engine import evaluate_no_trade_conditions
    from skill.regime_classifier import classify_regime

    sigs = _signals(funding=0.05, net_flow=6000, fear_greed=81)
    flags = evaluate_flags(sigs)
    regime = classify_regime(sigs)

    f004 = _get_flag(flags, "FLAG_004")
    f005 = _get_flag(flags, "FLAG_005")
    assert f004["triggered"] is True, "FLAG_004 should trigger at net_flow=6000"
    assert f005["triggered"] is True, "FLAG_005 should trigger at fear_greed=81"

    nt = evaluate_no_trade_conditions(flags, regime)
    assert any("NT-3" in c for c in nt), f"NT-3 not found in: {nt}"


# T04 — NT-3 does NOT fire when only FLAG_004 is HIGH (FLAG_005 clear)
def test_T04_nt3_absent_when_only_one_flag():
    from skill.verdict_engine import evaluate_no_trade_conditions
    from skill.regime_classifier import classify_regime

    sigs = _signals(funding=0.05, net_flow=6000, fear_greed=55)
    flags = evaluate_flags(sigs)
    regime = classify_regime(sigs)

    f004 = _get_flag(flags, "FLAG_004")
    f005 = _get_flag(flags, "FLAG_005")
    assert f004["triggered"] is True
    assert f005["triggered"] is False, "FLAG_005 should be clear at fear_greed=55"

    nt = evaluate_no_trade_conditions(flags, regime)
    assert not any("NT-3" in c for c in nt), f"NT-3 should not fire: {nt}"


# Extra — FLAG_001 triggers when volume_ratio < 1.2
def test_flag001_triggers_on_weak_volume():
    flags = evaluate_flags(_signals(vol_ratio=1.1))
    f = _get_flag(flags, "FLAG_001")
    assert f["triggered"] is True


# Extra — FLAG_001 clear when volume_ratio >= 1.5
def test_flag001_clear_on_strong_volume():
    flags = evaluate_flags(_signals(vol_ratio=1.668))
    f = _get_flag(flags, "FLAG_001")
    assert f["triggered"] is False


# Extra — FLAG_005 triggers at Extreme Greed (> 80)
def test_flag005_triggers_extreme_greed():
    flags = evaluate_flags(_signals(fear_greed=81))
    f = _get_flag(flags, "FLAG_005")
    assert f["triggered"] is True


# Extra — FLAG_005 triggers at Extreme Fear (< 20)
def test_flag005_triggers_extreme_fear():
    flags = evaluate_flags(_signals(fear_greed=15))
    f = _get_flag(flags, "FLAG_005")
    assert f["triggered"] is True


# Extra — FLAG_005 clear in neutral territory
def test_flag005_clear_in_neutral():
    flags = evaluate_flags(_signals(fear_greed=55))
    f = _get_flag(flags, "FLAG_005")
    assert f["triggered"] is False


# Extra — FLAG_006 triggers at >= 3.0x
def test_flag006_triggers_at_narrative_spike():
    flags = evaluate_flags(_signals(vel_ratio=3.5))
    f = _get_flag(flags, "FLAG_006")
    assert f["triggered"] is True


# Extra — all six flags present in output
def test_all_six_flags_always_present():
    flags = evaluate_flags(_signals())
    ids = [f["id"] for f in flags]
    for expected in ["FLAG_001", "FLAG_002", "FLAG_003", "FLAG_004", "FLAG_005", "FLAG_006"]:
        assert expected in ids
