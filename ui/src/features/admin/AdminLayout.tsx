import { useState, useEffect } from 'react'
import { Routes, Route, NavLink } from 'react-router-dom'
import api from '../../services/api'
import ThreeDBackground from '../../components/ThreeDBackground'

function Users() {
  const [users, setUsers] = useState<Array<{ id: string; username: string; role: string; lastActive: string }>>([])

  useEffect(() => {
    api.get('/api/admin/users').then((res) => setUsers(res.data.users ?? [])).catch(() => {})
  }, [])

  return (
    <div className="card">
      <h3 style={{ color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', fontSize: '0.85rem', marginBottom: 12 }}>
        User Management
      </h3>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Role</th>
              <th>Last Active</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td><code style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{u.id}</code></td>
                <td style={{ fontWeight: 600 }}>{u.username}</td>
                <td><span className="badge" style={{ background: 'rgba(99,102,241,0.1)', color: '#a78bfa', borderColor: 'rgba(99,102,241,0.2)' }}>{u.role}</span></td>
                <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{u.lastActive}</td>
              </tr>
            ))}
            {users.length === 0 && (
              <tr><td colSpan={4} style={{ textAlign: 'center', opacity: 0.6, padding: 20 }}>No users found</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function Audit() {
  const [logs, setLogs] = useState<Array<{ id: string; action: string; user: string; timestamp: string; details: string }>>([])

  useEffect(() => {
    api.get('/api/admin/audit').then((res) => setLogs(res.data.logs ?? [])).catch(() => {})
  }, [])

  return (
    <div className="card">
      <h3 style={{ color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', fontSize: '0.85rem', marginBottom: 12 }}>
        Audit Log
      </h3>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Action</th>
              <th>User</th>
              <th>Timestamp</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td><span className="badge" style={{ background: 'rgba(99,102,241,0.1)', color: '#a78bfa', borderColor: 'rgba(99,102,241,0.2)' }}>{log.action}</span></td>
                <td style={{ fontWeight: 600 }}>{log.user}</td>
                <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{log.timestamp}</td>
                <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{log.details}</td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr><td colSpan={4} style={{ textAlign: 'center', opacity: 0.6, padding: 20 }}>No audit logs available</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function AdminLayout() {
  return (
    <div className="page">
      <ThreeDBackground />
      <h1><span className="gradient-text">Admin Panel</span></h1>
      <nav className="admin-tabs">
        <NavLink to="/admin/users" className={({ isActive }) => isActive ? 'active' : ''}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: 4, verticalAlign: 'middle' }}>
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          Users
        </NavLink>
        <NavLink to="/admin/audit" className={({ isActive }) => isActive ? 'active' : ''}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: 4, verticalAlign: 'middle' }}>
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          Audit
        </NavLink>
      </nav>
      <Routes>
        <Route index element={<Users />} />
        <Route path="users" element={<Users />} />
        <Route path="audit" element={<Audit />} />
      </Routes>
    </div>
  )
}
