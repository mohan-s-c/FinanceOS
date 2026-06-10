# Finance OS / APAR — V1 Handoff (context package for V2)

> Purpose: a self-contained snapshot of V1 so a fresh V2 project starts informed but with a clean conversation history. Drop this file into the V2 project folder. Nothing about V1 carries over automatically — separate project = separate conversation history, separate memory, separate (unless overlapping) folder.
> Snapshot date: 2026-06-05.

## What V1 is

An **AI/agentic Finance OS** prototype that automates the **Accounts Payable & Accounts Receivable (APAR)** workflows of an organization's finance department. V1 is a **front-end prototype with mock data** — a clickable, visually complete UI that demonstrates the target product, not a system wired to real ERP/banking data. The framing is agent-driven: software "agents" auto-approve invoices, surface exceptions, apply incoming cash, chase collections, and flag anomalies, with a human analyst supervising.

Primary persona built into the UI: **Dana Okafor, AP/AR Analyst**. The product is designed around her supervising a queue rather than doing manual matching.

## Tech stack (as built)

- **React 19** + **TypeScript** + **Vite 8** (SPA, no router — view switching via Zustand state).
- **Zustand 5** for global state (`src/store/useStore.ts`). Single store: current view, theme (dark/light), sidebar collapse, density, exceptions list, open-count badge, toasts, activity feed.
- **No backend.** All content comes from `src/data/mock.ts` (~220 lines of typed mock data).
- Styling is hand-written CSS (`src/styles/index.css` ~449 lines, plus `App.css`, `index.css`), CSS variables for theming, dark mode default. Custom icon set via `src/components/Icon.tsx` + `public/icons.svg` sprite. Custom fonts (Hanken, Geist Mono) self-hosted in `public/fonts`.
- Build: `npm run dev` / `npm run build` (`tsc -b && vite build`). A built `dist/` is checked in.
- The standalone `APAR FinanceOS.html` at the repo root appears to be an early single-file mock predating the React app.

Note: `README.md` is still the stock Vite template — it does **not** describe this project.

## Screen / feature map

Navigation lives in `src/chrome/Sidebar.tsx`, grouped as Overview / (AP) / (AR) / Intelligence. Seven screens (`src/screens/*.tsx`):

1. **Command Center** (`Dashboard.tsx`) — top-level KPIs, AP & AR health tiles, live agent activity feed, cash-forecast. The home view.
2. **Exception Queue** (`Exceptions.tsx`) — the core AP screen. List of invoice exceptions with a detail pane: 3-way match (PO / goods-receipt / invoice) with mismatch highlighting, line items, agent confidence score, reasoning, and source documents. Resolve actions: approve / reject / adjust & approve / request clarification / escalate. Largest screen (~209 lines).
3. **Cash Application** (`Cash.tsx`) — core AR screen. Unapplied deposits, agent-suggested invoice matches with confidence, apply flow.
4. **Collections** (`Collections.tsx`) — overdue accounts, risk scoring, suggested collection actions, DSO context.
5. **Anomalies & Leakage** (`Anomalies.tsx`) — fraud/duplicate/leakage detection, severity-ranked, with a leakage-over-time trend.
6. **Agent & Audit Trail** (`Audit.tsx`) — chronological log of agent actions with confidence + outcome + source, plus per-agent auto-action **confidence thresholds** (the human-in-the-loop control surface).
7. **Analytics** (`Analytics.tsx`) — trend charts: touchless rate, cost per invoice, close-cycle time, DSO, override rate, against targets.

## Domain data model (the part worth keeping)

V1's mock types in `src/data/mock.ts` are effectively the **draft domain schema** for the product. Key entities:

- **Exception** — invoice exception with `vendor`, `amount`, `po`, `terms`, `lineItems[]`, a `match` object (`po`/`gr`/`inv` cells with rate + mismatch flag — i.e. 3-way match), `confidence`, `agent`, `reasoning`, and `sources[]`. This is the richest entity and the heart of the AP flow.
- **Deposit / SuggestedMatch** — AR cash-application: incoming payment + agent-proposed invoice matches with confidence.
- **Collection / RiskDist** — overdue account with days-outstanding, risk score, suggested action.
- **Anomaly** — severity, risk, type (duplicate, leakage, etc.).
- **AuditEntry / Threshold** — agent action log + the confidence thresholds that gate auto-action.
- **Metric / APHealth / ARHealth / Analytics** — dashboard/reporting aggregates. Headline mock KPIs: 81% touchless AP, 94% auto-applied AR, DSO 28.4, 47 invoices in review.

## What V1 is NOT (the V2 gap)

- No real integrations — no ERP, no bank feed, no vendor portal, no email/OCR ingestion. All agent "actions" are simulated client-side (e.g. resolving an exception just removes it from the list and fires a toast).
- No persistence — refresh resets everything to mock data.
- No auth, no multi-user, no real audit storage.
- No actual AI/agent logic — confidence scores and reasoning are hand-authored mock strings.
- `README.md` and `CLAUDE.md` are absent/stock — no real project documentation exists besides this handoff.

## Suggested V2 starting points (not decisions — prompts for the next conversation)

These are open questions to resolve at the start of V2, informed by where V1 left off:

- **Is V2 still front-end, or does it add a real backend / agent layer?** If real: what's the ingestion path (ERP connector, bank feed, invoice OCR) and where does the agent logic run?
- **Reuse the V1 domain types** (`mock.ts`) as the seed schema rather than redesigning from scratch — the Exception/3-way-match model is the most considered part.
- **Carry the screen map forward** — the seven-screen IA is coherent; V2 likely refines rather than replaces it.
- **Human-in-the-loop thresholds** (Audit screen) are the key trust mechanism; worth making real and configurable in V2.

## How to bootstrap V2 cleanly

1. Create the new project pointed at a **new folder** (so the conversation/history is separate, as intended).
2. Copy this `V1_HANDOFF.md` into that folder.
3. If V2 should build on the V1 codebase, also copy the `src/` tree (or the whole repo minus `node_modules`/`dist`); if it's a clean rebuild, keep just this doc + `src/data/mock.ts` as the schema reference.
4. In the first V2 message, tell me to read `V1_HANDOFF.md` so I pick up context without inheriting V1's chat.

---

## Looking ahead to V3 — Supervisor / agent control plane

> Added after V2 shipped. This is the forward-pointer for whoever picks up the project next.

**Where V2 landed.** All seven screens run on live, persisted, agent-computed data. The agent layer (deterministic 3-way match, cash match, collections risk scoring, anomaly detection) acts under per-agent confidence thresholds with a global kill switch, RBAC + segregation of duties, an immutable audit trail, CSV/ERP ingestion, and an LLM that *explains* gray-area exceptions (local Ollama/Qwen by default, data-minimized). The product can be deployed as a single service (see `DEPLOY.md`).

**The governance gap V2 leaves.** V2 gates each *action*, but nothing watches the *agents themselves*. Thresholds are static and human-tuned; there is no detection of agent degradation, drift, or rogue/out-of-envelope actions, and no automatic intervention. The Anomaly agent watches the ledger, not the agents. A human has to notice.

**V3 — the Supervisor / agent control plane.** A deterministic control plane that monitors each agent (override rate, confidence drift, volume, error/latency, envelope conformance), trips a circuit breaker to demote a misbehaving agent to suggest-only, gates out-of-envelope actions, and pages a human — with all actions audited and autonomy only ever *restored* by a Controller. The guardrail is rule-based, never an autonomous LLM, so it can't itself go rogue. Full design, data model, APIs, and phased plan are in **`V3_TECH_SPEC.md`**.

**Two complementary V3 tracks** (see also the manual's roadmap):

1. **Supervisor / control plane** — the *guardrail* half (this spec).
2. **Closed-loop learning from analyst decisions** — the *improvement* half: use the override signal to auto-tune thresholds and refine the match/risk models so the touchless rate climbs on its own.

**How to bootstrap V3 cleanly.** Same pattern as the V1→V2 handoff: start the next conversation pointed at this repo, tell me to read `CLAUDE.md`, `V2_DESIGN_SPEC.md`, and `V3_TECH_SPEC.md`, and begin at V3 phase P1 (observe-only telemetry on the Agents console) before enabling any enforcement.
