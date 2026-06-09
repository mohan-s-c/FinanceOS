import { useState } from 'react';
import { Icon } from '../components/Icon';
import { ConfidenceRing, AgentBadge, SourceChip, StatusPill } from '../components';
import type { Exception } from '../data/mock';

interface Props {
  rows: Exception[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  onResolve: (id: string, kind: string) => void;
  openCount: number;
}

export function Exceptions({ rows, selectedId, onSelect, onResolve, openCount }: Props) {
  const sel = rows.find((r) => r.id === selectedId) || null;
  const [filter, setFilter] = useState<'all'|'bad'|'warn'>('all');

  const filtered = rows.filter((r) => filter === 'all' ? true : r.tone === filter);
  const totalAmt = rows.reduce((a, r) => a + r.amount, 0);

  return (
    <div style={{ position: 'relative', height: '100%', overflow: 'hidden' }}>
      <div className="canvas" style={{ position: 'absolute', inset: 0 }}>
        <div className="page page-wide">
          {/* Summary strip */}
          <div className="grid" style={{ gridTemplateColumns: 'repeat(4,1fr)' }}>
            <MiniStat label="Open exceptions" value={openCount} icon="alert" />
            <MiniStat label="Total value at risk" value={'$' + totalAmt.toLocaleString()} icon="dollar" />
            <MiniStat label="Priority for review" value={rows.length} icon="gauge" />
            <MiniStat label="Oldest in queue" value="2 days" icon="clock" />
          </div>

          <div className="card" style={{ overflow: 'hidden' }}>
            <div className="card-h">
              <div className="tabs" style={{ border: 'none' }}>
                {([['all','All'],['bad','Critical'],['warn','Needs review']] as [string,string][]).map(([k, lbl]) => (
                  <div key={k} className={'tab' + (filter === k ? ' active' : '')}
                    onClick={() => setFilter(k as any)}
                    style={{ padding: '6px 12px', marginBottom: 0 }}>
                    {lbl}<span className="tcount">{k === 'all' ? rows.length : rows.filter(r => r.tone === k).length}</span>
                  </div>
                ))}
              </div>
              <div className="hstack" style={{ gap: 8 }}>
                <button className="btn btn-quiet btn-sm"><Icon name="filter" size={14} /> Filter</button>
                <button className="btn btn-quiet btn-sm"><Icon name="download" size={14} /> Export</button>
              </div>
            </div>
            <div className="tbl-wrap">
              <table className="tbl">
                <thead>
                  <tr>
                    <th>Invoice</th><th>Vendor</th><th className="num">Amount</th><th>Location</th>
                    <th>Flag reason</th><th>Confidence</th><th>Flagged by</th><th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((r) => (
                    <tr key={r.id} className={r.id === selectedId ? 'sel' : ''} onClick={() => onSelect(r.id)}>
                      <td><span className="t-mono">{r.id}</span><div className="t-sub">{r.date}</div></td>
                      <td>
                        <div className="t-vendor">
                          <span className="t-logo">{r.vinit}</span>
                          <span className="t-strong">{r.vendor}</span>
                        </div>
                      </td>
                      <td className="num t-amt">{r.amountStr}</td>
                      <td><span className="mono" style={{ fontSize: 11.5 }}>{r.location}</span></td>
                      <td style={{ maxWidth: 200 }}><span style={{ color: 'var(--tx-1)' }}>{r.reason}</span></td>
                      <td><ConfidenceRing value={r.confidence} size={38} stroke={3.5} /></td>
                      <td><AgentBadge agent={r.agent} small /></td>
                      <td><StatusPill tone={r.tone}>{r.status}</StatusPill></td>
                    </tr>
                  ))}
                  {filtered.length === 0 && (
                    <tr><td colSpan={8}>
                      <div className="empty">
                        <Icon name="checkCircle" size={34} />
                        <div><b style={{ color: 'var(--tx-1)' }}>Queue clear.</b><div style={{ marginTop: 4 }}>Every exception in this view has been resolved.</div></div>
                      </div>
                    </td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Drawer */}
      <div className={'drawer-scrim' + (sel ? ' open' : '')} onClick={() => onSelect(null)} />
      <ExceptionDrawer row={sel} onClose={() => onSelect(null)} onResolve={onResolve} />
    </div>
  );
}

function MiniStat({ label, value, icon }: { label: string; value: string|number; icon: string }) {
  return (
    <div className="metric" style={{ flexDirection: 'row', alignItems: 'center', gap: 14 }}>
      <span className="m-ico" style={{ height: 40, width: 40 }}><Icon name={icon} size={19} /></span>
      <div className="vstack" style={{ gap: 2 }}>
        <span className="m-val tnum" style={{ fontSize: 26 }}>{value}</span>
        <span className="m-lab">{label}</span>
      </div>
    </div>
  );
}

function ExceptionDrawer({ row, onClose, onResolve }: { row: Exception|null; onClose: () => void; onResolve: (id: string, kind: string) => void }) {
  if (!row) return <div className="drawer" />;
  const m = row.match;
  return (
    <div className="drawer open">
      <div className="drawer-h">
        <div className="vstack" style={{ gap: 6 }}>
          <span className="eyebrow">{row.location}</span>
          <div className="hstack" style={{ gap: 10 }}>
            <span style={{ fontSize: 20, fontWeight: 600, color: 'var(--tx-1)' }} className="t-mono">{row.id}</span>
            <StatusPill tone={row.tone}>{row.status}</StatusPill>
          </div>
          <span className="t-sub">{row.vendor} · {row.terms} · {row.date}</span>
        </div>
        <button className="x" onClick={onClose}><Icon name="x" size={16} /></button>
      </div>

      <div className="drawer-b">
        {/* Reasoning */}
        <div className="reason">
          <div className="rh">
            <ConfidenceRing value={row.confidence} size={52} stroke={5} />
            <div className="vstack" style={{ gap: 4 }}>
              <AgentBadge agent={row.agent} />
              <span className="eyebrow" style={{ color: 'var(--tx-3)' }}>Confidence assessment</span>
            </div>
          </div>
          <p className="rq">{row.reasoning}</p>
        </div>

        {row.recommendation && (() => {
          const map: Record<string, [string, string]> = {
            approve: ['approved', 'Approve'], reject: ['rejected', 'Reject'],
            escalate: ['escalated', 'Escalate'], hold: ['escalated', 'Hold for PO'],
            adjust: ['adjusted', 'Adjust & approve'],
          };
          const [kind, label] = map[row.recommendation] || ['escalated', 'Escalate'];
          return (
            <div className="dsec">
              <div className="spread"><span className="eyebrow">Agent recommendation</span><AgentBadge agent={row.agent} small icon="sparkle2" /></div>
              <div style={{ background: 'var(--agent-dim)', border: '1px solid var(--line-1)', borderRadius: 'var(--r-sm)', padding: '12px 14px', display: 'flex', alignItems: 'center', gap: 12, marginTop: 8 }}>
                <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--tx-1)' }}>Recommends: {label}</span>
                <button className="btn btn-grad btn-sm" style={{ marginLeft: 'auto' }} onClick={() => onResolve(row.id, kind)}><Icon name="check" size={14} /> Accept</button>
              </div>
              <span className="t-sub" style={{ display: 'block', marginTop: 6 }}>Or choose a different action below to override.</span>
            </div>
          );
        })()}

        {/* Extracted invoice data */}
        <div className="dsec">
          <div className="spread">
            <span className="eyebrow">Extracted invoice data</span>
            <AgentBadge agent="Invoice Ingestion Agent" small icon="sparkle2" />
          </div>
          <table className="li">
            <thead><tr><th>Line item</th><th className="num">Qty</th><th className="num">Unit</th><th className="num">Total</th></tr></thead>
            <tbody>
              {row.lineItems.map((li, i) => (
                <tr key={i}>
                  <td style={{ color: li.flag ? 'var(--bad)' : 'var(--tx-1)' }}>
                    {li.flag && <Icon name="alert" size={12} style={{ display: 'inline', verticalAlign: '-1px', marginRight: 5 }} />}
                    {li.desc}
                  </td>
                  <td className="num">{li.qty}</td>
                  <td className="num">{li.unit}</td>
                  <td className="num" style={{ color: 'var(--tx-1)', fontWeight: 600 }}>{li.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* 3-way match */}
        <div className="dsec">
          <span className="eyebrow">3-way match</span>
          <div className="match">
            <div className={'mc' + (m.po.mismatch ? ' mismatch' : '')}>
              <span className="mh">Purchase order</span>
              <span className="mv">{m.po.rate}</span>
              <span className="t-sub">{m.po.label}{row.po !== '—' ? ' · ' + row.po : ''}</span>
            </div>
            <div className={'mc' + (m.gr.mismatch ? ' mismatch' : '')}>
              <span className="mh">Goods receipt</span>
              <span className="mv">{m.gr.rate}</span>
              <span className="t-sub">{m.gr.label}</span>
            </div>
            <div className={'mc' + (m.inv.mismatch ? ' mismatch' : '')}>
              <span className="mh">Invoice</span>
              <span className="mv">{m.inv.rate}</span>
              <span className="t-sub">{m.inv.label}</span>
            </div>
          </div>
        </div>

        {/* RAG sources */}
        <div className="dsec">
          <span className="eyebrow">Grounded in</span>
          <div className="chips">
            {row.sources.map((s, i) => <SourceChip key={i} type={s.type} refId={s.ref} note={s.note} />)}
          </div>
        </div>

        <div className="audit-note"><Icon name="lock" size={13} /> All actions logged to the SOX audit trail.</div>
      </div>

      <div className="drawer-f">
        <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <button className="btn btn-ok" onClick={() => onResolve(row.id, 'approved')}><Icon name="check" size={15} /> Approve</button>
          <button className="btn btn-bad" onClick={() => onResolve(row.id, 'rejected')}><Icon name="x" size={15} /> Reject</button>
        </div>
        <div className="grid" style={{ gridTemplateColumns: '1fr 1fr 1fr', gap: 10 }}>
          <button className="btn btn-quiet btn-sm" onClick={() => onResolve(row.id, 'adjusted')}><Icon name="scale" size={14} /> Adjust</button>
          <button className="btn btn-quiet btn-sm" onClick={() => onResolve(row.id, 'clarify')}><Icon name="send" size={14} /> Clarify</button>
          <button className="btn btn-quiet btn-sm" onClick={() => onResolve(row.id, 'escalated')}><Icon name="arrowUp" size={14} /> Escalate</button>
        </div>
      </div>
    </div>
  );
}
