"""Collections read model + send-outreach command (Phase 3, suggest-only drafts)."""
from fastapi import APIRouter, HTTPException

from .. import store
from ..models import ApplyRequest, CollectionDetail, CollectionList, SendResponse

router = APIRouter(prefix="/api", tags=["collections"])


@router.get("/collections", response_model=CollectionList)
def list_collections() -> CollectionList:
    return store.list_collections()


@router.get("/collections/{cid}", response_model=CollectionDetail)
def get_collection(cid: str) -> CollectionDetail:
    c = store.get_collection(cid)
    if c is None:
        raise HTTPException(status_code=404, detail=f"collection {cid} not found")
    return c


@router.post("/collections/{cid}/send", response_model=SendResponse)
def send_collection(cid: str, req: ApplyRequest | None = None) -> SendResponse:
    """SIDE-EFFECTFUL: sends the drafted outreach and writes audit."""
    try:
        return store.send_collection(cid, (req.by if req else None))
    except KeyError:
        raise HTTPException(status_code=404, detail=f"collection {cid} not found")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
