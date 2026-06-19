"""
SignalAudit — Input/Output Schema
Evidence modes: LIVE_CMC | SIMULATED | ASSUMED
"""

from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


# ── Input ────────────────────────────────────────────────────────────────────

class AuditInput(BaseModel):
    strategy_hypothesis: str = Field(
        default=(
            "Long BTC when the daily close prints above the 20-day high "
            "on volume at least 1.5x the 20-day average volume."
        ),
        description="Plain-language strategy to audit.",
    )
    asset: str = Field(default="BTC")
    timeframe: Literal["4h", "1d", "1w"] = Field(default="1d")
    risk_tolerance: Literal["conservative", "moderate", "aggressive"] = Field(
        default="moderate"
    )
    evidence_mode: Literal["LIVE_CMC", "SIMULATED", "ASSUMED"] = Field(
        default="SIMULATED"
    )


# ── Regime ───────────────────────────────────────────────────────────────────

class Regime(BaseModel):
    label: Literal[
        "TRENDING_UP", "TRENDING_DOWN", "RANGING", "VOLATILE_BREAKDOWN"
    ]
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    basis: List[str]
    evidence_mode: Literal["LIVE_CMC", "SIMULATED", "ASSUMED"]


# ── Flags ────────────────────────────────────────────────────────────────────

class Flag(BaseModel):
    id: str
    name: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    value: str
    threshold: str
    triggered: bool
    source: str                                          # CMC tool name | SIMULATED | ASSUMED
    evidence_mode: Literal["LIVE_CMC", "SIMULATED", "ASSUMED"]


# ── Verdict ──────────────────────────────────────────────────────────────────

class Verdict(BaseModel):
    status: Literal["PROCEED", "REDUCE_RISK", "ABORT"]
    rationale: str                                       # References ≥ 1 flag by name


# ── Modified Strategy Spec ───────────────────────────────────────────────────

class ModifiedStrategySpec(BaseModel):
    hypothesis: str
    regime_gate: str
    entry_condition: str
    exit_condition: str
    position_size_rule: str
    stop_loss: str
    no_trade_condition: str
    backtest_hypothesis: str
    re_evaluate_when: Optional[str] = None
    monitor_condition: Optional[str] = None
    evidence_status: Literal["LIVE_CMC", "SIMULATED", "ASSUMED"]


# ── Historical Reference ──────────────────────────────────────────────────────

class HistoricalReference(BaseModel):
    included: bool
    example_id: str
    description: str
    audit_verdict: str
    active_flags: List[str]
    actual_outcome: str
    interpretation: str
    evidence_status: Literal["LIVE_CMC", "SIMULATED", "ASSUMED"] = "ASSUMED"


# ── Full Output ───────────────────────────────────────────────────────────────

class AuditOutput(BaseModel):
    skill: str = "signal_audit"
    version: str = "1.0"
    asset: str
    timeframe: str
    timestamp: str
    evidence_mode: Literal["LIVE_CMC", "SIMULATED", "ASSUMED"]

    regime: Regime
    verdict: Verdict
    flags: List[Flag]
    no_trade_conditions_active: List[str]
    modified_strategy_spec: ModifiedStrategySpec          # Always present — AC-3
    historical_reference: HistoricalReference
