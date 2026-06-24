import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import api from '../../services/api'
import type { GoalItem } from '../../types'

const CATEGORIES = ['Savings', 'Debt', 'Investment', 'Education', 'Travel', 'Health', 'Other']

const categoryColors: Record<string, string> = {
  Savings: '#6366f1',
  Debt: '#ef4444',
  Investment: '#10b981',
  Education: '#3b82f6',
  Travel: '#f59e0b',
  Health: '#ec4899',
  Other: '#8b5cf6',
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
}

function CircularProgress({
  current,
  target,
  color,
  size = 100,
  strokeWidth = 8,
}: {
  current: number
  target: number
  color: string
  size?: number
  strokeWidth?: number
}) {
  const r = (size - strokeWidth) / 2
  const circ = 2 * Math.PI * r
  const pct = target > 0 ? Math.min(current / target, 1) : 0
  const offset = circ - pct * circ

  return (
    <div style={{ width: size, height: size, position: 'relative', flexShrink: 0 }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: 'rotate(-90deg)' }}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="rgba(99,102,241,0.1)"
          strokeWidth={strokeWidth}
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
        />
      </svg>
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          fontSize: '1.1rem',
          fontWeight: 700,
          color,
        }}
      >
        {Math.round(pct * 100)}%
      </div>
    </div>
  )
}

export default function GoalsPage() {
  const [goals, setGoals] = useState<GoalItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [title, setTitle] = useState('')
  const [targetAmount, setTargetAmount] = useState('')
  const [deadline, setDeadline] = useState('')
  const [category, setCategory] = useState('Savings')
  const [submitting, setSubmitting] = useState(false)
  const [progressGoalId, setProgressGoalId] = useState<number | null>(null)
  const [progressAmount, setProgressAmount] = useState('')
  const [progressSubmitting, setProgressSubmitting] = useState(false)

  const fetchGoals = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get('/api/goals')
      setGoals(res.data.goals ?? res.data ?? [])
    } catch {
      setError('Failed to load financial goals. Server may be unavailable.')
      setGoals([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchGoals()
  }, [])

  const handleAddGoal = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title || !targetAmount || !deadline) return
    setSubmitting(true)
    try {
      const res = await api.post('/api/goals', {
        title,
        target_amount: parseFloat(targetAmount),
        deadline,
        category,
      })
      if (res.data?.goal) {
        setGoals((prev) => [...prev, res.data.goal])
      } else {
        await fetchGoals()
      }
      setTitle('')
      setTargetAmount('')
      setDeadline('')
      setCategory('Savings')
      setShowForm(false)
    } catch {
      setError('Failed to create goal. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleAddProgress = async (goalId: number) => {
    if (!progressAmount || parseFloat(progressAmount) <= 0) return
    setProgressSubmitting(true)
    try {
      const res = await api.patch(`/api/goals/${goalId}/progress`, {
        amount: parseFloat(progressAmount),
      })
      if (res.data?.goal) {
        setGoals((prev) => prev.map((g) => (g.id === goalId ? res.data.goal : g)))
      } else {
        await fetchGoals()
      }
      setProgressAmount('')
      setProgressGoalId(null)
    } catch {
      setError('Failed to update progress.')
    } finally {
      setProgressSubmitting(false)
    }
  }

  const handleDeleteGoal = async (goalId: number) => {
    try {
      await api.delete(`/api/goals/${goalId}`)
      setGoals((prev) => prev.filter((g) => g.id !== goalId))
    } catch {
      setError('Failed to delete goal.')
    }
  }

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat('en-PK', { style: 'currency', currency: 'PKR', maximumFractionDigits: 0 }).format(amount)

  const isGoalOverdue = (deadline: string) => new Date(deadline) < new Date()

  return (
    <motion.div className="page" variants={containerVariants} initial="hidden" animate="visible">
      <motion.div variants={itemVariants} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <h1><span className="gradient-text">Financial Goals</span></h1>
        <motion.button className="btn btn-primary" onClick={() => setShowForm(!showForm)}
          whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          {showForm ? 'Cancel' : '+ New Goal'}
        </motion.button>
      </motion.div>

      {error && (
        <motion.div className="card" style={{ border: '1px solid var(--danger)', background: 'rgba(239,68,68,0.05)', marginBottom: 16 }}
          initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <p style={{ color: 'var(--danger)' }}>{error}</p>
        </motion.div>
      )}

      <AnimatePresence>
        {showForm && (
          <motion.form className="card" onSubmit={handleAddGoal} style={{ marginBottom: 24 }}
            initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.3 }}>
            <h3 style={{ marginBottom: 16, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', fontSize: '0.85rem' }}>Create New Goal</h3>
            <div className="form-grid">
              <div className="form-group">
                <label>Title</label>
                <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g., Save for a car" required />
              </div>
              <div className="form-group">
                <label>Target Amount (PKR)</label>
                <input type="number" value={targetAmount} onChange={(e) => setTargetAmount(e.target.value)} placeholder="500000" min="1" required />
              </div>
              <div className="form-group">
                <label>Deadline</label>
                <input type="date" value={deadline} onChange={(e) => setDeadline(e.target.value)} required />
              </div>
              <div className="form-group">
                <label>Category</label>
                <select value={category} onChange={(e) => setCategory(e.target.value)}>
                  {CATEGORIES.map((cat) => (<option key={cat} value={cat}>{cat}</option>))}
                </select>
              </div>
            </div>
            <motion.button type="submit" className="btn btn-primary" disabled={submitting} style={{ marginTop: 12 }}
              whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              {submitting ? 'Creating...' : 'Create Goal'}
            </motion.button>
          </motion.form>
        )}
      </AnimatePresence>

      {/* Loading */}
      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: 60 }}>
          <div className="spinner" />
          <p style={{ marginTop: 12, color: 'var(--text-muted)' }}>Loading goals...</p>
        </div>
      ) : goals.length === 0 ? (
        <motion.div className="card" style={{ textAlign: 'center', padding: 60 }} variants={itemVariants}>
          <div style={{ fontSize: '3rem', marginBottom: 12 }}>🎯</div>
          <h3 style={{ marginBottom: 8 }}>No Financial Goals Yet</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: 20 }}>
            Start by creating your first financial goal. Set savings targets, plan for investments, or track debt repayment.
          </p>
          {!showForm && (
            <motion.button className="btn btn-primary" onClick={() => setShowForm(true)}
              whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              Create Your First Goal
            </motion.button>
          )}
        </motion.div>
      ) : (
        <motion.div className="goals-grid" variants={containerVariants} initial="hidden" animate="visible">
          {goals.map((goal) => {
            const color = categoryColors[goal.category] || '#6366f1'
            const isComplete = goal.current_amount >= goal.target_amount
            const overdue = !isComplete && isGoalOverdue(goal.deadline)
            return (
              <motion.div key={goal.id} className="card goal-card" variants={itemVariants} layout
                whileHover={{ y: -4, boxShadow: '0 8px 40px rgba(0,0,0,0.3)' }}
                style={{ border: overdue ? '1px solid rgba(239,68,68,0.3)' : undefined }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 16 }}>
                  <CircularProgress current={goal.current_amount} target={goal.target_amount} color={color} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <h3 style={{ fontSize: '1.1rem', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
                      {goal.title}
                      {isComplete && <span>✅</span>}
                      {overdue && <span style={{ fontSize: '0.8rem', color: 'var(--danger)' }}>⚠️ Overdue</span>}
                    </h3>
                    <span className="badge" style={{ background: `${color}20`, color, borderColor: `${color}30` }}>{goal.category}</span>
                  </div>
                </div>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Progress</span>
                    <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{formatCurrency(goal.current_amount)} / {formatCurrency(goal.target_amount)}</span>
                  </div>
                  <div className="progress-bar" style={{ background: 'rgba(99,102,241,0.1)' }}>
                    <motion.div className="progress-fill"
                      style={{ background: `linear-gradient(90deg, ${color}, ${color}88)` }}
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min((goal.current_amount / goal.target_amount) * 100, 100)}%` }}
                      transition={{ duration: 1, ease: 'easeOut' }} />
                  </div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 12, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  <span>Deadline: {new Date(goal.deadline).toLocaleDateString()}</span>
                  <span>Status: {goal.status}</span>
                </div>
                <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
                  {!isComplete && (
                    <motion.button className="btn btn-sm"
                      style={{ background: 'rgba(99,102,241,0.15)', color: 'var(--primary)', border: '1px solid rgba(99,102,241,0.2)' }}
                      onClick={() => setProgressGoalId(progressGoalId === goal.id ? null : goal.id)}
                      whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                      {progressGoalId === goal.id ? 'Cancel' : '+ Add Progress'}
                    </motion.button>
                  )}
                  <motion.button className="btn btn-sm"
                    style={{ background: 'rgba(239,68,68,0.1)', color: 'var(--danger)', border: '1px solid rgba(239,68,68,0.2)' }}
                    onClick={() => handleDeleteGoal(goal.id)}
                    whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    Delete
                  </motion.button>
                </div>
                {progressGoalId === goal.id && (
                  <motion.div style={{ marginTop: 12, display: 'flex', gap: 8 }}
                    initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
                    <input type="number" value={progressAmount}
                      onChange={(e) => setProgressAmount(e.target.value)}
                      placeholder="Amount to add" min="1" style={{ flex: 1 }} />
                    <motion.button className="btn btn-sm btn-primary"
                      onClick={() => handleAddProgress(goal.id)} disabled={progressSubmitting || !progressAmount}
                      whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                      {progressSubmitting ? '...' : 'Add'}
                    </motion.button>
                  </motion.div>
                )}
              </motion.div>
            )
          })}
        </motion.div>
      )}
    </motion.div>
  )
}