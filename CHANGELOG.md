# Changelog

## V2.0 — Agentic Finance OS (Phases 0–4)

Extends the V1 front-end prototype into a working agentic AP/AR system: a backend, a
deterministic agent layer, persistence, RBAC, and all seven screens on live data.
Generic `financeos` naming; Espresso theme; mock connector seam keeps it runnable offline.

### Architecture (Phase 0)
- Monorepo: `apps/web` (React 19 + Vite + Zustand), `services/api` (FastAPI),
  `services/agents` (agent layer), `packages/shared` (domain schema), `packages/connectors`
  (ERP/bank/ingestion contracts + mock adapters), `infra/` (env templates).
- FastAPI BFF with read models + command endpoints; Exception Queue wired end-to-end.

### AP — exceptions for real (Phase 1)
- Deterministic, tolerance-aware 3-way match engine (PO↔GR↔invoice) with missing-PO,
  over-limit, duplicate, tax-jurisdiction checks → recommendation + confidence + reasoning + sources.
- AP Matching agent (suggest-only) over the mock ERP under a confidence-threshold gate.
- Persistence via stdlib `sqlite3` (`db.py`/`repo.py`): exceptions lifecycle, append-only audit,
  persisted agent config. Seeded on startup by the agent.

### AR — cash application (Phase 2)
- Cash-match engine (exact / remittance / customer-batch / fuzzy / unmatched) + Cash Application
  agent; `deposits` persistence; `/api/deposits` list, detail, and apply (audited).

### Collections, integration, autonomy, live data (Phase 3)
- Collections agent: risk-scored overdue accounts + drafted outreach (human-sent); `/api/collections`.
- Command Center "Agents at work" strip; Exception drawer agent-recommendation (Accept/Override);
  Audit screen on the live trail; Anomaly detection (`/api/anomalies`) + leakage trend;
  Analytics read model with a live-this-session block from the audit trail.
- Auto-action: promoting an agent suggest-only→auto re-runs its pipeline and auto-acts on
  threshold-clearing items, moving the touchless rate.
- All seven screens now run on live, persisted, agent-computed data.

### Hardening (Phase 4)
- Auth + RBAC: Analyst (default, least-privilege) and Controller roles; segregation of duties
  (agent autonomy changes + high-value resolves ≥ $20k require Controller); global kill switch.
- `SECURITY.md` review + connector vendor-swap guide.

### Quality
- 14 unit tests (AP match, AR cash-match, collections) via `python -m unittest` in `services/agents`.
- Clean `tsc -b` + `vite build`.

### Deferred (need real credentials / infra)
- Real ERP/bank/OCR vendor adapters (swap seam: `services/api/app/connectors.py`),
  real IdP/JWT, Postgres, async intake, deployment.
