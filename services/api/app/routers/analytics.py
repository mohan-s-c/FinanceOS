"""Analytics read model — seeded trends + live-session metrics from the audit trail."""
from fastapi import APIRouter

from ..analytics_data import get_analytics
from ..models import AnalyticsResp

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/analytics", response_model=AnalyticsResp)
def analytics() -> AnalyticsResp:
    return AnalyticsResp(**get_analytics())
