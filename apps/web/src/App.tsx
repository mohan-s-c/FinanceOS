import { useEffect } from 'react';
import { useStore } from './store/useStore';
import { Sidebar } from './chrome/Sidebar';
import { TopBar } from './chrome/TopBar';
import { Dashboard } from './screens/Dashboard';
import { Exceptions } from './screens/Exceptions';
import { CashApplication } from './screens/Cash';
import { Collections } from './screens/Collections';
import { Anomalies } from './screens/Anomalies';
import { Audit } from './screens/Audit';
import { Analytics } from './screens/Analytics';
import { Agents } from './screens/Agents';
import { Icon } from './components/Icon';

export default function App() {
  const {
    view, collapsed, theme, openCount,
    exceptions, selectedEx,
    toasts,
    setView, toggleCollapsed, toggleTheme,
    openException, resolveException, setSelectedEx,
    addToast, loadExceptions,
  } = useStore();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-density', 'regular');
    // Pull the exception queue through the API (mock fallback if offline).
    void loadExceptions();
  }, []);

  const dark = theme === 'dark';
  const selfScroll = view === 'exceptions' || view === 'cash';

  const screen = (() => {
    switch (view) {
      case 'dashboard':
        return <Dashboard onNav={setView} onOpenException={openException} openCount={openCount} />;
      case 'exceptions':
        return <Exceptions rows={exceptions} selectedId={selectedEx} onSelect={setSelectedEx} onResolve={resolveException} openCount={openCount} />;
      case 'cash':
        return <CashApplication toast={addToast} />;
      case 'collections':
        return <Collections toast={addToast} />;
      case 'anomalies':
        return <Anomalies toast={addToast} />;
      case 'audit':
        return <Audit toast={addToast} />;
      case 'analytics':
        return <Analytics />;
      case 'agents':
        return <Agents toast={addToast} />;
      default:
        return null;
    }
  })();

  return (
    <div className="app">
      <Sidebar active={view} onNav={setView} collapsed={collapsed} openCount={openCount} />
      <div className="main">
        <TopBar view={view} onCollapse={toggleCollapsed} dark={dark} onToggleTheme={toggleTheme} />
        {selfScroll ? (
          <div style={{ flex: 1, minHeight: 0, position: 'relative' }}>{screen}</div>
        ) : (
          <div className="canvas">{screen}</div>
        )}
      </div>

      <div className="toasts">
        {toasts.map((to: { id: number; title: string; sub: string; tone: string }) => (
          <div className="toast" key={to.id}>
            <div className="ti" style={{
              background: to.tone === 'ok' ? 'rgba(91,201,140,.14)' : 'var(--agent-dim)',
              color: to.tone === 'ok' ? 'var(--ok)' : 'var(--agent-bright)',
            }}>
              <Icon name={to.tone === 'ok' ? 'checkCircle' : 'sparkle'} size={16} />
            </div>
            <div className="tx">
              <h5>{to.title}</h5>
              <p>{to.sub}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
