"""In-memory mock ingestion/OCR adapter. No pending artifacts in Phase 0."""
from __future__ import annotations

from ..base import Capability
from ..ingestion import IngestionConnector


class MockIngestionConnector(IngestionConnector):
    name = "mock-ingestion"

    def capabilities(self) -> set[Capability]:
        return {Capability.INGEST_INVOICES}

    def fetch_pending(self) -> list[dict]:
        return []
