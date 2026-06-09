import { useEffect, useState } from 'react';
import { Icon } from '../components/Icon';
import { AgentBadge, StatusPill, Donut } from '../components';
import { MOCK } from '../data/mock';
import type { Collection, CollectionDetail } from '@financeos/shared';
import { fetchCollections, fetchCollection, sendCollection } from '../api/client';

interface Props { toast: (title: string, sub: string, tone?: string) => void; }

type Col = Collection & { id: string; status: string };

export function Collections({ toast }: Props) {
  const M = MOCK;
  const [tab, setTab] = useState<'collections'|'settlement'>('collections');
  const [cols, setCols] = useState<Col[]>([]);
  const [summary, setSummary] = useState<{ atRisk: string; dso: string }>({ atRisk: '—', dso: '—' });
  const [sel, setSel] = useState<string | null>(null);
  const [detail, setDetail] = useState<CollectionDetail | null>(null);

  async function refresh() {
    const { list } = await fetchCollections();
    setCols(list.items as Col[]); setSummary({ atRisk: list.atRisk, dso: list.dso });
  }
  useEffect(() => { void refresh(); }, []);
  useEffect(() => {
    if (!sel) { setDetail(null); return; }
    (async () => setDetail(await fetchCollection(sel)))();
  }, [sel]);

  const selCol = cols.find((c) => c.id === sel) || null;
  const dist = [
    { label: 'High risk', value: cols.filter((c) => c.tone === 'bad').length, color: 'var(--bad)' },
    { label: 'Medium risk', value: cols.filter((c) => c.tone === 'warn').length, color: 'var(--warn)' },
    { label: 'Low risk', value: cols.filter((c) => c.tone === 'ok').length, color: 'var(--ok)' },
  ];

  async function doSend(id: string) {
    const r = await sendCollection(id);
    setSel(null);
    toast('Outreach sent', `${selCol?.account ?? id} · logged to audit trail`);
    if (r) await refresh();
  }

  return (
    <div style={{ position: 'relative', height: '100%', overflow: 'hidden' }}>
      <div className="canvas" style={{ position: 'absolute', inset: 0 }}>
        <div className="page page-wide">
          <div className="tabs">
            <div className={'tab' + (tab === 'collections' ? ' active' : '')} onClick={() => setTab('collections')}>
              <Icon name="phone" size={15} /> Collections <span className="tcount">{cols.length}</span>
            </div>
            <div className={'tab' + (tab === 'settlement' ? ' active' : '')} onClick={() => setTab('settlement')}>
              <Icon name="building" size={15} /> Owner Settlement <span className="tcount">{M.settlements.length}</span>
            </div>
          </div>

          {tab === 'collections' ? (
            <>
              <div className="banner warn">
                <Icon name="phone" size={22} />
                <div className="bt">
                  <h4>{summary.atRisk} across {cols.length} overdue accounts · DSO {summary.dso} days</h4>
                  <p>The Collections Agent risk-ranks accounts and drafts outreach. Review a draft and send it.</p>
                </div>
              </div>
              <div className="grid" style={{ gridTemplateColumns: '1.7fr 1fr' }}>
                <div className="card" style={{ overflow: 'hidden' }}>
                  <div className="card-h">
                    <h3><Icon name="phone" /> Overdue Accounts</h3>
                    <span className="eyebrow">Risk-ranked by Collections Agent</span>
                  </div>
                  <div className="tbl-wrap">
                    <table className="tbl">
                      <thead><tr><th>Account</th><th className="num">Balance</th><th className="num">Days</th><th>Risk</th><th>Agent action</th><th></th></tr></thead>
                      <tbody>
                        {cols.map((c) => (
                          <tr key={c.id} className={c.id === sel ? 'sel' : ''} onClick={() => setSel(c.id)} style={{ cursor: 'pointer' }}>
                            <td><span className="t-strong">{c.account}</span><div className="t-sub">{c.loc}</div></td>
                            <td className="num t-amt">{c.balance}</td>
                            <td className="num"><span style={{ color: c.days > 45 ? 'var(--bad)' : c.days > 30 ? 'var(--warn)' : 'var(--tx-2)' }} className="tnum">{c.days}d</span></td>
                            <td>
                              <div className="hstack" style={{ gap: 9 }}>
                                <div className="conf-bar" style={{ width: 52 }}>
                                  <i style={{ width: c.risk + '%', background: c.tone === 'bad' ? 'var(--bad)' : c.tone === 'warn' ? 'var(--warn)' : 'var(--ok)' }} />
                                </div>
                                <span className="mono tnum" style={{ color: c.tone === 'bad' ? 'var(--bad)' : c.tone === 'warn' ? 'var(--warn)' : 'var(--ok)', fontWeight: 600 }}>{c.risk}</span>
                              </div>
                            </td>
                            <td><AgentBadge agent={c.action} small icon="send" /></td>
                            <td className="num">{c.status === 'Sent' ? <StatusPill tone="ok">Sent</StatusPill> : <button className="btn btn-quiet btn-sm" onClick={(e) => { e.stopPropagation(); setSel(c.id); }}>Review</button>}</td>
                          </tr>
                        ))}
                        {cols.length === 0 && <tr><td colSpan={6}><div className="empty"><Icon name="phone" size={34} /><div>No overdue accounts — start the API to load the live queue.</div></div></td></tr>}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="card">
                  <div className="card-h"><h3><Icon name="gauge" /> Risk Distribution</h3></div>
                  <div className="card-b" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
                    <Donut data={dist} size={170} stroke={24} centerVal={cols.length} centerLab="ACCOUNTS" />
                    <div className="legend" style={{ flexDirection: 'column', gap: 12, width: '100%' }}>
                      {dist.map((d, i) => (
                        <div key={i} className="spread" style={{ width: '100%' }}>
                          <span className="lg"><i style={{ background: d.color }} /> {d.label}</span>
                          <span className="mono" style={{ color: 'var(--tx-1)' }}>{d.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="banner" style={{ background: 'var(--agent-dim)', borderColor: 'color-mix(in srgb,var(--agent) 26%,transparent)' }}>
                <Icon name="refresh" size={22} style={{ color: 'var(--agent-bright)' }} />
                <div className="bt">
                  <h4>Owner payouts moved from monthly to weekly</h4>
                  <p>The Owner Settlement Agent now calculates revenue-share weekly, cutting owner wait time from 30 days to 7.</p>
                </div>
                <AgentBadge agent="Owner Settlement Agent" icon="sparkle2" />
              </div>
              <div className="grid" style={{ gridTemplateColumns: 'repeat(3,1fr)' }}>
                <Mini label="This week's payouts" value="$1.25M" sub="31 owners" tone="flat" />
                <Mini label="Avg facility performance" value="+5.3%" sub="vs. prior week" tone="ok" />
                <Mini label="Settlement cadence" value="Weekly" sub="was monthly" tone="ok" />
              </div>
              <div className="card" style={{ overflow: 'hidden' }}>
                <div className="card-h"><h3><Icon name="building" /> Revenue-Share Owners</h3><span className="eyebrow">Week of May 25 – 31</span></div>
                <div className="tbl-wrap">
                  <table className="tbl">
                    <thead><tr><th>Owner</th><th>Portfolio</th><th className="num">Weekly payout</th><th>Performance</th><th>Status</th></tr></thead>
                    <tbody>
                      {M.settlements.map((s, i) => (
                        <tr key={i}>
                          <td className="t-strong">{s.owner}</td>
                          <td><span className="t-sub">{s.loc}</span></td>
                          <td className="num t-amt">{s.payout}</td>
                          <td><span className="mono tnum" style={{ color: s.perf.startsWith('−') ? 'var(--bad)' : 'var(--ok)' }}>{s.perf}</span></td>
                          <td><StatusPill tone={s.tone}>{s.status}</StatusPill></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      <div className={'drawer-scrim' + (selCol ? ' open' : '')} onClick={() => setSel(null)} />
      <div className={'drawer' + (selCol ? ' open' : '')}>
        {selCol && (
          <>
            <div className="drawer-h">
              <div className="vstack" style={{ gap: 6 }}>
                <span className="eyebrow">Overdue account · {selCol.loc}</span>
                <div className="hstack" style={{ gap: 10 }}>
                  <span style={{ fontSize: 19, fontWeight: 600, color: 'var(--tx-1)' }}>{selCol.account}</span>
                  <StatusPill tone={selCol.tone}>Risk {selCol.risk}</StatusPill>
                </div>
                <span className="t-sub">{selCol.balance} · {selCol.days} days past due</span>
              </div>
              <button className="x" onClick={() => setSel(null)}><Icon name="x" size={16} /></button>
            </div>
            <div className="drawer-b">
              <div className="reason">
                <div className="rh">
                  <AgentBadge agent="Collections Agent" />
                  <span className="eyebrow" style={{ color: 'var(--tx-3)' }}>Recommended: {selCol.action}</span>
                </div>
                <p className="rq">{detail ? detail.draft : 'Loading the agent’s drafted outreach…'}</p>
              </div>
              <div className="audit-note"><Icon name="lock" size={13} /> Sent outreach is logged to the SOX audit trail.</div>
            </div>
            <div className="drawer-f">
              {selCol.status === 'Sent' ? (
                <button className="btn btn-quiet btn-block" disabled><Icon name="check" size={15} /> Already sent</button>
              ) : (
                <button className="btn btn-grad btn-block" disabled={!detail} onClick={() => doSend(selCol.id)}>
                  <Icon name="send" size={15} /> Send outreach
                </button>
              )}
              <button className="btn btn-quiet btn-block" onClick={() => setSel(null)}>Close</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function Mini({ label, value, sub, tone }: { label: string; value: string; sub: string; tone: string }) {
  const col = tone === 'ok' ? 'var(--ok)' : tone === 'bad' ? 'var(--bad)' : 'var(--tx-1)';
  return (
    <div className="metric">
      <span className="m-lab">{label}</span>
      <span className="m-val tnum" style={{ color: col, fontSize: 30 }}>{value}</span>
      <span className="m-foot">{sub}</span>
    </div>
  );
}
