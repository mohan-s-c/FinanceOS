"""Ingestion / OCR connector contract.

Captures invoices from email + document upload and parses them to structured fields.
Phase 0 defines the surface; real OCR/document-AI is Phase 1+.
"""
from __future__ import annotations

from abc import abstractmethod

from .base import Connector


class IngestionConnector(Connector):
    name = "ingestion"

    @abstractmethod
    def fetch_pending(self) -> list[dict]:
        """Return artifacts captured but not yet normalized into the schema."""
        raise NotImplementedError

    def parse(self, artifact: dict) -> dict:  # Phase 1
        """Normalize a raw artifact into a structured, unvalidated invoice record."""
        raise NotImplementedError
