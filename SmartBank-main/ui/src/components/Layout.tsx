import { useUser, useAuth, UserButton } from '@clerk/clerk-react'
import { useEffect } from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import { useChatStore } from '../stores/chatStore'
import api from '../services/api'
import ChatWidget from './ChatWidget'

const navItems = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'Classify', path: '/classify' },
  { label: 'Document', path: '/document' },
  { label: 'Workflows', path: '/workflows' },
  { label: 'Chat', path: '/chat' },
  { label: 'Admin', path: '/admin' },
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
        <div className="sidebar-logo">SmartBank</div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span>{user?.fullName ?? user?.primaryEmailAddress?.emailAddress ?? 'User'}</span>
          <UserButton afterSignOutUrl="/" />
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
      <button className="chat-fab" onClick={toggleChat} title="Chat with Zara">
        💬
      </button>
      <ChatWidget />
    </div>
  )
}
