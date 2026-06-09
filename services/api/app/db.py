"""Persistence — stdlib sqlite3 (no extra deps).

Tables: exceptions (with a lifecycle state), audit (append-only), agent_config
(editable, persisted threshold/mode). The DB file path is configurable via
FINANCEOS_DB; default lives beside the service. The repo layer (repo.py) is the
only caller, so swapping to Postgres later is a contained change.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

_DEFAULT = Path(__file__).resolve().parent.parent / "financeos.db"
DB_PATH = os.getenv("FINANCEOS_DB", str(_DEFAULT))


def connect() -> sqlite3.Connection:
    # Plain rollback journal (not WAL): more robust on cloud-synced / networked
    # folders where WAL shared-memory locks can hang. busy timeout avoids deadlocks.
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def session():
    """Connection that always commits on success and closes (releases locks)."""
    conn = connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with session() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS exceptions (
              id TEXT PRIMARY KEY,
              state TEXT NOT NULL DEFAULT 'open',     -- open | resolved
              resolution TEXT,                         -- approved | rejected | adjusted | clarify | escalated
              amount REAL,
              payload TEXT NOT NULL                    -- full Exception JSON
            );
            CREATE TABLE IF NOT EXISTS audit (
              seq INTEGER PRIMARY KEY AUTOINCREMENT,
              time TEXT, agent TEXT, action TEXT, conf INTEGER,
              outcome TEXT, src TEXT, by_whom TEXT
            );
            CREATE TABLE IF NOT EXISTS agent_config (
              agent_id TEXT PRIMARY KEY,
              threshold INTEGER,
              mode TEXT
            );
            CREATE TABLE IF NOT EXISTS deposits (
              id TEXT PRIMARY KEY,
              state TEXT NOT NULL DEFAULT 'unapplied',   -- unapplied | applied
              amount REAL,
              payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS collections (
              id TEXT PRIMARY KEY,
              state TEXT NOT NULL DEFAULT 'pending',      -- pending | sent
              risk INTEGER,
              payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS datasets (
              key TEXT PRIMARY KEY,
              payload TEXT NOT NULL
            );
            """
        )


def seed_if_empty() -> None:
    """Populate exceptions + audit from the AP Matching agent on first run."""
    from . import connectors  # sets sys.path for financeos_agents
    from financeos_agents.ap_matching import generate_exceptions  # noqa: E402

    with session() as c:
        n = c.execute("SELECT COUNT(*) AS n FROM exceptions").fetchone()["n"]
        if n:
            return
        records = generate_exceptions(connectors.erp, suggest_only=True)
        for e in records:
            state = "resolved" if e["status"] == "Auto-approved" else "open"
            c.execute(
                "INSERT OR REPLACE INTO exceptions (id, state, resolution, amount, payload) VALUES (?,?,?,?,?)",
                (e["id"], state, "approved" if state == "resolved" else None, e["amount"], json.dumps(e)),
            )
            # derive an audit row from the agent's decision
            auto = e["status"] == "Auto-approved"
            c.execute(
                "INSERT INTO audit (time, agent, action, conf, outcome, src, by_whom) VALUES (?,?,?,?,?,?,?)",
                (time.strftime("%H:%M:%S"), e["agent"],
                 ("Auto-approved " if auto else "Escalated ") + e["id"] + f" — {e['reason']}",
                 e["confidence"], "auto" if auto else "escalated",
                 ", ".join(s["ref"] for s in e.get("sources", [])), None),
            )
        print(f"[db] seeded {len(records)} exceptions from AP Matching agent")

    from financeos_agents.cash_application import generate_deposits  # noqa: E402
    with connect() as c:
        if not c.execute("SELECT COUNT(*) AS n FROM deposits").fetchone()["n"]:
            deps = generate_deposits(connectors.erp, connectors.bank, suggest_only=True)
            for d in deps:
                state = "applied" if d["status"] == "Auto-applied" else "unapplied"
                c.execute("INSERT OR REPLACE INTO deposits (id, state, amount, payload) VALUES (?,?,?,?)",
                          (d["id"], state, d["amountValue"], __import__("json").dumps(d)))
            c.commit()
            print(f"[db] seeded {len(deps)} deposits from Cash Application agent")

    from financeos_agents.collections import generate_collections  # noqa: E402
    with connect() as c:
        if not c.execute("SELECT COUNT(*) AS n FROM collections").fetchone()["n"]:
            cols = generate_collections(connectors.erp, suggest_only=True)
            for col in cols:
                c.execute("INSERT OR REPLACE INTO collections (id, state, risk, payload) VALUES (?,?,?,?)",
                          (col["id"], "pending", col["risk"], __import__("json").dumps(col)))
            c.commit()
            print(f"[db] seeded {len(cols)} collections from Collections agent")
