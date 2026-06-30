"""Supervisor P1 — observe-only agent-health computation (V3 Part A, milestone M1).

Pure module: computes per-agent rolling-window health metrics from audit-trail
rows. No I/O, no clock, no enforcement — the Supervisor at this phase only
*observes*. Persistence (agent_health snapshots) and cadence live behind
repo.py / the API evaluator; the decision logic here is deterministic and
auditable per the V3 tech spec (A5): an auditor must be able to recompute any
status from the same rows.

Metrics (tech spec A3), all derived from the existing append-only audit table:
- override rate    — overridden / completed decisions (auto + human_resolved
                     + overridden). The core trust signal.
- confidence drift — mean confidence of the newer half of the window minus the
                     older half (explainable stats only, no model).
- volume           — decision count in the window.
- error rate       — share of 'error' outcomes (agents emit none today; the
                     metric is wired so P2+ telemetry lands without a schema change).
- escalation share — escalated / volume (a context signal for the tooltip).
- latency p95      — not derivable from the audit trail; None until agents emit
                     per-call telemetry (P2).
"""
from __future__ import annotations

# Outcomes that represent an agent decision reaching the trail.
DECISION_OUTCOMES = {"auto", "escalated", "human_resolved", "overridden"}
# Decisions that reached a disposition (denominator for the override rate).
COMPLETED_OUTCOMES = {"auto", "human_resolved", "overridden"}

DEFAULT_WINDOW = 200

# Status thresholds. Deterministic and versioned with the code for P1;
# P2 moves them into policy_rule records so Controllers can tune them.
OVERRIDE_ALERT = 0.15
OVERRIDE_WATCH = 0.05
ERROR_ALERT = 0.10
DRIFT_WATCH = -10.0     # avg confidence fell ≥ 10 pts across the window
ESCALATION_WATCH = 0.60


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def compute_agent_health(rows: list[dict], window: int = DEFAULT_WINDOW) -> dict:
    """Health metrics for ONE agent from its audit rows (oldest → newest).

    Rows are dicts with at least 'outcome' and 'conf'. Returns the metric set;
    status mapping is applied by health_status().
    """
    relevant = [r for r in rows if r.get("outcome") in DECISION_OUTCOMES or r.get("outcome") == "error"]
    windowed = relevant[-window:]
    decisions = [r for r in windowed if r.get("outcome") in DECISION_OUTCOMES]
    errors = [r for r in windowed if r.get("outcome") == "error"]

    volume = len(decisions)
    completed = [r for r in decisions if r["outcome"] in COMPLETED_OUTCOMES]
    overridden = [r for r in completed if r["outcome"] == "overridden"]
    escalated = [r for r in decisions if r["outcome"] == "escalated"]

    override_rate = len(overridden) / len(completed) if completed else 0.0
    escalation_share = len(escalated) / volume if volume else 0.0
    error_rate = len(errors) / (len(errors) + volume) if (errors or volume) else 0.0

    confs = [r["conf"] for r in decisions if r.get("conf")]
    avg_conf = _mean(confs)
    # Drift: newer half vs older half of the confidence series. Needs enough
    # points on both sides to mean anything; otherwise report 0 (no drift signal).
    conf_drift = 0.0
    if len(confs) >= 4:
        half = len(confs) // 2
        conf_drift = _mean(confs[half:]) - _mean(confs[:half])

    return {
        "volume": volume,
        "override_rate": round(override_rate, 4),
        "escalation_share": round(escalation_share, 4),
        "error_rate": round(error_rate, 4),
        "avg_confidence": round(avg_conf, 1),
        "conf_drift": round(conf_drift, 1),
        "latency_p95": None,
    }


def health_status(m: dict) -> tuple[str, list[str]]:
    """Map metrics → (status, reasons). Statuses: ok | watch | alert | nodata."""
    if m["volume"] == 0:
        return "nodata", ["no decisions in window"]
    reasons: list[str] = []
    status = "ok"
    if m["override_rate"] >= OVERRIDE_ALERT:
        status = "alert"
        reasons.append(f"override rate {m['override_rate']:.0%} ≥ {OVERRIDE_ALERT:.0%}")
    if m["error_rate"] >= ERROR_ALERT:
        status = "alert"
        reasons.append(f"error rate {m['error_rate']:.0%} ≥ {ERROR_ALERT:.0%}")
    if status != "alert":
        if m["override_rate"] >= OVERRIDE_WATCH:
            status = "watch"
            reasons.append(f"override rate {m['override_rate']:.0%} ≥ {OVERRIDE_WATCH:.0%}")
        if m["conf_drift"] <= DRIFT_WATCH:
            status = "watch"
            reasons.append(f"confidence drifted {m['conf_drift']:+.1f} pts")
        if m["escalation_share"] >= ESCALATION_WATCH:
            status = "watch"
            reasons.append(f"escalation share {m['escalation_share']:.0%} ≥ {ESCALATION_WATCH:.0%}")
    if not reasons:
        reasons.append("all signals within bands")
    return status, reasons


def evaluate(audit_rows: list[dict], roster: list[dict], window: int = DEFAULT_WINDOW) -> list[dict]:
    """Health snapshot for every roster agent. Observe-only: returns data, never acts.

    audit_rows: audit-trail dicts (oldest → newest) with 'agent' (display name),
                'outcome', 'conf'.
    roster:     [{'id': ..., 'name': ...}] — every agent is reported, including
                those with no telemetry yet (status 'nodata'), so silence is
                visible rather than green (fail-safe principle, tech spec A1).
    """
    by_name: dict[str, list[dict]] = {}
    for r in audit_rows:
        by_name.setdefault(r.get("agent") or "", []).append(r)

    out = []
    for a in roster:
        metrics = compute_agent_health(by_name.get(a["name"], []), window)
        status, reasons = health_status(metrics)
        signals = [
            {"metric": "volume", "label": "Decisions in window", "value": str(metrics["volume"])},
            {"metric": "override_rate", "label": "Override rate", "value": f"{metrics['override_rate']:.1%}"},
            {"metric": "escalation_share", "label": "Escalation share", "value": f"{metrics['escalation_share']:.0%}"},
            {"metric": "avg_confidence", "label": "Avg confidence", "value": f"{metrics['avg_confidence']:.0f}%"},
            {"metric": "conf_drift", "label": "Confidence drift", "value": f"{metrics['conf_drift']:+.1f} pts"},
            {"metric": "error_rate", "label": "Error rate", "value": f"{metrics['error_rate']:.1%}"},
        ]
        out.append({
            "agent_id": a["id"],
            "name": a["name"],
            "window": f"last-{window}",
            "status": status,
            "reasons": reasons,
            "override_rate": metrics["override_rate"],
            "conf_drift": metrics["conf_drift"],
            "volume": metrics["volume"],
            "error_rate": metrics["error_rate"],
            "latency_p95": metrics["latency_p95"],
            "signals": signals,
        })
    return out
