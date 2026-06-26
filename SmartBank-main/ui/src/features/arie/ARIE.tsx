import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import api from '../../services/api'
import ThreeDBackground from '../../components/ThreeDBackground'

export default function ARIE() {
  const [status, setStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/api/arie/status').then(r => { setStatus(r.data); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const testScam = async () => {
    try {
      const r = await api.post('/api/classify', { text: 'kisi ne call pe code pucha hai mera account safe nahi hai', telemetry: { core_banking_status: { api_live: true }, recent_system_logs: [{ timestamp: new Date().toISOString(), event: 'UNAUTHORIZED_LOGIN_ATTEMPT' }] } })
      alert(JSON.stringify(r.data, null, 2))
    } catch { alert('Test failed') }
  }

  const testUrdu = async () => {
    try {
      const r = await api.post('/api/classify', { text: 'yaar wo band kardo mera', telemetry: { core_banking_status: { api_live: true }, recent_system_logs: [{ timestamp: new Date().toISOString(), event: 'ATM_CARD_RETAINED' }] } })
      alert(JSON.stringify(r.data, null, 2))
    } catch { alert('Test failed') }
  }

  return (
    <div className="page">
      <ThreeDBackground />
      <h1><span className="gradient-text">ARIE Engine</span></h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 24 }}>
        Autonomous Resilience &amp; Interceptor Engine — Proactive scam detection, Urdu repair, self-healing circuit breaker
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16, marginBottom: 24 }}>
        <div className="card" style={{ borderLeft: '3px solid var(--danger)' }}>
          <h3>Proactive Scam Interceptor</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Detects vishing, active fraud, phishing in real-time. Triggers SEC01 account lockdown.</p>
        </div>
        <div className="card" style={{ borderLeft: '3px solid var(--warning)' }}>
          <h3>Roman Urdu Repair Engine</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Cross-references ambiguous Urdu input with telemetry logs to repair low-confidence intents.</p>
        </div>
        <div className="card" style={{ borderLeft: '3px solid var(--info)' }}>
          <h3>Self-Healing Circuit Breaker</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>When core banking is down, queues request with cryptographic audit hash for auto-replay.</p>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h2>System Status</h2>
        {loading ? (
          <p>Loading...</p>
        ) : status ? (
          <div className="result-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
            <div><strong>ARIE Active:</strong> <span className={`badge badge-${status.arie_active ? 'safe' : 'danger'}`}>{status.arie_active ? 'True' : 'False'}</span></div>
            <div><strong>Total Scam Lockdowns:</strong> <span className="badge" style={{ background: 'rgba(239,68,68,0.1)', color: 'var(--danger)' }}>{status.stats?.total_scam_lockdowns || 0}</span></div>
            <div><strong>Total Urdu Repairs:</strong> <span className="badge" style={{ background: 'rgba(245,158,11,0.1)', color: 'var(--warning)' }}>{status.stats?.total_urdu_repairs || 0}</span></div>
            <div><strong>Core Banking API:</strong> <span className={`badge badge-${status.core_banking_status?.api_live ? 'safe' : 'danger'}`}>{status.core_banking_status?.api_live ? 'Online' : 'Offline'}</span></div>
          </div>
        ) : <p style={{ color: 'var(--danger)' }}>Failed to fetch ARIE status</p>}
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h2>Test ARIE Capabilities</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 12 }}>Click to send a test request and see ARIE interception in action</p>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <button className="btn btn-danger" onClick={testScam}>Test Scam Interceptor</button>
          <button className="btn btn-warning" onClick={testUrdu}>Test Urdu Repair</button>
        </div>
      </div>

      <div className="card">
        <h2>Recent Intercepts</h2>
        {status?.recent_intercepts?.length ? (
          <table className="data-table" style={{ width: '100%', borderCollapse: 'collapse', marginTop: 12 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th style={{ textAlign: 'left', padding: 8 }}>Type</th>
                <th style={{ textAlign: 'left', padding: 8 }}>Timestamp</th>
                <th style={{ textAlign: 'left', padding: 8 }}>Details</th>
              </tr>
            </thead>
            <tbody>
              {status.recent_intercepts.map((i: any) => (
                <tr key={i.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: 8 }}>
                    <span className={`badge ${i.type.includes('Scam') ? 'badge-danger' : i.type.includes('Urdu') ? 'badge-warning' : 'badge-safe'}`}>{i.type}</span>
                  </td>
                  <td style={{ padding: 8, fontSize: '0.85rem', color: 'var(--text-muted)' }}>{i.timestamp}</td>
                  <td style={{ padding: 8, fontSize: '0.85rem' }}>{i.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: 'var(--text-muted)', marginTop: 8 }}>No intercepts recorded yet</p>
        )}
      </div>
    </div>
  )
}
