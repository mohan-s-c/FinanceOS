"""Exception Queue read models + the resolve command (Phase 0)."""
import time

from fastapi import APIRouter, Depends, HTTPException

from .. import auth, repo, store as _store
from ..config import settings

from .. import store
from ..models import AuditEntry, Exception, ExceptionExplanation, ExceptionList, ResolveRequest, ResolveResponse

router = APIRouter(prefix="/api", tags=["exceptions"])


@router.get("/exceptions", response_model=ExceptionList)
def list_exceptions() -> ExceptionList:
    return store.list_exceptions()


@router.get("/exceptions/{exception_id}", response_model=Exception)
def get_exception(exception_id: str) -> Exception:
    ex = store.get_exception(exception_id)
    if ex is None:
        raise HTTPException(status_code=404, detail=f"exception {exception_id} not found")
    return ex


@router.post("/exceptions/{exception_id}/resolve", response_model=ResolveResponse)
def resolve_exception(exception_id: str, req: ResolveRequest, user: dict = Depends(auth.current_user)) -> ResolveResponse:
    """SIDE-EFFECTFUL: posts a disposition to the ERP and writes an audit entry.
    Segregation of duties: resolving a high-value item (>= SOD limit) needs Controller."""
    ex = _store.get_exception(exception_id)
    if ex is not None and ex.amount >= settings.sod_limit and user["role"] != "controller":
        raise HTTPException(status_code=403, detail=f"Resolving items ≥ ${settings.sod_limit:,.0f} requires the Controller role.")
    try:
        return store.resolve_exception(exception_id, req)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"exception {exception_id} not found")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/exceptions/{exception_id}/explain", response_model=ExceptionExplanation)
def explain_exception(exception_id: str, user: dict = Depends(auth.current_user)) -> ExceptionExplanation:
    """LLM-assisted (or offline-narrator) explanation + suggested disposition.
    Each explanation is written to the audit trail with the model that produced it."""
    e = store.explain_exception(exception_id)
    if e is None:
        raise HTTPException(status_code=404, detail=f"exception {exception_id} not found")
    ex = store.get_exception(exception_id)
    repo.record_audit({
        "time": time.strftime("%H:%M:%S"), "agent": "Reasoning Agent",
        "action": f"AI explanation for {exception_id} — suggested: {e.suggestedAction}",
        "conf": ex.confidence if ex else 0, "outcome": "explain", "src": e.model,
        "by": user["name"],
    })
    return e


@router.get("/audit", response_model=list[AuditEntry])
def audit() -> list[AuditEntry]:
    return store.audit_log()
