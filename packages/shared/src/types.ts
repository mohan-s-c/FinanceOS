/* Finance OS — shared domain types (V2).
 * Source of truth for the AP/AR domain model. The FastAPI service mirrors these
 * shapes with Pydantic models; keep the two in sync until codegen is introduced. */

export interface User { name: string; role: string; initials: string; }
export interface Metric { id: string; label: string; value: string; suffix?: string; delta: string; dir: "up"|"down"|"flat"; foot: string; tone: string; spark: number[]; icon: string; }
export interface APHealth { processedToday: string; autoApproved: string; inReview: string; avgTime: string; touchless: number; }
export interface ARHealth { paymentsApplied: string; autoApplied: string; overdue: string; dso: string; }
export interface FeedItem { id: string|number; type: string; agent: string; action: string; html: string; amt: string|null; time: string; live?: boolean; }
export interface LineItem { desc: string; qty: number; unit: string; total: string; flag: boolean; }
export interface MatchCell { rate: string; label: string; mismatch?: boolean; }
export interface Source { type: string; ref: string; note: string; }
export interface Exception {
  id: string; vendor: string; vinit: string; amount: number; amountStr: string;
  location: string; reason: string; confidence: number; tone: string;
  agent: string; status: string; date: string; po: string; terms: string;
  lineItems: LineItem[];
  match: { po: MatchCell; gr: MatchCell; inv: MatchCell; };
  reasoning: string;
  sources: Source[];
  recommendation?: string;
}
export interface Deposit { id: string; amount: string; payer: string; invoices: string; confidence: number; status: string; tone: string; agent: boolean; }
export interface SuggestedMatch { inv: string; customer: string; amount: string; confidence: number; }
export interface Collection { account: string; loc: string; balance: string; days: number; risk: number; action: string; agent: boolean; tone: string; id?: string; status?: string; }
export interface RiskDist { label: string; value: number; color: string; }
export interface Settlement { owner: string; loc: string; payout: string; perf: string; status: string; tone: string; }
export interface Anomaly { id: number; sev: string; title: string; sub: string; risk: string; agent: string; icon: string; }
export interface AuditEntry { time: string; agent: string; action: string; conf: number; outcome: string; src: string; by?: string; }
export interface Threshold { agent: string; value: number; desc: string; }
export interface Analytics {
  touchlessTrend: number[]; costPerInvoice: number[]; closeCycle: number[];
  dso: number[]; overrideRate: number[]; months: string[];
}
export interface AnalyticsCard { label: string; value: string; target: string; pct: number; dir: string; delta: string; }

/* ---- V2 additions: resolution semantics shared by web + api ---- */
export type ResolutionKind = "approved" | "rejected" | "adjusted" | "clarify" | "escalated";
export interface ResolveRequest { kind: ResolutionKind; note?: string; by?: string; }
export interface ResolveResponse { id: string; kind: ResolutionKind; openCount: number; audit: AuditEntry; }

/* ---- V2: Agent layer (Agents console) ---- */
export type AgentMode = "suggest" | "auto" | "flag" | "advisory";
export type AgentStatus = "ok" | "warn" | "bad" | "idle";
export interface PipelineStage { key: string; label: string; value: string; sub: string; tone?: "act" | "esc" | null; }
export interface AgentDecision { id: string; recommendation: string; tone: string; confidence: number; why: string; sources: Source[]; }
export interface AgentPerformance { autoActionRate: string; overrideRate: string; avgConfidence: string; savedPerItem: string; }
export interface AgentSummary {
  id: string; name: string; abbr: string; subtitle: string;
  mode: AgentMode; modeLabel: string; status: AgentStatus;
  threshold: number | null; confidence: number; crossLinkedTo?: string | null;
}
export interface Agent extends AgentSummary {
  lastActionAgo: string;
  pipeline: PipelineStage[];
  decisions: AgentDecision[];
  performance: AgentPerformance;
  thresholdDesc: string;
  alwaysEscalateAbove?: string | null;
  tolerances?: string | null;
}
export interface AgentFleetStats {
  activeAgents: number; suggestOnly: number; autoActionsToday: string;
  escalatedToday: number; touchlessRate: number; avgConfidence: number; suggestOnlyMode: boolean;
}
export interface AgentList { items: AgentSummary[]; stats: AgentFleetStats; }
export interface AgentPatch { threshold?: number; mode?: AgentMode; }

/* ---- V2 Phase 2: AR cash application detail ---- */
export interface DepositDetail extends Deposit {
  customer: string | null;
  method: string;
  recommendation: string;
  reasoning: string;
  suggestions: SuggestedMatch[];
}
export interface DepositList { items: Deposit[]; unappliedTotal: string; unappliedCount: number; }
export interface ApplyResponse { id: string; unappliedCount: number; audit: AuditEntry; }

/* ---- V2 Phase 3: Collections ---- */
export interface CollectionDetail extends Collection {
  id: string;
  status: string;
  recommendation: string;
  draft: string;
}
export interface CollectionList { items: (Collection & { id: string; status: string })[]; atRisk: string; dso: string; }
export interface SendResponse { id: string; status: string; audit: AuditEntry; }

/* ---- V2 Phase 3: Anomalies + Analytics read models ---- */
export interface AnomalyList {
  items: Anomaly[];
  atRisk: string;
  leakageRecovered: string;
  leakageTrend: number[];
  leakageMonths: string[];
  highCount: number;
}
export interface AnalyticsLive {
  decisions: number; autoActions: number; escalations: number;
  touchlessSession: number; overrideSession: number; openExceptions: number; unappliedTotal: string;
}
export interface AnalyticsResp { analytics: Analytics; cards: AnalyticsCard[]; live: AnalyticsLive; }

/* ---- LLM-assisted exception reasoning ---- */
export interface ExceptionExplanation {
  id: string;
  narrative: string;
  suggestedAction: string;
  model: string;
  grounded: Source[];
}
