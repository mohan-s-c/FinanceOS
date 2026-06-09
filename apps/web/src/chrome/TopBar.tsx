import { Icon } from '../components/Icon';
import type { View } from '../store/useStore';
import { useStore } from '../store/useStore';

const TITLES: Record<View, { h: string; crumb: string }> = {
  dashboard: { h: 'Command Center', crumb: 'OVERVIEW' },
  exceptions: { h: 'AP Exception Queue', crumb: 'ACCOUNTS PAYABLE / REVIEW' },
  cash: { h: 'AR Cash Application', crumb: 'ACCOUNTS RECEIVABLE' },
  collections: { h: 'Collections & Owner Settlement', crumb: 'ACCOUNTS RECEIVABLE' },
  agents: { h: 'Agents', crumb: 'AUTONOMY / ROSTER' },
  anomalies: { h: 'Anomalies & Leakage', crumb: 'AUTONOMY' },
  audit: { h: 'Agent Activity & Audit Trail', crumb: 'AUTONOMY / SOX' },
  analytics: { h: 'Analytics', crumb: 'AUTONOMY' },
};

interface TopBarProps {
  view: View;
  onCollapse: () => void;
  dark: boolean;
  onToggleTheme: () => void;
}

export function TopBar({ view, onCollapse, dark, onToggleTheme }: TopBarProps) {
  const t = TITLES[view] || TITLES.dashboard;
  const { roleKey, user, loginAs } = useStore();
  return (
    <header className="topbar">
      <button className="tb-collapse" onClick={onCollapse} title="Toggle sidebar">
        <Icon name="menu" size={17} />
      </button>
      <div className="tb-title">
        <span className="crumb">{t.crumb}</span>
        <h1>{t.h}</h1>
      </div>
      <div className="tb-search">
        <Icon name="search" size={15} />
        <input placeholder="Search invoices, vendors, agents…" />
        <kbd>⌘K</kbd>
      </div>
      <div className="hstack" style={{ gap: 10, marginRight: 4 }}>
        <span title="Active role" className="hstack" style={{ gap: 7, fontSize: 12, color: 'var(--tx-2)' }}>
          <span style={{ width: 22, height: 22, borderRadius: '50%', background: 'var(--accent-grad)', display: 'grid', placeItems: 'center', fontSize: 9, fontWeight: 600, color: '#2a1c0a' }}>{user.initials}</span>
          {user.role}
        </span>
        <div className="ag-seg">
          <button className={roleKey === 'analyst' ? 'on' : ''} onClick={() => loginAs('dana')}>Analyst</button>
          <button className={roleKey === 'controller' ? 'on' : ''} onClick={() => loginAs('morgan')}>Controller</button>
        </div>
      </div>
      <button className="tb-icon" onClick={onToggleTheme} title="Toggle theme">
        <Icon name={dark ? 'sun' : 'moon'} size={17} />
      </button>
      <button className="tb-icon" title="Notifications">
        <Icon name="bell" size={17} />
        <span className="dot" />
      </button>
    </header>
  );
}
