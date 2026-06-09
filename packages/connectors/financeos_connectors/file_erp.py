"""File-backed ERP/Bank adapters — a *real* (non-hardcoded) data source.

Reads AP invoices, open AR invoices, and bank deposits from CSV files in a data
directory (the same format as the upload templates). Anything not provided as a file
falls back to the mock seed, so the app still runs. Selected via FINANCEOS_ERP=file.
This is the swappable seam from SECURITY.md made concrete; a vendor SDK adapter would
sit here too.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from .base import Capability
from .erp import ERPConnector
from .bank import BankConnector
from . import csv_formats as F
from .mock import seed as _seed


def _read(data_dir: str, name: str) -> Optional[str]:
    p = Path(data_dir) / name
    return p.read_text(encoding="utf-8") if p.is_file() else None


class FileERPConnector(ERPConnector):
    name = "file-erp"

    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir

    def capabilities(self) -> set[Capability]:
        return {Capability.READ_EXCEPTIONS, Capability.READ_OPEN_INVOICES}

    # ---- file-backed AP/AR data (used by the agent seeders) ----
    def list_ap_documents(self) -> list[dict]:
        text = _read(self.data_dir, "ap_invoices.csv")
        if text is None:
            return _seed.seed_ap_documents()
        docs, paid = F.parse_ap_invoices(text)
        self._paid = paid
        return docs

    def policies(self) -> dict:
        return dict(F.DEFAULT_POLICIES)

    def paid_invoices(self) -> list[dict]:
        text = _read(self.data_dir, "ap_invoices.csv")
        if text is None:
            return _seed.paid_invoices()
        _docs, paid = F.parse_ap_invoices(text)
        return paid

    def list_open_ar_invoices(self) -> list[dict]:
        text = _read(self.data_dir, "ar_open_invoices.csv")
        return F.parse_ar_open_invoices(text) if text is not None else _seed.seed_ar_invoices()

    def list_overdue_accounts(self) -> list[dict]:
        text = _read(self.data_dir, "overdue_accounts.csv")
        return F.parse_overdue_accounts(text) if text is not None else _seed.seed_overdue_accounts()

    def list_anomaly_signals(self) -> list[dict]:
        return _seed.seed_anomaly_signals()

    def leakage_series(self):
        return _seed.leakage_series()

    # ---- abstract ERP surface (exceptions are owned by the API's DB, not the file source) ----
    def list_open_exceptions(self) -> list[dict]:
        return []

    def get_exception(self, exception_id: str) -> Optional[dict]:
        return None

    def post_resolution(self, exception_id: str, kind: str, note=None, by=None) -> dict:
        raise NotImplementedError("FileERPConnector is read-only; dispositions persist in the API DB.")


class FileBankConnector(BankConnector):
    name = "file-bank"

    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir

    def capabilities(self) -> set[Capability]:
        return {Capability.READ_DEPOSITS}

    def list_raw_deposits(self) -> list[dict]:
        text = _read(self.data_dir, "ar_deposits.csv")
        return F.parse_ar_deposits(text) if text is not None else _seed.seed_raw_deposits()

    def list_deposits(self) -> list[dict]:
        return []

    def get_remittance(self, deposit_id: str):
        return None
