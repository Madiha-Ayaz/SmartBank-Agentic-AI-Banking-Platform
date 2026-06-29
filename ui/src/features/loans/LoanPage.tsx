import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ThreeDBackground from '../../components/ThreeDBackground'
import { useCurrentUser } from '../../stores/authStore'
import api from '../../services/api'

interface LoanRecord {
  id: number
  case_id: string
  customer_name: string
  account_number?: string
  amount: number
  purpose?: string
  duration_months: number
  profession?: string
  monthly_income: number
  monthly_installment: number
  total_repayment: number
  interest_rate: number
  status: string
  decision_reason: string
  new_balance?: number
  created_at: string
}

export default function LoanPage() {
  const user = useCurrentUser()
  const [name] = useState(user.name)
  const [accountNumber, setAccountNumber] = useState('')
  const [amount, setAmount] = useState('')
  const [purpose, setPurpose] = useState('Personal')
  const [profession, setProfession] = useState('')
  const [duration, setDuration] = useState(12)
  const [income, setIncome] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState<LoanRecord | null>(null)
  const [existingLoans, setExistingLoans] = useState<LoanRecord[]>([])
  const [loadingLoans, setLoadingLoans] = useState(true)

  useEffect(() => {
    api.get('/api/loans').then(r => {
      if (Array.isArray(r.data)) setExistingLoans(r.data)
      setLoadingLoans(false)
    }).catch(() => setLoadingLoans(false))
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!amount || !income || !profession) return
    setSubmitting(true)
    setSubmitted(false)
    setResult(null)
    try {
      const r = await api.post('/api/loans/apply', {
        customer_name: name,
        account_number: accountNumber,
        amount: parseFloat(amount),
        purpose,
        duration_months: duration,
        profession,
        monthly_income: parseFloat(income),
      })
      setResult(r.data)
      setSubmitted(true)
      // Refresh loan list
      api.get('/api/loans').then(r2 => {
        if (Array.isArray(r2.data)) setExistingLoans(r2.data)
      }).catch(() => {})
    } catch (e: any) {
      alert(e.response?.data?.message || 'Loan application failed')
    }
    setSubmitting(false)
  }

  const amt = parseFloat(amount) || 0
  const incomeNum = parseFloat(income) || 0
  const MAX_AFFORDABLE = incomeNum * 0.4
  const monthlyInstallment = duration > 0 ? Math.round(amt / duration * 1.18) : 0
  const totalRepayment = monthlyInstallment * duration
  const isAffordable = monthlyInstallment > 0 && monthlyInstallment <= MAX_AFFORDABLE

  const fmt = (n: number) => '$' + n.toLocaleString()

  const reset = () => {
    setSubmitted(false)
    setResult(null)
  }

  return (
    <div className="page">
      <ThreeDBackground />
      <h1><span className="gradient-text">Loan Application</span></h1>

      {result && (
        <div className="card" style={{ marginBottom: 16, border: `1px solid ${result.status === 'approved' ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`, background: result.status === 'approved' ? 'rgba(16,185,129,0.05)' : 'rgba(239,68,68,0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <span style={{ fontSize: '2rem' }}>{result.status === 'approved' ? '✅' : '❌'}</span>
            <div>
              <div style={{ fontWeight: 700, fontSize: '1.1rem', color: result.status === 'approved' ? 'var(--success)' : 'var(--danger)' }}>
                {result.status === 'approved' ? 'APPROVED' : 'DENIED'}
              </div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Case ID: {result.case_id}</div>
            </div>
          </div>
          <p style={{ color: 'var(--text)', fontSize: '0.9rem', lineHeight: 1.6, marginBottom: 8 }}>{result.decision_reason}</p>
          {result.status === 'approved' && (
            <div className="stats-grid" style={{ marginBottom: 0 }}>
              <div className="stat-card"><span>Amount</span><strong style={{ color: '#10b981' }}>{fmt(result.amount)}</strong></div>
              <div className="stat-card"><span>Installment</span><strong style={{ color: '#f59e0b' }}>{fmt(result.monthly_installment)}/mo</strong></div>
              <div className="stat-card"><span>Total</span><strong>{fmt(result.total_repayment)}</strong></div>
              <div className="stat-card"><span>Duration</span><strong>{result.duration_months}mo</strong></div>
              {result.account_number && (
                <div className="stat-card"><span>Account</span><strong style={{ color: 'var(--primary)' }}>{result.account_number}</strong></div>
              )}
              {result.new_balance !== null && result.new_balance !== undefined && (
                <div className="stat-card"><span>New Balance</span><strong style={{ color: '#10b981' }}>{fmt(result.new_balance)}</strong></div>
              )}
            </div>
          )}
          <button className="btn btn-sm" onClick={reset} style={{ marginTop: 8, background: 'rgba(99,102,241,0.1)', color: 'var(--primary)', border: '1px solid rgba(99,102,241,0.2)' }}>New Application</button>
        </div>
      )}

      <div className="grid-responsive" style={{ gap: 24, marginBottom: 24 }}>
        <div className="card" id="loan-form">
          <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 16 }}>
            Apply for a Loan
          </h3>
          {!submitted ? (
            <form onSubmit={handleSubmit}>
              <div className="form-group" style={{ marginBottom: 12 }}>
                <label>Full Name</label>
                <input type="text" value={name} disabled style={{ opacity: 0.7 }} />
              </div>
              <div className="form-group" style={{ marginBottom: 12 }}>
                <label>Account Number (jis mein paise aayenge)</label>
                <input type="text" value={accountNumber} onChange={e => setAccountNumber(e.target.value)} placeholder="e.g. 9021426090" required />
              </div>
              <div className="form-group" style={{ marginBottom: 12 }}>
                <label>Amount ($)</label>
                <input type="number" value={amount} onChange={e => setAmount(e.target.value)} placeholder="500000" min="1" required />
              </div>
              <div className="form-group" style={{ marginBottom: 12 }}>
                <label>Purpose / Reason</label>
                <select value={purpose} onChange={e => setPurpose(e.target.value)}>
                  <option>Home</option><option>Car</option><option>Business</option><option>Education</option><option>Personal</option>
                </select>
              </div>
              <div className="form-group" style={{ marginBottom: 12 }}>
                <label>Profession / Occupation</label>
                <input type="text" value={profession} onChange={e => setProfession(e.target.value)} placeholder="e.g. Software Engineer" required />
              </div>
              <div className="form-group" style={{ marginBottom: 12 }}>
                <label>Duration (months)</label>
                <select value={duration} onChange={e => setDuration(Number(e.target.value))}>
                  <option value={12}>12 months</option><option value={24}>24 months</option><option value={36}>36 months</option><option value={60}>60 months</option>
                </select>
              </div>
              <div className="form-group" style={{ marginBottom: 16 }}>
                <label>Monthly Income ($)</label>
                <input type="number" value={income} onChange={e => setIncome(e.target.value)} placeholder="100000" min="1" required />
              </div>

              {amt > 0 && incomeNum > 0 && (
                <div style={{ marginBottom: 16, padding: '10px 14px', borderRadius: 8, background: isAffordable ? 'rgba(16,185,129,0.08)' : 'rgba(239,68,68,0.08)', border: `1px solid ${isAffordable ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}` }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>Instant Check</div>
                  <div style={{ fontSize: '0.85rem' }}>
                    Installment: <strong>{fmt(monthlyInstallment)}/mo</strong> |
                    Max affordable (40%): <strong style={{ color: isAffordable ? 'var(--success)' : 'var(--danger)' }}>{fmt(MAX_AFFORDABLE)}</strong>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: isAffordable ? 'var(--success)' : 'var(--danger)', marginTop: 4 }}>
                    {isAffordable ? '✓ Within your capacity' : '✗ Exceeds 40% income limit'}
                  </div>
                </div>
              )}

              <motion.button type="submit" className="btn btn-primary"
                whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                style={{ width: '100%' }}
                disabled={submitting || !amount || !income || !profession}>
                {submitting ? 'Processing...' : 'Apply for Loan'}
              </motion.button>
            </form>
          ) : (
            <div style={{ textAlign: 'center', padding: 20 }}>
              <div style={{ fontSize: '2rem', marginBottom: 8 }}>{result?.status === 'approved' ? '✅' : '❌'}</div>
              <p style={{ color: 'var(--text-muted)' }}>{result?.status === 'approved' ? 'Loan approved!' : 'Loan denied.'}</p>
              <button className="btn btn-sm" onClick={reset} style={{ marginTop: 12, background: 'rgba(99,102,241,0.1)', color: 'var(--primary)', border: '1px solid rgba(99,102,241,0.2)' }}>New Application</button>
            </div>
          )}
        </div>

        {/* Decision logic explanation */}
        <div className="card">
          <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 16 }}>
            Bank Decision Criteria
          </h3>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.8 }}>
            <div>✅ Installment ≤ 40% of income → <strong style={{ color: 'var(--success)' }}>Approved</strong></div>
            <div>✅ Amount ≤ 12× monthly income → <strong style={{ color: 'var(--success)' }}>Approved</strong></div>
            <div>❌ Installment &gt; 40% of income → <strong style={{ color: 'var(--danger)' }}>Denied</strong></div>
            <div>❌ Amount &gt; 12× monthly income → <strong style={{ color: 'var(--danger)' }}>Denied</strong></div>
            <div style={{ marginTop: 12, padding: '12px 14px', background: 'rgba(245,158,11,0.08)', borderRadius: 8, border: '1px solid rgba(245,158,11,0.2)' }}>
              <strong style={{ color: 'var(--warning)' }}>Murabaha Rate:</strong> 18% p.a. (Islamic finance — no interest)
            </div>
          </div>
        </div>
      </div>

      <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 16 }}>
        Your Loan History
      </h3>
      {loadingLoans ? (
        <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>Loading...</div>
      ) : existingLoans.length > 0 ? (
        <div className="stats-grid" style={{ marginBottom: 24 }}>
          {existingLoans.map(loan => (
            <div key={loan.id || loan.case_id} className="stat-card" style={{ textAlign: 'left', borderTop: `3px solid ${loan.status === 'approved' ? 'var(--success)' : loan.status === 'denied' ? 'var(--danger)' : 'var(--warning)'}` }}>
              <div style={{ fontWeight: 600, fontSize: '1rem', marginBottom: 4 }}>{loan.purpose || 'Loan'} — {loan.case_id}</div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{fmt(loan.amount)} × {loan.duration_months}mo</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontSize: '0.8rem' }}>
                <span>{fmt(loan.monthly_installment)}/mo</span>
                <span className={`badge badge-${loan.status === 'approved' ? 'safe' : loan.status === 'denied' ? 'danger' : 'warning'}`} style={{ fontSize: '0.65rem' }}>{loan.status}</span>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>{loan.profession && `${loan.profession} · `}{loan.created_at ? new Date(loan.created_at).toLocaleDateString() : ''}</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
          No loan applications yet. Apply above to get started.
        </div>
      )}
    </div>
  )
}
