"""Anomaly & Leakage detection read model (flag-only)."""
from fastapi import APIRouter

from .. import connectors
from ..models import AnomalyList

router = APIRouter(prefix="/api", tags=["anomalies"])


@router.get("/anomalies", response_model=AnomalyList)
def list_anomalies() -> AnomalyList:
    from financeos_agents.anomaly import detect
    return AnomalyList(**detect(connectors.erp))
