"""LLM-assisted exception reasoning. Wraps the provider and packages a result."""
from __future__ import annotations

from .llm import get_provider

_ACTION = {
    "approve": "Approve", "reject": "Reject", "escalate": "Escalate for review",
    "hold": "Hold — obtain PO", "adjust": "Adjust & approve",
}


def explain_exception(ex: dict) -> dict:
    provider = get_provider()
    narrative = provider.explain(ex)
    rec = ex.get("recommendation", "escalate")
    return {
        "id": ex.get("id"),
        "narrative": narrative,
        "suggestedAction": _ACTION.get(rec, "Escalate for review"),
        "model": getattr(provider, "name", "offline-narrator"),
        "grounded": ex.get("sources", []),
    }
