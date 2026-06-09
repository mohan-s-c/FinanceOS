"""financeos_connectors — connector contracts + mock adapters."""
from .base import Capability, Connector
from .erp import ERPConnector
from .bank import BankConnector
from .ingestion import IngestionConnector
from .mock import MockERPConnector, MockBankConnector, MockIngestionConnector

__all__ = [
    "Capability", "Connector",
    "ERPConnector", "BankConnector", "IngestionConnector",
    "MockERPConnector", "MockBankConnector", "MockIngestionConnector",
]
