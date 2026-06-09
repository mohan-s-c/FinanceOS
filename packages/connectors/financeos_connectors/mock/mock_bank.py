"""In-memory mock bank/payments adapter (AR). Serves seed deposits; reads only for now."""
from __future__ import annotations

from typing import Optional

from ..base import Capability
from ..bank import BankConnector
from .seed import seed_deposits, seed_raw_deposits


class MockBankConnector(BankConnector):
    name = "mock-bank"

    def __init__(self) -> None:
        self._deposits: list[dict] = seed_deposits()

    def capabilities(self) -> set[Capability]:
        return {Capability.READ_DEPOSITS}

    def list_deposits(self) -> list[dict]:
        return [dict(d) for d in self._deposits]

    def list_raw_deposits(self) -> list[dict]:
        return seed_raw_deposits()

    def get_remittance(self, deposit_id: str) -> Optional[dict]:
        # Phase 2: remittance detail. Not modeled in the seed yet.
        return None
