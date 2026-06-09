"""Analytics read model.

Serves the historical trend series + summary cards (seeded), plus a *live this
session* block computed from the persisted audit trail and current queue state —
so the Analytics screen reflects real agent activity, not just static mock numbers.
"""
from __future__ import annotations

import copy
from collections import Counter

from . import repo

_ANALYTICS = {
    "touchlessTrend": [58, 61, 64, 67, 69, 72, 74, 77, 79, 80, 81, 82],
    "costPerInvoice": [4.10, 3.85, 3.60, 3.20, 2.95, 2.70, 2.40, 2.15, 1.90, 1.70, 1.55, 1.42],
    "closeCycle": [5.5, 5.1, 4.6, 4.0, 3.4, 2.9, 2.4, 2.0, 1.7, 1.5, 1.3, 1.2],
    "dso": [41, 40, 38, 37, 36, 34, 33, 32, 31, 30, 29, 28.4],
    "overrideRate": [12, 11, 10, 9.5, 8.8, 8.0, 7.2, 6.5, 6.0, 5.4, 5.0, 4.6],
    "months": ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May"],
}

_CARDS = [
    {"label": "Touchless Rate", "value": "82%", "target": "Target 85%", "pct": 96, "dir": "up", "delta": "+24 pts YoY"},
    {"label": "Cost / Invoice", "value": "$1.42", "target": "Target $1.25", "pct": 88, "dir": "up", "delta": "−65% YoY"},
    {"label": "Close Cycle", "value": "1.2 days", "target": "Target 1.0 day", "pct": 83, "dir": "up", "delta": "−78% YoY"},
    {"label": "DSO", "value": "28.4 days", "target": "Target 26 days", "pct": 91, "dir": "up", "delta": "−12.6 days YoY"},
    {"label": "Leakage Recovered", "value": "$1.3M", "target": "YTD $7.8M", "pct": 74, "dir": "up", "delta": "+$0.4M MTD"},
    {"label": "Human Override Rate", "value": "4.6%", "target": "Target <5%", "pct": 92, "dir": "up", "delta": "−7.4 pts YoY"},
]


def get_analytics() -> dict:
    audit = repo.audit_log(limit=1000)
    c = Counter(a["outcome"] for a in audit)
    auto = c.get("auto", 0)
    escalated = c.get("escalated", 0)
    overridden = c.get("overridden", 0)
    human = c.get("human_resolved", 0)
    total = auto + escalated + overridden + human
    touchless = round(100 * auto / total) if total else 0
    override = round(100 * overridden / total, 1) if total else 0.0
    unapplied_total, _ = repo.unapplied_summary()
    live = {
        "decisions": total,
        "autoActions": auto,
        "escalations": escalated + human,
        "touchlessSession": touchless,
        "overrideSession": override,
        "openExceptions": repo.open_count(),
        "unappliedTotal": unapplied_total,
    }
    return {"analytics": copy.deepcopy(_ANALYTICS), "cards": copy.deepcopy(_CARDS), "live": live}
