import { useEffect, useState } from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import { useAuthCtx } from '../firebase/AuthContext'
import { logOut } from '../firebase/authService'
import { useChatStore } from '../stores/chatStore'
import api from '../services/api'
import ChatWidget from './ChatWidget'
import LiveRobot from './LiveRobot'

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: '\u2302' },
  { label: 'Overview', path: '/overview', icon: '\u{1F4CA}' },
  { label: 'Classify', path: '/classify', icon: '\u2699' },
  { label: 'Document', path: '/document', icon: '\u{1F4C4}' },
  { label: 'Workflows', path: '/workflows', icon: '\u21BA' },
  { label: 'Goals', path: '/goals', icon: '\u{1F3AF}' },
  { label: 'Budget', path: '/budget', icon: '\u{1F4B0}' },
  { label: 'Cards', path: '/cards', icon: '\u{1F4B3}' },
  { label: 'Transactions', path: '/transactions', icon: '\u{1F4CB}' },
  { label: 'AI Transaction', path: '/ai-transaction', icon: '\u2728' },
  { label: 'Loans', path: '/loans', icon: '\u{1F3E6}' },
  { label: 'Chat', path: '/chat', icon: '\u{1F4AC}' },
  { label: 'ARIE', path: '/arie', icon: '\u26A1' },
  { label: 'Security', path: '/security', icon: '\u{1F6E1}' },
  { label: 'Admin', path: '/admin', icon: '\u2691' },
  { label: 'Guide', path: '/guide', icon: '\u2753' },
  { label: 'Banking', path: '/banking', icon: '\u{1F3E6}' },
]

export default function Layout() {
  const { user, isSignedIn } = useAuthCtx()
  const toggleChat = useChatStore((s) => s.toggle)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const closeSidebar = () => setSidebarOpen(false)

  useEffect(() => {
    if (user?.uid) {
      api.post('/api/auth/sync', { email: user.email }).catch(() => {})
    }
  }, [user?.uid, user?.email])

  return (
    <div className="layout">
      <button className="hamburger" onClick={() => setSidebarOpen(o => !o)} aria-label="Toggle menu">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          {sidebarOpen ? (
            <>
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </>
          ) : (
            <>
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </>
          )}
        </svg>
      </button>

      <div className={`sidebar-overlay${sidebarOpen ? ' open' : ''}`} onClick={closeSidebar} />

      <aside className={`sidebar${sidebarOpen ? ' open' : ''}`}>
        <div style={{ display: 'flex', flexDirection: 'column', padding: '12px 16px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div className="sidebar-logo" style={{ padding: 0, border: 'none' }}>
              <span className="logo-icon">S</span>
              SmartBank
            </div>
            <button onClick={() => logOut()} style={{
              background: 'rgba(239,68,68,0.15)', color: '#ef4444',
              border: '1px solid rgba(239,68,68,0.2)', borderRadius: 6, padding: '6px 12px',
              cursor: 'pointer', fontSize: '0.75rem', fontWeight: 600, whiteSpace: 'nowrap',
            }}>
              Sign Out
            </button>
          </div>
          <div style={{ marginTop: 6, fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{
              background: 'var(--primary)', color: '#fff', borderRadius: '50%',
              width: 20, height: 20, display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '0.6rem', fontWeight: 700, flexShrink: 0,
            }}>
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </span>
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 160 }}>
              {user?.email || 'Not signed in'}
            </span>
          </div>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
              onClick={closeSidebar}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>{user?.displayName || 'User'}</span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 160 }}>
            {user?.email || ''}
          </span>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
      <button className="chat-fab" onClick={toggleChat} title="Chat with SmartBank Assistant">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
      </button>
      <ChatWidget />
      <LiveRobot />
    </div>
  )
}
