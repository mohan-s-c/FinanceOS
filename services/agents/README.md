# services/agents

The agent layer: a **pipeline, not a single model** (see `V2_DESIGN_SPEC.md` §4).

```
Intake → Enrich & Match → Decide → (Auto-act | Escalate) → Audit
```

Each stage is independently testable and individually gated. Phase 0 ships **stubs**
that encode the contract and the human-in-the-loop default (suggest-only ⇒ always
escalate). Phase 1 fills in deterministic, tolerance-aware 3-way matching and the
AP Matching agent; LLM reasoning for exceptions arrives behind a swappable provider.

Guarantees that hold from day one:
- Every decision carries a **confidence** and a human-readable **reason** citing sources.
- Auto-action only fires when confidence ≥ the agent's threshold AND the global
  suggest-only kill switch is off. Otherwise the item escalates to the analyst.
- Every step writes an immutable audit entry.
