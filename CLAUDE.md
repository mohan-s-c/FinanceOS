# CLAUDE.md — Finance OS / APAR (V2)

> This file gives Claude the standing context and working rules for the V2 project. It is the persistent "how to work here" doc — read it first in any session. For the full backstory of where V1 left off, read `V1_HANDOFF.md`. For the V2 architecture and roadmap, read `V2_DESIGN_SPEC.md`.

## What this project is

An **AI/agentic Finance OS** that automates an organization's **Accounts Payable & Accounts Receivable (APAR)** workflows. Software agents ingest invoices and payments, perform 3-way matching, auto-approve within confidence thresholds, apply incoming cash, drive collections, and flag anomalies — with a human analyst supervising via a queue rather than doing manual work.

**V1** was a front-end-only prototype (React + mock data) that proved the UX. **V2 is an extend**: keep and evolve the V1 UI, and add the real substance V1 lacked — an **agent layer**, a **backend/API**, **persistence**, and **external integrations** (ERP, bank/payments, invoice ingestion).

Primary persona: **Dana Okafor, AP/AR Analyst** — supervises agents, resolves exceptions, tunes thresholds.

## Stack & structure

V2 moves from a single SPA to a multi-part system. Target top-level layout (see the design spec for rationale):

```
/                     repo root (workspace / monorepo)
  apps/
    web/              ← the V1 React app, moved here (Vite + React 19 + TS + Zustand)
  services/
    api/              ← backend API / BFF (Python · FastAPI)
    agents/           ← agent layer: orchestration, tools, thresholds
  packages/
    shared/           ← shared domain types & schemas (the evolved mock.ts model)
    connectors/       ← ERP / bank / OCR connector interfaces + adapters
  infra/              ← deployment, env, IaC
  V1_HANDOFF.md
  V2_DESIGN_SPEC.md
  CLAUDE.md
```

- **Front-end:** React 19 + TypeScript + Vite + Zustand (unchanged from V1; lives under `apps/web`).
- **Backend / agents:** Python + FastAPI. Agents reason with an LLM and call **typed tools** (connectors) under **confidence thresholds** with human-in-the-loop. Deterministic rules handle the happy path (e.g. clean 3-way match); LLM agents handle exceptions and explanations.
- **Domain schema** is the source of truth and lives in `packages/shared`, evolved from V1's `src/data/mock.ts` types (Exception, Deposit, Collection, Anomaly, AuditEntry, Threshold, etc.).

> Until the restructure happens, the repo is still the flat V1 Vite app at the root. Don't assume the layout above exists yet — check before referencing paths.

## How to work in this project

- **Read before assuming.** V1's `mock.ts` is the draft domain model; reuse it rather than inventing new shapes. The 3-way-match Exception is the most considered entity.
- **Preserve the V1 UX.** The seven-screen IA (Command Center, Exception Queue, Cash Application, Collections, Anomalies & Leakage, Agent & Audit Trail, Analytics) is coherent. Extend it; don't rebuild it without reason.
- **Human-in-the-loop is non-negotiable.** Every auto-action is gated by a per-agent confidence threshold and written to the audit trail. When in doubt, route to a human, don't act.
- **Connectors are interfaces first.** Design against abstract connector contracts (ERP, bank, OCR); concrete vendor adapters plug in behind them. Never hard-wire a vendor into agent logic.
- **Explainability.** Every agent decision must carry a reason and its source documents — this is a finance system; auditability beats cleverness.
- **Incremental & verifiable.** Prefer small, testable steps. New agent behavior ships behind a threshold/flag so it can run in suggest-only mode before auto-acting.

## Guardrails (finance domain)

- Treat anything involving money movement, approvals, or external sends as **side-effectful** — surface it and confirm before executing.
- Secrets (ERP/bank/API credentials) never go in code or the repo; use env/secret storage referenced in `infra/`.
- Mock vs. real: keep a clear seam between mock data and live connectors so the app stays runnable offline during development.

## Build / run (current V1 state)

- `npm install` then `npm run dev` (Vite dev server) / `npm run build` (`tsc -b && vite build`).
- `npm run lint` for ESLint.
- These commands target the front-end. Backend/agents commands will be added when `services/` is scaffolded.

## V2 bootstrap — what carried over & first steps

This V2 project is an extend of V1. The repo started as the flat V1 Vite app and is being migrated to the monorepo layout above, one phase at a time (see `V2_DESIGN_SPEC.md` §9).

What carried over from V1 (copied from the V1 repo, minus regenerables like `node_modules/` and `dist/`):

- `src/`, `public/`, `index.html`, and the build config (`vite.config.ts`, `tsconfig*.json`, `eslint.config.js`, `package.json`) — the V1 React app.
- `src/data/mock.ts` — the draft domain model and seed data, reused as the V2 schema source.
- `V1_HANDOFF.md` (V1 snapshot) and `V2_DESIGN_SPEC.md` (V2 architecture + roadmap).

### Phase 0 (done): foundation

The first migration step has been applied:

- The V1 app now lives under `apps/web/` (relocation only — same UI, same IA).
- Domain types are extracted into `packages/shared/` (`@financeos/shared`); `apps/web` imports them (`mock.ts` keeps the seed data and re-exports the types so existing imports keep working).
- `packages/connectors/` holds the abstract connector contracts (ERP, bank/payments, ingestion/OCR) plus **mock adapters** — the mock seam that keeps the app demoable offline.
- `services/api/` is a FastAPI skeleton serving read models + command endpoints (exception queue read/resolve), backed by the mock ERP connector with an in-memory store and audit write-through.
- `services/agents/` is scaffolded (pipeline stages stubbed, no real logic yet).
- `infra/` holds env/secrets scaffolding (`.env.example`).
- The **Exception Queue** screen reads and writes through the API end-to-end (with an offline fallback to the bundled mock so the front-end still runs without the backend).

### Running V2 (current state)

- **Front-end:** `npm install` at the repo root (npm workspaces), then `npm run dev` (runs `apps/web`).
- **Backend:** `cd services/api && pip install -r requirements.txt && uvicorn app.main:app --reload`. The web app points at it via `VITE_API_BASE_URL` (see `infra/.env.example`); if the API is unreachable it falls back to bundled mock data.

### Phase 1 (in progress): AP exceptions, for real

Delivered:

- **Deterministic 3-way match engine** — `services/agents/financeos_agents/matching.py` (pure, unit-tested in `services/agents/tests/`): tolerance-aware PO↔GR↔invoice match with missing-PO, over-limit, duplicate, and tax-jurisdiction checks; emits a recommendation + confidence + reasoning + source docs.
- **AP Matching agent (suggest-only)** — `financeos_agents/ap_matching.py` runs the engine over the ERP's raw AP documents (seeded in the mock ERP connector) under a `ThresholdGate`. Suggest-only ⇒ every item escalates; promoting to auto lets a clean match ≥ threshold auto-approve.
- **Persistence** — stdlib `sqlite3` (no extra deps), `services/api/app/db.py` + `repo.py`. Tables: `exceptions` (lifecycle state open→resolved), append-only `audit`, and `agent_config` (persisted threshold/mode). Seeded on startup by running the agent. DB path via `FINANCEOS_DB` (default `services/api/financeos.db`, gitignored). **[OPEN]** swap to Postgres later — `repo.py` is the only persistence caller.
- The Exception Queue + Agents screens now read agent-computed, persisted data; resolving transitions state and writes the audit trail; agent threshold/mode edits survive restart. Verified via `python -m unittest` (match engine) and a FastAPI `TestClient` smoke (seed → resolve → restart-persistence).

Not yet: real ERP/bank vendor adapters (still mock), auth/RBAC (Phase 4). See `V2_DESIGN_SPEC.md` §9.

### Phase 2 (in progress): AR cash application

Delivered:

- **Cash-match engine** — `services/agents/financeos_agents/cash_matching.py` (pure, unit-tested): deposit→invoice matching by exact, remittance-hint, customer batch, fuzzy subset (closest-summing), else unmatched; emits confidence + proposed invoice set + reasoning + display label.
- **Cash Application agent (suggest-only)** — `financeos_agents/cash_application.py` runs the engine over the bank connector's raw deposits + ERP open AR invoices under a `ThresholdGate`. Suggest-only ⇒ all route to review; auto applies reconciliations ≥ threshold.
- **Persistence + API** — `deposits` table (state unapplied→applied) seeded on startup by the agent; `repo.py` deposit funcs; endpoints `GET /api/deposits` (+ unapplied summary), `GET /api/deposits/{id}` (detail + suggestions), `POST /api/deposits/{id}/apply` (writes audit). The **Cash Application** screen reads/applies through these with an offline mock fallback.

Still mock: bank/ERP vendor adapters. The AR engine + agent are unit-tested alongside AP (`python -m unittest` in `services/agents`).

### Phase 3 (in progress): Collections, integration touchpoints, auto-action

Delivered:

- **Collections agent** — `financeos_agents/collections.py` (pure, unit-tested): transparent risk score (days-past-due + balance) → prioritized action + drafted outreach; suggest-only (agent drafts, human sends). `collections` table + `repo.py` funcs; `GET /api/collections` (+ at-risk/DSO summary), `GET /api/collections/{id}`, `POST /api/collections/{id}/send` (audit). Collections screen reads/sends through these.
- **Integration touchpoints** — Command Center "Agents at work" strip (live from `/api/agents`); Exception drawer **agent-recommendation** panel (Accept = resolve the recommended action / Override). Exceptions now carry a `recommendation` field from the match engine.
- **Audit screen** reads the live, persisted `/api/audit` trail.
- **Auto-action** — promoting an agent suggest-only → auto on the Agents screen re-runs its pipeline and auto-acts on items clearing the threshold (`repo.apply_auto_actions`), writing `auto` audit rows. AP auto-approves a clean 3-way match; AR auto-applies reconciliations ≥ threshold; touchless numbers move.

- **Anomalies & Analytics on live data** — `financeos_agents/anomaly.py` (severity-ranked signals + leakage trend) behind `GET /api/anomalies`; an analytics read model (`app/analytics_data.py`) behind `GET /api/analytics` that serves seeded trends/cards plus a **live-this-session** block computed from the audit trail (auto vs escalated, session touchless %, open count, unapplied total). Both screens read these. **All seven screens now run on live, persisted data.**

Tests: `python -m unittest` in `services/agents` (14 tests — AP match, AR cash-match, collections).

### Phase 4 (in progress): hardening

Delivered:

- **Auth + RBAC** — `services/api/app/auth.py` (dep-free for the research build): roles **Analyst** (default, least-privilege) and **Controller**; `/api/auth/login|me|users`; opaque in-memory bearer tokens. **Gated:** `PATCH /api/agents` (threshold/mode) → Controller; resolving an exception ≥ `FINANCEOS_SOD_LIMIT` (default $20k) → Controller (segregation of duties). Front-end has a role switcher (TopBar) and surfaces 403s as toasts.
- **Security review** — see `SECURITY.md`: hardened (RBAC, kill switch, immutable audit, parameterized SQL, env secrets, CORS, connector contracts) vs deferred (real IdP/JWT, TLS/rate-limit, Postgres, real vendor adapters, async intake, deploy) + the connector vendor-swap how-to.

- **File ERP adapter + CSV ingestion** — `FileERPConnector`/`FileBankConnector` (`packages/connectors`) read AP invoices, open AR invoices, and deposits from CSVs; selected via `FINANCEOS_ERP=file` + `FINANCEOS_DATA_DIR` (sample data in `infra/data/`). Upload endpoints `POST /api/ingest/{ap|ar-invoices|ar-deposits}` (raw `text/csv` body, no multipart dep) parse a CSV and rebuild the queues via the agents; templates at `GET /api/ingest/template/{kind}`. Exception Queue and Cash Application screens have Import + Template buttons. Shared format in `financeos_connectors/csv_formats.py`; the agents expose data-in variants (`generate_exceptions_from`, `generate_deposits_from`, `generate_collections_from`). AP ingest auto-detects duplicates by vendor+amount within an upload (no `dup_of` column needed); `POST /api/ingest/collections` rebuilds the collections queue from an overdue-accounts CSV (also read from `overdue_accounts.csv` in file-erp mode).

Not yet (Phase 4 remainder): real **vendor-SDK** ERP/bank/OCR adapters (file/CSV adapter shipped; SDK adapters slot into the same seam), real IdP/JWT, async intake, deployment.

### LLM-assisted reasoning

- `services/agents/financeos_agents/llm.py` — swappable LLM provider behind a thin interface (per spec §4/§10). Default is `OfflineNarrator`: deterministic, dependency-free, runs offline; it drafts a controls-analyst-style explanation + recommended disposition from the structured exception. `LLM_PROVIDER` selects the backend: `ollama` → **`OllamaProvider`** (local / self-hosted, `OLLAMA_HOST`+`OLLAMA_MODEL`, temperature 0 for repeatable audit output; also works against any OpenAI-compatible `/api/chat` runner like vLLM/TGI — data never leaves your infra, the preferred option for financial data); `anthropic` (or `LLM_API_KEY` set) → **`AnthropicProvider`** via stdlib `urllib` (no SDK). All providers send only the exception's discrepancy — never the vendor/customer master (data minimization, SECURITY.md). If the chosen model is unreachable, reasoning falls back to the offline narrator (never errors); the model string is returned for the audit trail. Recommended local default is **`qwen2.5:3b`** — the latency/quality sweet spot on CPU (clean 3-way-match and duplicate narratives at ~7-8s/call); `qwen2.5` (7B) is higher quality but ~3x slower, and `qwen2.5:0.5b` is fastest but unreliable.
- `financeos_agents/reasoning.py` + `POST /api/exceptions/{id}/explain` (auth-gated; writes an audit row) return `{narrative, suggestedAction, model, grounded}`. The Exception drawer has an **Explain with AI** button that renders the narrative + a model badge. Deterministic rules still own the disposition; the LLM only explains/justifies the gray-area items.