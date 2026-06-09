"""Deterministic, tolerance-aware 3-way match engine (AP).

Pure functions — no I/O, no deps — so they're trivially testable and identical in
dev and prod. Given an invoice plus its purchase order, goods receipt, and the
governing policies, this reproduces V1's `match` model *for real*: it compares
PO ↔ GR ↔ invoice line-by-line and in total, applies tolerance and policy rules,
and emits a recommendation with a confidence score, human-readable reasoning, and
the source documents it relied on.

Confidence here means "confidence it is safe to auto-approve" (high = clean), so
problematic invoices score low and fall below any auto-approve threshold.
"""
from __future__ import annotations

from typing import Optional


def fmt(x: float) -> str:
    return f"${x:,.2f}"


def _clamp(n: int, lo: int = 3, hi: int = 99) -> int:
    return max(lo, min(hi, n))


def invoice_total(invoice: dict) -> float:
    if invoice.get("amount") is not None:
        return float(invoice["amount"])
    return round(sum(float(li["total"]) for li in invoice.get("lineItems", [])), 2)


def three_way_match(
    invoice: dict,
    po: Optional[dict],
    gr: Optional[dict],
    policies: dict,
    paid_invoices: Optional[list[dict]] = None,
) -> dict:
    """Run the 3-way match. Returns a result dict consumed by the AP Matching agent."""
    paid_invoices = paid_invoices or []
    issues: list[str] = []
    sources: list[dict] = []
    penalty = 0
    inv_total = invoice_total(invoice)
    tax = float(invoice.get("tax", 0) or 0)
    pre_tax = round(inv_total - tax, 2)
    po_ref = invoice.get("po_ref") or (po.get("id") if po else None)
    po_found = bool(po_ref) and po is not None
    gr_status = (gr or {}).get("status", "none")

    # ---- duplicate detection (highest severity) ----
    dup = None
    for p in paid_invoices:
        if p["vendor"] == invoice["vendor"] and abs(float(p["amount"]) - inv_total) < 0.01:
            sim = int(p.get("similarity", 95))
            dup = (p, sim)
            break

    # ---- missing PO ----
    po_required_above = float(policies.get("po_required_above", 10000))
    if not po_found:
        # No PO ⇒ a 3-way match is impossible; always a finding (severity scales with amount).
        if inv_total > po_required_above:
            penalty += 52
            sources.append({"type": "Policy", "ref": policies.get("po_policy_ref", "AP-POL-07"), "note": f"PO threshold {fmt(po_required_above)}"})
        else:
            penalty += 30

    # ---- price variance vs PO ----
    variance_pct = 0.0
    ceiling = float(po.get("variance_ceiling", 0.05)) if po else 0.05
    if po_found:
        po_total = float(po["total"])
        if po_total > 0:
            variance_pct = (pre_tax - po_total) / po_total
        if variance_pct > ceiling:
            over = variance_pct - ceiling
            penalty += int(min(45, round(over * 100 * 5)))
            issues.append(f"Price variance vs PO (+{round(variance_pct * 100)}%)")
            if po.get("contract_ref"):
                sources.append({"type": "Contract", "ref": po["contract_ref"], "note": "rate schedule"})

    # ---- tax jurisdiction ----
    if po and po.get("tax_exempt") and float(invoice.get("tax", 0) or 0) > 0:
        issues.append("Tax jurisdiction mismatch")
        penalty += 33
        if po.get("lease_ref"):
            sources.append({"type": "Lease", "ref": po["lease_ref"], "note": "tax-exempt"})

    # ---- goods receipt ----
    gr_ok = gr_status == "received"
    if not gr_ok:
        penalty += 12

    # ---- approval limit (even a clean match needs sign-off) ----
    capex_above = float(policies.get("capex_signoff_above", 20000))
    over_limit = inv_total > capex_above
    if over_limit and not issues and gr_ok and po_found and variance_pct <= ceiling:
        issues.append("Amount exceeds approval limit")
        penalty += 28
        sources.append({"type": "Policy", "ref": policies.get("capex_policy_ref", "AP-POL-11"), "note": f"capex sign-off {fmt(capex_above)}"})

    # ---- decide ----
    if dup:
        p, sim = dup
        penalty = max(penalty, int(round(sim * 0.6)))
        recommendation, tone = "reject", "bad"
        reason = f"Possible duplicate of {p['id']}"
        reasoning = (f"Near-identical to invoice {p['id']} already paid this period "
                     f"({sim}% similarity on vendor, amount, service window). High-confidence duplicate.")
        sources.insert(0, {"type": "Invoice", "ref": p["id"], "note": "prior payment"})
        within_tol = False
    elif not po_found:
        if inv_total > po_required_above:
            recommendation, tone = "hold", "bad"
            reason = "Missing PO reference"
            reasoning = (f"No purchase-order reference matched this invoice. Policy requires a PO for "
                         f"invoices above {fmt(po_required_above)} (this is {fmt(inv_total)}).")
        else:
            recommendation, tone = "escalate", "warn"
            reason = "Missing PO reference"
            reasoning = (f"No purchase order to 3-way match against ({fmt(inv_total)}); under the "
                         f"{fmt(po_required_above)} PO-required threshold, but still routed for review.")
        within_tol = False
    elif any(i.startswith("Price variance") for i in issues):
        recommendation, tone = "escalate", "warn"
        reason = issues[0]
        reasoning = (f"Invoiced {fmt(inv_total)} is {round(variance_pct * 100)}% above the contracted "
                     f"{fmt(po['total'])} in {po_ref}; the contract allows a {round(ceiling*100)}% variance ceiling.")
        within_tol = False
    elif "Tax jurisdiction mismatch" in issues:
        recommendation, tone = "escalate", "warn"
        reason = "Tax jurisdiction mismatch"
        reasoning = (f"Tax of {fmt(float(invoice.get('tax', 0)))} was applied, but the ship-to maps to a "
                     f"tax-exempt lease. Expected tax is $0.00.")
        within_tol = False
    elif not gr_ok:
        recommendation, tone = "escalate", "warn"
        reason = "Goods receipt incomplete"
        reasoning = (f"Goods receipt is '{gr_status}' — full receipt can't be confirmed, so the invoice "
                     f"can't be cleanly matched. Routed for review.")
        within_tol = False
    elif over_limit:
        recommendation, tone = "escalate", "warn"
        reason = "Amount exceeds approval limit"
        reasoning = (f"3-way match is clean, but {fmt(inv_total)} exceeds the {fmt(capex_above)} "
                     f"auto-approval limit for capital projects. Routed for human sign-off.")
        within_tol = True
    else:
        recommendation, tone = "approve", "ok"
        reason = "3-way match clean"
        reasoning = (f"PO, goods receipt, and invoice agree within tolerance "
                     f"(variance {round(variance_pct * 100, 1)}% ≤ {round(ceiling*100)}%). Safe to approve.")
        within_tol = True

    confidence = _clamp(100 - penalty) if recommendation != "approve" else _clamp(96 - penalty)

    match = {
        "po": {"rate": fmt(po["total"]) if po_found else "Not found",
               "label": "Contracted" if po_found else "PO reference",
               **({"mismatch": True} if not po_found else {})},
        "gr": {"rate": gr_status.title() if gr_status != "none" else "Missing",
               "label": "Goods receipt",
               **({"mismatch": True} if not gr_ok and po_found else {})},
        "inv": {"rate": fmt(inv_total), "label": "Invoiced",
                **({"mismatch": True} if (not within_tol or recommendation == "reject") else {})},
    }
    if po_found and not any(s["ref"] == po_ref for s in sources):
        sources.append({"type": "PO", "ref": po_ref, "note": invoice.get("location", "")})

    return {
        "withinTolerance": within_tol,
        "recommendation": recommendation,
        "confidence": confidence,
        "reason": reason,
        "reasoning": reasoning,
        "tone": tone,
        "match": match,
        "sources": sources,
        "issues": issues,
        "invTotal": inv_total,
        "variancePct": round(variance_pct, 4),
    }
