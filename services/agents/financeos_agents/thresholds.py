"""Confidence-threshold gating — the human-in-the-loop control surface.

`suggest_only=True` forces every item to escalate regardless of confidence (the global
kill switch and the default for any newly-introduced agent). Thresholds are per-agent
and, in Phase 1, persisted + editable from the Audit/Thresholds screen.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ThresholdGate:
    agent: str
    threshold: int  # 0..100; auto-act only when confidence >= threshold
    suggest_only: bool = True

    def should_auto_act(self, confidence: int) -> bool:
        if self.suggest_only:
            return False
        return confidence >= self.threshold
