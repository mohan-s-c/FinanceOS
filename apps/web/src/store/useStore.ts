import { create } from 'zustand';
import { MOCK } from '../data/mock';
import type { Exception, FeedItem } from '../data/mock';
import type { ResolutionKind } from '@financeos/shared';
import { fetchExceptions, resolveExceptionApi, login } from '../api/client';

export type View = 'dashboard'|'exceptions'|'cash'|'collections'|'anomalies'|'audit'|'analytics'|'agents';
export type Theme = 'dark'|'light';
export type Density = 'compact'|'regular'|'comfy';

export interface Toast { id: number; title: string; sub: string; tone: string; }

interface AppState {
  view: View;
  collapsed: boolean;
  theme: Theme;
  density: Density;
  exceptions: Exception[];
  selectedEx: string | null;
  openCount: number;
  toasts: Toast[];
  feed: FeedItem[];
  loading: boolean;
  apiOnline: boolean;
  roleKey: 'analyst'|'controller';
  user: { name: string; initials: string; role: string };

  setView: (v: View) => void;
  toggleCollapsed: () => void;
  toggleTheme: () => void;
  setDensity: (d: Density) => void;
  openException: (id: string) => void;
  resolveException: (id: string, kind: string) => void;
  setSelectedEx: (id: string | null) => void;
  addToast: (title: string, sub: string, tone?: string) => void;
  prependFeedItem: (item: FeedItem) => void;
  loadExceptions: () => Promise<void>;
  loginAs: (username: string) => Promise<void>;
}

const RESOLVE_COPY: Record<string, [string, string]> = {
  approved: ["Approved", "logged to audit trail"],
  rejected: ["Rejected", "vendor notified · logged"],
  adjusted: ["Adjusted & approved", "delta posted · logged"],
  clarify: ["Clarification requested", "sent to vendor portal"],
  escalated: ["Escalated", "routed to Controller"],
};

export const useStore = create<AppState>((set, get) => ({
  view: 'dashboard',
  collapsed: false,
  theme: 'dark',
  density: 'regular',
  exceptions: [...MOCK.exceptions],
  selectedEx: null,
  openCount: 47,
  toasts: [],
  feed: [...MOCK.feed],
  loading: false,
  apiOnline: false,
  roleKey: 'analyst',
  user: { ...MOCK.user },

  setView: (v) => set({ view: v }),
  toggleCollapsed: () => set((s) => ({ collapsed: !s.collapsed })),

  toggleTheme: () => {
    const next = get().theme === 'dark' ? 'light' : 'dark';
    const root = document.documentElement;
    root.classList.add('theme-switching');
    root.setAttribute('data-theme', next);
    requestAnimationFrame(() => requestAnimationFrame(() => root.classList.remove('theme-switching')));
    set({ theme: next });
  },

  setDensity: (d) => {
    document.documentElement.setAttribute('data-density', d);
    set({ density: d });
  },

  openException: (id) => set({ view: 'exceptions', selectedEx: id }),

  // Load the exception queue from the API; falls back to bundled mock when offline.
  loadExceptions: async () => {
    set({ loading: true });
    const { list, offline } = await fetchExceptions();
    set({ exceptions: list.items, apiOnline: !offline, loading: false });
  },

  loginAs: async (username) => {
    const r = await login(username);
    if (r) set({
      roleKey: r.user.role === 'controller' ? 'controller' : 'analyst',
      user: { name: r.user.name, initials: r.user.initials, role: r.user.role === 'controller' ? 'Controller' : 'AP/AR Analyst' },
    });
  },

  resolveException: async (id, kind) => {
    const ex = get().exceptions.find((e) => e.id === id);
    // Confirm with the backend first so segregation-of-duties (Controller) is enforced.
    const res = await resolveExceptionApi(id, kind as ResolutionKind);
    if (res === 'forbidden') {
      get().addToast('Requires Controller', `${ex?.id ?? id} · ${ex?.amountStr ?? ''} needs Controller sign-off (≥ $20k)`, 'warn');
      return;
    }
    set((s) => ({ selectedEx: null, openCount: Math.max(0, s.openCount - 1) }));
    setTimeout(() => set((s) => ({ exceptions: s.exceptions.filter((e) => e.id !== id) })), 280);
    const [title, sub] = RESOLVE_COPY[kind] || ["Done", "logged"];
    get().addToast(`${title} · ${ex?.id ?? ''}`, `${ex?.amountStr ?? ''} · ${sub}`);
  },

  setSelectedEx: (id) => set({ selectedEx: id }),

  addToast: (title, sub, tone = 'ok') => {
    const id = Date.now() + Math.random();
    set((s) => ({ toasts: [...s.toasts, { id, title, sub, tone }] }));
    setTimeout(() => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })), 4200);
  },

  prependFeedItem: (item) => set((s) => ({ feed: [item, ...s.feed.map(x => ({ ...x, time: bumpTime(x.time) }))].slice(0, 9) })),
}));

function bumpTime(t: string): string {
  if (t === 'just now') return '1 min ago';
  const m = t.match(/^(\d+) min ago$/);
  if (m) return `${parseInt(m[1]) + 1} min ago`;
  return t;
}
