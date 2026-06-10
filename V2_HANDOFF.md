# Finance OS / APAR — V2 Handoff (context package for V3)

> Mirrors `V1_HANDOFF.md` (which set up V2). This is the snapshot of where **V2**
> landed and the context for whoever builds **V3**. Read `CLAUDE.md` first for
> standing project rules, `V2_DESIGN_SPEC.md` for the V2 architecture, and
> `V3_TECH_SPEC.md` for the next planned build.

## What V2 is

An AI/agentic Finance OS that automates an organization's Accounts Payable &
Receivable. Software agents ingest invoices and payments, run a deterministic
3-way match, apply incoming cash, drive collections, and flag anomalies — under
per-agent confidence thresholds, with a human analyst (persona: Dana Okafor)
supervising **by exception** rather than doing manual data entry. V2 took V1 (a
front-end-only prototype) and added the real substance: a backend, an agent layer,
persistence, integrations seam, auth, and LLM-assisted reasoning.

## Tech stack (as built)

- **Front-end:** React 19 + Vite + TypeScript + Zustand; the seven-screen UI in the
  Espresso theme; lives in `apps/web`.
- **Backend / BFF:** Python + FastAPI (`services/api`); read models + command
  endpoints, auth/RBAC, audit write-through, CSV ingestion.
- **Agents:** Python (`services/agents`); deterministic engines (3-way match, cash
  match, collections risk, anomaly) under a `ThresholdGate`, plus an LLM reasoning
  layer that only *explains* gray-area cases.
- **Shared/contracts:** `packages/shared` (domain schema) and `packages/connectors`
  (abstract ERP/bank/ingestion contracts + mock and file/CSV adapters).
- **Persistence:** stdlib `sqlite3` behind `repo.py` (the single Postgres-swap seam).
- **Deploy:** single-service `Dockerfile` + `render.yaml` (see `DEPLOY.md`).

## What's built (V2 phases, delivered)

- **Foundation** — monorepo, shared schema, FastAPI, connector contracts + mock seam;
  all seven screens wired to the API with an offline fallback.
- **AP exceptions** — tolerance-aware 3-way match engine; AP Matching agent
  (suggest-only); SQLite persistence + immutable audit; intra-batch duplicate detect.
- **AR cash application** — deposit→invoice match (exact / remittance / batch / fuzzy);
  apply flow with audit.
- **Collections, Anomalies, Analytics** — risk-scored outreach drafts; severity-ranked
  leakage detection; analytics with a live-this-session block from the audit trail.
- **Autonomy** — promote an agent suggest-only → auto and it auto-acts on
  threshold-clearing items; global kill switch.
- **Hardening** — Auth + RBAC (Analyst / Controller) with segregation of duties
  (≥ $20k → Controller); security review (`SECURITY.md`).
- **Data in** — File/CSV ERP adapter + AP/AR/Collections CSV upload with templates.
- **LLM-assisted reasoning** — swappable provider (local Ollama/Qwen, hosted, or
  offline narrator), data-minimized, audit-logged with the model used.
- **Docs/deploy** — V2 user manual (PDF), `DEPLOY.md`, this handoff.

## What V2 is NOT (the V3 gap)

- **No supervisor / control plane.** V2 gates each *action* via static thresholds, but
  nothing watches the *agents themselves* — no detection of degradation, confidence
  drift, or rogue/out-of-envelope actions, and no automatic intervention. The Anomaly
  agent watches the ledger, not the agents; the "All systems nominal" badge is static.
  A human has to notice.
- **No self-improvement loop.** Override signal is captured in the audit trail but not
  yet used to auto-tune thresholds or refine the match/risk models. The local LLM
  explains; it does not learn from inference.
- **Still mock-ish at the edges.** Real vendor-SDK ERP/bank/OCR adapters, real
  IdP/JWT, TLS/rate-limiting, Postgres, async intake, and production deploy are
  deferred (the connector swap seam is a single file).
- **Payment execution not closed.** Agents approve invoices but don't pay them; the
  Payment Run agent is roster-only.

## Suggested V3 starting points

Two complementary tracks (see the manual roadmap and the specs):

1. **Supervisor / agent control plane** — the *guardrail* half. A deterministic control
   plane that monitors each agent (override rate, confidence drift, volume, error /
   latency, envelope conformance), trips a circuit breaker to demote a misbehaving
   agent to suggest-only, gates out-of-envelope actions, and pages a human — all
   audited, with autonomy only ever *restored* by a Controller. The gating logic is
   rule-based, never an autonomous LLM, so the guardrail can't itself go rogue. Full
   design, data model, APIs, and phased plan in **`V3_TECH_SPEC.md`**.
2. **Closed-loop learning from analyst decisions** — the *improvement* half. Use the
   override signal to auto-tune thresholds and refine the match/risk models so the
   touchless rate climbs on its own.

Other high-value product features captured in the manual roadmap: autonomous payment
execution & run orchestration, and a two-way supplier/customer portal.

## How to bootstrap V3 cleanly

1. Work in this same repo (V3 extends V2; no new folder needed unless you want a clean
   history).
2. In the first V3 message, tell me to read `CLAUDE.md`, `V2_DESIGN_SPEC.md`, this
   `V2_HANDOFF.md`, and `V3_TECH_SPEC.md`.
3. Start at V3 phase **P1 (observe-only telemetry)** — live agent-health badges on the
   Agents console — before enabling any enforcement, the same suggest-only → auto
   progression V2 uses for agents.
