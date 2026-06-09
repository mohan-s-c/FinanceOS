"""Finance OS APAR API — application entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import settings
from .routers import agents, analytics, anomalies, auth, collections, deposits, exceptions, health, ingest

app = FastAPI(
    title="Finance OS / APAR API",
    version="0.2.0",
    description="V2 Phase 0 — Exception Queue read/resolve over the mock ERP connector.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(exceptions.router)
app.include_router(agents.router)
app.include_router(deposits.router)
app.include_router(collections.router)
app.include_router(anomalies.router)
app.include_router(analytics.router)
app.include_router(ingest.router)


@app.on_event("startup")
def _startup() -> None:
    import logging
    from .db import init_db, seed_if_empty
    try:
        init_db()
        seed_if_empty()
    except Exception:  # never let DB seeding block the server from serving
        logging.getLogger("uvicorn.error").exception("startup DB seed failed; serving without seed")


@app.get("/", include_in_schema=False)
def root() -> dict:
    return {"service": "financeos-apar-api", "docs": "/docs", "health": "/health"}


# Serve the built front-end (apps/web/dist) when present, so the API can host the
# production SPA. Mounted last so it never shadows /api, /health, or /docs.
_DIST = Path(__file__).resolve().parents[3] / "apps" / "web" / "dist"
if _DIST.is_dir():
    app.mount("/app", StaticFiles(directory=str(_DIST), html=True), name="web")
