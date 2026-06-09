# services/api

FastAPI backend-for-frontend. Phase 0 exposes the **Exception Queue** read models and
the **resolve** command, backed by the mock ERP connector (in-memory, mock seam intact)
with audit write-through.

## Run

```bash
cd services/api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs for the OpenAPI UI.

## Endpoints (Phase 0)

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness + kill-switch (suggest-only) state |
| GET | `/api/exceptions` | open AP exception queue + open count |
| GET | `/api/exceptions/{id}` | one exception (full 3-way-match detail) |
| POST | `/api/exceptions/{id}/resolve` | approve/reject/adjust/clarify/escalate; writes audit |
| GET | `/api/audit` | audit entries written this session |

State is in-memory and resets on restart — persistence (Postgres) is Phase 1.
