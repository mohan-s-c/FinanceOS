import { useState, useEffect, useRef } from 'react';
import { Icon } from '../components/Icon';
import { MetricCard, ConfidenceBar, AgentBadge, LineChart } from '../components';
import { MOCK } from '../data/mock';
import type { FeedItem } from '../data/mock';
import type { View } from '../store/useStore';
import type { AgentSummary, AgentFleetStats } from '@financeos/shared';
import { fetchAgents } from '../api/client';

interface Props {
  onNav: (v: View) => void;
  onOpenException: (id: string) => void;
  openCount: number;
}

function bumpTime(t: string): string {
  if (t === 'just now') return '1 min ago';
  const m = t.match(/^(\d+) min ago$/);
  if (m) return `${parseInt(m[1]) + 1} min ago`;
  return t;
}

export function Dashboard({ onNav, onOpenException, openCount }: Props) {
  const M = MOCK;
  const [feed, setFeed] = useState<FeedItem[]>(M.feed);
  const liveRef = useRef(0);

  useEffect(() => {
    const extras: FeedItem[] = [
      { id: 'x1', type:'ok', agent:'PO Matching Agent', action:'Auto-approved', html:"Auto-approved invoice <b class='t-mono'>#INV-44935</b> — match clean", amt:'$1,860', time:'just now', live:true },
      { id: 'x2', type:'ok', agent:'Cash Application Agent', action:'Matched', html:'Auto-applied lockbox deposit to <b>6 invoices</b>', amt:'$58,200', time:'just now', live:true },
      { id: 'x3', type:'agent', agent:'Vendor Inquiry Agent', action:'Replied', html:'Answered <b>4 vendor status inquiries</b> via portal', amt:null, time:'just now', live:true },
    ];
    const iv = setInterval(() => {
      const e = extras[liveRef.current % extras.length];
      liveRef.current++;
      setFeed((f) => [{ ...e, id: 'live' + Date.now(), time: 'just now' }, ...f.map(x => ({ ...x, time: bumpTime(x.time) }))].slice(0, 9));
    }, 7000);
    return () => clearInterval(iv);
  }, []);

  return (
    <div className="page page-wide">
      {/* Metric row */}
      <div className="grid" style={{ gridTemplateColumns: 'repeat(5,1fr)' }}>
        {M.metrics.map((m) => (
          <MetricCard key={m.id} m={m.id === 'exceptions' ? { ...m, value: String(openCount) } : m} />
        ))}
      </div>

      <AgentsStrip onNav={onNav} />

      {/* AP / AR health + forecast */}
      <div className="grid" style={{ gridTemplateColumns: '1fr 1fr 1.25fr' }}>
        <HealthPanel side="AP" />
        <HealthPanel side="AR" />
        <div className="card">
          <div className="card-h">
            <h3><Icon name="trending" /> Cash Flow Forecast</h3>
            <span className="eyebrow">Next 30 days</span>
          </div>
          <div className="card-b">
            <div className="legend" style={{ marginBottom: 6 }}>
              <span className="lg line"><i style={{ background: 'var(--ok)' }} /> AR inflow</span>
              <span className="lg line"><i style={{ background: 'var(--accent)' }} /> AP outflow</span>
              <span className="lg" style={{ marginLeft: 'auto', color: 'var(--ok)' }}>Net +$6.4M</span>
            </div>
            <LineChart
              labels={M.forecast.labels}
              yFmt={(v) => '$' + v.toFixed(0) + 'M'}
              series={[
                { data: M.forecast.inflow, color: 'var(--ok)', fill: true },
                { data: M.forecast.outflow, color: 'var(--accent)', dashed: true },
              ]}
              h={210}
            />
          </div>
        </div>
      </div>

      {/* Feed + exceptions */}
      <div className="grid" style={{ gridTemplateColumns: '1.15fr 1fr' }}>
        <div className="card">
          <div className="card-h">
            <h3><Icon name="activity" /> Agent Activity</h3>
            <span className="hstack" style={{ gap: 7 }}>
              <span className="live-dot" />
              <span className="eyebrow" style={{ color: 'var(--ok)' }}>Live</span>
            </span>
          </div>
          <div className="card-b" style={{ paddingTop: 4, paddingBottom: 4 }}>
            <div className="feed">
              {feed.map((f) => <FeedItemRow key={f.id} f={f} />)}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-h">
            <h3><Icon name="alert" /> Exceptions Requiring Attention</h3>
            <span className="card-link" onClick={() => onNav('exceptions')}>
              View queue <Icon name="arrowR" size={13} />
            </span>
          </div>
          <div className="tbl-wrap">
            <table className="tbl">
              <thead>
                <tr><th>Invoice</th><th>Vendor</th><th className="num">Amount</th><th>Confidence</th><th></th></tr>
              </thead>
              <tbody>
                {M.exceptions.slice(0, 5).map((e) => (
                  <tr key={e.id} onClick={() => onOpenException(e.id)}>
                    <td><span className="t-mono">{e.id}</span><div className="t-sub">{e.reason}</div></td>
                    <td className="t-strong">{e.vendor}</td>
                    <td className="num t-amt">{e.amountStr}</td>
                    <td><ConfidenceBar value={e.confidence} width={56} /></td>
                    <td className="num">
                      <button className="btn btn-quiet btn-sm" onClick={(ev) => { ev.stopPropagation(); onOpenException(e.id); }}>Review</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

function AgentsStrip({ onNav }: { onNav: (v: View) => void }) {
  const [items, setItems] = useState<AgentSummary[]>([]);
  const [stats, setStats] = useState<AgentFleetStats | null>(null);
  useEffect(() => { (async () => { const { list } = await fetchAgents(); setItems(list.items); setStats(list.stats); })(); }, []);
  if (!items.length) return null;
  return (
    <div className="card">
      <div className="card-h">
        <h3><Icon name="sparkle2" /> Agents at work</h3>
        <span className="hstack" style={{ gap: 8 }}>
          <span className="live-dot" /><span className="eyebrow" style={{ color: 'var(--ok)' }}>Live</span>
          <span className="card-link" style={{ marginLeft: 8 }} onClick={() => onNav('agents')}>Open console <Icon name="arrowR" size={13} /></span>
        </span>
      </div>
      <div className="card-b" style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', flex: 1 }}>
          {items.map((a) => (
            <span key={a.id} onClick={() => onNav('agents')}
              style={{ display:'inline-flex', alignItems:'center', gap:7, fontSize:12, padding:'6px 11px', borderRadius:8, background:'var(--surface-2)', border:'1px solid var(--line-1)', cursor:'pointer' }}>
              <span className={'dotx ' + a.status} />{a.name.replace(' Agent','')}
              <span className="mono" style={{ fontSize:9.5, color:'var(--tx-3)' }}>{a.modeLabel}</span>
            </span>
          ))}
        </div>
        {stats && (
          <div className="vstack" style={{ gap: 6, minWidth: 160 }}>
            <div className="spread"><span className="m-foot">Touchless today</span><span className="mono" style={{ color:'var(--ok)' }}>{stats.touchlessRate}%</span></div>
            <div className="conf-bar" style={{ width:'100%' }}><i style={{ width: stats.touchlessRate + '%', background:'var(--ok)' }} /></div>
            <span className="t-sub">{stats.autoActionsToday} auto-actions · {stats.escalatedToday} escalated</span>
          </div>
        )}
      </div>
    </div>
  );
}

function HealthPanel({ side }: { side: 'AP' | 'AR' }) {
  const M = MOCK;
  const isAP = side === 'AP';
  const ap = M.apHealth;
  const ar = M.arHealth;
  return (
    <div className="card">
      <div className="card-h">
        <h3><Icon name={isAP ? 'inbox' : 'coins'} /> {isAP ? 'Accounts Payable' : 'Accounts Receivable'}</h3>
        <span className="eyebrow">Today</span>
      </div>
      <div className="card-b" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {isAP ? (
          <>
            <Stat big label="Invoices processed" value={ap.processedToday} />
            <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <Stat label="Auto-approved" value={ap.autoApproved} tone="ok" />
              <Stat label="In review" value={ap.inReview} tone="warn" />
            </div>
            <div className="vstack" style={{ gap: 7 }}>
              <div className="spread"><span className="m-foot">Touchless</span><span className="mono" style={{ color: 'var(--ok)' }}>{ap.touchless}%</span></div>
              <div className="conf-bar" style={{ width: '100%' }}><i style={{ width: ap.touchless + '%', background: 'var(--ok)' }} /></div>
              <span className="t-sub">Avg processing time {ap.avgTime}</span>
            </div>
          </>
        ) : (
          <>
            <Stat big label="Payments applied" value={ar.paymentsApplied} />
            <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <Stat label="Auto-applied" value={ar.autoApplied + '%'} tone="ok" />
              <Stat label="Overdue accounts" value={ar.overdue} tone="warn" />
            </div>
            <div className="vstack" style={{ gap: 7 }}>
              <div className="spread"><span className="m-foot">Cash applied automatically</span><span className="mono" style={{ color: 'var(--ok)' }}>{ar.autoApplied}%</span></div>
              <div className="conf-bar" style={{ width: '100%' }}><i style={{ width: Number(ar.autoApplied) + '%', background: 'var(--ok)' }} /></div>
              <span className="t-sub">DSO {ar.dso} days</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function Stat({ label, value, tone, big }: { label: string; value: string; tone?: string; big?: boolean }) {
  const col = tone === 'ok' ? 'var(--ok)' : tone === 'warn' ? 'var(--warn)' : 'var(--tx-1)';
  return (
    <div className="vstack" style={{ gap: 3 }}>
      <span style={{ fontWeight: 300, fontSize: big ? 38 : 26, letterSpacing: '-.03em', color: col, lineHeight: 1 }} className="tnum">{value}</span>
      <span className="m-lab">{label}</span>
    </div>
  );
}

function FeedItemRow({ f }: { f: FeedItem }) {
  const icon = f.type === 'ok' ? 'checkCircle' : f.type === 'bad' ? 'alert' : f.type === 'warn' ? 'arrowUp' : 'sparkle';
  return (
    <div className="feed-item">
      <div className={'feed-ico fi-' + f.type}><Icon name={icon} size={15} /></div>
      <div className="feed-body">
        <p dangerouslySetInnerHTML={{ __html: f.html + (f.amt ? ` <span class='amt'>${f.amt}</span>` : '') }} />
        <div className="feed-meta">
          <AgentBadge agent={f.agent} small icon="sparkle" />
          <span className="feed-time">{f.time}</span>
        </div>
      </div>
    </div>
  );
}
