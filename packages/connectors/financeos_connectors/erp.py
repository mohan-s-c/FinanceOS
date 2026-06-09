"""ERP / accounting connector contract.

System of record for AP/AR: purchase orders, goods receipts, open invoices, and the
exceptions that fall out of matching. Read methods are safe; write methods are
SIDE-EFFECTFUL and must be surfaced/confirmed by the caller before use.
"""
from __future__ import annotations

from abc import abstractmethod
from typing import Optional

from .base import Connector


class ERPConnector(Connector):
    name = "erp"

    # ---- reads (safe) ----
    @abstractmethod
    def list_open_exceptions(self) -> list[dict]:
        """All AP exceptions currently awaiting disposition (shared `Exception` shape)."""
        raise NotImplementedError

    @abstractmethod
    def get_exception(self, exception_id: str) -> Optional[dict]:
        """A single exception by id, or None if not found / already resolved."""
        raise NotImplementedError

    def get_purchase_order(self, po_id: str) -> Optional[dict]:  # Phase 1
        """Fetch a PO for tolerance-aware 3-way matching. Not implemented in mock Phase 0."""
        raise NotImplementedError

    def get_goods_receipt(self, gr_id: str) -> Optional[dict]:  # Phase 1
        raise NotImplementedError

    def list_open_invoices(self) -> list[dict]:  # Phase 2 (AR)
        raise NotImplementedError

    # ---- writes (SIDE-EFFECTFUL) ----
    @abstractmethod
    def post_resolution(
        self,
        exception_id: str,
        kind: str,
        note: Optional[str] = None,
        by: Optional[str] = None,
    ) -> dict:
        """SIDE-EFFECTFUL. Record a disposition (approve/reject/adjust/clarify/escalate)
        against the ERP and return an audit record (shared `AuditEntry` shape)."""
        raise NotImplementedError
