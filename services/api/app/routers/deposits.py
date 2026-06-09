"""AR Cash Application read model + apply command (Phase 2, suggest-only)."""
from fastapi import APIRouter, HTTPException

from .. import store
from ..models import ApplyRequest, ApplyResponse, DepositDetail, DepositList

router = APIRouter(prefix="/api", tags=["deposits"])


@router.get("/deposits", response_model=DepositList)
def list_deposits() -> DepositList:
    return store.list_deposits()


@router.get("/deposits/{deposit_id}", response_model=DepositDetail)
def get_deposit(deposit_id: str) -> DepositDetail:
    d = store.get_deposit(deposit_id)
    if d is None:
        raise HTTPException(status_code=404, detail=f"deposit {deposit_id} not found")
    return d


@router.post("/deposits/{deposit_id}/apply", response_model=ApplyResponse)
def apply_deposit(deposit_id: str, req: ApplyRequest | None = None) -> ApplyResponse:
    """SIDE-EFFECTFUL: applies the deposit to its matched invoices and writes audit."""
    try:
        return store.apply_deposit(deposit_id, (req.by if req else None))
    except KeyError:
        raise HTTPException(status_code=404, detail=f"deposit {deposit_id} not found")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
