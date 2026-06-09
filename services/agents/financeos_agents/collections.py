"""Collections agent (AR, Phase 3).

Deterministic risk scoring over overdue accounts → a prioritized action and a
drafted outreach message. Suggest-only: the agent drafts; a human sends. Risk is a
transparent function of days-past-due and outstanding balance.
"""
from __future__ import annotations

import re


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _fmt(x: float) -> str:
    return f"${x:,.0f}"


def _clamp(n: int, lo: int = 0, hi: int = 99) -> int:
    return max(lo, min(hi, n))


def score_account(acct: dict) -> dict:
    days = int(acct["days"])
    bal = float(acct["balance"])
    risk = _clamp(round(days * 1.05 + bal / 2500))
    if risk >= 80:
        action, tone, rec = "Offer payment plan", "bad", "plan"
        body = f"propose a structured payment plan to clear the {_fmt(bal)} balance"
    elif risk >= 60:
        action, tone, rec = "Send 2nd reminder", "bad", "reminder2"
        body = f"second reminder that {_fmt(bal)} is now {days} days past due"
    elif risk >= 40:
        action, tone, rec = "Send reminder", "warn", "reminder"
        body = f"a courteous reminder that {_fmt(bal)} is {days} days past due"
    else:
        action, tone, rec = "Monitor", "ok", "monitor"
        body = f"no outreach yet — monitor; {_fmt(bal)} is only {days} days out"
    draft = (f"Hi {acct['account']} team — this is a note regarding {body}. "
             f"Please reply with a payment date or let us know if you have any questions.")
    return {"risk": risk, "action": action, "tone": tone, "recommendation": rec, "draft": draft}


def generate_collections(erp, suggest_only: bool = True) -> list[dict]:
    out: list[dict] = []
    for a in erp.list_overdue_accounts():
        s = score_account(a)
        out.append({
            "id": _slug(a["account"]), "account": a["account"], "loc": a["loc"],
            "balance": _fmt(a["balance"]), "balanceValue": float(a["balance"]),
            "days": int(a["days"]), "risk": s["risk"], "action": s["action"],
            "agent": True, "tone": s["tone"], "recommendation": s["recommendation"],
            "draft": s["draft"], "status": "Drafted",
        })
    # highest risk first
    return sorted(out, key=lambda c: -c["risk"])
