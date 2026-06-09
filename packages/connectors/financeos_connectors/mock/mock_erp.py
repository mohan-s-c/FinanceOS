"""In-memory mock ERP adapter.

Stands in for the system of record during development/demo. Holds a mutable copy of
the seed exceptions and an append-only audit list, so resolutions persist for the life
of the process (real persistence arrives in Phase 1).
"""
from __future__ import annotations

import time
from typing import Optional

from ..base import Capability
from ..erp import ERPConnector
from .seed import seed_exceptions, seed_ap_documents, ap_policies, paid_invoices, seed_ar_invoices, seed_overdue_accounts, seed_anomaly_signals, leakage_series

# Map a resolution kind to (audit action verb, audit outcome).
_KIND_TO_AUDIT = {
    "approved": ("Approved", "human_resolved"),
    "rejected": ("Rejected", "human_resolved"),
    "adjusted": ("Adjusted & approved", "overridden"),
    "clarify": ("Requested clarification", "escalated"),
    "escalated": ("Escalated", "escalated"),
}


class MockERPConnector(ERPConnector):
    name = "mock-erp"

    def __init__(self) -> None:
        self._exceptions: list[dict] = seed_exceptions()
        self._audit: list[dict] = []

    def capabilities(self) -> set[Capability]:
        return {Capability.READ_EXCEPTIONS, Capability.WRITE_RESOLUTION}

    # ---- reads ----
    def list_open_exceptions(self) -> list[dict]:
        return [dict(e) for e in self._exceptions]

    def get_exception(self, exception_id: str) -> Optional[dict]:
        for e in self._exceptions:
            if e["id"] == exception_id:
                return dict(e)
        return None

    # ---- writes (SIDE-EFFECTFUL) ----
    def post_resolution(
        self,
        exception_id: str,
        kind: str,
        note: Optional[str] = None,
        by: Optional[str] = None,
    ) -> dict:
        ex = self.get_exception(exception_id)
        if ex is None:
            raise KeyError(f"exception {exception_id!r} not found")
        if kind not in _KIND_TO_AUDIT:
            raise ValueError(f"unknown resolution kind {kind!r}")

        # Remove from the open queue (the disposition has been posted to the ERP).
        self._exceptions = [e for e in self._exceptions if e["id"] != exception_id]

        action_verb, outcome = _KIND_TO_AUDIT[kind]
        src = ", ".join(s["ref"] for s in ex.get("sources", [])) or ex.get("po", "")
        entry = {
            "time": time.strftime("%H:%M:%S"),
            "agent": ex.get("agent", "Exception Agent"),
            "action": f"{action_verb} {exception_id}",
            "conf": ex.get("confidence", 0),
            "outcome": outcome,
            "src": src,
            "by": by or "D. Okafor",
        }
        if note:
            entry["action"] += f" — {note}"
        self._audit.append(entry)
        return entry

    # ---- Phase 1: raw AP documents for the matching agent ----
    def list_ap_documents(self) -> list[dict]:
        return seed_ap_documents()

    def list_open_ar_invoices(self) -> list[dict]:
        return seed_ar_invoices()

    def list_overdue_accounts(self) -> list[dict]:
        return seed_overdue_accounts()

    def list_anomaly_signals(self) -> list[dict]:
        return seed_anomaly_signals()

    def leakage_series(self):
        return leakage_series()

    def policies(self) -> dict:
        return ap_policies()

    def paid_invoices(self) -> list[dict]:
        return paid_invoices()

    # ---- convenience for the API store ----
    def record_audit(self, entry: dict) -> dict:
        """Append an externally-produced audit entry (e.g. a threshold/mode change)."""
        self._audit.append(entry)
        return entry

    def audit_log(self) -> list[dict]:
        return [dict(a) for a in self._audit]

    def open_count(self) -> int:
        return len(self._exceptions)
