from fastapi import APIRouter

from .. import connectors
from ..config import settings
from ..models import Health

router = APIRouter(tags=["health"])


@router.get("/health", response_model=Health)
def health() -> Health:
    return Health(status="ok", suggestOnly=settings.suggest_only, erp=connectors.erp.name)
