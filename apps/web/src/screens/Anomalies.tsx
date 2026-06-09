import { useEffect, useState } from 'react';
import { Icon } from '../components/Icon';
import { AgentBadge, StatusPill, LineChart } from '../components';
import { MOCK } from '../data/mock';
import type { AnomalyList } from '@financeos/shared';
import { fetchAnomalies } from '../api/client';

interface Props { toast: (title: string, sub: string, tone?: string) => void; }

export function Anomalies({ toast }: Props) {
  const M = MOCK;
  const [data, setData] = useState<AnomalyList | null>(null);
  useEffect(() => { (async () => setData(await fetchAnomalies()))(); }, []);

  const items = data?.items ?? M.anomalies;
  const atRisk = data?.atRisk ?? ('$' + M.anomalies.reduce((a, x) => a + parseInt(String(x.risk).replace(/[$,]/g, '')), 0).toLocaleString());
  const recovered = data?.leakageRecovered ?? '$1.3M';
  const trend = data?.leakageTrend ?? M.leakageTrend;
  const months = data?.leakageMonths ?? M.leakageMonths;

  return (
    <div className="page page-wide">
      <div className="grid" style={{ gridTemplateColumns: '1fr 1fr 1fr' }}>
        <Mini label="Leakage recovered MTD" value={recovered} sub="+$0.4M this month" tone="ok" big />
        <Mini label="At risk · open signals" value={atRisk} sub={items.length + ' active anomalies'} tone="bad" />
        <Mini label="Detection precision" value="91%" sub="confirmed / flagged" tone="ok" />
      </div>

      <div className="grid" style={{ gridTemplateColumns: '1.45fr 1fr' }}>
        <div className="vstack" style={{ gap: 'var(--gap)' }}>
          {items.map((a) => (
            <div key={a.id} className={'alert sev-' + a.sev}>
              <div className="alert-top">
                <div className="alert-ico" style={{ color: a.sev === 'high' ? 'var(--bad)' : a.sev === 'med' ? 'var(--warn)' : 'var(--accent)' }}>
                  <Icon name={a.icon} size={19} />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="hstack" style={{ gap: 9, marginBottom: 3 }}>
                    <StatusPill tone={a.sev === 'high' ? 'bad' : a.sev === 'med' ? 'warn' : 'neutral'}>
                      {a.sev === 'high' ? 'High severity' : a.sev === 'med' ? 'Medium' : 'Low'}
                    </StatusPill>
                  </div>
                  <h4>{a.title}</h4>
                  <p className="asub">{a.sub}</p>
                </div>
                <div className="alert-risk">
                  <div className="ar-val">{a.risk}</div>
                  <div className="ar-lab">at risk</div>
                </div>
              </div>
              <div className="alert-foot">
                <AgentBadge agent={a.agent} small icon="radar" />
                <div className="hstack" style={{ gap: 8, marginLeft: 'auto' }}>
                  <button className="btn btn-quiet btn-sm" onClick={() => toast('Dismissed', a.title + ' marked as reviewed')}>Dismiss</button>
                  <button className="btn btn-grad btn-sm" onClick={() => toast('Investigation opened', 'Case created · routed to your queue')}>
                    <Icon name="eye" size={14} /> Investigate
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="card" style={{ alignSelf: 'flex-start' }}>
          <div className="card-h">
            <h3><Icon name="shield" /> Leakage Recovered</h3>
            <span className="eyebrow">Trailing 10 months</span>
          </div>
          <div className="card-b">
            <div className="hstack" style={{ alignItems: 'baseline', gap: 10, marginBottom: 14 }}>
              <span style={{ fontWeight: 300, fontSize: 44, letterSpacing: '-.03em', color: 'var(--tx-1)' }} className="tnum">$7.8M</span>
              <span className="mono" style={{ color: 'var(--ok)' }}>YTD recovered</span>
            </div>
            <LineChart
              labels={months}
              yFmt={(v) => '$' + v.toFixed(1) + 'M'}
              series={[{ data: trend, color: 'var(--ok)', fill: true }]}
              h={200}
            />
            <hr className="divider" style={{ margin: '16px 0' }} />
            <div className="vstack" style={{ gap: 12 }}>
              {([['Duplicate invoices','$3.2M',41],['Validation abuse','$2.4M',31],['Rate discrepancies','$1.3M',17],['Failed-charge recovery','$0.9M',11]] as [string,string,number][]).map(([k, v, pct], i) => (
                <div key={i} className="vstack" style={{ gap: 5 }}>
                  <div className="spread"><span className="m-foot">{k}</span><span className="t-amt">{v}</span></div>
                  <div className="conf-bar" style={{ width: '100%' }}><i style={{ width: pct + '%', background: 'var(--accent-grad)' }} /></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Mini({ label, value, sub, tone, big }: { label: string; value: string; sub: string; tone: string; big?: boolean }) {
  const col = tone === 'ok' ? 'var(--ok)' : tone === 'bad' ? 'var(--bad)' : 'var(--tx-1)';
  return (
    <div className="metric">
      <span className="m-lab">{label}</span>
      <span className="m-val tnum" style={{ color: col, fontSize: big ? 36 : 30 }}>{value}</span>
      <span className="m-foot">{sub}</span>
    </div>
  );
}
