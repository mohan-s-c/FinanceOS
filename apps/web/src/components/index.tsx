import React, { useMemo } from 'react';
import { Icon } from './Icon';

export function confColor(c: number): string {
  if (c >= 80) return 'var(--ok)';
  if (c >= 60) return 'var(--warn)';
  return 'var(--bad)';
}

/* ---- Confidence Ring ---- */
interface RingProps { value: number; size?: number; stroke?: number; showLabel?: boolean; }
export function ConfidenceRing({ value, size = 46, stroke = 4, showLabel = true }: RingProps) {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const off = circ * (1 - value / 100);
  const col = confColor(value);
  return (
    <div className="conf-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="var(--surface-3)" strokeWidth={stroke} />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={col} strokeWidth={stroke}
          strokeDasharray={circ} strokeDashoffset={off} strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset .6s cubic-bezier(.22,.61,.36,1)' }} />
      </svg>
      {showLabel && <div className="cv" style={{ color: col, fontSize: size * 0.27 }}>{value}</div>}
    </div>
  );
}

/* ---- Confidence Bar ---- */
interface BarProps { value: number; width?: number; showVal?: boolean; }
export function ConfidenceBar({ value, width = 70, showVal = true }: BarProps) {
  const col = confColor(value);
  return (
    <div className="conf">
      <div className="conf-bar" style={{ width }}>
        <i style={{ width: value + '%', background: col, transition: 'width .6s cubic-bezier(.22,.61,.36,1)' }} />
      </div>
      {showVal && <span className="mono tnum" style={{ color: col, fontWeight: 600 }}>{value}%</span>}
    </div>
  );
}

/* ---- Agent Badge ---- */
interface BadgeProps { agent: string; human?: boolean; icon?: string; small?: boolean; }
export function AgentBadge({ agent, human = false, icon = 'sparkle', small = false }: BadgeProps) {
  const style = small ? { fontSize: 9.5, padding: '2px 7px 2px 6px' } : undefined;
  if (human) return <span className="abadge human" style={style}><Icon name="users" size={11} />{agent}</span>;
  return <span className="abadge" style={style}><Icon name={icon} size={11} />{agent}</span>;
}

/* ---- Source Chip ---- */
interface ChipProps { type: string; refId: string; note?: string; onClick?: () => void; }
export function SourceChip({ type, refId, note, onClick }: ChipProps) {
  const iconName = type === 'Invoice' ? 'receipt' : type === 'Policy' ? 'scale' : type === 'PO' ? 'fileText' : (type === 'Contract' || type === 'Lease') ? 'file' : 'link';
  return (
    <span className="chip" onClick={onClick} title={note}>
      <Icon name={iconName} />
      <span><span className="ctype">{type}</span> {refId}</span>
    </span>
  );
}

/* ---- Status Pill ---- */
interface PillProps { tone?: string; children: React.ReactNode; dot?: boolean; }
export function StatusPill({ tone = 'neutral', children, dot = true }: PillProps) {
  return (
    <span className={'pill ' + tone}>
      {dot && <span className="pdot" />}
      {children}
    </span>
  );
}

/* ---- Sparkline ---- */
interface SparkProps { data: number[]; w?: number; h?: number; color?: string; fill?: boolean; }
export function Sparkline({ data, w = 120, h = 46, color = 'var(--ok)', fill = true }: SparkProps) {
  const { path, area, gid } = useMemo(() => {
    const min = Math.min(...data), max = Math.max(...data);
    const span = max - min || 1;
    const pts = data.map((v, i) => {
      const x = (i / (data.length - 1)) * w;
      const y = h - 4 - ((v - min) / span) * (h - 8);
      return [x, y] as [number, number];
    });
    const path = pts.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' ');
    const area = path + ` L${w} ${h} L0 ${h} Z`;
    const gid = 'sg' + Math.random().toString(36).slice(2, 7);
    return { path, area, gid };
  }, [data, w, h]);
  return (
    <svg className="spark" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" style={{ width: w, height: h }}>
      <defs>
        <linearGradient id={gid} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.28" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      {fill && <path d={area} fill={`url(#${gid})`} />}
      <path d={path} fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

/* ---- Line Chart ---- */
interface Series { data: number[]; color: string; fill?: boolean; dashed?: boolean; dots?: boolean; }
interface LineChartProps { series: Series[]; labels: string[]; h?: number; yFmt?: (v: number) => string; yMax?: number; yMin?: number; }
export function LineChart({ series, labels, h = 240, yFmt = (v) => String(v), yMax, yMin }: LineChartProps) {
  const pad = { l: 44, r: 16, t: 16, b: 28 };
  const w = 760;
  const all = series.flatMap((s) => s.data);
  const max = yMax != null ? yMax : Math.max(...all) * 1.12;
  const min = yMin != null ? yMin : Math.min(0, ...all);
  const span = max - min || 1;
  const innerW = w - pad.l - pad.r, innerH = h - pad.t - pad.b;
  const X = (i: number, n: number) => pad.l + (i / (n - 1)) * innerW;
  const Y = (v: number) => pad.t + innerH - ((v - min) / span) * innerH;
  const ticks = 4;
  return (
    <svg className="chart" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="xMidYMid meet">
      {Array.from({ length: ticks + 1 }).map((_, i) => {
        const v = min + (span * i) / ticks;
        const y = Y(v);
        return (
          <g key={i}>
            <line x1={pad.l} y1={y} x2={w - pad.r} y2={y} stroke="var(--line-1)" strokeWidth="1" />
            <text x={pad.l - 10} y={y + 3.5} textAnchor="end" fontSize="10" fontFamily="var(--font-mono)" fill="var(--tx-4)">{yFmt(v)}</text>
          </g>
        );
      })}
      {labels.map((lb, i) => (
        <text key={i} x={X(i, labels.length)} y={h - 8} textAnchor="middle" fontSize="10" fontFamily="var(--font-mono)" fill="var(--tx-4)">{lb}</text>
      ))}
      {series.map((s, si) => {
        const pts = s.data.map((v, i) => [X(i, s.data.length), Y(v)] as [number, number]);
        const d = pts.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' ');
        const gid = 'lc' + si + Math.round(X(0, 2));
        return (
          <g key={si}>
            {s.fill && (
              <>
                <defs>
                  <linearGradient id={gid} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={s.color} stopOpacity="0.22" />
                    <stop offset="100%" stopColor={s.color} stopOpacity="0" />
                  </linearGradient>
                </defs>
                <path d={d + ` L${pts[pts.length-1][0]} ${pad.t+innerH} L${pts[0][0]} ${pad.t+innerH} Z`} fill={`url(#${gid})`} />
              </>
            )}
            <path d={d} fill="none" stroke={s.color} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={s.dashed ? '5 5' : undefined} />
            {s.dots !== false && pts.map((p, i) => (
              <circle key={i} cx={p[0]} cy={p[1]} r="3" fill="var(--surface)" stroke={s.color} strokeWidth="2" />
            ))}
          </g>
        );
      })}
    </svg>
  );
}

/* ---- Bar Chart ---- */
interface BarChartProps { data: number[]; labels: string[]; h?: number; color?: string | ((v: number, i: number) => string); yFmt?: (v: number) => string; }
export function BarChart({ data, labels, h = 220, color = 'var(--accent)', yFmt = (v) => String(v) }: BarChartProps) {
  const pad = { l: 44, r: 12, t: 14, b: 28 };
  const w = 760;
  const max = Math.max(...data) * 1.12;
  const innerW = w - pad.l - pad.r, innerH = h - pad.t - pad.b;
  const bw = (innerW / data.length) * 0.56;
  const gap = innerW / data.length;
  const ticks = 4;
  return (
    <svg className="chart" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="xMidYMid meet">
      {Array.from({ length: ticks + 1 }).map((_, i) => {
        const v = (max * i) / ticks;
        const y = pad.t + innerH - (v / max) * innerH;
        return (
          <g key={i}>
            <line x1={pad.l} y1={y} x2={w - pad.r} y2={y} stroke="var(--line-1)" strokeWidth="1" />
            <text x={pad.l - 10} y={y + 3.5} textAnchor="end" fontSize="10" fontFamily="var(--font-mono)" fill="var(--tx-4)">{yFmt(v)}</text>
          </g>
        );
      })}
      {data.map((v, i) => {
        const bh = (v / max) * innerH;
        const x = pad.l + i * gap + (gap - bw) / 2;
        const y = pad.t + innerH - bh;
        const fill = typeof color === 'function' ? color(v, i) : color;
        return (
          <g key={i}>
            <rect x={x} y={y} width={bw} height={bh} rx="4" fill={fill} opacity="0.9" />
            <text x={x + bw / 2} y={h - 8} textAnchor="middle" fontSize="10" fontFamily="var(--font-mono)" fill="var(--tx-4)">{labels[i]}</text>
          </g>
        );
      })}
    </svg>
  );
}

/* ---- Donut ---- */
interface DonutProps { data: { value: number; color: string; label: string }[]; size?: number; stroke?: number; centerVal?: string|number; centerLab?: string; }
export function Donut({ data, size = 150, stroke = 22, centerVal, centerLab }: DonutProps) {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const total = data.reduce((a, d) => a + d.value, 0);
  let acc = 0;
  return (
    <div style={{ position: 'relative', width: size, height: size, flex: '0 0 auto' }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="var(--surface-3)" strokeWidth={stroke} />
        {data.map((d, i) => {
          const frac = d.value / total;
          const dash = frac * circ;
          const el = (
            <circle key={i} cx={size/2} cy={size/2} r={r} fill="none" stroke={d.color} strokeWidth={stroke}
              strokeDasharray={`${dash} ${circ - dash}`} strokeDashoffset={-acc * circ}
              style={{ transition: 'stroke-dashoffset .6s' }} />
          );
          acc += frac;
          return el;
        })}
      </svg>
      <div className="donut-center">
        <div>
          <div className="dc-val">{centerVal}</div>
          <div className="dc-lab">{centerLab}</div>
        </div>
      </div>
    </div>
  );
}

/* ---- Metric Card ---- */
interface MetricCardProps { m: { id: string; label: string; value: string; suffix?: string; delta: string; dir: string; foot: string; tone: string; spark: number[]; icon: string; }; }
export function MetricCard({ m }: MetricCardProps) {
  const dirIcon = m.dir === 'up' ? 'arrowUp' : m.dir === 'down' ? 'arrowDown' : 'minus';
  const sparkColor = m.tone === 'ok' ? 'var(--ok)' : m.tone === 'warn' ? 'var(--warn)' : 'var(--accent)';
  return (
    <div className="metric">
      <div className="m-top">
        <span className="m-lab">{m.label}</span>
        <span className="m-ico"><Icon name={m.icon} size={15} /></span>
      </div>
      <div className="m-val tnum">{m.value}{m.suffix && <small>{m.suffix}</small>}</div>
      <div className="hstack" style={{ gap: 10 }}>
        <span className={'m-delta ' + m.dir}><Icon name={dirIcon} size={12} />{m.delta}</span>
        <span className="m-foot">{m.foot}</span>
      </div>
      <Sparkline data={m.spark} color={sparkColor} />
    </div>
  );
}
