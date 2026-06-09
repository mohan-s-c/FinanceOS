import { useEffect, useState } from 'react';
import { Icon } from '../components/Icon';
import { ConfidenceRing, ConfidenceBar, AgentBadge, StatusPill } from '../components';
import type { Deposit, DepositDetail } from '@financeos/shared';
import { fetchDeposits, fetchDeposit, applyDeposit } from '../api/client';

interface Props { toast: (title: string, sub: string, tone?: string) => void; }

export function CashApplication({ toast }: Props) {
  const [deposits, setDeposits] = useState<Deposit[]>([]);
  const [unapplied, setUnapplied] = useState<{ total: string; count: number }>({ total: '—', count: 0 });
  const [sel, setSel] = useState<string | null>(null);
  const [detail, setDetail] = useState<DepositDetail | null>(null);

  async function refresh() {
    const { list } = await fetchDeposits();
    setDeposits(list.items);
    setUnapplied({ total: list.unappliedTotal, count: list.unappliedCount });
  }
  useEffect(() => { void refresh(); }, []);
  useEffect(() => {
    if (!sel) { setDetail(null); return; }
    (async () => setDetail(await fetchDeposit(sel)))();
  }, [sel]);

  const selDep = deposits.find((d) => d.id === sel) || null;
  const unmatched = deposits.filter((d) => d.tone === 'bad');

  async function doApply(id: string) {
    const r = await applyDeposit(id);
    setSel(null);
    toast('Cash applied', `${id} posted to the AR sub-ledger · logged`);
    if (r) await refresh();
  }

  return (
    <div style={{ position: 'relative', height: '100%', overflow: 'hidden' }}>
      <div className="canvas" style={{ position: 'absolute', inset: 0 }}>
        <div className="page page-wide">
          <div className="banner warn">
            <Icon name="wallet" size={22} />
            <div className="bt">
              <h4>{unapplied.total} in {unapplied.count} deposits awaiting application</h4>
              <p>The Cash Application Agent auto-applies high-confidence reconciliations. These need a human match.</p>
            </div>
          </div>

          <div className="grid" style={{ gridTemplateColumns: 'repeat(4,1fr)' }}>
            <Mini label="Cash applied today" value="$3.1M" sub="94% automatically" tone="ok" />
            <Mini label="Auto-match rate" value="94%" sub="+6 pts vs last month" tone="ok" />
            <Mini label="Awaiting review" value={String(unapplied.count)} sub="deposits" tone="flat" />
            <Mini label="Unmatched" value={String(unmatched.length)} sub="needs identification" tone="bad" />
          </div>

          <div className="card" style={{ overflow: 'hidden' }}>
            <div className="card-h">
              <h3><Icon name="coins" /> Matched Payments</h3>
              <span className="eyebrow">Agent-computed · click a row to review</span>
            </div>
            <div className="tbl-wrap">
              <table className="tbl">
                <thead>
                  <tr><th>Deposit</th><th>Source</th><th className="num">Amount</th><th>Matched to</th><th>Confidence</th><th>Status</th><th></th></tr>
                </thead>
                <tbody>
                  {deposits.map((d) => (
                    <tr key={d.id} className={d.id === sel ? 'sel' : ''}
                      onClick={() => d.status !== 'Auto-applied' && setSel(d.id)}
                      style={{ cursor: d.status === 'Auto-applied' ? 'default' : 'pointer' }}>
                      <td><span className="t-mono">{d.id}</span></td>
                      <td>{d.payer}</td>
                      <td className="num t-amt">{d.amount}</td>
                      <td>
                        {d.agent
                          ? <span className="hstack" style={{ gap: 8 }}>{d.invoices}<AgentBadge agent="Cash App Agent" small /></span>
                          : <span style={{ color: d.tone === 'bad' ? 'var(--bad)' : 'var(--warn)' }}>{d.invoices}</span>}
                      </td>
                      <td><ConfidenceBar value={d.confidence} width={56} /></td>
                      <td><StatusPill tone={d.tone}>{d.status}</StatusPill></td>
                      <td className="num">
                        {d.status !== 'Auto-applied' && (
                          <button className="btn btn-quiet btn-sm" onClick={(e) => { e.stopPropagation(); setSel(d.id); }}>Review</button>
                        )}
                      </td>
                    </tr>
                  ))}
                  {deposits.length === 0 && (
                    <tr><td colSpan={7}><div className="empty"><Icon name="coins" size={34} /><div>No deposits — start the API to load the live cash queue.</div></div></td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div className={'drawer-scrim' + (selDep ? ' open' : '')} onClick={() => setSel(null)} />
      <div className={'drawer' + (selDep ? ' open' : '')}>
        {selDep && (
          <>
            <div className="drawer-h">
              <div className="vstack" style={{ gap: 6 }}>
                <span className="eyebrow">Unapplied deposit</span>
                <div className="hstack" style={{ gap: 10 }}>
                  <span style={{ fontSize: 20, fontWeight: 600 }} className="t-mono">{selDep.id}</span>
                  <StatusPill tone={selDep.tone}>{selDep.status}</StatusPill>
                </div>
                <span className="t-sub">{selDep.payer} · received today</span>
              </div>
              <button className="x" onClick={() => setSel(null)}><Icon name="x" size={16} /></button>
            </div>
            <div className="drawer-b">
              <div className="reason">
                <div className="rh">
                  <ConfidenceRing value={selDep.confidence} size={52} stroke={5} />
                  <div className="vstack" style={{ gap: 4 }}>
                    <AgentBadge agent="Cash Application Agent" />
                    <span className="eyebrow" style={{ color: 'var(--tx-3)' }}>{detail ? detail.method + ' match' : 'Suggested matches'}</span>
                  </div>
                </div>
                <p className="rq">{detail ? detail.reasoning : 'Loading the agent’s reasoning…'}</p>
              </div>

              <div className="dsec">
                <span className="eyebrow">Candidate invoices</span>
                {(detail?.suggestions ?? []).map((s, i) => (
                  <div key={i} className="card" style={{ padding: '12px 14px' }}>
                    <div className="spread">
                      <div className="vstack" style={{ gap: 3 }}>
                        <span className="t-mono" style={{ color: 'var(--tx-1)' }}>{s.inv}</span>
                        <span className="t-sub">{s.customer}</span>
                      </div>
                      <div className="hstack" style={{ gap: 14 }}>
                        <span className="t-amt">{s.amount}</span>
                        <ConfidenceRing value={s.confidence} size={40} stroke={3.5} />
                        <input type="checkbox" defaultChecked style={{ width: 18, height: 18, accentColor: 'var(--accent)' }} />
                      </div>
                    </div>
                  </div>
                ))}
                {detail && detail.suggestions.length === 0 && (
                  <p className="t-sub">No candidate invoices reconcile — this deposit needs manual identification.</p>
                )}
              </div>
              <div className="audit-note"><Icon name="lock" size={13} /> Applied matches post to the AR sub-ledger and SOX audit trail.</div>
            </div>
            <div className="drawer-f">
              <button className="btn btn-grad btn-block" disabled={!detail || detail.suggestions.length === 0}
                onClick={() => doApply(selDep.id)}>
                <Icon name="check" size={15} /> Apply match
              </button>
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
