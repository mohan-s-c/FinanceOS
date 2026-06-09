"""Repository over the sqlite3 DB — the only module that touches persistence."""
from __future__ import annotations

import json
import time

from .db import session

_KIND = {
    "approved": ("Approved", "human_resolved"),
    "rejected": ("Rejected", "human_resolved"),
    "adjusted": ("Adjusted & approved", "overridden"),
    "clarify": ("Requested clarification", "escalated"),
    "escalated": ("Escalated", "escalated"),
}


def list_open_exceptions() -> list[dict]:
    with session() as c:
        rows = c.execute("SELECT payload FROM exceptions WHERE state='open' ORDER BY amount DESC").fetchall()
    return [json.loads(r["payload"]) for r in rows]


def open_count() -> int:
    with session() as c:
        return c.execute("SELECT COUNT(*) AS n FROM exceptions WHERE state='open'").fetchone()["n"]


def get_exception(exception_id: str) -> dict | None:
    with session() as c:
        row = c.execute("SELECT payload, state FROM exceptions WHERE id=?", (exception_id,)).fetchone()
    if not row or row["state"] != "open":
        return None
    return json.loads(row["payload"])


def _add_audit(c, entry: dict) -> None:
    c.execute(
        "INSERT INTO audit (time, agent, action, conf, outcome, src, by_whom) VALUES (?,?,?,?,?,?,?)",
        (entry["time"], entry["agent"], entry["action"], entry["conf"], entry["outcome"], entry["src"], entry.get("by")),
    )


def resolve_exception(exception_id: str, kind: str, note: str | None = None, by: str | None = None) -> dict:
    if kind not in _KIND:
        raise ValueError(f"unknown resolution kind {kind!r}")
    with session() as c:
        row = c.execute("SELECT payload, state FROM exceptions WHERE id=?", (exception_id,)).fetchone()
        if not row or row["state"] != "open":
            raise KeyError(exception_id)
        ex = json.loads(row["payload"])
        c.execute("UPDATE exceptions SET state='resolved', resolution=? WHERE id=?", (kind, exception_id))
        verb, outcome = _KIND[kind]
        entry = {
            "time": time.strftime("%H:%M:%S"), "agent": ex.get("agent", "AP Matching Agent"),
            "action": f"{verb} {exception_id}" + (f" — {note}" if note else ""),
            "conf": ex.get("confidence", 0), "outcome": outcome,
            "src": ", ".join(s["ref"] for s in ex.get("sources", [])) or ex.get("po", ""),
            "by": by or "D. Okafor",
        }
        _add_audit(c, entry)
        n = c.execute("SELECT COUNT(*) AS n FROM exceptions WHERE state='open'").fetchone()["n"]
    return {"id": exception_id, "kind": kind, "openCount": n, "audit": entry}


def record_audit(entry: dict) -> dict:
    with session() as c:
        _add_audit(c, entry)
    return entry


def audit_log(limit: int = 60) -> list[dict]:
    with session() as c:
        rows = c.execute("SELECT * FROM audit ORDER BY seq DESC LIMIT ?", (limit,)).fetchall()
    return [{"time": r["time"], "agent": r["agent"], "action": r["action"], "conf": r["conf"],
             "outcome": r["outcome"], "src": r["src"], "by": r["by_whom"]} for r in rows]


def get_agent_config(agent_id: str) -> dict | None:
    with session() as c:
        r = c.execute("SELECT threshold, mode FROM agent_config WHERE agent_id=?", (agent_id,)).fetchone()
    return {"threshold": r["threshold"], "mode": r["mode"]} if r else None


def set_agent_config(agent_id: str, threshold: int | None, mode: str | None) -> None:
    cur = get_agent_config(agent_id) or {"threshold": None, "mode": None}
    thr = threshold if threshold is not None else cur["threshold"]
    md = mode if mode is not None else cur["mode"]
    with session() as c:
        c.execute(
            "INSERT INTO agent_config (agent_id, threshold, mode) VALUES (?,?,?) "
            "ON CONFLICT(agent_id) DO UPDATE SET threshold=excluded.threshold, mode=excluded.mode",
            (agent_id, thr, md),
        )


# ---- AR deposits ----
def list_deposits() -> list[dict]:
    with session() as c:
        rows = c.execute("SELECT payload FROM deposits ORDER BY amount DESC").fetchall()
    return [json.loads(r["payload"]) for r in rows]


def get_deposit(deposit_id: str) -> dict | None:
    with session() as c:
        row = c.execute("SELECT payload FROM deposits WHERE id=?", (deposit_id,)).fetchone()
    return json.loads(row["payload"]) if row else None


def unapplied_summary() -> tuple[str, int]:
    with session() as c:
        rows = c.execute("SELECT amount FROM deposits WHERE state='unapplied'").fetchall()
    total = sum(r["amount"] for r in rows)
    return (f"${total:,.0f}", len(rows))


def apply_deposit(deposit_id: str, by: str | None = None) -> dict:
    with session() as c:
        row = c.execute("SELECT payload, state FROM deposits WHERE id=?", (deposit_id,)).fetchone()
        if not row:
            raise KeyError(deposit_id)
        if row["state"] == "applied":
            raise ValueError("already applied")
        dep = json.loads(row["payload"])
        c.execute("UPDATE deposits SET state='applied' WHERE id=?", (deposit_id,))
        n_inv = len(dep.get("suggestions", []))
        entry = {
            "time": time.strftime("%H:%M:%S"), "agent": "Cash Application Agent",
            "action": f"Applied {deposit_id} → {n_inv} invoice(s)",
            "conf": dep.get("confidence", 0), "outcome": "human_resolved",
            "src": ", ".join(s["inv"] for s in dep.get("suggestions", [])) or dep.get("payer", ""),
            "by": by or "D. Okafor",
        }
        _add_audit(c, entry)
        n = c.execute("SELECT COUNT(*) AS n FROM deposits WHERE state='unapplied'").fetchone()["n"]
    return {"id": deposit_id, "unappliedCount": n, "audit": entry}


# ---- AR collections ----
def list_collections() -> list[dict]:
    with session() as c:
        rows = c.execute("SELECT payload FROM collections ORDER BY risk DESC").fetchall()
    return [json.loads(r["payload"]) for r in rows]


def get_collection(cid: str) -> dict | None:
    with session() as c:
        row = c.execute("SELECT payload FROM collections WHERE id=?", (cid,)).fetchone()
    return json.loads(row["payload"]) if row else None


def collections_summary() -> tuple[str, str]:
    with session() as c:
        rows = c.execute("SELECT payload FROM collections WHERE state='pending'").fetchall()
    at_risk = sum(json.loads(r["payload"]).get("balanceValue", 0) for r in rows)
    return (f"${at_risk:,.0f}", "28.4")


def send_collection(cid: str, by: str | None = None) -> dict:
    with session() as c:
        row = c.execute("SELECT payload, state FROM collections WHERE id=?", (cid,)).fetchone()
        if not row:
            raise KeyError(cid)
        if row["state"] == "sent":
            raise ValueError("already sent")
        col = json.loads(row["payload"])
        col["status"] = "Sent"
        c.execute("UPDATE collections SET state='sent', payload=? WHERE id=?", (json.dumps(col), cid))
        entry = {
            "time": time.strftime("%H:%M:%S"), "agent": "Collections Agent",
            "action": f"Sent outreach to {col['account']} — {col['action']}",
            "conf": col.get("risk", 0), "outcome": "human_resolved",
            "src": f"Risk {col.get('risk')}", "by": by or "D. Okafor",
        }
        _add_audit(c, entry)
    return {"id": cid, "status": "Sent", "audit": entry}


def apply_auto_actions(agent_id: str, threshold: int | None = None) -> int:
    """Re-run an agent's pipeline and auto-act on items that clear its threshold.
    Called when an agent is promoted suggest-only → auto. Writes 'auto' audit rows."""
    from . import connectors
    acted = 0
    with session() as c:
        if agent_id == "ap-matching":
            from financeos_agents.ap_matching import generate_exceptions
            for e in generate_exceptions(connectors.erp, suggest_only=False, threshold=threshold or 85):
                if e["status"] != "Auto-approved":
                    continue
                row = c.execute("SELECT state FROM exceptions WHERE id=?", (e["id"],)).fetchone()
                if row and row["state"] == "open":
                    c.execute("UPDATE exceptions SET state='resolved', resolution='approved' WHERE id=?", (e["id"],))
                    _add_audit(c, {"time": time.strftime("%H:%M:%S"), "agent": e["agent"],
                                   "action": f"Auto-approved {e['id']} — {e['reason']}", "conf": e["confidence"],
                                   "outcome": "auto", "src": ", ".join(s["ref"] for s in e.get("sources", [])), "by": None})
                    acted += 1
        elif agent_id == "cash-application":
            from financeos_agents.cash_application import generate_deposits
            for d in generate_deposits(connectors.erp, connectors.bank, suggest_only=False, threshold=threshold or 90):
                if d["status"] != "Auto-applied":
                    continue
                row = c.execute("SELECT state FROM deposits WHERE id=?", (d["id"],)).fetchone()
                if row and row["state"] == "unapplied":
                    c.execute("UPDATE deposits SET state='applied' WHERE id=?", (d["id"],))
                    _add_audit(c, {"time": time.strftime("%H:%M:%S"), "agent": "Cash Application Agent",
                                   "action": f"Auto-applied {d['id']} → {len(d.get('suggestions', []))} invoice(s)", "conf": d["confidence"],
                                   "outcome": "auto", "src": ", ".join(s["inv"] for s in d.get("suggestions", [])), "by": None})
                    acted += 1
    return acted
