"""T11–T14 — Integration tests against simulated data files."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from signal_audit import run_audit
from skill.output_formatter import format_terminal, format_json

PROFIT_CLAIM_PHRASES = [
    "guaranteed",
    "will profit",
    "will make money",
    "profitable",
    "expected return",
    "alpha generation",
    "beat the market",
    "outperform",
]


# T11 — Full ABORT run against simulated_signals.json
def test_T11_full_abort_run():
    result = run_audit(signal_file="simulated_signals.json")
    assert result["verdict"]["status"] == "ABORT"
    # Must contain: verdict, ≥1 triggered flag, modified_spec, historical_reference
    triggered = [f for f in result["flags"] if f["triggered"]]
    assert len(triggered) >= 1, "At least one flag must be triggered"
    assert "modified_strategy_spec" in result
    assert result["modified_strategy_spec"] is not None
    assert "historical_reference" in result
    assert result["historical_reference"]["included"] is True


# T12 — Full PROCEED run against simulated_signals_clean.json
def test_T12_full_proceed_run():
    result = run_audit(signal_file="simulated_signals_clean.json")
    assert result["verdict"]["status"] == "PROCEED"
    # modified_spec still present
    assert "modified_strategy_spec" in result
    assert result["modified_strategy_spec"]["entry_condition"] != ""


# T13 — evidence_mode visible in all output blocks
def test_T13_evidence_mode_present_throughout():
    result = run_audit(signal_file="simulated_signals.json", evidence_mode="SIMULATED")

    # Top level
    assert result["evidence_mode"] == "SIMULATED"

    # Regime
    assert result["regime"]["evidence_mode"] == "SIMULATED"

    # Every flag
    for flag in result["flags"]:
        assert "evidence_mode" in flag, f"Missing evidence_mode on {flag['id']}"
        assert flag["evidence_mode"] == "SIMULATED"

    # Modified spec
    assert result["modified_strategy_spec"]["evidence_status"] == "SIMULATED"

    # Historical reference
    assert result["historical_reference"]["evidence_status"] == "ASSUMED"


# T14 — No profit claims anywhere in terminal or JSON output
def test_T14_no_profit_claims():
    result = run_audit(signal_file="simulated_signals.json")
    terminal = format_terminal(result).lower()
    json_out = format_json(result).lower()

    for phrase in PROFIT_CLAIM_PHRASES:
        assert phrase not in terminal, (
            f"Profit claim phrase '{phrase}' found in terminal output"
        )
        assert phrase not in json_out, (
            f"Profit claim phrase '{phrase}' found in JSON output"
        )


# Extra — historical reference evidence_status is ASSUMED
def test_historical_reference_is_assumed():
    result = run_audit(signal_file="simulated_signals.json")
    ref = result["historical_reference"]
    assert ref["evidence_status"] == "ASSUMED"
    # Must not claim profit
    full_text = json.dumps(ref).lower()
    for phrase in PROFIT_CLAIM_PHRASES:
        assert phrase not in full_text


# Extra — SIMULATED mode does not raise
def test_simulated_mode_runs_without_error():
    result = run_audit(evidence_mode="SIMULATED", signal_file="simulated_signals.json")
    assert result["skill"] == "signal_audit"


# Extra — LIVE_CMC mode raises NotImplementedError (stub only)
def test_live_cmc_raises_not_implemented():
    import pytest
    with pytest.raises(NotImplementedError):
        run_audit(evidence_mode="LIVE_CMC")


# Extra — output is schema-valid (AuditOutput) for both paths
def test_schema_valid_both_paths():
    from skill.schema import AuditOutput
    for sf in ("simulated_signals.json", "simulated_signals_clean.json"):
        result = run_audit(signal_file=sf)
        # AuditOutput(**result) called inside run_audit; if we get here schema passed
        assert result["version"] == "1.0"
