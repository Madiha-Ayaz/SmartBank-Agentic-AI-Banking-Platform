import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDashboardStore } from '../../stores/dashboardStore'
import api from '../../services/api'
import ThreeDBackground from '../../components/ThreeDBackground'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, AreaChart, Area,
} from 'recharts'
import { wsService } from '../../services/websocket'

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#3b82f6']

function Gauge({ value, label, color }: { value: number; label: string; color: string }) {
  const r = 52
  const circ = 2 * Math.PI * r
  const offset = circ - (value / 100) * circ
  return (
    <div className="stat-card" style={{ cursor: 'default' }}>
      <div className="metric-gauge">
        <svg width="120" height="120" viewBox="0 0 120 120">
          <circle className="bg" cx="60" cy="60" r={r} />
          <circle className="fill" cx="60" cy="60" r={r} stroke={color}
            strokeDasharray={circ} strokeDashoffset={offset}
          />
        </svg>
        <div className="value" style={{ color }}>{value}%</div>
      </div>
      <span>{label}</span>
    </div>
  )
}

const QUICK_LINKS = [
  { label: 'My Cards', path: '/cards', icon: '\u{1F4B3}', sub: '3 active cards', color: '#6366f1' },
  { label: 'Transactions', path: '/transactions', icon: '\u{1F4CB}', sub: '20 recent', color: '#10b981' },
  { label: 'Loans', path: '/loans', icon: '\u{1F3E6}', sub: '2 active loans', color: '#f59e0b' },
  { label: 'Budget', path: '/budget', icon: '\u{1F4B0}', sub: 'On track this month', color: '#3b82f6' },
]

export default function Dashboard() {
  const navigate = useNavigate()
  const { stats, cases, analytics, loading, fetchStats, fetchCases, fetchAnalytics } =
    useDashboardStore()
  const [finance, setFinance] = useState<{ account: any; transactions: any[] } | null>(null)

  useEffect(() => {
    api.get('/dashboard/finance').then(r => setFinance(r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    fetchStats()
    fetchCases()
    fetchAnalytics()
    const socket = wsService.connect()
    socket?.on('dashboard_update', () => {
      fetchStats()
      fetchCases()
      fetchAnalytics()
    })
    return () => { wsService.disconnect() }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const statusData = analytics ? Object.entries(analytics.by_status).map(([k, v]) => ({ name: k, value: v })) : []
  const priorityData = analytics ? Object.entries(analytics.by_priority).map(([k, v]) => ({ name: k, value: v })) : []
  const channelData = analytics ? Object.entries(analytics.by_channel).map(([k, v]) => ({ name: k, value: v })) : []

  const slaData = stats ? [
    { name: 'Automation', value: stats.automation_rate },
    { name: 'SLA', value: stats.sla_compliance },
  ] : []

  return (
    <div className="page">
      <ThreeDBackground />
      <h1><span className="gradient-text">Dashboard</span></h1>

      {stats && (
        <>
          <div className="stats-grid">
            <div className="stat-card"><span>Total</span><strong>{stats.total_cases}</strong></div>
            <div className="stat-card resolved"><span>Resolved</span><strong>{stats.resolved}</strong></div>
            <div className="stat-card pending"><span>Pending</span><strong>{stats.pending}</strong></div>
            <div className="stat-card review"><span>Human Review</span><strong>{stats.human_review}</strong></div>
          </div>
          <div className="stats-grid" style={{ marginTop: 0 }}>
            <Gauge value={stats.automation_rate} label="Automation Rate" color="#6366f1" />
            <Gauge value={stats.sla_compliance} label="SLA Compliance" color="#10b981" />
            <div className="stat-card">
              <span>Avg Resolution</span>
              <strong style={{ fontSize: '1.2rem', WebkitTextFillColor: 'unset', color: 'var(--text)' }}>
                {stats.avg_resolution_time}
              </strong>
            </div>
            <div className="stat-card">
              <span>Critical</span>
              <strong style={{ WebkitTextFillColor: 'var(--danger)' }}>{stats.critical}</strong>
            </div>
          </div>
        </>
      )}

      {/* Finance Summary */}
      {finance?.account && (
        <div className="card" style={{ marginTop: 16, background: 'linear-gradient(135deg,rgba(99,102,241,0.15),rgba(16,185,129,0.15))', border: '1px solid rgba(99,102,241,0.3)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 2 }}>Account Balance</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#10b981' }}>
                ${parseFloat(finance.account.account_balance || 0).toLocaleString()}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {finance.account.account_number} — {finance.account.full_name}
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              {finance.transactions.length > 0 && (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Last txn: ${parseFloat(finance.transactions[0].transaction_amount).toLocaleString()} · {finance.transactions[0].transaction_type}
                </div>
              )}
            </div>
          </div>
          {finance.transactions.length > 0 && (
            <>
              <div style={{ marginTop: 12, fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Recent Transactions
              </div>
              <div className="table-container" style={{ marginTop: 8 }}>
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>From</th>
                      <th>To</th>
                      <th>Amount</th>
                      <th>Type</th>
                      <th>Status</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {finance.transactions.map(t => (
                      <tr key={t.transaction_id || t.id}>
                        <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>{(t.transaction_id || t.id || '').slice(0, 12)}</td>
                        <td>{t.sender_account_number}</td>
                        <td>{t.receiver_account_number}</td>
                        <td style={{ fontWeight: 600, color: t.sender_account_number === finance.account.account_number ? '#ef4444' : '#10b981' }}>
                          {t.sender_account_number === finance.account.account_number ? '-' : '+'}${parseFloat(t.transaction_amount || 0).toLocaleString()}
                        </td>
                        <td><span className="badge" style={{ background: 'rgba(99,102,241,0.1)', color: '#a78bfa' }}>{t.transaction_type}</span></td>
                        <td><span className={`badge badge-${t.transaction_status || 'completed'}`}>{t.transaction_status || 'completed'}</span></td>
                        <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{t.created_at ? new Date(t.created_at).toLocaleDateString() : '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}

      {/* Quick Access */}
      <div className="stats-grid" style={{ marginTop: 16 }}>
        {QUICK_LINKS.map(q => (
          <div key={q.path} className="stat-card" style={{ cursor: 'pointer', borderLeft: `3px solid ${q.color}` }}
            onClick={() => navigate(q.path)} onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 30px rgba(0,0,0,0.3)'; }}
            onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = ''; }}>
            <div style={{ fontSize: '1.8rem', marginBottom: 4 }}>{q.icon}</div>
            <div style={{ fontWeight: 600, fontSize: '1rem' }}>{q.label}</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{q.sub}</div>
          </div>
        ))}
      </div>

      {analytics && (
        <div className="chart-grid">
          <div className="card">
            <h3>By Status</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={statusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                  {statusData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Legend />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="card">
            <h3>By Priority</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={priorityData}>
                <XAxis dataKey="name" tick={{ fill: '#8892b0' }} />
                <YAxis tick={{ fill: '#8892b0' }} />
                <Tooltip contentStyle={{ background: 'rgba(15,16,40,0.9)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 8 }} />
                <Bar dataKey="value" fill="#6366f1" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="card">
            <h3>By Channel</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={channelData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                  {channelData.map((_, i) => <Cell key={i} fill={COLORS[(i + 2) % COLORS.length]} />)}
                </Pie>
                <Legend />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="card">
            <h3>Performance Trend</h3>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={slaData.length > 0 ? slaData : [{ name: 'Automation', value: 0 }, { name: 'SLA', value: 0 }]}>
                <XAxis dataKey="name" tick={{ fill: '#8892b0' }} />
                <YAxis domain={[0, 100]} tick={{ fill: '#8892b0' }} />
                <Tooltip contentStyle={{ background: 'rgba(15,16,40,0.9)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 8 }} />
                <Area type="monotone" dataKey="value" stroke="#6366f1" fill="rgba(99,102,241,0.1)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <div className="card" style={{ marginTop: 16 }}>
        <h3 style={{ color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', fontSize: '0.85rem', marginBottom: 12 }}>
          Recent Cases
        </h3>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Customer</th>
                <th>Type</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Channel</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((c) => (
                <tr key={c.id}>
                  <td>{c.customer_name}</td>
                  <td>{c.type}</td>
                  <td><span className={`badge badge-${c.status}`}>{c.status}</span></td>
                  <td><span className={`badge badge-${c.priority}`}>{c.priority}</span></td>
                  <td><span className="badge" style={{ background: 'rgba(99,102,241,0.1)', color: '#a78bfa', borderColor: 'rgba(99,102,241,0.2)' }}>{c.channel}</span></td>
                  <td>{c.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
