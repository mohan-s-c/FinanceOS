"""Bank / payments connector contract (AR cash application + outgoing payment status).

Phase 0 defines the surface; the mock adapter serves seed deposits. Wiring the
Cash Application screen to these reads is Phase 2.
"""
from __future__ import annotations

from abc import abstractmethod
from typing import Optional

from .base import Connector


class BankConnector(Connector):
    name = "bank"

    @abstractmethod
    def list_deposits(self) -> list[dict]:
        """Incoming deposits awaiting application (shared `Deposit` shape)."""
        raise NotImplementedError

    def get_remittance(self, deposit_id: str) -> Optional[dict]:  # Phase 2
        raise NotImplementedError
