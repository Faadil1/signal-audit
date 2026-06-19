"""
Output formatter — terminal and JSON.
No profit claims. Evidence mode visible on every block.
"""

from __future__ import annotations
import json
from typing import List


_VERDICT_ICON = {
    "PROCEED":     "✅",
    "REDUCE_RISK": "⚠️ ",
    "ABORT":       "🛑",
}

_SEV_ICON = {
    "CRITICAL": "🔴",
    "HIGH":     "🟠",
    "MEDIUM":   "🟡",
    "LOW":      "🟢",
}


def format_terminal(output: dict) -> str:
    lines = []
    em = output.get("evidence_mode", "UNKNOWN")

    lines += [
        "",
        "━" * 60,
        "  SignalAudit v1.0 — Strategy Readiness Assessment",
        f"  Asset: {output['asset']} | Timeframe: {output['timeframe']}",
        f"  Evidence mode: {em}",
        f"  Timestamp: {output['timestamp']}",
        "━" * 60,
    ]

    # ── Regime ───────────────────────────────────────────────────────────────
    regime = output["regime"]
    lines += [
        "",
        f"REGIME  [{regime['evidence_mode']}]",
        f"  Label:      {regime['label']}",
        f"  Confidence: {regime['confidence']}",
    ]
    for b in regime["basis"]:
        lines.append(f"  Basis:      {b}")

    # ── Flags ─────────────────────────────────────────────────────────────────
    lines += ["", "FLAGS"]
    triggered_any = False
    for flag in output["flags"]:
        icon = _SEV_ICON.get(flag["severity"], "⬜")
        mark = "✗" if flag["triggered"] else "✓"
        lines.append(
            f"  {mark} {flag['id']}  {flag['name']:<20}  "
            f"{icon} {flag['severity']:<8}  "
            f"{flag['value']:<30}  [{flag['evidence_mode']}]"
        )
        if flag["triggered"]:
            lines.append(f"    └─ threshold: {flag['threshold']}")
            triggered_any = True
    if not triggered_any:
        lines.append("  All flags clear.")

    # ── No-trade conditions ──────────────────────────────────────────────────
    nt = output.get("no_trade_conditions_active", [])
    if nt:
        lines += ["", "NO-TRADE CONDITIONS ACTIVE"]
        for condition in nt:
            lines.append(f"  ⛔ {condition}")

    # ── Verdict ───────────────────────────────────────────────────────────────
    verdict = output["verdict"]
    icon = _VERDICT_ICON.get(verdict["status"], "")
    lines += [
        "",
        f"VERDICT  {icon} {verdict['status']}",
        f"  {verdict['rationale']}",
    ]

    # ── Modified Strategy Spec ────────────────────────────────────────────────
    spec = output["modified_strategy_spec"]
    lines += [
        "",
        f"MODIFIED STRATEGY SPEC  [{spec['evidence_status']}]",
        f"  Regime gate:      {spec['regime_gate']}",
        f"  Entry:            {spec['entry_condition']}",
        f"  Exit:             {spec['exit_condition']}",
        f"  Position size:    {spec['position_size_rule']}",
        f"  Stop loss:        {spec['stop_loss']}",
        f"  No-trade:         {spec['no_trade_condition']}",
        f"  Backtest spec:    {spec['backtest_hypothesis']}",
    ]
    if spec.get("re_evaluate_when"):
        lines.append(f"  Re-evaluate when: {spec['re_evaluate_when']}")
    if spec.get("monitor_condition"):
        lines.append(f"  Monitor:          {spec['monitor_condition']}")

    # ── Historical Reference ──────────────────────────────────────────────────
    ref = output.get("historical_reference", {})
    if ref.get("included"):
        lines += [
            "",
            f"HISTORICAL REFERENCE  [{ref.get('evidence_status', 'ASSUMED')}]",
            f"  ID:              {ref['example_id']}",
            f"  Context:         {ref['description']}",
            f"  Verdict:         {ref['audit_verdict']}",
            f"  Flags active:    {', '.join(ref['active_flags'])}",
            f"  Outcome:         {ref['actual_outcome']}",
            f"  Interpretation:  {ref['interpretation']}",
            "  ⚠️  Not a profit claim. Directional illustration only.",
        ]

    lines += [
        "",
        "━" * 60,
        "  DISCLOSURE: This output is not investment advice.",
        "  No live trading. No profit claims. Evidence mode labeled above.",
        "  See DISCLOSURE.md for full statement.",
        "━" * 60,
        "",
    ]

    return "\n".join(lines)


def format_json(output: dict) -> str:
    return json.dumps(output, indent=2)
