"""Cash Application agent (AR).

For each incoming bank deposit, pulls open AR invoices from the ERP, runs the
deterministic cash-match engine, and produces a Deposit record with the proposed
invoice set + rationale. Gated by the agent's threshold: suggest-only routes
everything to the analyst; auto applies high-confidence reconciliations.
"""
from __future__ import annotations

from .cash_matching import match_deposit
from .thresholds import ThresholdGate

AGENT_NAME = "Cash Application Agent"


def generate_deposits(erp, bank, suggest_only: bool = True, threshold: int = 90) -> list[dict]:
    deposits = bank.list_raw_deposits()
    open_ar = erp.list_open_ar_invoices()
    gate = ThresholdGate(agent=AGENT_NAME, threshold=threshold, suggest_only=suggest_only)

    out: list[dict] = []
    for dep in deposits:
        r = match_deposit(dep, open_ar)
        auto = r["recommendation"] == "apply" and gate.should_auto_act(r["confidence"])
        if r["method"] == "unmatched":
            status = "Unmatched"
        elif auto:
            status = "Auto-applied"
        else:
            status = "Needs Review"
        out.append({
            "id": dep["id"], "amount": r["amountStr"], "amountValue": r["amount"],
            "payer": dep["payer"], "invoices": r["invoicesLabel"], "confidence": r["confidence"],
            "status": status, "tone": r["tone"], "agent": auto,
            "customer": dep.get("customer"), "method": r["method"],
            "recommendation": r["recommendation"], "reasoning": r["reasoning"],
            "suggestions": r["suggestions"],
        })
    return out
