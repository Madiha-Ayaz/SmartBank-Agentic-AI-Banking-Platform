import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import api from '../../services/api'
import ThreeDBackground from '../../components/ThreeDBackground'

interface SecurityLog {
  id: number
  user_id: string
  action_type: string
  description: string
  risk_level: string
  status: string
  ip_address: string
  metadata: string
  created_at: string
}

interface FraudAlert {
  id: number
  user_id: string
  transaction_id: string
  amount: number
  risk_score: number
  risk_level: string
  reason: string
  status: string
  created_at: string
}

interface RiskScore {
  id: number
  score: number
  level: string
  factors: string
  created_at: string
}

interface FreezeHistory {
  id: number
  action: string
  account_number: string
  reason: string
  frozen_by: string
  created_at: string
}

interface LoginActivity {
  id: number
  action: string
  email: string
  ip_address: string
  timestamp: string
}

interface DashboardData {
  logs: SecurityLog[]
  alerts: FraudAlert[]
  risk_score: RiskScore | null
  freeze_history: FreezeHistory[]
  login_activity: LoginActivity[]
  account_status: string
  freeze_reason: string | null
}

const riskColor = (level: string) => {
  if (level === 'HIGH') return '#ef4444'
  if (level === 'MEDIUM') return '#f59e0b'
  return '#10b981'
}

const statusBadge: Record<string, { bg: string, color: string }> = {
  completed: { bg: 'rgba(16,185,129,0.15)', color: '#10b981' },
  blocked: { bg: 'rgba(239,68,68,0.15)', color: '#ef4444' },
  open: { bg: 'rgba(245,158,11,0.15)', color: '#f59e0b' },
  flagged: { bg: 'rgba(245,158,11,0.15)', color: '#f59e0b' },
  error: { bg: 'rgba(239,68,68,0.15)', color: '#ef4444' },
}

export default function SecurityDashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [freezeReason, setFreezeReason] = useState('')
  const [freezing, setFreezing] = useState(false)
  const [unfreezeAcct, setUnfreezeAcct] = useState('')
  const [unfreezeReason, setUnfreezeReason] = useState('')

  const loadData = () => {
    setLoading(true)
    api.get('/api/security/dashboard').then(res => {
      setData(res.data)
    }).catch(() => {}).finally(() => setLoading(false))
  }

  useEffect(() => { loadData() }, [])

  const handleFreeze = async () => {
    setFreezing(true)
    try {
      await api.post('/api/accounts/freeze', { reason: freezeReason })
      loadData()
      setFreezeReason('')
    } catch(e: any) {
      alert('Freeze failed: ' + (e.response?.data?.error || e.message))
    }
    setFreezing(false)
  }

  const handleUnfreeze = async () => {
    try {
      await api.post('/api/accounts/unfreeze', { account_number: unfreezeAcct, reason: unfreezeReason })
      loadData()
      setUnfreezeAcct('')
      setUnfreezeReason('')
    } catch(e: any) {
      alert('Unfreeze failed: ' + (e.response?.data?.error || e.message))
    }
  }

  if (loading) {
    return (
      <div className="page">
        <ThreeDBackground />
        <div style={{ textAlign: 'center', padding: 80, color: 'var(--text-muted)' }}>Loading security dashboard...</div>
      </div>
    )
  }

  return (
    <div className="page">
      <ThreeDBackground />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 8 }}>
        <div>
          <h1 style={{ fontWeight: 700, margin: 0 }}>Security Dashboard</h1>
          <p style={{ color: 'var(--text-muted)', margin: '4px 0 0' }}>Cybersecurity & Risk Intelligence Layer</p>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span style={{
            padding: '4px 12px', borderRadius: 999, fontSize: '0.75rem', fontWeight: 600,
            background: data?.account_status === 'frozen' ? 'rgba(239,68,68,0.15)' : 'rgba(16,185,129,0.15)',
            color: data?.account_status === 'frozen' ? '#ef4444' : '#10b981',
          }}>
            {data?.account_status === 'frozen' ? 'FROZEN' : 'ACTIVE'}
          </span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 24 }}>
        <StatCard title="Risk Score" value={data?.risk_score ? `${data.risk_score.score}/100` : 'N/A'} color={riskColor(data?.risk_score?.level || 'LOW')} subtitle={data?.risk_score?.level || 'No data'} />
        <StatCard title="Open Alerts" value={String(data?.alerts?.length || 0)} color="#f59e0b" subtitle="Requires attention" />
        <StatCard title="Security Events" value={String(data?.logs?.length || 0)} color="#6366f1" subtitle="Recent activity" />
        <StatCard title="Freeze History" value={String(data?.freeze_history?.length || 0)} color="#ec4899" subtitle="Account actions" />
      </div>

      <div className="grid-responsive" style={{ gap: 24, marginBottom: 24 }}>
        <div className="card">
          <h3 style={{ margin: '0 0 12px', fontSize: '1rem', fontWeight: 600 }}>
            Account Protection
            {data?.account_status === 'frozen' && <span style={{ color: '#ef4444', marginLeft: 8, fontSize: '0.75rem' }}>({data.freeze_reason})</span>}
          </h3>
          {data?.account_status !== 'frozen' ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <input className="input" placeholder="Reason for freeze (optional)" value={freezeReason} onChange={e => setFreezeReason(e.target.value)} style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--bg-card)', color: 'var(--text)' }} />
              <button className="btn" onClick={handleFreeze} disabled={freezing} style={{ background: 'rgba(239,68,68,0.15)', color: '#ef4444', border: '1px solid rgba(239,68,68,0.2)', padding: '8px 16px', borderRadius: 8, cursor: 'pointer', fontWeight: 600 }}>
                {freezing ? 'Freezing...' : 'Freeze Account'}
              </button>
            </div>
          ) : (
            <p style={{ color: '#ef4444', fontSize: '0.875rem' }}>Account is frozen. Financial operations blocked. Contact admin to unfreeze.</p>
          )}
          <div style={{ marginTop: 16, borderTop: '1px solid var(--border)', paddingTop: 12 }}>
            <h4 style={{ margin: '0 0 8px', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-muted)' }}>Admin: Unfreeze Account</h4>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <input className="input" placeholder="Account number" value={unfreezeAcct} onChange={e => setUnfreezeAcct(e.target.value)} style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid var(--border)', background: 'var(--bg-card)', color: 'var(--text)', flex: '1 1 100px', fontSize: '0.8rem' }} />
              <input className="input" placeholder="Reason" value={unfreezeReason} onChange={e => setUnfreezeReason(e.target.value)} style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid var(--border)', background: 'var(--bg-card)', color: 'var(--text)', flex: '1 1 100px', fontSize: '0.8rem' }} />
              <button className="btn" onClick={handleUnfreeze} style={{ background: 'rgba(16,185,129,0.15)', color: '#10b981', border: '1px solid rgba(16,185,129,0.2)', padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontWeight: 600, fontSize: '0.8rem', whiteSpace: 'nowrap' }}>Unfreeze</button>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 style={{ margin: '0 0 12px', fontSize: '1rem', fontWeight: 600 }}>Fraud Alerts {data && data.alerts.length > 0 && <span style={{ background: '#ef4444', color: '#fff', padding: '2px 8px', borderRadius: 999, fontSize: '0.7rem', marginLeft: 8 }}>{data.alerts.length}</span>}</h3>
          {data && data.alerts.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 200, overflowY: 'auto' }}>
              {data.alerts.map(a => (
                <div key={a.id} style={{ padding: '8px 12px', borderRadius: 8, background: 'var(--bg-card)', border: '1px solid var(--border)', fontSize: '0.8rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ color: riskColor(a.risk_level), fontWeight: 600 }}>{a.risk_level} · Score: {a.risk_score}</span>
                    <span style={{ background: statusBadge[a.status]?.bg || 'rgba(100,116,139,0.15)', color: statusBadge[a.status]?.color || '#94a3b8', padding: '2px 8px', borderRadius: 999, fontSize: '0.7rem', fontWeight: 600 }}>{a.status}</span>
                  </div>
                  <div style={{ color: 'var(--text-muted)' }}>{a.reason}</div>
                  {a.amount > 0 && <div style={{ color: 'var(--text)', fontWeight: 600, marginTop: 2 }}>${a.amount.toLocaleString()}</div>}
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No active fraud alerts. Your account is secure.</p>
          )}
        </div>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h3 style={{ margin: '0 0 12px', fontSize: '1rem', fontWeight: 600 }}>Security Event Log</h3>
        {data && data.logs.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  <th style={{ textAlign: 'left', padding: '8px 12px', color: 'var(--text-muted)', fontWeight: 600 }}>Action</th>
                  <th style={{ textAlign: 'left', padding: '8px 12px', color: 'var(--text-muted)', fontWeight: 600 }}>Description</th>
                  <th style={{ textAlign: 'left', padding: '8px 12px', color: 'var(--text-muted)', fontWeight: 600 }}>Risk</th>
                  <th style={{ textAlign: 'left', padding: '8px 12px', color: 'var(--text-muted)', fontWeight: 600 }}>Status</th>
                  <th style={{ textAlign: 'left', padding: '8px 12px', color: 'var(--text-muted)', fontWeight: 600 }}>Date</th>
                </tr>
              </thead>
              <tbody>
                {data.logs.map(log => (
                  <tr key={log.id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '8px 12px', fontWeight: 600, whiteSpace: 'nowrap' }}>{log.action_type}</td>
                    <td style={{ padding: '8px 12px', maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{log.description}</td>
                    <td style={{ padding: '8px 12px' }}><span style={{ color: riskColor(log.risk_level), fontWeight: 600 }}>{log.risk_level}</span></td>
                    <td style={{ padding: '8px 12px' }}>
                      <span style={{
                        background: statusBadge[log.status]?.bg || 'rgba(100,116,139,0.15)',
                        color: statusBadge[log.status]?.color || '#94a3b8',
                        padding: '2px 8px', borderRadius: 999, fontSize: '0.7rem', fontWeight: 600,
                      }}>{log.status}</span>
                    </td>
                    <td style={{ padding: '8px 12px', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                      {log.created_at ? new Date(log.created_at).toLocaleString() : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No security events recorded yet.</p>
        )}
      </div>

      <div className="grid-responsive" style={{ gap: 24 }}>
        <div className="card">
          <h3 style={{ margin: '0 0 12px', fontSize: '1rem', fontWeight: 600 }}>Login Activity</h3>
          {data && data.login_activity.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 200, overflowY: 'auto' }}>
              {data.login_activity.map((la, i) => (
                <div key={i} style={{ padding: '8px 12px', borderRadius: 8, background: 'var(--bg-card)', border: '1px solid var(--border)', fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>{la.action}</span>
                    <span style={{ color: 'var(--text-muted)', marginLeft: 8 }}>{la.email}</span>
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                    {la.timestamp ? new Date(la.timestamp).toLocaleString() : '-'}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No login activity recorded.</p>
          )}
        </div>

        <div className="card">
          <h3 style={{ margin: '0 0 12px', fontSize: '1rem', fontWeight: 600 }}>Freeze History</h3>
          {data && data.freeze_history.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 200, overflowY: 'auto' }}>
              {data.freeze_history.map(fh => (
                <div key={fh.id} style={{ padding: '8px 12px', borderRadius: 8, background: 'var(--bg-card)', border: '1px solid var(--border)', fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <span style={{ fontWeight: 600, color: fh.action === 'freeze' ? '#ef4444' : '#10b981', textTransform: 'uppercase' }}>{fh.action}</span>
                    <span style={{ color: 'var(--text-muted)', marginLeft: 8 }}>{fh.account_number}</span>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: 2 }}>{fh.reason || '-'}</div>
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                    {fh.created_at ? new Date(fh.created_at).toLocaleString() : '-'}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No freeze history.</p>
          )}
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, color, subtitle }: { title: string, value: string, color: string, subtitle: string }) {
  return (
    <motion.div className="card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} style={{ padding: 20 }}>
      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>{title}</div>
      <div style={{ fontSize: '1.75rem', fontWeight: 700, color }}>{value}</div>
      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>{subtitle}</div>
    </motion.div>
  )
}
