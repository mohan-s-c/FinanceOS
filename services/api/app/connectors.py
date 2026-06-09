"""Connector wiring.

The connector contracts + mock adapters live in the sibling package
`packages/connectors`. We add it to sys.path so the API runs without an editable
install; for production, `pip install -e packages/connectors` instead.

Which adapter is used is a *configuration* choice — swap MockERPConnector for a real
vendor adapter here and nothing else in the API changes.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CONNECTORS_PATH = _REPO_ROOT / "packages" / "connectors"
if str(_CONNECTORS_PATH) not in sys.path:
    sys.path.insert(0, str(_CONNECTORS_PATH))
_AGENTS_PATH = _REPO_ROOT / "services" / "agents"
if str(_AGENTS_PATH) not in sys.path:
    sys.path.insert(0, str(_AGENTS_PATH))

from financeos_connectors import (  # noqa: E402
    ERPConnector,
    MockERPConnector,
    MockBankConnector,
    MockIngestionConnector,
    FileERPConnector,
    FileBankConnector,
)

# Adapter selection (the swappable seam). FINANCEOS_ERP=file boots from CSVs in
# FINANCEOS_DATA_DIR (default infra/data); otherwise the in-memory mock is used.
_VENDOR = os.getenv("FINANCEOS_ERP", "mock").lower()
_DATA_DIR = os.getenv("FINANCEOS_DATA_DIR", str(_REPO_ROOT / "infra" / "data"))

if _VENDOR == "file":
    erp: ERPConnector = FileERPConnector(_DATA_DIR)
    bank = FileBankConnector(_DATA_DIR)
else:
    erp = MockERPConnector()
    bank = MockBankConnector()
ingestion = MockIngestionConnector()
