/* Typed API client for the Exception Queue.
 *
 * Mock seam: if the backend is unreachable (e.g. running the front-end alone), every
 * call falls back to the bundled MOCK data so the app stays demoable offline. The
 * `offline` flag lets the UI surface which mode it's in. */

import { MOCK } from "../data/mock";
import type { Exception, ResolutionKind, AuditEntry } from "@financeos/shared";
import type { Agent, AgentSummary, AgentFleetStats, AgentMode } from "@financeos/shared";
import type { Deposit, DepositDetail, DepositList, ApplyResponse } from "@financeos/shared";
import type { Collection, CollectionDetail, CollectionList, SendResponse } from "@financeos/shared";
import type { AnomalyList, AnalyticsResp } from "@financeos/shared";

const BASE: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://127.0.0.1:8000";

export interface ExceptionList {
  items: Exception[];
  openCount: number;
}
export interface ResolveResponse {
  id: string;
  kind: ResolutionKind;
  openCount: number;
  audit: AuditEntry;
}

let _token = "";
export function setAuthToken(t: string): void { _token = t; }

class HttpError extends Error {
  status: number;
  constructor(status: number, message: string) { super(message); this.status = status; }
}

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json", ...(init?.headers as Record<string, string> | undefined) };
  if (_token) headers["Authorization"] = `Bearer ${_token}`;
  const res = await fetch(BASE + path, { ...init, headers });
  if (!res.ok) throw new HttpError(res.status, `${res.status} ${res.statusText} for ${path}`);
  return (await res.json()) as T;
}

export interface AuthUser { username: string; name: string; role: string; initials: string; }

/** Sign in as a seeded user (dev). Sets the bearer token for subsequent calls. */
export async function login(username: string): Promise<{ token: string; user: AuthUser } | null> {
  try {
    const r = await http<{ token: string; user: AuthUser }>("/api/auth/login", { method: "POST", body: JSON.stringify({ username }) });
    setAuthToken(r.token);
    return r;
  } catch { return null; }
}

/** Load the open exception queue. Falls back to bundled mock data when offline. */
export async function fetchExceptions(): Promise<{ list: ExceptionList; offline: boolean }> {
  try {
    const list = await http<ExceptionList>("/api/exceptions");
    return { list, offline: false };
  } catch {
    const items = [...MOCK.exceptions];
    return { list: { items, openCount: items.length }, offline: true };
  }
}

/** Post a disposition. Returns the server response, or null when offline. */
export async function resolveExceptionApi(
  id: string,
  kind: ResolutionKind,
  by = "D. Okafor",
): Promise<ResolveResponse | "forbidden" | null> {
  try {
    return await http<ResolveResponse>(`/api/exceptions/${id}/resolve`, {
      method: "POST",
      body: JSON.stringify({ kind, by }),
    });
  } catch (e) {
    return (e as { status?: number })?.status === 403 ? "forbidden" : null;
  }
}


export interface AgentListResp { items: AgentSummary[]; stats: AgentFleetStats; }

/** Load the agent roster + fleet stats. Falls back to an empty/offline state. */
export async function fetchAgents(): Promise<{ list: AgentListResp; offline: boolean }> {
  try {
    const list = await http<AgentListResp>("/api/agents");
    return { list, offline: false };
  } catch {
    return {
      list: { items: [], stats: { activeAgents: 0, suggestOnly: 0, autoActionsToday: "0", escalatedToday: 0, touchlessRate: 0, avgConfidence: 0, suggestOnlyMode: false } },
      offline: true,
    };
  }
}

/** Full detail for one agent, or null when offline. */
export async function fetchAgent(id: string): Promise<Agent | null> {
  try { return await http<Agent>(`/api/agents/${id}`); } catch { return null; }
}

/** Update an agent's threshold and/or mode. Returns the updated summary, or null offline. */
export async function patchAgent(id: string, patch: { threshold?: number; mode?: AgentMode }): Promise<AgentSummary | null> {
  try { return await http<AgentSummary>(`/api/agents/${id}`, { method: "PATCH", body: JSON.stringify(patch) }); } catch { return null; }
}


/** AR deposits + unapplied summary. Falls back to bundled mock when offline. */
export async function fetchDeposits(): Promise<{ list: DepositList; offline: boolean }> {
  try {
    const list = await http<DepositList>("/api/deposits");
    return { list, offline: false };
  } catch {
    const items = [...MOCK.deposits] as unknown as Deposit[];
    return { list: { items, unappliedTotal: MOCK.unappliedTotal, unappliedCount: MOCK.unappliedCount }, offline: true };
  }
}

export async function fetchDeposit(id: string): Promise<DepositDetail | null> {
  try { return await http<DepositDetail>(`/api/deposits/${id}`); } catch { return null; }
}

export async function applyDeposit(id: string, by = "D. Okafor"): Promise<ApplyResponse | null> {
  try { return await http<ApplyResponse>(`/api/deposits/${id}/apply`, { method: "POST", body: JSON.stringify({ by }) }); } catch { return null; }
}


/** The persisted, append-only audit trail. Falls back to bundled mock offline. */
export async function fetchAudit(): Promise<AuditEntry[]> {
  try { return await http<AuditEntry[]>("/api/audit"); } catch { return [...MOCK.audit]; }
}


/** Risk-ranked overdue accounts. Falls back to bundled mock offline. */
export async function fetchCollections(): Promise<{ list: CollectionList; offline: boolean }> {
  try {
    const list = await http<CollectionList>("/api/collections");
    return { list, offline: false };
  } catch {
    const items = (MOCK.collections as unknown as (Collection & { id: string; status: string })[]);
    return { list: { items, atRisk: "—", dso: "28.4" }, offline: true };
  }
}

export async function fetchCollection(id: string): Promise<CollectionDetail | null> {
  try { return await http<CollectionDetail>(`/api/collections/${id}`); } catch { return null; }
}

export async function sendCollection(id: string, by = "D. Okafor"): Promise<SendResponse | null> {
  try { return await http<SendResponse>(`/api/collections/${id}/send`, { method: "POST", body: JSON.stringify({ by }) }); } catch { return null; }
}


export async function fetchAnomalies(): Promise<AnomalyList | null> {
  try { return await http<AnomalyList>("/api/anomalies"); } catch { return null; }
}

export async function fetchAnalytics(): Promise<AnalyticsResp | null> {
  try { return await http<AnalyticsResp>("/api/analytics"); } catch { return null; }
}
