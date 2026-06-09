"""Deterministic AR cash-application matcher (deposit → open invoices).

Pure, dependency-free, testable. Mirrors the spec's AR strategy: exact, then
remittance-hint, then customer batch, then fuzzy subset, else unmatched. Returns a
confidence ("confidence it's safe to auto-apply"), the proposed invoice set, a
human-readable rationale, and a display label.
"""
from __future__ import annotations

from itertools import combinations
from typing import Optional


def fmt(x: float) -> str:
    return f"${x:,.2f}"


def _clamp(n: int, lo: int = 3, hi: int = 99) -> int:
    return max(lo, min(hi, n))


def match_deposit(deposit: dict, open_invoices: list[dict], tol: float = 1.0) -> dict:
    """Match one deposit against open AR invoices. `tol` is the $ reconciliation slack."""
    amount = float(deposit["amount"])
    customer = deposit.get("customer")
    remittance = deposit.get("remittance") or []
    by_id = {inv["id"]: inv for inv in open_invoices}
    cust_invs = [inv for inv in open_invoices if customer and inv["customer"] == customer]

    method = "unmatched"
    matched: list[dict] = []
    confidence = 31
    reconciled = False

    # 1) remittance-hint
    if remittance:
        refs = [by_id[r] for r in remittance if r in by_id]
        if refs and abs(sum(i["amount"] for i in refs) - amount) <= tol:
            method, matched, confidence, reconciled = "remittance", refs, 97, True

    # 2) exact single
    if method == "unmatched":
        exact = [inv for inv in open_invoices if abs(inv["amount"] - amount) <= tol]
        if exact:
            method, matched, confidence, reconciled = "exact", [exact[0]], 93, True

    # 3) customer batch (all of the customer's open invoices reconcile)
    if method == "unmatched" and cust_invs and abs(sum(i["amount"] for i in cust_invs) - amount) <= tol:
        method, matched, confidence, reconciled = "batch", cust_invs, 88, True

    # 4) fuzzy subset — the subset of the customer's open invoices whose sum is
    #    closest to the deposit (full search; per-customer sets are small).
    if method == "unmatched" and cust_invs:
        pool = sorted(cust_invs, key=lambda i: -i.get("age", 0))[:12]
        best = None  # (diff, fewest_items, subset)
        for r_ in range(1, len(pool) + 1):
            for combo in combinations(pool, r_):
                diff = abs(sum(i["amount"] for i in combo) - amount)
                key = (diff, len(combo))
                if best is None or key < best[0]:
                    best = (key, list(combo))
        subset = best[1]
        diff_ratio = abs(sum(i["amount"] for i in subset) - amount) / amount if amount else 1.0
        if diff_ratio <= 0.02:
            method, matched, confidence = "fuzzy", subset, 64
        elif diff_ratio <= 0.12:
            method, matched, confidence = "fuzzy", subset, 52

    n = len(matched)
    if method == "unmatched":
        recommendation, tone, label = "unmatched", "bad", "No match"
        reasoning = f"No open invoice or customer reconciles to {fmt(amount)} from “{deposit.get('payer','')}”. Needs manual identification."
    elif method == "remittance":
        recommendation, tone, label = "apply", "ok", f"{n} invoices"
        reasoning = f"Remittance advice references {n} open invoices that sum to {fmt(amount)} — exact reconciliation."
    elif method == "exact":
        recommendation, tone, label = "apply", "ok", f"{n} invoice"
        reasoning = f"Deposit {fmt(amount)} exactly matches open invoice {matched[0]['id']} ({matched[0]['customer']})."
    elif method == "batch":
        recommendation, tone, label = "apply", "ok", f"{n} invoices"
        reasoning = f"{customer}'s {n} open invoices sum to {fmt(amount)} — full batch reconciliation."
    else:  # fuzzy
        recommendation, tone, label = "review", ("warn" if confidence < 60 else "ok"), f"Suggested: {n}"
        reasoning = (f"No exact match. Best candidate: {n} oldest open invoice(s) for {customer} "
                     f"(≈{fmt(sum(i['amount'] for i in matched))} vs {fmt(amount)}). Suggest analyst confirm.")

    suggestions = [{"inv": i["id"], "customer": i["customer"], "amount": fmt(i["amount"]), "confidence": confidence} for i in matched]

    return {
        "amount": amount, "amountStr": fmt(amount), "method": method,
        "confidence": _clamp(confidence), "recommendation": recommendation, "tone": tone,
        "reasoning": reasoning, "invoicesLabel": label, "reconciled": reconciled,
        "suggestions": suggestions, "matchedCount": n,
    }
