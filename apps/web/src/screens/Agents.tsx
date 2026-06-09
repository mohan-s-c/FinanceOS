import { Fragment, useEffect, useState } from 'react';
import { Icon } from '../components/Icon';
import { ConfidenceRing, SourceChip, StatusPill, confColor } from '../components';
import type { Agent, AgentSummary, AgentFleetStats, AgentMode } from '@financeos/shared';
import { fetchAgents, fetchAgent, patchAgent } from '../api/client';

interface Props { toast: (title: string, sub: string, tone?: string) => void; }

export function Agents({ toast }: Props) {
  const [items, setItems] = useState<AgentSummary[]>([]);
  const [stats, setStats] = useState<AgentFleetStats | null>(null);
  const [sel, setSel] = useState<string | null>(null);
  const [detail, setDetail] = useState<Agent | null>(null);
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    (async () => {
      const { list, offline } = await fetchAgents();
      setItems(list.items); setStats(list.stats); setOffline(offline);
      if (list.items.length) setSel(list.items[0].id);
    })();
  }, []);

  useEffect(() => {
    if (!sel) { setDetail(null); return; }
    (async () => setDetail(await fetchAgent(sel)))();
  }, [sel]);

  function mergeSummary(s: AgentSummary) {
    setItems((arr) => arr.map((a) => a.id === s.id ? { ...a, ...s } : a));
    setDetail((d) => d && d.id === s.id ? { ...d, ...s } : d);
  }

  async function changeMode(id: string, mode: AgentMode) {
    const updated = await patchAgent(id, { mode });
    if (updated) { mergeSummary(updated); toast('Mode updated', `${updated.name} → ${mode === 'auto' ? 'Auto' : 'Suggest-only'} · logged`); }
    else { toast('Requires Controller', 'Changing agent autonomy needs the Controller role', 'warn'); }
  }
  async function commitThreshold(id: string, threshold: number) {
    const updated = await patchAgent(id, { threshold });
    if (updated) { mergeSummary(updated); toast('Threshold updated', `${updated.name} auto-acts ≥ ${threshold}% · logged`); }
    else { toast('Requires Controller', 'Tuning thresholds needs the Controller role', 'warn'); }
  }

  return (
    <div className="page page-wide">
      <div className="phead">
        <div>
          <span className="eyebrow">Autonomy / Roster</span>
          <h2>Agents</h2>
          <p>Every agent, its mode and confidence threshold, and what it did today. Supervise by exception — promote an agent to auto only once it's earned trust.</p>
        </div>
        <StatusPill tone={stats?.suggestOnlyMode ? 'warn' : 'ok'} dot>
          {stats?.suggestOnlyMode ? 'Global suggest-only ON' : 'All systems nominal'}
        </StatusPill>
      </div>

      {offline && (
        <div className="banner warn"><Icon name="alert" size={18} /><div className="bt"><h4>Agents API unavailable</h4><p>Start the API (uvicorn) to load the live roster.</p></div></div>
      )}

      {stats && (
        <div className="grid" style={{ gridTemplateColumns: 'repeat(5,1fr)' }}>
          <Stat label="Active agents" value={stats.activeAgents} foot={`${stats.suggestOnly} suggest-only`} icon="sparkle2" />
          <Stat label="Auto-actions today" value={stats.autoActionsToday} foot="across all agents" icon="zap" />
          <Stat label="Escalated to you" value={stats.escalatedToday} foot="awaiting review" icon="inbox" tone="warn" />
          <Stat label="Touchless rate" value={stats.touchlessRate + '%'} foot="vs. last month" icon="gauge" tone="ok" />
          <Stat label="Avg confidence" value={stats.avgConfidence + '%'} foot="fleet-wide" icon="target" />
        </div>
      )}

      <div className="ag-split">
        {/* Roster */}
        <div className="card">
          <div className="card-h"><h3><Icon name="layers" /> Roster</h3><span className="t-sub">{items.length} agents</span></div>
          <div className="card-b ag-roster">
            {items.map((a) => (
              <div key={a.id} className={'ag-row' + (a.id === sel ? ' sel' : '')} onClick={() => setSel(a.id)}>
                <span className="ag-ico">{a.abbr}</span>
                <div style={{ minWidth: 0 }}>
                  <div className="ag-rn">{a.name.replace(' Agent', '')}</div>
                  <div className="ag-rs"><span className={'dotx ' + a.status} />{a.subtitle}{a.crossLinkedTo ? ' · also in Anomalies' : ''}</div>
                </div>
                <div className="ag-rr">
                  <span className={'ag-mode ' + (a.mode === 'auto' ? 'auto' : a.mode === 'suggest' ? 'sg' : '')}>{a.modeLabel}</span>
                  <ConfidenceRing value={a.confidence} size={34} stroke={3.5} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Detail */}
        {detail ? <Detail key={detail.id} a={detail} onMode={changeMode} onThreshold={commitThreshold} /> : (
          <div className="card"><div className="empty"><Icon name="sparkle2" size={34} /><div>Select an agent to see its pipeline and decisions.</div></div></div>
        )}
      </div>
    </div>
  );
}

function Stat({ label, value, foot, icon, tone }: { label: string; value: string | number; foot: string; icon: string; tone?: string }) {
  const col = tone === 'ok' ? 'var(--ok)' : tone === 'warn' ? 'var(--warn)' : 'var(--tx-1)';
  return (
    <div className="metric">
      <div className="m-top"><span className="m-lab">{label}</span><span className="m-ico"><Icon name={icon} size={15} /></span></div>
      <div className="m-val tnum" style={{ color: col, fontSize: 28 }}>{value}</div>
      <span className="m-foot">{foot}</span>
    </div>
  );
}

function Detail({ a, onMode, onThreshold }: { a: Agent; onMode: (id: string, m: AgentMode) => void; onThreshold: (id: string, v: number) => void }) {
  const [thr, setThr] = useState<number>(a.threshold ?? 0);
  useEffect(() => { setThr(a.threshold ?? 0); }, [a.id, a.threshold]);
  const togglable = a.mode === 'suggest' || a.mode === 'auto';

  return (
    <div className="vstack" style={{ gap: 'var(--gap)' }}>
      {/* header */}
      <div className="card"><div className="card-b ag-dethead">
        <span className="ag-ico" style={{ width: 38, height: 38 }}>{a.abbr}</span>
        <div>
          <div className="hstack" style={{ gap: 9 }}>
            <span style={{ fontSize: 17, fontWeight: 600, color: 'var(--tx-1)' }}>{a.name}</span>
            {a.crossLinkedTo && <StatusPill tone="agent" dot={false}>also in Anomalies</StatusPill>}
          </div>
          <span className="t-sub">{a.subtitle} · {a.mode === 'suggest' ? 'suggest-only' : a.mode} · last action {a.lastActionAgo}</span>
        </div>
        <div className="hstack" style={{ gap: 10, marginLeft: 'auto' }}>
          {togglable ? (
            <div className="ag-seg">
              <button className={a.mode === 'suggest' ? 'on' : ''} onClick={() => onMode(a.id, 'suggest')}>Suggest-only</button>
              <button className={a.mode === 'auto' ? 'on' : ''} onClick={() => onMode(a.id, 'auto')}>Auto</button>
            </div>
          ) : <StatusPill tone="neutral" dot={false}>{a.mode === 'flag' ? 'Flag-only' : 'Advisory'}</StatusPill>}
        </div>
      </div></div>

      {/* pipeline */}
      <div className="card"><div className="card-h"><h3><Icon name="activity" /> Pipeline — today</h3><span className="eyebrow">Intake → Match → Decide → Act → Audit</span></div>
        <div className="card-b"><div className="ag-pipe">
          {a.pipeline.map((s, i) => (
            <Fragment key={s.key}>
              <div className={'ag-step' + (s.tone ? ' ' + s.tone : '')}>
                <span className="ag-sl">{s.label}</span>
                <span className="ag-sv" style={{ color: s.tone === 'act' ? 'var(--ok)' : s.tone === 'esc' ? 'var(--warn)' : 'var(--tx-1)' }}>{s.value}</span>
                <span className="ag-ss">{s.sub}</span>
              </div>
              {i < a.pipeline.length - 1 && <span className="ag-arrow"><Icon name="chevR" size={15} /></span>}
            </Fragment>
          ))}
        </div></div>
      </div>

      {/* decisions + threshold/perf */}
      <div className="grid" style={{ gridTemplateColumns: '1.5fr 1fr', alignItems: 'start' }}>
        <div className="card" style={{ overflow: 'hidden' }}>
          <div className="card-h"><h3><Icon name="checkCircle" /> Recent decisions</h3><span className="eyebrow">reason + sources</span></div>
          <div className="tbl-wrap"><table className="tbl">
            <thead><tr><th>Item</th><th>Recommendation</th><th>Conf.</th><th>Why</th><th>Grounded in</th></tr></thead>
            <tbody>
              {a.decisions.map((d) => (
                <tr key={d.id} style={{ cursor: 'default' }}>
                  <td><span className="t-mono">{d.id}</span></td>
                  <td><StatusPill tone={d.tone}>{d.recommendation}</StatusPill></td>
                  <td><span className="t-amt" style={{ color: confColor(d.confidence) }}>{d.confidence}%</span></td>
                  <td style={{ maxWidth: 220, color: 'var(--tx-1)' }}>{d.why}</td>
                  <td>{d.sources.map((s, i) => <SourceChip key={i} type={s.type} refId={s.ref} note={s.note} />)}</td>
                </tr>
              ))}
            </tbody>
          </table></div>
        </div>

        <div className="vstack" style={{ gap: 'var(--gap)' }}>
          <div className="card"><div className="card-h"><h3><Icon name="sliders" /> Threshold</h3><span className="eyebrow">versioned</span></div>
            <div className="card-b">
              {a.threshold != null ? (
                <>
                  <div className="spread" style={{ marginBottom: 8 }}><span className="t-sub">Auto-act at</span><span className="thresh-val tnum">≥ {thr}%</span></div>
                  <input className="ag-range" type="range" min={50} max={99} value={thr}
                    onChange={(e) => setThr(parseInt(e.target.value))}
                    onMouseUp={() => onThreshold(a.id, thr)} onTouchEnd={() => onThreshold(a.id, thr)} />
                  <p className="t-sub" style={{ marginTop: 8, lineHeight: 1.5 }}>{a.thresholdDesc}</p>
                </>
              ) : <p className="t-sub" style={{ lineHeight: 1.5 }}>{a.thresholdDesc}</p>}
              {a.alwaysEscalateAbove && <div className="audit-note" style={{ marginTop: 12, color: 'var(--bad)' }}><Icon name="lock" size={13} /> Always escalate above {a.alwaysEscalateAbove}</div>}
              {a.tolerances && <div className="t-sub" style={{ marginTop: 8 }}>Tolerances — {a.tolerances}</div>}
            </div>
          </div>
          <div className="card"><div className="card-h"><h3><Icon name="chart" /> Performance</h3><span className="eyebrow">last 30 days</span></div>
            <div className="card-b ag-kpis">
              <div className="ag-kpi"><div className="l">Auto-action</div><div className="v" style={{ color: 'var(--ok)' }}>{a.performance.autoActionRate}</div></div>
              <div className="ag-kpi"><div className="l">Override</div><div className="v">{a.performance.overrideRate}</div></div>
              <div className="ag-kpi"><div className="l">Avg confidence</div><div className="v">{a.performance.avgConfidence}</div></div>
              <div className="ag-kpi"><div className="l">Saved / item</div><div className="v">{a.performance.savedPerItem}</div></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
