"""Connector wiring.

The connector contracts + mock adapters live in the sibling package
`packages/connectors`. We add it to sys.path so the API runs without an editable
install; for production, `pip install -e packages/connectors` instead.

Which adapter is used is a *configuration* choice — swap MockERPConnector for a real
vendor adapter here and nothing else in the API changes.
"""
from __future__ import annotations

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
)

# Singletons for the process lifetime (Phase 0 = in-memory state).
erp: ERPConnector = MockERPConnector()
bank = MockBankConnector()
ingestion = MockIngestionConnector()
