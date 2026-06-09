import React, { useState, useRef, useEffect } from 'react';
import { Icon } from '../components/Icon';
import { AgentBadge, StatusPill, confColor } from '../components';
import { MOCK } from '../data/mock';
import { fetchAudit } from '../api/client';

interface Props { toast: (title: string, sub: string, tone?: string) => void; }

export function Audit({ toast }: Props) {
  const M = MOCK;
  const [outcome, setOutcome] = useState('all');
  const [audit, setAudit] = useState(M.audit);
  useEffect(() => { (async () => setAudit(await fetchAudit()))(); }, []);
  const rows = audit.filter((r) => outcome === 'all' ? true : r.outcome === outcome);
  const [thresholds, setThresholds] = useState(M.thresholds.map((t) => t.value));

  return (
    <div className="page page-wide">
      <div className="grid" style={{ gridTemplateColumns: '1.55fr 1fr', alignItems: 'start' }}>
        {/* Audit log */}
        <div className="card" style={{ overflow: 'hidden' }}>
          <div className="card-h">
            <h3><Icon name="activity" /> Agent Decision Log</h3>
            <div className="hstack" style={{ gap: 4 }}>
              {([['all','All'],['auto','Auto'],['escalated','Escalated'],['overridden','Overridden']] as [string,string][]).map(([k, lbl]) => (
                <span key={k}
                  className={'tab' + (outcome === k ? ' active' : '')}
                  onClick={() => setOutcome(k)}
                  style={{ padding: '5px 10px', fontSize: 12, marginBottom: 0, borderBottom: 'none', borderRadius: 8, background: outcome === k ? 'var(--surface-3)' : 'transparent' }}>
                  {lbl}
                </span>
              ))}
            </div>
          </div>
          <div className="tbl-wrap">
            <table className="tbl">
              <thead><tr><th>Time</th><th>Agent</th><th>Action</th><th>Conf.</th><th>Outcome</th><th>Source</th></tr></thead>
              <tbody>
                {rows.map((r, i) => (
                  <tr key={i} style={{ cursor: 'default' }}>
                    <td><span className="mono" style={{ fontSize: 11.5 }}>{r.time}</span></td>
                    <td><AgentBadge agent={r.agent.replace(' Agent', '')} small /></td>
                    <td><span style={{ color: 'var(--tx-1)' }}>{r.action}</span>{r.by && <div className="t-sub">by {r.by}</div>}</td>
                    <td><span className="t-amt" style={{ color: confColor(r.conf) }}>{r.conf}%</span></td>
                    <td>
                      <StatusPill tone={r.outcome === 'auto' || r.outcome === 'human_resolved' ? 'ok' : r.outcome === 'escalated' ? 'warn' : 'agent'}>
                        {r.outcome === 'auto' ? 'Auto-executed' : r.outcome === 'escalated' ? 'Escalated' : r.outcome === 'human_resolved' ? 'Resolved' : r.outcome === 'config' ? 'Config' : 'Overridden'}
                      </StatusPill>
                    </td>
                    <td><span className="mono" style={{ fontSize: 11, color: 'var(--tx-3)' }}>{r.src}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="card-h" style={{ borderTop: '1px solid var(--line-1)', borderBottom: 'none', justifyContent: 'center' }}>
            <span className="audit-note"><Icon name="lock" size={13} /> Immutable SOX log · 7-year retention · exportable for audit</span>
          </div>
        </div>

        {/* Threshold controls */}
        <div className="card">
          <div className="card-h">
            <h3><Icon name="sliders" /> Confidence Thresholds</h3>
            <StatusPill tone="agent" dot={false}>Co-owned w/ Controller</StatusPill>
          </div>
          <div className="card-b">
            <p className="t-sub" style={{ marginBottom: 6, lineHeight: 1.5 }}>Above the threshold, the agent auto-executes. Below it, the item routes here for human review.</p>
            {M.thresholds.map((t, i) => (
              <ThreshSlider key={i} name={t.agent} desc={t.desc} value={thresholds[i]}
                onChange={(v) => setThresholds((arr) => arr.map((x, j) => j === i ? v : x))}
                onCommit={(v) => toast('Threshold updated', t.agent + ' auto-approve ≥ ' + v + '% · logged')} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function ThreshSlider({ name, desc, value, onChange, onCommit }: {
  name: string; desc: string; value: number;
  onChange: (v: number) => void; onCommit: (v: number) => void;
}) {
  const trackRef = useRef<HTMLDivElement>(null);
  const draggingRef = useRef(false);

  function setFromClientX(clientX: number) {
    const el = trackRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    let pct = Math.round(((clientX - rect.left) / rect.width) * 100);
    pct = Math.max(50, Math.min(99, pct));
    onChange(pct);
    return pct;
  }

  function down(e: React.MouseEvent | React.TouchEvent) {
    draggingRef.current = true;
    const clientX = 'touches' in e ? e.touches[0].clientX : (e as React.MouseEvent).clientX;
    setFromClientX(clientX);
    e.preventDefault();
  }

  useEffect(() => {
    function move(e: MouseEvent | TouchEvent) {
      if (!draggingRef.current) return;
      const clientX = 'touches' in e ? e.touches[0].clientX : (e as MouseEvent).clientX;
      setFromClientX(clientX);
    }
    function up() {
      if (draggingRef.current) { draggingRef.current = false; onCommit(value); }
    }
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
    window.addEventListener('touchmove', move as EventListener, { passive: false });
    window.addEventListener('touchend', up);
    return () => {
      window.removeEventListener('mousemove', move);
      window.removeEventListener('mouseup', up);
      window.removeEventListener('touchmove', move as EventListener);
      window.removeEventListener('touchend', up);
    };
  }, [value]);

  return (
    <div className="thresh">
      <div className="thresh-top">
        <div className="tl"><span className="thresh-name">{name}</span></div>
        <span className="thresh-val tnum">≥ {value}%</span>
      </div>
      <span className="t-sub" style={{ marginTop: -2 }}>{desc}</span>
      <div className="thresh-track" ref={trackRef} onMouseDown={down} onTouchStart={down}>
        <div className="thresh-rail"><i style={{ width: value + '%' }} /></div>
        <div className="thresh-knob" style={{ left: value + '%' }} />
      </div>
      <div className="thresh-zones"><span>Review ↤ 50</span><span>↦ auto-execute 99</span></div>
    </div>
  );
}
