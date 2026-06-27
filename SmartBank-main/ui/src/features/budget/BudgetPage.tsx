import { useEffect, useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import api from '../../services/api'
import type { BudgetItem, BudgetTransaction } from '../../types'

const BUDGET_CATEGORIES = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Shopping', 'Other']

const FALLBACK_BUDGETS: BudgetItem[] = [
  { id: 1, category: 'Food', planned_amount: 25000, spent_amount: 15000, month: '06', year: '2025' },
  { id: 2, category: 'Transport', planned_amount: 12000, spent_amount: 8500, month: '06', year: '2025' },
  { id: 3, category: 'Shopping', planned_amount: 30000, spent_amount: 22000, month: '06', year: '2025' },
  { id: 4, category: 'Utilities', planned_amount: 8000, spent_amount: 5200, month: '06', year: '2025' },
  { id: 5, category: 'Entertainment', planned_amount: 5000, spent_amount: 3100, month: '06', year: '2025' },
]

const FALLBACK_TXNS: BudgetTransaction[] = [
  { id: 1, budget_id: 1, description: 'Grocery shopping', amount: 4500, date: '2025-06-15' },
  { id: 2, budget_id: 1, description: 'Restaurant dinner', amount: 2800, date: '2025-06-20' },
  { id: 3, budget_id: 3, description: 'Clothing purchase', amount: 8500, date: '2025-06-18' },
  { id: 4, budget_id: 4, description: 'Electricity bill', amount: 3200, date: '2025-06-10' },
  { id: 5, budget_id: 5, description: 'Netflix subscription', amount: 1100, date: '2025-06-05' },
]

const categoryColors: Record<string, string> = {
  Food: '#6366f1',
  Transport: '#f59e0b',
  Utilities: '#10b981',
  Entertainment: '#ec4899',
  Shopping: '#3b82f6',
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

export default function BudgetPage() {
  const [budgets, setBudgets] = useState<BudgetItem[]>([])
  const [transactions, setTransactions] = useState<BudgetTransaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showBudgetForm, setShowBudgetForm] = useState(false)
  const [showTxForm, setShowTxForm] = useState(false)

  const [budgetCategory, setBudgetCategory] = useState('Food')
  const [plannedAmount, setPlannedAmount] = useState('')
  const [budgetMonth, setBudgetMonth] = useState(new Date().toISOString().slice(0, 7))
  const [budgetSubmitting, setBudgetSubmitting] = useState(false)

  const [txBudgetId, setTxBudgetId] = useState<number | null>(null)
  const [txDescription, setTxDescription] = useState('')
  const [txAmount, setTxAmount] = useState('')
  const [txSubmitting, setTxSubmitting] = useState(false)

  const getTxForBudget = (budgetId: number) =>
    transactions.filter((t) => t.budget_id === budgetId)

  const fetchBudgets = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get('/api/budgets')
      setBudgets(res.data.budgets ?? res.data ?? [])
    } catch {
      setBudgets(FALLBACK_BUDGETS)
    } finally {
      setLoading(false)
    }
  }

  const fetchTransactions = async () => {
    try {
      const res = await api.get('/api/budgets/transactions')
      setTransactions(res.data.transactions ?? res.data ?? [])
    } catch {
      setTransactions(FALLBACK_TXNS)
    }
  }

  useEffect(() => {
    fetchBudgets()
    fetchTransactions()
  }, [])

  const handleAddBudget = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!plannedAmount) return
    setBudgetSubmitting(true)
    try {
      const [year, month] = budgetMonth.split('-')
      const res = await api.post('/api/budgets', {
        category: budgetCategory,
        planned_amount: parseFloat(plannedAmount),
        month,
        year,
      })
      if (res.data?.budget) {
        setBudgets((prev) => [...prev, res.data.budget])
      } else {
        await fetchBudgets()
      }
      setPlannedAmount('')
      setBudgetCategory('Food')
      setShowBudgetForm(false)
    } catch {
      setError('Failed to create budget.')
    } finally {
      setBudgetSubmitting(false)
    }
  }

  const handleAddTransaction = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!txDescription || !txAmount || !txBudgetId) return
    setTxSubmitting(true)
    try {
      const res = await api.post(`/api/budgets/${txBudgetId}/transactions`, {
        description: txDescription,
        amount: parseFloat(txAmount),
      })
      if (res.data?.transaction) {
        setTransactions((prev) => [...prev, res.data.transaction])
      } else {
        await fetchTransactions()
      }
      await fetchBudgets()
      setTxDescription('')
      setTxAmount('')
      setTxBudgetId(null)
      setShowTxForm(false)
    } catch {
      setError('Failed to add transaction.')
    } finally {
      setTxSubmitting(false)
    }
  }

  const handleDeleteBudget = async (budgetId: number) => {
    try {
      await api.delete(`/api/budgets/${budgetId}`)
      setBudgets((prev) => prev.filter((b) => b.id !== budgetId))
    } catch {
      setError('Failed to delete budget.')
    }
  }

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat('en-PK', { style: 'currency', currency: 'PKR', maximumFractionDigits: 0 }).format(amount)

  const pieData = useMemo(() => {
    return budgets
      .filter((b) => b.spent_amount > 0)
      .map((b) => ({
        name: b.category,
        value: b.spent_amount,
        color: categoryColors[b.category] || '#6366f1',
      }))
  }, [budgets])

  const totalPlanned = budgets.reduce((sum, b) => sum + b.planned_amount, 0)
  const totalSpent = budgets.reduce((sum, b) => sum + b.spent_amount, 0)
  const overspentBudgets = budgets.filter((b) => b.spent_amount > b.planned_amount)

  return (
    <motion.div className="page" variants={containerVariants} initial="hidden" animate="visible">
      <motion.div variants={itemVariants} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <h1><span className="gradient-text">Budget Planner</span></h1>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <motion.button className="btn btn-primary" onClick={() => setShowBudgetForm(!showBudgetForm)}
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            {showBudgetForm ? 'Cancel' : '+ New Budget'}
          </motion.button>
          <motion.button className="btn" style={{ background: 'rgba(16,185,129,0.15)', color: 'var(--success)', border: '1px solid rgba(16,185,129,0.2)' }}
            onClick={() => setShowTxForm(!showTxForm)} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            {showTxForm ? 'Cancel' : '+ Add Transaction'}
          </motion.button>
        </div>
      </motion.div>

      {error && (
        <motion.div className="card" style={{ border: '1px solid var(--danger)', background: 'rgba(239,68,68,0.05)', marginBottom: 16 }}
          initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <p style={{ color: 'var(--danger)' }}>{error}</p>
        </motion.div>
      )}

      <AnimatePresence>
        {showBudgetForm && (
          <motion.form className="card" onSubmit={handleAddBudget} style={{ marginBottom: 24 }}
            initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.3 }}>
            <h3 style={{ marginBottom: 16, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', fontSize: '0.85rem' }}>Create Budget</h3>
            <div className="form-grid">
              <div className="form-group">
                <label>Category</label>
                <select value={budgetCategory} onChange={(e) => setBudgetCategory(e.target.value)}>
                  {BUDGET_CATEGORIES.map((cat) => (<option key={cat} value={cat}>{cat}</option>))}
                </select>
              </div>
              <div className="form-group">
                <label>Planned Amount (PKR)</label>
                <input type="number" value={plannedAmount} onChange={(e) => setPlannedAmount(e.target.value)} placeholder="50000" min="1" required />
              </div>
              <div className="form-group">
                <label>Month</label>
                <input type="month" value={budgetMonth} onChange={(e) => setBudgetMonth(e.target.value)} required />
              </div>
            </div>
            <motion.button type="submit" className="btn btn-primary" disabled={budgetSubmitting} style={{ marginTop: 12 }}
              whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              {budgetSubmitting ? 'Creating...' : 'Create Budget'}
            </motion.button>
          </motion.form>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showTxForm && (
          <motion.form className="card" onSubmit={handleAddTransaction} style={{ marginBottom: 24 }}
            initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.3 }}>
            <h3 style={{ marginBottom: 16, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', fontSize: '0.85rem' }}>Add Transaction</h3>
            <div className="form-grid">
              <div className="form-group">
                <label>Budget Category</label>
                <select value={txBudgetId ?? ''} onChange={(e) => setTxBudgetId(Number(e.target.value))} required>
                  <option value="" disabled>Select a budget</option>
                  {budgets.map((b) => (
                    <option key={b.id} value={b.id}>{b.category} ({formatCurrency(b.planned_amount)})</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Description</label>
                <input type="text" value={txDescription} onChange={(e) => setTxDescription(e.target.value)} placeholder="e.g., Grocery shopping" required />
              </div>
              <div className="form-group">
                <label>Amount (PKR)</label>
                <input type="number" value={txAmount} onChange={(e) => setTxAmount(e.target.value)} placeholder="1500" min="1" required />
              </div>
            </div>
            <motion.button type="submit" className="btn" style={{ background: 'rgba(16,185,129,0.15)', color: 'var(--success)', border: '1px solid rgba(16,185,129,0.2)', marginTop: 12 }}
              disabled={txSubmitting} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              {txSubmitting ? 'Adding...' : 'Add Transaction'}
            </motion.button>
          </motion.form>
        )}
      </AnimatePresence>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: 60 }}>
          <div className="spinner" />
          <p style={{ marginTop: 12, color: 'var(--text-muted)' }}>Loading budgets...</p>
        </div>
      ) : budgets.length === 0 ? (
        <motion.div className="card" style={{ textAlign: 'center', padding: 60 }} variants={itemVariants}>
          <div style={{ fontSize: '3rem', marginBottom: 12 }}>💰</div>
          <h3 style={{ marginBottom: 8 }}>No Budgets Yet</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: 20 }}>
            Create your first monthly budget to track spending across categories.
          </p>
          {!showBudgetForm && (
            <motion.button className="btn btn-primary" onClick={() => setShowBudgetForm(true)}
              whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              Create Your First Budget
            </motion.button>
          )}
        </motion.div>
      ) : (
        <>
          <motion.div className="stats-grid" variants={itemVariants} style={{ marginBottom: 24 }}>
            <div className="stat-card">
              <span>Total Planned</span>
              <strong style={{ color: 'var(--primary)' }}>{formatCurrency(totalPlanned)}</strong>
            </div>
            <div className="stat-card">
              <span>Total Spent</span>
              <strong style={{ color: totalSpent > totalPlanned ? 'var(--danger)' : 'var(--success)' }}>{formatCurrency(totalSpent)}</strong>
            </div>
            <div className="stat-card">
              <span>Remaining</span>
              <strong style={{ color: totalPlanned - totalSpent > 0 ? 'var(--success)' : 'var(--danger)' }}>{formatCurrency(totalPlanned - totalSpent)}</strong>
            </div>
            <div className="stat-card">
              <span>Overspent Categories</span>
              <strong style={{ color: overspentBudgets.length > 0 ? 'var(--danger)' : 'var(--success)' }}>{overspentBudgets.length}</strong>
            </div>
          </motion.div>

          {pieData.length > 0 && (
            <motion.div className="card" variants={itemVariants} style={{ marginBottom: 24 }}>
              <h3 style={{ color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', fontSize: '0.85rem', marginBottom: 16 }}>Spending Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                    {pieData.map((entry, i) => (<Cell key={i} fill={entry.color} />))}
                  </Pie>
                  <Tooltip contentStyle={{ background: 'rgba(15,16,40,0.9)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 8 }} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </motion.div>
          )}

          <motion.div className="goals-grid" variants={containerVariants} initial="hidden" animate="visible">
            {budgets.map((budget) => {
              const color = categoryColors[budget.category] || '#6366f1'
              const spentPct = budget.planned_amount > 0 ? (budget.spent_amount / budget.planned_amount) * 100 : 0
              const overspent = spentPct > 100
              const remaining = budget.planned_amount - budget.spent_amount
              return (
                <motion.div key={budget.id} className="card goal-card" variants={itemVariants} layout
                  whileHover={{ y: -4, boxShadow: '0 8px 40px rgba(0,0,0,0.3)' }}
                  style={{ border: overspent ? '1px solid rgba(239,68,68,0.3)' : undefined }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                    <div>
                      <h3 style={{ fontSize: '1.1rem', marginBottom: 4 }}>{budget.category}</h3>
                      <span className="badge" style={{ background: `${color}20`, color, borderColor: `${color}30` }}>{budget.month}/{budget.year}</span>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontWeight: 700, fontSize: '1.1rem', color: overspent ? 'var(--danger)' : 'var(--text)' }}>{formatCurrency(budget.spent_amount)}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>of {formatCurrency(budget.planned_amount)}</div>
                    </div>
                  </div>
                  <div className="progress-bar" style={{ background: 'rgba(99,102,241,0.1)', height: 12 }}>
                    <motion.div className="progress-fill"
                      style={{
                        background: overspent ? 'linear-gradient(90deg, var(--danger), #f87171)' : `linear-gradient(90deg, ${color}, ${color}88)`,
                        height: 12,
                      }}
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(spentPct, 100)}%` }}
                      transition={{ duration: 1, ease: 'easeOut' }} />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontSize: '0.85rem' }}>
                    <span style={{ color: overspent ? 'var(--danger)' : 'var(--success)', fontWeight: 600 }}>
                      {overspent ? 'Overspent by ' : 'Remaining '}{formatCurrency(Math.abs(remaining))}
                    </span>
                    <span style={{ color: 'var(--text-muted)' }}>{spentPct.toFixed(1)}%</span>
                  </div>
                  {getTxForBudget(budget.id).length > 0 && (
                    <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--border)' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>Transactions</div>
                      {getTxForBudget(budget.id).slice(0, 3).map((tx) => (
                        <div key={tx.id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', padding: '2px 0' }}>
                          <span>{tx.description}</span>
                          <span style={{ color: 'var(--danger)' }}>-{formatCurrency(tx.amount)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  <div style={{ marginTop: 12 }}>
                    <motion.button className="btn btn-sm"
                      style={{ background: 'rgba(239,68,68,0.1)', color: 'var(--danger)', border: '1px solid rgba(239,68,68,0.2)' }}
                      onClick={() => handleDeleteBudget(budget.id)} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                      Delete
                    </motion.button>
                  </div>
                </motion.div>
              )
            })}
          </motion.div>
        </>
      )}
    </motion.div>
  )
}
