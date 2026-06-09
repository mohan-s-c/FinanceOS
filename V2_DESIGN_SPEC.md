# Finance OS / APAR — V2 Design Spec

> Scope: architecture + roadmap to extend V1 (front-end prototype) into a working agentic AP/AR system with a backend, an agent layer, persistence, and external integrations. Companion docs: `V1_HANDOFF.md` (where V1 left off) and `CLAUDE.md` (working rules).
> Status: draft for alignment. Decisions marked **[OPEN]** need a call before/early in build.
> Date: 2026-06-05.

## 1. Goal & guiding principles

Turn the V1 prototype into a system where agents do the routine AP/AR work and a human analyst supervises by exception. The product is judged on **touchless rate** (work done without human touch) **without sacrificing auditability or control**.

Principles:

1. **Supervise by exception.** The analyst's default job is reviewing what the agent couldn't safely auto-handle — not data entry.
2. **Every action is gated and logged.** Auto-actions only fire below/above explicit confidence thresholds; everything lands in the audit trail with a reason and source documents.
3. **Deterministic where possible, LLM where needed.** Clean 3-way matches and standard cash application run on rules; LLM agents handle ambiguity, narrative reasoning, and edge cases.
4. **Connectors are contracts.** ERP, bank, and OCR sit behind abstract interfaces; vendors are swappable adapters.
5. **Runnable offline.** A mock seam keeps the app demoable without live credentials throughout development.

## 2. Current state (V1) → target (V2)

| Capability | V1 | V2 |
|---|---|---|
| UI / screens | ✅ React SPA, 7 screens, mock data | Same UI, wired to live API |
| Domain model | ✅ Types in `mock.ts` | Promoted to shared schema + DB persistence |
| Backend / API | ❌ none | FastAPI service |
| Agents | ❌ simulated client-side | Real agent layer (rules + LLM + tools) |
| Persistence | ❌ resets on refresh | Database (invoices, payments, audit, thresholds) |
| Integrations | ❌ none | ERP, bank/payments, invoice ingestion (OCR/email) |
| Auth / multi-user | ❌ none | Auth + roles (analyst, controller) |
| Audit trail | ⚠️ mock log | Real, immutable, queryable |

## 3. System architecture

Four layers, front to back:

```
┌──────────────────────────────────────────────────────────────┐
│  apps/web  — React 19 + Zustand (V1 UI, unchanged IA)          │
└───────────────▲──────────────────────────────────────────────┘
                │ REST/JSON (typed against packages/shared)
┌───────────────┴──────────────────────────────────────────────┐
│  services/api  — FastAPI                                       │
│   • read models for screens (queue, deposits, collections…)   │
│   • command endpoints (resolve exception, apply cash…)        │
│   • auth, RBAC, audit write-through                           │
└───────────────▲──────────────────────────────────────────────┘
                │ invokes / observes
┌───────────────┴──────────────────────────────────────────────┐
│  services/agents — orchestration + tools                      │
│   • Intake → Match → Decision → (Auto-act | Escalate)         │
│   • rules engine (happy path) + LLM agents (exceptions)       │
│   • confidence thresholds, human-in-the-loop, explanations    │
└───────────────▲──────────────────────────────────────────────┘
                │ typed connector calls
┌───────────────┴──────────────────────────────────────────────┐
│  packages/connectors — ERP · Bank/Payments · Ingestion/OCR    │
│   abstract interfaces + vendor adapters                       │
└──────────────────────────────────────────────────────────────┘
        │                │                 │
   ERP/accounting    bank feed        email + docs
```

Cross-cutting: `packages/shared` (domain types/schemas shared by web + api), `infra/` (env, secrets, deploy), and an **event/audit log** that every agent action writes to.

**[OPEN]** Sync vs. async agent execution: start synchronous (request → agent → response) for simplicity; add a queue/worker (e.g. for batch invoice intake) when volume warrants.

## 4. The agent layer

A pipeline, not a single model. Each stage is independently testable and individually gated.

1. **Intake** — normalize an incoming artifact (invoice PDF/EDI, bank deposit, remittance) into the shared schema via the ingestion/OCR connector. Output: a structured, unvalidated record.
2. **Enrich & match** — pull the counterpart records from the ERP (PO, goods receipt, open invoices) and run matching:
   - **AP:** 3-way match (PO ↔ GR ↔ invoice), line-by-line, tolerance-aware. This is V1's `match` model made real.
   - **AR:** match a deposit to open invoices (exact, then remittance-hint, then fuzzy).
3. **Decide** — produce a decision + **confidence**:
   - Clean match within tolerance → **rules** decide (no LLM needed).
   - Mismatch / ambiguity → **LLM agent** reasons over the discrepancy, proposes an action (approve / adjust / reject / request clarification / escalate), and writes a human-readable rationale citing sources.
4. **Act or escalate** — compare confidence to the agent's **threshold** (from the Audit/Thresholds screen):
   - Above threshold → auto-act via connector (post approval, apply cash, send vendor note) and log.
   - Below → land it in the **Exception Queue** / **Cash Application** screen for the analyst, pre-filled with the agent's recommendation.
5. **Audit** — every step (auto or human) writes an immutable `AuditEntry` (agent, action, confidence, outcome, source, by-whom).

Initial agent roster maps to V1 screens: **AP Matching agent**, **Cash Application agent**, **Collections agent**, **Anomaly/Leakage agent**. Each ships in **suggest-only mode** first (threshold effectively at 100% = always escalate), then is dialed toward auto-action as it earns trust.

**[OPEN]** LLM provider/model and where tool-calling runs. Recommend starting with one provider behind a thin abstraction so it's swappable.

## 5. Connector design

One interface per integration class; vendor adapters implement it. Agents and the API only ever see the interface.

- **ERP / accounting connector** — read POs, goods receipts, open invoices, GL accounts, vendor/customer master; write approvals, adjustments, applied-cash entries. (Candidates: NetSuite, SAP, QuickBooks, Xero.)
- **Bank / payments connector** — read incoming deposits + remittance detail; read outgoing payment status. (Candidates: Plaid-style aggregator, direct bank API, BAI2/MT940 files.)
- **Ingestion / OCR connector** — capture invoices from email + document upload, OCR/parse to structured fields. (Candidates: a document-AI service, or email + parser.)

Each connector exposes: capability discovery, typed read methods, typed write methods (clearly marked side-effectful), and a **mock adapter** used in dev/demo. Credentials resolve from secret storage, never code.

**[OPEN]** Which concrete vendors to build first. Spec is vendor-agnostic; pick based on what the deploying organization actually runs (likely the ERP first, since it's the system of record).

## 6. Data model evolution

Promote V1's `mock.ts` types into the persisted schema in `packages/shared`. Minimal additions for V2:

- **Identity & provenance** — every record gets a stable ID, source connector, and ingest timestamp.
- **State machine** — exceptions/deposits/collections get explicit lifecycle states (e.g. `ingested → matched → decided → auto_resolved | escalated → human_resolved`) instead of just being removed from a list.
- **AuditEntry** becomes an append-only table, the backbone of compliance.
- **Threshold** becomes per-agent persisted config, editable from the UI, versioned (so a threshold change is itself auditable).
- **Links** — Exception ↔ PO ↔ GR ↔ invoice ↔ vendor; Deposit ↔ invoices ↔ customer — as real foreign keys, not strings.

Keep field names aligned with V1 where sensible so the front-end migration is mechanical.

**[OPEN]** Database choice (Postgres recommended for relational AP/AR + JSON columns for raw source payloads).

## 7. Security, compliance, control

- **Auth + RBAC** — at minimum Analyst and Controller roles; auto-action thresholds and escalations respect role.
- **Immutable audit** — append-only, queryable, exportable; covers both agent and human actions.
- **Segregation of duties** — agents propose; high-value actions can require human approval regardless of confidence (a per-rule "always escalate above $X").
- **Secrets** — connector credentials in a secret manager, referenced via `infra/`, never in the repo.
- **PII / financial data** — encrypt at rest and in transit; minimize what the LLM sees (send the discrepancy, not the whole vendor master).
- **Kill switch** — a global "suggest-only" mode that forces every agent to escalate, for incidents.

## 8. Repo restructure

V1 is a flat Vite app. Move to the monorepo layout in `CLAUDE.md`:

1. Move the current app to `apps/web` (no code changes, just relocation + path fixes).
2. Add `services/api` (FastAPI skeleton) and `services/agents`.
3. Extract domain types from `apps/web/src/data/mock.ts` into `packages/shared`; have web import from there.
4. Add `packages/connectors` with interfaces + mock adapters.
5. Add `infra/` for env/secrets/deploy.

**[OPEN]** Monorepo tooling (npm workspaces for the JS side; Python managed separately with its own venv/uv). Keep it simple — a workspace + a Python service is enough; no heavyweight monorepo tool needed initially.

## 9. Phased roadmap

**Phase 0 — Foundation (restructure + contracts).** Monorepo layout; extract shared schema; stand up FastAPI skeleton; define connector interfaces with mock adapters; wire one V1 screen (Exception Queue) to the API against mock data end-to-end. *Exit:* the UI reads/writes through the backend, still on mock data.

**Phase 1 — AP exceptions, for real.** Persist invoices/exceptions; implement deterministic 3-way match + tolerances; add the AP Matching agent in suggest-only mode; real audit trail; editable thresholds. *Exit:* analyst resolves real exceptions; agent recommends but doesn't auto-act.

**Phase 2 — Turn on auto-action + AR cash application.** Dial AP thresholds to allow auto-approve within tolerance; build Cash Application agent (deposit → invoice matching); same suggest-then-autonomous path. *Exit:* measurable touchless rate on AP; AR cash applied with agent assist.

**Phase 3 — Collections, anomalies, analytics on live data.** Collections agent (prioritize + draft outreach, human-sent); Anomaly/Leakage detection on the real ledger; Analytics screen fed by real metrics. *Exit:* all seven screens running on live data.

**Phase 4 — Hardening.** Real ERP/bank vendor adapters replacing mocks; auth/RBAC; security review; async intake for volume; deployment. *Exit:* pilot-ready.

Each phase keeps the mock seam intact so the app stays demoable throughout.

## 10. Open decisions to resolve first

1. **[OPEN]** Backend stack confirm — Python/FastAPI assumed (best agent ecosystem). Alternative: Node/TS for one-language simplicity.
2. **[OPEN]** LLM provider + tool-calling host.
3. **[OPEN]** First concrete ERP and bank vendors (drives which adapter is built beyond mock).
4. **[OPEN]** Database (Postgres recommended).
5. **[OPEN]** Sync-first vs. queue-based agent execution.

Recommended first V2 task: **Phase 0** — do the restructure and get one screen flowing through a real (mock-backed) API. It's low-risk, unblocks everything else, and forces the schema and connector contracts to be made concrete.
