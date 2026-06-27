import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ThreeDBackground from '../../components/ThreeDBackground'

const EXISTING_LOANS = [
  { id: 1, type: 'Home Loan', amount: 2500000, months: 36, status: 'Active', monthly: 82500, icon: '\u{1F3E0}' },
  { id: 2, type: 'Car Finance', amount: 850000, months: 24, status: 'Active', monthly: 39200, icon: '\u{1F697}' },
  { id: 3, type: 'Personal Loan', amount: 150000, months: 12, status: 'Completed', monthly: 13500, icon: '\u{1F4B0}' },
]

const BPMN_STEPS = [
  { key: 'received', label: 'Application Received', color: '#10b981' },
  { key: 'eligibility', label: 'Eligibility Check', color: '#10b981' },
  { key: 'sharia', label: 'Sharia Compliance', color: '#10b981' },
  { key: 'fraud', label: 'Fraud Analysis', color: '#3b82f6' },
  { key: 'credit', label: 'Credit Score', color: '#6366f1' },
  { key: 'review', label: 'Human Review', color: '#f59e0b' },
  { key: 'decision', label: 'Decision', color: '#10b981' },
]

type StepStatus = 'completed' | 'in-progress' | 'pending'

export default function LoanPage() {
  const [name] = useState('Madiha Ayaz')
  const [amount, setAmount] = useState('')
  const [purpose, setPurpose] = useState('Personal')
  const [duration, setDuration] = useState(12)
  const [income, setIncome] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [stepStatuses, setStepStatuses] = useState<StepStatus[]>(['pending', 'pending', 'pending', 'pending', 'pending', 'pending', 'pending'])
  const [showResult, setShowResult] = useState(false)
  const timers = useRef<ReturnType<typeof setTimeout>[]>([])

  useEffect(() => {
    return () => timers.current.forEach(clearTimeout)
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!amount || !income) return
    setSubmitted(true)
    setShowResult(false)
    setStepStatuses(['completed', 'completed', 'completed', 'in-progress', 'pending', 'pending', 'pending'])

    timers.current.forEach(clearTimeout)
    timers.current = [
      setTimeout(() => setStepStatuses(['completed', 'completed', 'completed', 'completed', 'in-progress', 'pending', 'pending']), 2000),
      setTimeout(() => setStepStatuses(['completed', 'completed', 'completed', 'completed', 'completed', 'in-progress', 'pending']), 4000),
      setTimeout(() => setStepStatuses(['completed', 'completed', 'completed', 'completed', 'completed', 'completed', 'in-progress']), 6000),
      setTimeout(() => { setStepStatuses(['completed', 'completed', 'completed', 'completed', 'completed', 'completed', 'completed']); setShowResult(true) }, 8000),
    ]
  }

  const amt = parseFloat(amount) || 0
  const monthlyInstallment = duration > 0 ? Math.round(amt / duration * 1.08) : 0
  const caseId = 'CASE-' + Math.random().toString(36).slice(2, 6).toUpperCase()

  const reset = () => {
    timers.current.forEach(clearTimeout)
    setSubmitted(false)
    setShowResult(false)
    setStepStatuses(['pending', 'pending', 'pending', 'pending', 'pending', 'pending', 'pending'])
  }

  return (
    <div className="page">
      <ThreeDBackground />
      <h1><span className="gradient-text">Loan Application</span></h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
        <div className="card">
          <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 16 }}>{submitted ? 'Application Submitted' : 'Apply for a Loan'}</h3>
          {!submitted ? (
            <form onSubmit={handleSubmit}>
              <div className="form-group" style={{ marginBottom: 12 }}>
                <label>Full Name</label>
                <input type="text" value={name} disabled style={{ opacity: 0.7 }} />
              </div>
              <div className="form-group" style={{ marginBottom: 12 }}>
                <label>Amount (PKR)</label>
                <input type="number" value={amount} onChange={e => setAmount(e.target.value)} placeholder="500000" min="1" required />
              </div>
              <div className="form-group" style={{ marginBottom: 12 }}>
                <label>Purpose</label>
                <select value={purpose} onChange={e => setPurpose(e.target.value)}>
                  <option>Home</option><option>Car</option><option>Business</option><option>Education</option><option>Personal</option>
                </select>
              </div>
              <div className="form-group" style={{ marginBottom: 12 }}>
                <label>Duration (months)</label>
                <select value={duration} onChange={e => setDuration(Number(e.target.value))}>
                  <option value={12}>12 months</option><option value={24}>24 months</option><option value={36}>36 months</option><option value={60}>60 months</option>
                </select>
              </div>
              <div className="form-group" style={{ marginBottom: 16 }}>
                <label>Monthly Income (PKR)</label>
                <input type="number" value={income} onChange={e => setIncome(e.target.value)} placeholder="100000" min="1" required />
              </div>
              <motion.button type="submit" className="btn btn-primary" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} style={{ width: '100%' }}>
                Apply via BPMN Workflow
              </motion.button>
            </form>
          ) : (
            <div style={{ textAlign: 'center', padding: 20 }}>
              <div style={{ fontSize: '2rem', marginBottom: 8 }}>\u2705</div>
              <p style={{ color: 'var(--text-muted)' }}>Application submitted! Processing via UiPath Maestro BPMN...</p>
              <button className="btn btn-sm" onClick={reset} style={{ marginTop: 12, background: 'rgba(99,102,241,0.1)', color: 'var(--primary)', border: '1px solid rgba(99,102,241,0.2)' }}>New Application</button>
            </div>
          )}
        </div>

        <div className="card">
          <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 16 }}>BPMN Process Tracker</h3>
          <div style={{ position: 'relative', display: 'flex', flexDirection: 'column', gap: 0 }}>
            {BPMN_STEPS.map((step, i) => {
              const status = stepStatuses[i]
              return (
                <div key={step.key} style={{ display: 'flex', alignItems: 'stretch', gap: 12 }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 32 }}>
                    <div style={{
                      width: 28, height: 28, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7rem', fontWeight: 700, flexShrink: 0,
                      background: status === 'completed' ? step.color : status === 'in-progress' ? step.color : 'rgba(255,255,255,0.06)',
                      color: status === 'completed' || status === 'in-progress' ? '#fff' : 'var(--text-muted)',
                      boxShadow: status === 'in-progress' ? `0 0 12px ${step.color}66` : 'none',
                      animation: status === 'in-progress' ? 'pulse 1.5s infinite' : 'none',
                    }}>
                      {status === 'completed' ? '\u2713' : i + 1}
                    </div>
                    {i < BPMN_STEPS.length - 1 && (
                      <div style={{ width: 2, flex: 1, margin: '2px 0', background: status === 'completed' ? step.color : 'rgba(255,255,255,0.06)' }} />
                    )}
                  </div>
                  <div style={{ flex: 1, paddingBottom: i < BPMN_STEPS.length - 1 ? 12 : 0 }}>
                    <div style={{ fontWeight: 500, fontSize: '0.85rem', color: status === 'pending' ? 'var(--text-muted)' : 'var(--text)' }}>{step.label}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 2 }}>
                      {status === 'completed' ? 'Completed' : status === 'in-progress' ? 'In Progress...' : 'Pending'}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          <AnimatePresence>
            {showResult && (
              <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} style={{ marginTop: 20, padding: 20, background: 'rgba(16,185,129,0.1)', borderRadius: 12, border: '1px solid rgba(16,185,129,0.2)', textAlign: 'center' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: 8 }}>\u2705</div>
                <h2 style={{ color: 'var(--success)', marginBottom: 8 }}>APPROVED</h2>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 12 }}>
                  <div>Approved Amount: <strong style={{ color: 'var(--text)' }}>PKR {amt.toLocaleString()}</strong></div>
                  <div>Monthly Installment: <strong style={{ color: 'var(--text)' }}>PKR {monthlyInstallment.toLocaleString()}</strong></div>
                  <div>Processing Fee: <strong style={{ color: 'var(--text)' }}>PKR 2,500</strong></div>
                  <div>Case ID: <strong style={{ color: 'var(--primary)' }}>{caseId}</strong></div>
                </div>
                <div className="badge badge-safe" style={{ fontSize: '0.7rem' }}>Processed via UiPath Maestro BPMN</div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 16 }}>Your Existing Loans</h3>
      <div className="stats-grid" style={{ marginBottom: 24 }}>
        {EXISTING_LOANS.map(loan => (
          <div key={loan.id} className="stat-card" style={{ textAlign: 'left' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: 8 }}>{loan.icon}</div>
            <div style={{ fontWeight: 600, fontSize: '1rem' }}>{loan.type}</div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>PKR {loan.amount.toLocaleString()}</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontSize: '0.8rem' }}>
              <span>{loan.months} months</span>
              <span>PKR {loan.monthly.toLocaleString()}/mo</span>
            </div>
            <div style={{ marginTop: 8 }}>
              <span className={`badge badge-${loan.status === 'Completed' ? 'safe' : 'critical'}`} style={{ fontSize: '0.65rem' }}>{loan.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
