"""LLM-assisted exception reasoning. Wraps the provider and packages a result."""
from __future__ import annotations

from .llm import get_provider, OfflineNarrator

_ACTION = {
    "approve": "Approve", "reject": "Reject", "escalate": "Escalate for review",
    "hold": "Hold — obtain PO", "adjust": "Adjust & approve",
}


def explain_exception(ex: dict) -> dict:
    provider = get_provider()
    model = getattr(provider, "name", "offline-narrator")
    try:
        narrative = provider.explain(ex)
        if not narrative.strip():
            raise ValueError("empty response")
    except Exception:
        # Local model down / unreachable -> never fail the request; fall back to offline.
        narrative = OfflineNarrator().explain(ex)
        model = f"{model} (unavailable -> offline)"
    rec = ex.get("recommendation", "escalate")
    return {
        "id": ex.get("id"),
        "narrative": narrative,
        "suggestedAction": _ACTION.get(rec, "Escalate for review"),
        "model": model,
        "grounded": ex.get("sources", []),
    }
