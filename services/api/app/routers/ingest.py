"""CSV ingestion — upload AP/AR files (raw text/csv body) and rebuild the queues.

Raw-body upload (no multipart dependency). Parsing is shared with the File ERP
adapter via financeos_connectors.csv_formats, so uploaded files and file-boot data
use the identical format (download a template from /api/ingest/template/{kind}).
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse

from .. import connectors, repo
from financeos_connectors.csv_formats import (
    DEFAULT_POLICIES, TEMPLATES, parse_ap_invoices, parse_ar_deposits, parse_ar_open_invoices, parse_overdue_accounts,
)
from financeos_agents.ap_matching import generate_exceptions_from
from financeos_agents.cash_application import generate_deposits_from
from financeos_agents.collections import generate_collections_from

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


async def _body(request: Request) -> str:
    text = (await request.body()).decode("utf-8-sig")
    if not text.strip():
        raise HTTPException(status_code=422, detail="empty CSV body")
    return text


@router.get("/template/{kind}")
def template(kind: str) -> PlainTextResponse:
    if kind not in TEMPLATES:
        raise HTTPException(status_code=404, detail=f"no template '{kind}'")
    return PlainTextResponse(TEMPLATES[kind], media_type="text/csv")


@router.post("/ap")
async def ingest_ap(request: Request) -> dict:
    """SIDE-EFFECTFUL: replace the AP exception queue from an uploaded invoices CSV."""
    docs, paid = parse_ap_invoices(await _body(request))
    recs = generate_exceptions_from(docs, DEFAULT_POLICIES, paid, suggest_only=True)
    repo.replace_exceptions(recs)
    return {"kind": "ap", "ingested": len(docs), "openExceptions": repo.open_count()}


@router.post("/ar-invoices")
async def ingest_ar_invoices(request: Request) -> dict:
    """Store uploaded open AR invoices (used to match deposits against)."""
    invs = parse_ar_open_invoices(await _body(request))
    repo.set_dataset("ar_open_invoices", invs)
    return {"kind": "ar-invoices", "ingested": len(invs)}


@router.post("/ar-deposits")
async def ingest_ar_deposits(request: Request) -> dict:
    """SIDE-EFFECTFUL: replace the cash-application queue from an uploaded deposits CSV."""
    deposits = parse_ar_deposits(await _body(request))
    open_ar = repo.get_dataset("ar_open_invoices") or connectors.erp.list_open_ar_invoices()
    recs = generate_deposits_from(deposits, open_ar, suggest_only=True)
    repo.replace_deposits(recs)
    _, count = repo.unapplied_summary()
    return {"kind": "ar-deposits", "ingested": len(deposits), "unappliedCount": count}


@router.post("/collections")
async def ingest_collections(request: Request) -> dict:
    """SIDE-EFFECTFUL: replace the collections queue from an uploaded overdue-accounts CSV."""
    accounts = parse_overdue_accounts(await _body(request))
    recs = generate_collections_from(accounts, suggest_only=True)
    repo.replace_collections(recs)
    return {"kind": "collections", "ingested": len(accounts)}
