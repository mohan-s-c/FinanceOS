# Finance OS / APAR — V3 Tech Spec: Supervisor / Agent Control Plane

> Status: proposed (V3). This spec defines a new governance layer that watches the
> agents themselves. It builds on the V2 architecture (`V2_DESIGN_SPEC.md`) and the
> shipped V2 control surface (per-agent `ThresholdGate`, global kill switch, RBAC,
> immutable audit). Read `CLAUDE.md` first for standing project context.

## 1. Goal & guiding principles

V2 made the *agents* safe to act by gating each action behind a confidence
threshold and keeping a human in the loop by exception. What V2 does **not** have is
anything that watches the *agents themselves*. Thresholds are static and
human-tuned; nothing detects an agent degrading, drifting, or behaving anomalously,
and nothing intervenes automatically. A human has to notice.

V3 adds a **Supervisor** — a control plane that monitors every agent, detects
degradation or rogue behavior, trips a circuit breaker to pull a misbehaving agent
back to suggest-only, and pages a human. Principles:

- **The guardrail is deterministic, not another autonomous agent.** The Supervisor's
  decision logic is rule-based and auditable. We do **not** put an LLM in charge of
  the other agents — that would add a new thing that can go rogue and hand it
  authority. An LLM may *explain* a tripped breaker; it never decides to trip one.
- **Fail safe, not open.** Any uncertainty (missing telemetry, an unrecognized
  action, a tripped threshold) resolves toward *less* autonomy: demote to
  suggest-only and escalate. The safe state is "humans decide."
- **Observable and reversible.** Every supervisor action is written to the same
  immutable audit trail, is attributable, and can be reviewed and reversed by a
  Controller.
- **Additive, behind a flag.** The Supervisor ships in observe-only mode first; its
  enforcement powers are enabled per-capability once trusted — the same
  suggest-only → auto progression the product already uses for agents.

## 2. Problem statement (the V2 gap)

Concretely, in V2 today:

- `ThresholdGate` gates each *action* but is static — it cannot notice an agent whose
  quality is sliding.
- The global kill switch is all-or-nothing and **manual**.
- The Anomaly agent watches the **ledger** (duplicate invoices, leakage), not the
  **agents**.
- The Agents console "All systems nominal" is a static indicator, not a live health
  signal.
- There is no concept of an agent acting **outside its allowed envelope** (e.g. an AP
  agent attempting an action it should never take), nor any automated response to it.

The risk this leaves: silent degradation (a model or data-source change quietly
raises the error/override rate), and unforeseen/rogue actions that no rule
anticipated. Both currently depend on a human happening to look.

## 3. What the Supervisor monitors

Per agent, on a rolling window, sourced from the audit trail + lightweight runtime
telemetry:

- **Override rate** — share of the agent's auto-actions or recommendations a human
  reverses. The single most important trust signal; a rising override rate means the
  agent is wrong more often.
- **Confidence distribution & drift** — shifts in the agent's confidence histogram vs.
  a baseline (e.g. a sudden mass of borderline-threshold decisions).
- **Volume & mix** — exception/auto-action counts and their composition vs. expected
  ranges (a spike or collapse signals an upstream data or logic change).
- **Error & latency** — exceptions thrown, connector/LLM timeouts, fallback-to-offline
  rate, p95 latency.
- **Outcome lag** — auto-applied items later reversed downstream (e.g. a cash match
  un-applied), i.e. decisions that looked confident but were wrong.
- **Envelope conformance** — every action checked against a declared per-agent
  *action envelope* (the finite set of actions + value/scope limits that agent is ever
  allowed to take). Anything outside it is, by definition, a rogue action.

Baselines are computed from the agent's own trailing history (and seeded defaults for
new agents). Drift is flagged on deviation beyond configurable bands.

## 4. Control actions

When a rule fires, the Supervisor takes the **least-disruptive sufficient** action and
audits it:

1. **Warn** — annotate the Agents console with a health flag; no behavior change.
2. **Demote (circuit breaker)** — force the agent to `suggest_only` (it keeps
   producing recommendations, but every item now escalates to a human). This is the
   core safety move: autonomy is removed, the agent is not stopped.
3. **Quarantine** — for an out-of-envelope/rogue action: block the specific action,
   demote the agent, and open an incident.
4. **Page a human** — open an **incident** (owner = Controller) with the evidence:
   which rule, the metric vs. baseline, and the offending action(s).
5. **Global kill switch** — for a correlated, multi-agent failure, trip the existing
   system-wide suggest-only switch.

Re-enabling autonomy after a breaker trip is a **human (Controller) action**, written
to the audit trail (segregation of duties) — the Supervisor never re-grants autonomy
to itself.

## 5. Design: a deterministic control plane

The Supervisor is a policy engine, not a model:

- **Policy rules** are declarative `{signal, window, comparator, threshold, action}`
  records, versioned and persisted (e.g. "override_rate over 7d > 15% ⇒ demote +
  incident"). Editing policy is a Controller-gated, audited change — exactly like
  editing a threshold today.
- **Envelopes** are declarative per-agent allow-lists of action types and limits.
  Enforcement is a pure check at the act step (extends `ThresholdGate` /
  `repo.apply_auto_actions`).
- **Baselining / drift** uses simple, explainable statistics (rolling mean/σ,
  rate-of-change), not a black box — an auditor must be able to see *why* a breaker
  tripped.
- **LLM role (optional, explain-only):** mirror the V2 pattern — the offline/Ollama
  narrator may draft the human-readable incident summary, but it is never in the
  decision path and only sees the structured incident, never master data.

## 6. Architecture & integration

```
services/agents/financeos_agents/supervisor.py   ← policy engine (pure, unit-tested)
                                  envelopes.py    ← per-agent action allow-lists
services/api/app/
  routers/supervisor.py                           ← health, incidents, policy CRUD
  repo.py                                          ← agent_health, incidents, policy tables
apps/web/src/screens/Agents.tsx                    ← health badges + Incidents panel
```

- **Inputs:** reads the existing append-only `audit` table + per-call telemetry the
  agents already emit; no new data source required for P1–P3.
- **Hooks:** the act step (`repo.apply_auto_actions`) consults the Supervisor for
  envelope conformance before any auto-action; a scheduled evaluator runs the policy
  rules over the rolling windows.
- **Outputs:** writes `agent_health` snapshots, `incidents`, and `audit` rows for every
  supervisor action; toggles per-agent `suggest_only` via the same path the Agents
  console already uses.
- **Persistence:** new tables behind `repo.py` (the single Postgres-swap seam), so V3
  inherits V2's persistence story unchanged.

## 7. Data model additions

- `agent_health(agent, window, override_rate, conf_drift, volume, error_rate, latency_p95, computed_at)`
- `incident(id, agent, rule_id, severity, status[open|ack|resolved], evidence_json, opened_at, owner, resolved_by)`
- `policy_rule(id, agent|*, signal, window, comparator, threshold, action, enabled, version, updated_by)`
- `action_envelope(agent, allowed_actions_json, limits_json, version, updated_by)`

## 8. API & UI surface

- `GET /api/supervisor/health` — per-agent health snapshot (drives the console badges).
- `GET /api/supervisor/incidents` / `POST /api/supervisor/incidents/{id}/ack|resolve`.
- `GET|PATCH /api/supervisor/policy` and `/envelopes` — Controller-gated.
- **Agents console:** replace the static "All systems nominal" with live per-agent
  health (green/amber/red), an **Incidents** panel, and a visible "demoted by
  Supervisor" state with the reason and the one-click (Controller) path to restore.

## 9. Safety & governance

- The Supervisor can **only reduce** autonomy automatically; **raising** it is always a
  human, audited action.
- Its logic is deterministic and versioned; an auditor can reconstruct any breaker
  trip from the audit trail + the policy version in force at the time.
- It has no payment, approval, or data-modification powers — it only flips autonomy
  flags, blocks out-of-envelope actions, and opens incidents.
- It does not see vendor/customer master data; it operates on metrics and structured
  incidents.
- If the Supervisor itself is unavailable, agents fall back to their last known mode
  and new agents stay suggest-only — fail safe.

## 10. Phased plan

- **P1 — Observe-only telemetry.** Compute and persist `agent_health` from the audit
  trail; surface live health badges on the Agents console. No enforcement.
- **P2 — Baselines, drift & incidents.** Policy rules + baselining; open incidents and
  warn; still no automatic demotion.
- **P3 — Circuit breaker.** Enable automatic demote-to-suggest-only + page on rule
  trips; Controller-only restore. This is the core safety capability.
- **P4 — Envelope enforcement.** Per-agent action envelopes checked at the act step;
  quarantine + incident on any out-of-envelope action.
- **P5 — Correlated-failure handling & LLM incident summaries.** Multi-agent trip →
  global kill switch; optional offline/Ollama narrator drafts incident write-ups.

## 11. Open decisions

- Evaluator cadence: event-driven (on each audit write) vs. scheduled sweep vs. both.
- Where envelopes live — declared in code with each agent, or data-driven in
  `action_envelope` (leaning data-driven so policy changes don't require a deploy).
- Baseline source for brand-new agents (seeded defaults vs. a probation period).
- Whether P3 demotion is per-agent only, or can also narrow scope (e.g. demote only
  for amounts over a band) before a full demotion.
