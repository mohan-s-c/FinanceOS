"""Read-model + command layer. Phase 1: persistence-backed via the sqlite repo,
seeded by the AP Matching agent. Resolving an exception transitions its state and
appends to the immutable audit trail.
"""
from __future__ import annotations

from . import repo
from .models import (AuditEntry, Exception, ExceptionList, ResolveRequest, ResolveResponse,
                     Deposit, DepositDetail, DepositList, ApplyResponse)


def list_exceptions() -> ExceptionList:
    items = [Exception(**e) for e in repo.list_open_exceptions()]
    return ExceptionList(items=items, openCount=repo.open_count())


def get_exception(exception_id: str) -> Exception | None:
    raw = repo.get_exception(exception_id)
    return Exception(**raw) if raw else None


def resolve_exception(exception_id: str, req: ResolveRequest) -> ResolveResponse:
    r = repo.resolve_exception(exception_id, req.kind, note=req.note, by=req.by)
    return ResolveResponse(id=r["id"], kind=r["kind"], openCount=r["openCount"], audit=AuditEntry(**r["audit"]))


def audit_log() -> list[AuditEntry]:
    return [AuditEntry(**a) for a in repo.audit_log()]


def list_deposits() -> DepositList:
    items = [Deposit(**d) for d in repo.list_deposits()]
    total, count = repo.unapplied_summary()
    return DepositList(items=items, unappliedTotal=total, unappliedCount=count)


def get_deposit(deposit_id: str) -> DepositDetail | None:
    raw = repo.get_deposit(deposit_id)
    return DepositDetail(**raw) if raw else None


def apply_deposit(deposit_id: str, by: str | None = None) -> ApplyResponse:
    r = repo.apply_deposit(deposit_id, by)
    return ApplyResponse(id=r["id"], unappliedCount=r["unappliedCount"], audit=AuditEntry(**r["audit"]))


def list_collections() -> 'CollectionList':
    from .models import Collection, CollectionList
    items = [Collection(**c) for c in repo.list_collections()]
    at_risk, dso = repo.collections_summary()
    return CollectionList(items=items, atRisk=at_risk, dso=dso)


def get_collection(cid: str):
    from .models import CollectionDetail
    raw = repo.get_collection(cid)
    return CollectionDetail(**raw) if raw else None


def send_collection(cid: str, by: str | None = None):
    from .models import SendResponse, AuditEntry
    r = repo.send_collection(cid, by)
    return SendResponse(id=r["id"], status=r["status"], audit=AuditEntry(**r["audit"]))


def explain_exception(exception_id: str):
    from .models import ExceptionExplanation
    from financeos_agents.reasoning import explain_exception as _explain
    raw = repo.get_exception(exception_id)
    if raw is None:
        return None
    return ExceptionExplanation(**_explain(raw))
