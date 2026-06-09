"""Connector base types.

Connectors are *contracts first*: the agent layer and the API depend only on these
abstract interfaces, never on a concrete vendor. Records are passed as plain dicts
shaped like the shared domain schema (packages/shared) to keep this package free of
any web/api framework dependency.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum


class Capability(str, Enum):
    """What a given adapter actually supports, for capability discovery."""
    READ_EXCEPTIONS = "read_exceptions"
    READ_PURCHASE_ORDER = "read_purchase_order"
    READ_GOODS_RECEIPT = "read_goods_receipt"
    READ_OPEN_INVOICES = "read_open_invoices"
    WRITE_RESOLUTION = "write_resolution"
    READ_DEPOSITS = "read_deposits"
    READ_REMITTANCE = "read_remittance"
    INGEST_INVOICES = "ingest_invoices"


class Connector(ABC):
    """Common base. `name` identifies the concrete vendor/adapter for audit/logging."""

    name: str = "connector"

    @abstractmethod
    def capabilities(self) -> set[Capability]:
        """Return the set of capabilities this adapter supports."""
        raise NotImplementedError

    def supports(self, cap: Capability) -> bool:
        return cap in self.capabilities()
