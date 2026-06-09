# Security review — Finance OS / APAR (V2)

> Status: research build. This documents the current security posture, what is hardened,
> what is deliberately deferred before a pilot, and how the vendor-connector seam is swapped.
> Companion: `CLAUDE.md` (working rules), `V2_DESIGN_SPEC.md` §7 (security/compliance/control).

## In place (hardened)

- **RBAC — Analyst vs Controller.** `services/api/app/auth.py` defines roles and FastAPI
  dependencies. Gated actions: tuning agent autonomy (`PATCH /api/agents/{id}` — threshold/mode)
  and **segregation of duties** on high-value dispositions (resolving an exception ≥
  `FINANCEOS_SOD_LIMIT`, default $20,000) both require **Controller**. Analysts handle the
  routine queue; controllers govern.
- **Global kill switch.** `FINANCEOS_SUGGEST_ONLY` (and per-agent suggest-only mode) forces
  every agent to escalate — incident lever. Surfaced on `/health` and the Agents console.
- **Immutable audit trail.** Append-only `audit` table; every disposition, config change, and
  auto-action is logged with confidence, outcome, source documents, and actor. No update/delete path.
- **No SQL injection.** All persistence (`db.py`/`repo.py`) uses `sqlite3` parameterized queries;
  no string-built SQL.
- **Secrets never in the repo.** Config reads from env (`infra/.env.example` is the template);
  `.gitignore` excludes `.env*` and `*.db`. No credentials are committed.
- **CORS allow-list.** `FINANCEOS_CORS_ORIGINS` restricts browser origins (defaults to the local
  dev hosts only).
- **Connectors are contracts.** Agents and the API depend only on the abstract connector
  interfaces (`packages/connectors`); vendor credentials never reach agent logic. The mock seam
  keeps the system runnable offline with no secrets.
- **Deterministic-first.** AP/AR/collections decisions run on pure, unit-tested rules engines
  (no LLM yet), so there is no prompt-injection or data-exfiltration surface in the decision path.

## Deferred (resolve before pilot)

- **Real identity provider.** Current bearer tokens are opaque and in-memory with no expiry,
  refresh, or password/SSO — a dev convenience (`/api/auth/login` picks a seeded user). Replace
  with OIDC/SSO + signed, expiring JWTs and per-tenant user management.
- **Transport + platform.** TLS termination, HSTS, rate limiting, request size limits, CSRF (if
  cookie auth is adopted), and a secrets manager for connector credentials.
- **Persistence.** SQLite → Postgres with encryption at rest, least-privilege DB users, and
  migrations; raw source payloads stored as JSON columns.
- **Real vendor adapters.** ERP/bank/OCR are still mock (see swap guide below). Each needs
  credential handling via the secret manager and PII minimization (send the discrepancy, not the
  whole vendor/customer master) once an LLM agent is introduced.
- **Async intake** (queue/worker) for batch volume, and deployment hardening (IaC, image scanning,
  audit log shipping/retention per SOX).

## Connector vendor-swap seam

Swapping a mock adapter for a real vendor is a one-file change — nothing in the agents or API
references a concrete vendor:

1. Implement the abstract interface in `packages/connectors/financeos_connectors/` (e.g.
   `NetSuiteERPConnector(ERPConnector)`), resolving credentials from the secret manager.
2. In `services/api/app/connectors.py`, select the adapter (e.g. by `FINANCEOS_ERP=netsuite`)
   and instantiate it as `erp`. No other code changes — the read models, agents, and routers are
   unchanged because they only see the interface.
3. Keep the mock adapter available so the app stays demoable offline (mock seam).
