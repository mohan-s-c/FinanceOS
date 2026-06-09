"""Pydantic models mirroring packages/shared (the TS domain schema).

Kept in sync by hand for Phase 0; field names match the TS interfaces exactly so the
JSON the front-end receives is identical to V1's mock shapes (mechanical migration).
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel

ResolutionKind = Literal["approved", "rejected", "adjusted", "clarify", "escalated"]


class LineItem(BaseModel):
    desc: str
    qty: float
    unit: str
    total: str
    flag: bool


class MatchCell(BaseModel):
    rate: str
    label: str
    mismatch: Optional[bool] = None


class Match(BaseModel):
    po: MatchCell
    gr: MatchCell
    inv: MatchCell


class Source(BaseModel):
    type: str
    ref: str
    note: str


class Exception(BaseModel):
    id: str
    vendor: str
    vinit: str
    amount: float
    amountStr: str
    location: str
    reason: str
    confidence: int
    tone: str
    agent: str
    status: str
    date: str
    po: str
    terms: str
    lineItems: list[LineItem]
    match: Match
    reasoning: str
    sources: list[Source]
    recommendation: Optional[str] = None


class AuditEntry(BaseModel):
    time: str
    agent: str
    action: str
    conf: int
    outcome: str
    src: str
    by: Optional[str] = None


class ExceptionList(BaseModel):
    items: list[Exception]
    openCount: int


class ResolveRequest(BaseModel):
    kind: ResolutionKind
    note: Optional[str] = None
    by: Optional[str] = None


class ResolveResponse(BaseModel):
    id: str
    kind: ResolutionKind
    openCount: int
    audit: AuditEntry


class Health(BaseModel):
    status: str
    suggestOnly: bool
    erp: str


# ---- Agent layer ----
AgentMode = Literal["suggest", "auto", "flag", "advisory"]
AgentStatus = Literal["ok", "warn", "bad", "idle"]


class PipelineStage(BaseModel):
    key: str
    label: str
    value: str
    sub: str
    tone: Optional[Literal["act", "esc"]] = None


class AgentDecision(BaseModel):
    id: str
    recommendation: str
    tone: str
    confidence: int
    why: str
    sources: list[Source]


class AgentPerformance(BaseModel):
    autoActionRate: str
    overrideRate: str
    avgConfidence: str
    savedPerItem: str


class AgentSummary(BaseModel):
    id: str
    name: str
    abbr: str
    subtitle: str
    mode: AgentMode
    modeLabel: str
    status: AgentStatus
    threshold: Optional[int] = None
    confidence: int
    crossLinkedTo: Optional[str] = None


class Agent(AgentSummary):
    lastActionAgo: str
    pipeline: list[PipelineStage]
    decisions: list[AgentDecision]
    performance: AgentPerformance
    thresholdDesc: str
    alwaysEscalateAbove: Optional[str] = None
    tolerances: Optional[str] = None


class AgentFleetStats(BaseModel):
    activeAgents: int
    suggestOnly: int
    autoActionsToday: str
    escalatedToday: int
    touchlessRate: int
    avgConfidence: int
    suggestOnlyMode: bool


class AgentListResp(BaseModel):
    items: list[AgentSummary]
    stats: AgentFleetStats


class AgentPatch(BaseModel):
    threshold: Optional[int] = None
    mode: Optional[AgentMode] = None


# ---- AR deposits / cash application ----
class SuggestedMatch(BaseModel):
    inv: str
    customer: str
    amount: str
    confidence: int


class Deposit(BaseModel):
    id: str
    amount: str
    payer: str
    invoices: str
    confidence: int
    status: str
    tone: str
    agent: bool


class DepositDetail(Deposit):
    customer: Optional[str] = None
    method: str
    recommendation: str
    reasoning: str
    suggestions: list[SuggestedMatch]


class DepositList(BaseModel):
    items: list[Deposit]
    unappliedTotal: str
    unappliedCount: int


class ApplyRequest(BaseModel):
    by: Optional[str] = None


class ApplyResponse(BaseModel):
    id: str
    unappliedCount: int
    audit: AuditEntry


# ---- AR collections ----
class Collection(BaseModel):
    id: str
    account: str
    loc: str
    balance: str
    days: int
    risk: int
    action: str
    agent: bool
    tone: str
    status: str


class CollectionDetail(Collection):
    recommendation: str
    draft: str


class CollectionList(BaseModel):
    items: list[Collection]
    atRisk: str
    dso: str


class SendResponse(BaseModel):
    id: str
    status: str
    audit: AuditEntry


# ---- Anomalies & Analytics ----
class Anomaly(BaseModel):
    id: int
    sev: str
    title: str
    sub: str
    risk: str
    agent: str
    icon: str


class AnomalyList(BaseModel):
    items: list[Anomaly]
    atRisk: str
    leakageRecovered: str
    leakageTrend: list[float]
    leakageMonths: list[str]
    highCount: int


class Analytics(BaseModel):
    touchlessTrend: list[float]
    costPerInvoice: list[float]
    closeCycle: list[float]
    dso: list[float]
    overrideRate: list[float]
    months: list[str]


class AnalyticsCard(BaseModel):
    label: str
    value: str
    target: str
    pct: int
    dir: str
    delta: str


class AnalyticsLive(BaseModel):
    decisions: int
    autoActions: int
    escalations: int
    touchlessSession: int
    overrideSession: float
    openExceptions: int
    unappliedTotal: str


class AnalyticsResp(BaseModel):
    analytics: Analytics
    cards: list[AnalyticsCard]
    live: AnalyticsLive


# ---- Auth / RBAC ----
class AuthUser(BaseModel):
    username: str
    name: str
    role: str
    initials: str


class LoginRequest(BaseModel):
    username: str


class LoginResponse(BaseModel):
    token: str
    user: AuthUser


class ExceptionExplanation(BaseModel):
    id: str
    narrative: str
    suggestedAction: str
    model: str
    grounded: list[Source]
