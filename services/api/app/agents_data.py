"""In-memory Agent read model for the Agents console (Phase 0 / suggest-only era).

Mirrors the wireframe: a roster of agents plus per-agent detail (pipeline, recent
decisions with reasons + sources, threshold, performance). Editable threshold/mode is
held in memory and written through to the audit log.
"""
from __future__ import annotations

import copy
import time

from . import connectors, repo

_AGENTS: list[dict] = [
    {
        "id": "ap-matching", "name": "AP Matching Agent", "abbr": "AP",
        "subtitle": "3-way match", "mode": "suggest", "modeLabel": "≥85", "status": "warn",
        "threshold": 85, "confidence": 72, "crossLinkedTo": None, "lastActionAgo": "1 min ago",
        "pipeline": [
            {"key": "intake", "label": "Intake", "value": "1,284", "sub": "ingested (OCR)"},
            {"key": "match", "label": "Match", "value": "1,284", "sub": "PO · GR · invoice"},
            {"key": "decide", "label": "Decide", "value": "1,042 / 242", "sub": "clean / reasoned"},
            {"key": "act", "label": "Act", "value": "1,042", "sub": "auto in tolerance", "tone": "act"},
            {"key": "escalate", "label": "Escalate", "value": "47", "sub": "to analyst", "tone": "esc"},
        ],
        "decisions": [
            {"id": "INV-44821", "recommendation": "Approve", "tone": "ok", "confidence": 96, "why": "3-way match clean, within tolerance", "sources": [{"type": "PO", "ref": "PO-3360", "note": "match"}]},
            {"id": "INV-44903", "recommendation": "Escalate", "tone": "warn", "confidence": 61, "why": "Price +12% > 5% contract ceiling", "sources": [{"type": "Contract", "ref": "C-2024-0142", "note": "rate schedule"}]},
            {"id": "INV-44912", "recommendation": "Escalate", "tone": "warn", "confidence": 72, "why": "Clean, but > $20k capex sign-off", "sources": [{"type": "Policy", "ref": "AP-POL-11", "note": "capex"}]},
            {"id": "INV-44888", "recommendation": "Reject", "tone": "bad", "confidence": 41, "why": "98% duplicate of paid invoice", "sources": [{"type": "Invoice", "ref": "INV-44602", "note": "paid May 9"}]},
        ],
        "performance": {"autoActionRate": "82%", "overrideRate": "4.6%", "avgConfidence": "91%", "savedPerItem": "3.2h"},
        "thresholdDesc": "Confidence to auto-approve a 3-way match without review.",
        "alwaysEscalateAbove": "$20,000", "tolerances": "price ±5%, qty 0%",
    },
    {
        "id": "cash-application", "name": "Cash Application Agent", "abbr": "CA",
        "subtitle": "deposit → invoice", "mode": "auto", "modeLabel": "≥90", "status": "ok",
        "threshold": 90, "confidence": 93, "crossLinkedTo": None, "lastActionAgo": "6 min ago",
        "pipeline": [
            {"key": "intake", "label": "Intake", "value": "318", "sub": "deposits received"},
            {"key": "match", "label": "Match", "value": "312", "sub": "exact + remittance"},
            {"key": "decide", "label": "Decide", "value": "312 / 6", "sub": "matched / fuzzy"},
            {"key": "act", "label": "Act", "value": "312", "sub": "auto-applied", "tone": "act"},
            {"key": "escalate", "label": "Escalate", "value": "6", "sub": "to Cash App screen", "tone": "esc"},
        ],
        "decisions": [
            {"id": "DEP-90412", "recommendation": "Apply", "tone": "ok", "confidence": 97, "why": "Remittance matched 14 open invoices", "sources": [{"type": "Invoice", "ref": "R-2241", "note": "remittance"}]},
            {"id": "DEP-90421", "recommendation": "Review", "tone": "warn", "confidence": 64, "why": "Lockbox — 5 candidate invoices", "sources": [{"type": "Invoice", "ref": "Lockbox-2241", "note": "partial"}]},
            {"id": "DEP-90440", "recommendation": "Hold", "tone": "bad", "confidence": 31, "why": "Unidentified ACH, no match", "sources": [{"type": "Invoice", "ref": "—", "note": "unmatched"}]},
        ],
        "performance": {"autoActionRate": "94%", "overrideRate": "2.1%", "avgConfidence": "93%", "savedPerItem": "1.8h"},
        "thresholdDesc": "Confidence to auto-apply a deposit to open invoices.",
        "alwaysEscalateAbove": "$250,000", "tolerances": "amount ±$0.01",
    },
    {
        "id": "anomaly", "name": "Anomaly Detection Agent", "abbr": "AN",
        "subtitle": "fraud · duplicate · leakage", "mode": "flag", "modeLabel": "flag", "status": "bad",
        "threshold": None, "confidence": 41, "crossLinkedTo": "anomalies", "lastActionAgo": "2 min ago",
        "pipeline": [
            {"key": "intake", "label": "Scan", "value": "4,120", "sub": "transactions/day"},
            {"key": "match", "label": "Model", "value": "12", "sub": "patterns evaluated"},
            {"key": "decide", "label": "Score", "value": "5", "sub": "above sensitivity"},
            {"key": "act", "label": "Flag", "value": "5", "sub": "raised for review", "tone": "esc"},
            {"key": "escalate", "label": "Recover", "value": "$1.3M", "sub": "leakage MTD", "tone": "act"},
        ],
        "decisions": [
            {"id": "INV-44888", "recommendation": "Duplicate", "tone": "bad", "confidence": 41, "why": "Cluster of 3 near-identical invoices", "sources": [{"type": "Invoice", "ref": "INV-44602", "note": "prior"}]},
            {"id": "DEN-Lot-A", "recommendation": "Abuse", "tone": "bad", "confidence": 38, "why": "218 validations vs ~40 baseline", "sources": [{"type": "Policy", "ref": "VAL-09", "note": "merchant code"}]},
            {"id": "SFO-T2", "recommendation": "Capture fault", "tone": "warn", "confidence": 55, "why": "Charge failures up 3.4× — LPR camera", "sources": [{"type": "Policy", "ref": "LANE-4", "note": "exit lane"}]},
        ],
        "performance": {"autoActionRate": "—", "overrideRate": "1.2%", "avgConfidence": "—", "savedPerItem": "$1.3M"},
        "thresholdDesc": "Flag sensitivity — anomalies always escalate; never auto-acts.",
        "alwaysEscalateAbove": None, "tolerances": None,
    },
    {
        "id": "collections", "name": "Collections Agent", "abbr": "CO",
        "subtitle": "outreach · drafts", "mode": "auto", "modeLabel": "≥80", "status": "ok",
        "threshold": 80, "confidence": 84, "crossLinkedTo": None, "lastActionAgo": "14 min ago",
        "pipeline": [
            {"key": "intake", "label": "Aging", "value": "212", "sub": "overdue accounts"},
            {"key": "match", "label": "Risk score", "value": "212", "sub": "ranked by risk"},
            {"key": "decide", "label": "Draft", "value": "38 / 4", "sub": "drafted / hold"},
            {"key": "act", "label": "Send", "value": "38", "sub": "reminders sent", "tone": "act"},
            {"key": "escalate", "label": "Escalate", "value": "4", "sub": "need your send", "tone": "esc"},
        ],
        "decisions": [
            {"id": "Lattice Logistics", "recommendation": "Payment plan", "tone": "warn", "confidence": 84, "why": "62 days, risk 84 — offer plan", "sources": [{"type": "Policy", "ref": "COL-04", "note": "plan"}]},
            {"id": "Cobalt Retail", "recommendation": "Reminder", "tone": "ok", "confidence": 81, "why": "47 days — 2nd reminder", "sources": [{"type": "Policy", "ref": "COL-02", "note": "cadence"}]},
        ],
        "performance": {"autoActionRate": "78%", "overrideRate": "6.0%", "avgConfidence": "82%", "savedPerItem": "0.6h"},
        "thresholdDesc": "Confidence to auto-send standard collection outreach.",
        "alwaysEscalateAbove": "$50,000", "tolerances": None,
    },
    {
        "id": "payment-run", "name": "Payment Run Agent", "abbr": "PA",
        "subtitle": "scheduling", "mode": "auto", "modeLabel": "≥95", "status": "ok",
        "threshold": 95, "confidence": 99, "crossLinkedTo": None, "lastActionAgo": "1 hr ago",
        "pipeline": [
            {"key": "intake", "label": "Approved", "value": "214", "sub": "invoices ready"},
            {"key": "match", "label": "Terms", "value": "214", "sub": "discount/aging"},
            {"key": "decide", "label": "Batch", "value": "214", "sub": "Friday run"},
            {"key": "act", "label": "Schedule", "value": "$1.94M", "sub": "scheduled", "tone": "act"},
            {"key": "escalate", "label": "Hold", "value": "0", "sub": "none", "tone": "esc"},
        ],
        "decisions": [
            {"id": "PB-0528", "recommendation": "Schedule", "tone": "ok", "confidence": 99, "why": "214 approved payments batched", "sources": [{"type": "Policy", "ref": "PAY-01", "note": "run"}]},
        ],
        "performance": {"autoActionRate": "99%", "overrideRate": "0.3%", "avgConfidence": "99%", "savedPerItem": "2.0h"},
        "thresholdDesc": "Confidence to schedule a payment batch without review.",
        "alwaysEscalateAbove": "$1,000,000", "tolerances": None,
    },
    {
        "id": "invoice-ingestion", "name": "Invoice Ingestion Agent", "abbr": "IN",
        "subtitle": "email · OCR", "mode": "auto", "modeLabel": "≥88", "status": "ok",
        "threshold": 88, "confidence": 93, "crossLinkedTo": None, "lastActionAgo": "31 min ago",
        "pipeline": [
            {"key": "intake", "label": "Inbox", "value": "41", "sub": "documents"},
            {"key": "match", "label": "OCR", "value": "41", "sub": "fields extracted"},
            {"key": "decide", "label": "Validate", "value": "41 / 0", "sub": "clean / unclear"},
            {"key": "act", "label": "Post", "value": "41", "sub": "to AP queue", "tone": "act"},
            {"key": "escalate", "label": "Escalate", "value": "0", "sub": "none", "tone": "esc"},
        ],
        "decisions": [
            {"id": "OCR-1190", "recommendation": "Extract", "tone": "ok", "confidence": 93, "why": "41 invoices parsed, fields validated", "sources": [{"type": "Policy", "ref": "OCR-v4", "note": "model"}]},
        ],
        "performance": {"autoActionRate": "97%", "overrideRate": "1.0%", "avgConfidence": "93%", "savedPerItem": "0.4h"},
        "thresholdDesc": "Field-extraction confidence to post without review.",
        "alwaysEscalateAbove": None, "tolerances": None,
    },
    {
        "id": "revenue-classification", "name": "Revenue Classification Agent", "abbr": "RC",
        "subtitle": "ASC 606", "mode": "auto", "modeLabel": "≥88", "status": "ok",
        "threshold": 88, "confidence": 95, "crossLinkedTo": None, "lastActionAgo": "15 min ago",
        "pipeline": [
            {"key": "intake", "label": "Lines", "value": "62", "sub": "revenue lines"},
            {"key": "match", "label": "Rules", "value": "62", "sub": "RC-606-v4"},
            {"key": "decide", "label": "Classify", "value": "62 / 0", "sub": "clean / exception"},
            {"key": "act", "label": "Post", "value": "62", "sub": "classified", "tone": "act"},
            {"key": "escalate", "label": "Escalate", "value": "0", "sub": "none", "tone": "esc"},
        ],
        "decisions": [
            {"id": "RC-606", "recommendation": "Classify", "tone": "ok", "confidence": 95, "why": "62 lines under ASC 606, no exceptions", "sources": [{"type": "Policy", "ref": "RC-606-v4", "note": "ruleset"}]},
        ],
        "performance": {"autoActionRate": "96%", "overrideRate": "2.4%", "avgConfidence": "95%", "savedPerItem": "0.5h"},
        "thresholdDesc": "Confidence to auto-classify revenue under ASC 606.",
        "alwaysEscalateAbove": None, "tolerances": None,
    },
    {
        "id": "cash-flow-forecast", "name": "Cash Flow Forecast Agent", "abbr": "CF",
        "subtitle": "advisory", "mode": "advisory", "modeLabel": "model", "status": "idle",
        "threshold": None, "confidence": 90, "crossLinkedTo": None, "lastActionAgo": "44 min ago",
        "pipeline": [
            {"key": "intake", "label": "Signals", "value": "30d", "sub": "AP + AR + bank"},
            {"key": "match", "label": "Model", "value": "CF-v7", "sub": "forecast"},
            {"key": "decide", "label": "Project", "value": "+$6.4M", "sub": "net inflow 30d"},
            {"key": "act", "label": "Publish", "value": "live", "sub": "to dashboard", "tone": "act"},
            {"key": "escalate", "label": "Alert", "value": "0", "sub": "no breach", "tone": "esc"},
        ],
        "decisions": [
            {"id": "CF-v7", "recommendation": "Forecast", "tone": "ok", "confidence": 90, "why": "30-day projection updated, +$6.4M net", "sources": [{"type": "Policy", "ref": "CF-v7", "note": "model"}]},
        ],
        "performance": {"autoActionRate": "—", "overrideRate": "—", "avgConfidence": "90%", "savedPerItem": "advisory"},
        "thresholdDesc": "Advisory only — surfaces forecasts, never moves money.",
        "alwaysEscalateAbove": None, "tolerances": None,
    },
]

_SUMMARY_KEYS = ["id", "name", "abbr", "subtitle", "mode", "modeLabel", "status", "threshold", "confidence", "crossLinkedTo"]


class AgentStore:
    def __init__(self) -> None:
        self._agents = copy.deepcopy(_AGENTS)
        self.suggest_only_mode = False  # global kill switch (mirrors API settings)

    def _apply_config(self, a: dict) -> dict:
        cfg = repo.get_agent_config(a["id"])
        if cfg:
            if cfg.get("threshold") is not None:
                a["threshold"] = cfg["threshold"]
            if cfg.get("mode"):
                a["mode"] = cfg["mode"]
            if a["mode"] in ("suggest", "auto") and a["threshold"] is not None:
                a["modeLabel"] = f"≥{a['threshold']}"
            if cfg.get("mode") in ("suggest", "auto"):
                a["status"] = "warn" if a["mode"] == "suggest" else "ok"
        return a

    def _summary(self, a: dict) -> dict:
        return {k: a[k] for k in _SUMMARY_KEYS}

    def list(self) -> dict:
        items = [self._summary(self._apply_config(dict(a))) for a in self._agents]
        return {"items": items, "stats": self.stats()}

    def stats(self) -> dict:
        suggest = sum(1 for a in self._agents if a["mode"] == "suggest")
        return {
            "activeAgents": len(self._agents),
            "suggestOnly": suggest,
            "autoActionsToday": "1,042",
            "escalatedToday": 47,
            "touchlessRate": 82,
            "avgConfidence": 91,
            "suggestOnlyMode": self.suggest_only_mode,
        }

    def get(self, agent_id: str) -> dict | None:
        for a in self._agents:
            if a["id"] == agent_id:
                return self._apply_config(copy.deepcopy(a))
        return None

    def patch(self, agent_id: str, threshold: int | None, mode: str | None) -> dict | None:
        for a in self._agents:
            if a["id"] == agent_id:
                changes = []
                if threshold is not None:
                    a["threshold"] = threshold
                    a["modeLabel"] = f"≥{threshold}" if a["mode"] in ("suggest", "auto") else a["modeLabel"]
                    changes.append(f"threshold→{threshold}%")
                if mode is not None:
                    a["mode"] = mode
                    a["status"] = "warn" if mode == "suggest" else "ok"
                    changes.append(f"mode→{mode}")
                if changes:
                    repo.set_agent_config(agent_id, a["threshold"] if a["mode"] in ("suggest", "auto") else None, a["mode"])
                    repo.record_audit({
                        "time": time.strftime("%H:%M:%S"),
                        "agent": a["name"], "action": "Config: " + ", ".join(changes),
                        "conf": a["confidence"], "outcome": "config", "src": "Agents console",
                        "by": "D. Okafor",
                    })
                    if mode == "auto":
                        repo.apply_auto_actions(agent_id, a["threshold"])
                return self._summary(a)
        return None


store = AgentStore()
