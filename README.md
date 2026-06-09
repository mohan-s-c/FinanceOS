# Finance OS / APAR — V2

An AI/agentic Finance OS that automates an organization's **Accounts Payable & Accounts
Receivable** workflows: agents ingest invoices and payments, run 3-way matching, apply
cash, drive collections, and flag anomalies — with an analyst supervising by exception.

This is the **V2 monorepo**. V1 was a front-end prototype; V2 adds a backend, an agent
layer, and connector contracts. See `V2_DESIGN_SPEC.md` for the architecture/roadmap,
`V1_HANDOFF.md` for V1 context, and `CLAUDE.md` for working rules.

## Layout

```
apps/web            React 19 + Vite + Zustand UI (the V1 app, relocated)
services/api        FastAPI BFF (read models + commands + audit)
services/agents     Agent pipeline (intake → match → decide → act); Phase 0 stubs
packages/shared     TS domain schema shared by web + api
packages/connectors Connector contracts (ERP/bank/ingestion) + mock adapters
infra               env/secrets templates
```

## Run (Phase 0)

Front-end (npm workspaces):

```bash
npm install
npm run dev          # serves apps/web on http://localhost:5174
```

Backend:

```bash
cd services/api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000   # http://localhost:8000/docs
```

The web app reads/writes the Exception Queue through the API (`VITE_API_BASE_URL`,
default `http://127.0.0.1:8000`). If the API is unreachable it falls back to bundled
mock data, so the front-end still runs standalone. Copy `infra/.env.example` as needed.

## Status

Phase 0 (foundation) is in place: monorepo restructure, shared schema, connector
contracts + mock adapters, FastAPI skeleton, and the Exception Queue wired end-to-end
on mock data. Next: Phase 1 (persistence + deterministic tolerance-aware 3-way match +
AP Matching agent in suggest-only mode). See `V2_DESIGN_SPEC.md` §9.
