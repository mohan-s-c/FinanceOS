"""LLM provider abstraction (Phase: LLM-assisted reasoning).

Per V2_DESIGN_SPEC §4/§10: deterministic rules handle the happy path; an LLM agent
drafts narrative reasoning for the gray-area exceptions. The provider is swappable:

- OfflineNarrator (default) — deterministic, dependency-free; runs with no API key,
  offline. Produces a controls-analyst-style explanation from the structured exception.
- AnthropicProvider — used only when LLM_API_KEY is set. Calls the Messages API via
  stdlib urllib (no SDK dependency). Model via LLM_MODEL.

Data minimization: only the exception's discrepancy is sent to a real model, never the
vendor/customer master (see SECURITY.md).
"""
from __future__ import annotations

import json
import os
import urllib.request

SYSTEM = (
    "You are an AP/AR controls analyst. Given one invoice exception, explain the issue "
    "in 2-3 precise sentences and recommend a disposition, citing the source documents. "
    "Be concrete and concise; no preamble."
)


def _facts(ex: dict) -> dict:
    return {
        "id": ex.get("id"), "vendor": ex.get("vendor"), "amount": ex.get("amountStr"),
        "reason": ex.get("reason"), "recommendation": ex.get("recommendation"),
        "po": ex.get("po"), "terms": ex.get("terms"), "confidence": ex.get("confidence"),
        "match": ex.get("match"), "sources": ex.get("sources"),
        "lineItems": [{"desc": li.get("desc"), "total": li.get("total"), "flag": li.get("flag")} for li in ex.get("lineItems", [])],
    }


class OfflineNarrator:
    name = "offline-narrator"

    def explain(self, ex: dict) -> str:
        vendor = ex.get("vendor", "the vendor")
        amt = ex.get("amountStr", "")
        reason = ex.get("reason", "")
        po = ex.get("po", "—")
        srcs = ex.get("sources", [])
        src = (srcs[0]["ref"] if srcs else po)
        r = reason.lower()
        if "duplicate" in r:
            prior = next((s["ref"] for s in srcs if s["type"] == "Invoice"), "a prior invoice")
            return (f"This {amt} invoice from {vendor} closely matches {prior} already paid this period. "
                    f"The vendor, amount, and service window align, which is the signature of a re-submission. "
                    f"Recommend rejecting unless {vendor} confirms it covers a distinct period.")
        if "missing po" in r:
            return (f"No purchase order could be matched to this {amt} invoice from {vendor}, so a 3-way match "
                    f"isn't possible. Procurement policy requires a PO for spend at this level. "
                    f"Recommend obtaining the PO (or routing to procurement) before any payment is released.")
        if "price variance" in r:
            return (f"The invoiced amount on {ex.get('id')} is above the contracted rate in {po} beyond the "
                    f"allowed variance ceiling ({src}). The overage appears on a flagged line. "
                    f"Recommend confirming whether the excess was pre-authorized; if not, adjust to the contracted rate or reject that line.")
        if "tax" in r:
            tax = next((li["total"] for li in ex.get("lineItems", []) if li.get("flag")), "the tax line")
            return (f"Sales tax ({tax}) was applied to this {vendor} invoice, but the ship-to location maps to a "
                    f"tax-exempt municipal lease ({src}). Expected tax is $0.00. "
                    f"Recommend adjusting the tax to zero and re-approving the net amount.")
        if "approval limit" in r:
            return (f"The 3-way match on {ex.get('id')} is clean, but {amt} exceeds the capital-project "
                    f"auto-approval limit ({src}). Nothing looks wrong with the charge itself. "
                    f"Recommend Controller sign-off to release it.")
        if "goods receipt" in r:
            return (f"The goods receipt for this {amt} {vendor} invoice is incomplete, so full delivery can't be "
                    f"confirmed against {po}. Paying now risks settling for goods/services not yet received. "
                    f"Recommend confirming receipt with the receiving team before approval.")
        return (f"PO, goods receipt, and invoice for {ex.get('id')} agree within tolerance, so this is a clean match. "
                f"It is surfaced only because the AP Matching agent is in suggest-only mode. Safe to approve.")


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        self.name = f"anthropic:{model}"

    def explain(self, ex: dict) -> str:
        body = json.dumps({
            "model": self.model, "max_tokens": 320, "system": SYSTEM,
            "messages": [{"role": "user", "content": json.dumps(_facts(ex))}],
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages", data=body,
            headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
        return "".join(b.get("text", "") for b in data.get("content", [])).strip()


def get_provider():
    """OfflineNarrator unless LLM_API_KEY is set (then a real Anthropic model)."""
    key = os.getenv("LLM_API_KEY")
    if key:
        return AnthropicProvider(key, os.getenv("LLM_MODEL", "claude-haiku-4-5-20251001"))
    return OfflineNarrator()
