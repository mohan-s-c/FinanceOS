"""Anomaly & Leakage detection agent.

Scans ledger signals from the ERP connector, ranks by severity, and reports a
leakage-recovered trend. Flag-only — anomalies always surface for human review and
never auto-resolve.
"""
from __future__ import annotations

_SEV_ORDER = {"high": 0, "med": 1, "low": 2}


def detect(erp) -> dict:
    signals = erp.list_anomaly_signals()
    ranked = sorted(signals, key=lambda a: (_SEV_ORDER.get(a["sev"], 9), -a["risk"]))
    items = [{**a, "risk": f"${a['risk']:,.0f}"} for a in ranked]
    trend, months = erp.leakage_series()
    at_risk = sum(a["risk"] for a in signals)
    recovered = trend[-1] if trend else 0.0
    return {
        "items": items,
        "atRisk": f"${at_risk:,.0f}",
        "leakageRecovered": f"${recovered:.1f}M",
        "leakageTrend": trend,
        "leakageMonths": months,
        "highCount": sum(1 for a in signals if a["sev"] == "high"),
    }
