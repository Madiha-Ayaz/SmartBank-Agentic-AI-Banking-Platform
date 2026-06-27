import { useUser, useAuth, UserButton } from '@clerk/clerk-react'
import { useEffect } from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import { useChatStore } from '../stores/chatStore'
import api from '../services/api'
import ChatWidget from './ChatWidget'

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: '\u2302' },
  { label: 'Classify', path: '/classify', icon: '\u2699' },
  { label: 'Document', path: '/document', icon: '\u{1F4C4}' },
  { label: 'Workflows', path: '/workflows', icon: '\u21BA' },
  { label: 'Goals', path: '/goals', icon: '\u{1F3AF}' },
  { label: 'Budget', path: '/budget', icon: '\u{1F4B0}' },
  { label: 'Cards', path: '/cards', icon: '\u{1F4B3}' },
  { label: 'Transactions', path: '/transactions', icon: '\u{1F4CB}' },
  { label: 'Loans', path: '/loans', icon: '\u{1F3E6}' },
  { label: 'Chat', path: '/chat', icon: '\u{1F4AC}' },
  { label: 'ARIE', path: '/arie', icon: '\u26A1' },
  { label: 'Admin', path: '/admin', icon: '\u2691' },
  { label: 'Guide', path: '/guide', icon: '\u2753' },
]

export default function Layout() {
  const { user } = useUser()
  const { signOut } = useAuth()
  const toggleChat = useChatStore((s) => s.toggle)

  useEffect(() => {
    if (user?.id) {
      api.post('/api/auth/sync', { email: user.primaryEmailAddress?.emailAddress }).catch(() => {})
    }
  }, [user?.id, user?.primaryEmailAddress?.emailAddress])

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span className="logo-icon">S</span>
          SmartBank
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 140 }}>
            {user?.fullName ?? user?.primaryEmailAddress?.emailAddress ?? 'User'}
          </span>
          <UserButton afterSignOutUrl="/" />
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
      <button className="chat-fab" onClick={toggleChat} title="Chat with Zara">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
      </button>
      <ChatWidget />
    </div>
  )
}
