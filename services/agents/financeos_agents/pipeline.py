"""The agent pipeline contract (Phase 0 stubs).

Stages transform a record and append audit; `Decide` attaches an action + confidence;
`Act` either auto-acts (via a connector) or escalates per the ThresholdGate. The real
logic lands in Phase 1 — these stubs make the shape explicit and testable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .thresholds import ThresholdGate


@dataclass
class Decision:
    action: str           # approved | adjusted | rejected | clarify | escalated
    confidence: int       # 0..100
    reason: str           # human-readable rationale
    sources: list[dict] = field(default_factory=list)
    auto: bool = False    # True only if it cleared the threshold gate


class PipelineStage(Protocol):
    name: str
    def run(self, record: dict) -> dict: ...


class IntakeStage:
    name = "intake"
    def run(self, record: dict) -> dict:
        # Phase 1: normalize a raw artifact via the ingestion connector.
        raise NotImplementedError("Intake is a Phase 1 capability.")


class MatchStage:
    name = "match"
    def run(self, record: dict) -> dict:
        # Phase 1: deterministic, tolerance-aware 3-way match (PO ↔ GR ↔ invoice).
        raise NotImplementedError("Matching is a Phase 1 capability.")


class DecideStage:
    name = "decide"
    def run(self, record: dict) -> dict:
        # Phase 1: rules for clean matches, LLM agent for ambiguity.
        raise NotImplementedError("Decisioning is a Phase 1 capability.")


def run_pipeline(record: dict, gate: ThresholdGate) -> Decision:
    """Phase 0 placeholder: with no decision logic yet and suggest-only on by default,
    everything escalates to the analyst — exactly the safe starting posture."""
    decision = Decision(
        action="escalated",
        confidence=int(record.get("confidence", 0)),
        reason="Phase 0: no automated decisioning yet — routed to analyst for review.",
        sources=record.get("sources", []),
    )
    decision.auto = gate.should_auto_act(decision.confidence)  # False while suggest-only
    if decision.auto:
        decision.action = "approved"
    return decision
