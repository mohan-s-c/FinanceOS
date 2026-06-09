import { useEffect, useState } from 'react';
import { Icon } from '../components/Icon';
import { LineChart, BarChart } from '../components';
import { MOCK } from '../data/mock';
import type { AnalyticsResp } from '@financeos/shared';
import { fetchAnalytics } from '../api/client';

export function Analytics() {
  const M = MOCK;
  const [resp, setResp] = useState<AnalyticsResp | null>(null);
  useEffect(() => { (async () => setResp(await fetchAnalytics()))(); }, []);

  const A = resp?.analytics ?? M.analytics;
  const cards = resp?.cards ?? M.analyticsCards;
  const live = resp?.live;
  const [metric, setMetric] = useState<'touchless'|'cost'|'close'|'dso'>('touchless');

  const charts = {
    touchless: { label: 'Touchless Rate', data: A.touchlessTrend, color: 'var(--ok)', fmt: (v: number) => v.toFixed(0) + '%', fill: true },
    cost: { label: 'Cost per Invoice', data: A.costPerInvoice, color: 'var(--accent)', fmt: (v: number) => '$' + v.toFixed(2), fill: true },
    close: { label: 'Close Cycle Time', data: A.closeCycle, color: 'var(--agent)', fmt: (v: number) => v.toFixed(1) + 'd', fill: true },
    dso: { label: 'DSO', data: A.dso, color: 'var(--warn)', fmt: (v: number) => v.toFixed(0) + 'd', fill: true },
  };
  const c = charts[metric];

  return (
    <div className="page page-wide">
      {/* Live this session — computed from the persisted audit trail */}
      {live && (
        <div className="card">
          <div className="card-h">
            <h3><Icon name="activity" /> Live this session</h3>
            <span className="eyebrow">From the audit trail · agent decisions so far</span>
          </div>
          <div className="card-b grid" style={{ gridTemplateColumns: 'repeat(5,1fr)', gap: 14 }}>
            <LiveStat label="Decisions" value={String(live.decisions)} />
            <LiveStat label="Auto-actions" value={String(live.autoActions)} tone="ok" />
            <LiveStat label="Escalated" value={String(live.escalations)} tone="warn" />
            <LiveStat label="Touchless (session)" value={live.touchlessSession + '%'} tone="ok" />
            <LiveStat label="Open exceptions" value={String(live.openExceptions)} />
          </div>
        </div>
      )}

      {/* Scorecard */}
      <div className="grid" style={{ gridTemplateColumns: 'repeat(3,1fr)' }}>
        {cards.map((card, i) => (
          <div key={i} className="metric">
            <div className="m-top">
              <span className="m-lab">{card.label}</span>
              <span className={'m-delta ' + card.dir}><Icon name="arrowUp" size={12} />{card.delta}</span>
            </div>
            <div className="hstack" style={{ alignItems: 'baseline', gap: 10 }}>
              <span className="m-val tnum" style={{ fontSize: 32 }}>{card.value}</span>
              <span className="t-sub">{card.target}</span>
            </div>
            <div className="vstack" style={{ gap: 5, marginTop: 2 }}>
              <div className="conf-bar" style={{ width: '100%' }}>
                <i style={{ width: card.pct + '%', background: card.pct >= 90 ? 'var(--ok)' : 'var(--accent-grad)' }} />
              </div>
              <span className="t-sub">{card.pct}% to target</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid" style={{ gridTemplateColumns: '1.5fr 1fr' }}>
        <div className="card">
          <div className="card-h">
            <h3><Icon name="chart" /> Trend</h3>
            <div className="hstack" style={{ gap: 4 }}>
              {(Object.entries(charts) as [string, typeof c][]).map(([k, v]) => (
                <span key={k} className={'tab' + (metric === k ? ' active' : '')}
                  onClick={() => setMetric(k as any)}
                  style={{ padding: '5px 10px', fontSize: 12, marginBottom: 0, borderBottom: 'none', borderRadius: 8, background: metric === k ? 'var(--surface-3)' : 'transparent' }}>
                  {v.label}
                </span>
              ))}
            </div>
          </div>
          <div className="card-b">
            <div className="hstack" style={{ alignItems: 'baseline', gap: 10, marginBottom: 10 }}>
              <span style={{ fontWeight: 300, fontSize: 40, letterSpacing: '-.03em', color: 'var(--tx-1)' }} className="tnum">
                {c.fmt(c.data[c.data.length - 1])}
              </span>
              <span className="mono" style={{ color: c.color }}>{c.label} · trailing 12 mo</span>
            </div>
            <LineChart labels={A.months} yFmt={c.fmt} series={[{ data: c.data, color: c.color, fill: true }]} h={260} />
          </div>
        </div>

        <div className="card">
          <div className="card-h">
            <h3><Icon name="users" /> Human Override Rate</h3>
            <span className="eyebrow">Lower is better</span>
          </div>
          <div className="card-b">
            <div className="hstack" style={{ alignItems: 'baseline', gap: 10, marginBottom: 10 }}>
              <span style={{ fontWeight: 300, fontSize: 40, letterSpacing: '-.03em', color: 'var(--ok)' }} className="tnum">{A.overrideRate[A.overrideRate.length - 1].toFixed(1)}%</span>
              <span className="mono" style={{ color: 'var(--ok)' }}>−7.4 pts YoY</span>
            </div>
            <BarChart data={A.overrideRate} labels={A.months} yFmt={(v) => v.toFixed(0) + '%'} h={260}
              color={(v) => v > 8 ? 'var(--warn)' : 'var(--ok)'} />
            <p className="t-sub" style={{ marginTop: 10, lineHeight: 1.5 }}>As agents earn trust, humans override fewer decisions — the program's core trust signal.</p>
          </div>
        </div>
      </div>

      <div className="banner" style={{ background: 'var(--agent-dim)', borderColor: 'color-mix(in srgb,var(--agent) 24%,transparent)' }}>
        <Icon name="sparkle2" size={22} style={{ color: 'var(--agent-bright)' }} />
        <div className="bt">
          <h4>The human's job has shifted from data entry to governance</h4>
          <p>{live ? `This session the agents made ${live.autoActions} auto-actions and escalated ${live.escalations} to you. Promote an agent to auto to lift the touchless rate.` : '82% of invoices now process untouched. The team’s time goes to the 18% that need judgment — and to tuning the agents that handle the rest.'}</p>
        </div>
      </div>
    </div>
  );
}

function LiveStat({ label, value, tone }: { label: string; value: string; tone?: string }) {
  const col = tone === 'ok' ? 'var(--ok)' : tone === 'warn' ? 'var(--warn)' : 'var(--tx-1)';
  return (
    <div className="vstack" style={{ gap: 3 }}>
      <span className="tnum" style={{ fontSize: 26, fontWeight: 300, color: col, lineHeight: 1 }}>{value}</span>
      <span className="m-lab">{label}</span>
    </div>
  );
}
