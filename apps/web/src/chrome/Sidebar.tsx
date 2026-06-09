import { Icon } from '../components/Icon';
import type { View } from '../store/useStore';
import { useStore } from '../store/useStore';

const NAV = [
  { group: 'Overview', items: [
    { id: 'dashboard' as View, label: 'Command Center', icon: 'grid' },
  ]},
  { group: 'Accounts Payable', items: [
    { id: 'exceptions' as View, label: 'Exception Queue', icon: 'inbox', badge: '47', badgeTone: 'warn' },
  ]},
  { group: 'Accounts Receivable', items: [
    { id: 'cash' as View, label: 'Cash Application', icon: 'coins', badge: '6', badgeTone: 'warn' },
    { id: 'collections' as View, label: 'Collections', icon: 'phone' },
  ]},
  { group: 'Autonomy', items: [
    { id: 'agents' as View, label: 'Agents', icon: 'sparkle2', badge: '8' },
    { id: 'anomalies' as View, label: 'Anomalies & Leakage', icon: 'radar', badge: '5', badgeTone: 'warn' },
    { id: 'audit' as View, label: 'Agent & Audit Trail', icon: 'activity' },
    { id: 'analytics' as View, label: 'Analytics', icon: 'chart' },
  ]},
];

interface SidebarProps {
  active: View;
  onNav: (v: View) => void;
  collapsed: boolean;
  openCount: number;
}

export function Sidebar({ active, onNav, collapsed, openCount }: SidebarProps) {
  const user = useStore((s) => s.user);
  return (
    <aside className={'sidebar' + (collapsed ? ' collapsed' : '')}>
      <div className="sb-brand">
        <div className="sb-mark"><Icon name="eye" size={15} style={{ color: '#fff' }} /></div>
        <div className="sb-text vstack">
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 15, fontWeight: 500, color: 'var(--tx-1)', letterSpacing: '0.04em' }}>APAR</span>
          <span className="sb-os">FinanceOS</span>
          <span className="sb-ver">V2.0</span>
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', paddingBottom: 8 }}>
        {NAV.map((sec) => (
          <div className="sb-section" key={sec.group}>
            <span className="eyebrow">{sec.group}</span>
            <div className="sb-nav" style={{ marginTop: 6 }}>
              {sec.items.map((it) => {
                const badge = it.id === 'exceptions' ? String(openCount) : it.badge;
                return (
                  <div key={it.id} className={'sb-item' + (active === it.id ? ' active' : '')}
                    onClick={() => onNav(it.id)} title={it.label}>
                    <Icon name={it.icon} size={18} />
                    <span className="sb-label">{it.label}</span>
                    {badge && <span className={'sb-badge ' + (it.badgeTone || '')}>{badge}</span>}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <div className="sb-foot">
        <div className="sb-user">
          <div className="sb-ava">{user.initials}</div>
          <div className="sb-text vstack" style={{ minWidth: 0 }}>
            <span className="sb-uname">{user.name}</span>
            <span className="sb-urole">{user.role}</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
