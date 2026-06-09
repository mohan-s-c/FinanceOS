"""AP Matching agent.

Pulls each invoice + its PO/GR from the ERP connector, runs the deterministic
3-way match engine, and turns the result into an Exception in the shared schema.
Gated by the agent's confidence threshold: in suggest-only mode every item routes
to the analyst (the Phase 1 trust posture); once promoted to auto, a clean match
at/above the threshold auto-approves and the rest still escalate.
"""
from __future__ import annotations

from .matching import three_way_match, fmt, invoice_total
from .thresholds import ThresholdGate

AGENT_NAME = "AP Matching Agent"


def _exception_from(inv: dict, r: dict, status: str) -> dict:
    return {
        "id": inv["id"], "vendor": inv["vendor"], "vinit": inv.get("vinit", inv["vendor"][:2].upper()),
        "amount": r["invTotal"], "amountStr": fmt(r["invTotal"]),
        "location": inv.get("location", "—"), "reason": r["reason"],
        "confidence": r["confidence"], "tone": r["tone"], "agent": AGENT_NAME,
        "status": status, "date": inv.get("date", ""), "po": inv.get("po_ref") or "—",
        "terms": inv.get("terms", ""),
        "lineItems": [
            {"desc": li["desc"], "qty": li["qty"], "unit": fmt(float(li["unit"])), "total": fmt(float(li["total"])), "flag": bool(li.get("flag"))}
            for li in inv.get("lineItems", [])
        ],
        "match": r["match"], "reasoning": r["reasoning"], "sources": r["sources"],
        "recommendation": r["recommendation"],
    }


def generate_exceptions(erp, suggest_only: bool = True, threshold: int = 85) -> list[dict]:
    """Run the agent over the ERP's open AP invoices; return Exception records."""
    docs = erp.list_ap_documents()
    policies = erp.policies()
    paid = erp.paid_invoices()
    gate = ThresholdGate(agent=AGENT_NAME, threshold=threshold, suggest_only=suggest_only)

    out: list[dict] = []
    for d in docs:
        inv = d["invoice"]
        r = three_way_match(inv, d.get("po"), d.get("gr"), policies, paid)
        auto = r["recommendation"] == "approve" and gate.should_auto_act(r["confidence"])
        status = "Auto-approved" if auto else "Needs Review"
        out.append(_exception_from(inv, r, status))
    return out


def open_exceptions(erp, suggest_only: bool = True, threshold: int = 85) -> list[dict]:
    """Just the items that still need a human (status == Needs Review)."""
    return [e for e in generate_exceptions(erp, suggest_only, threshold) if e["status"] == "Needs Review"]
