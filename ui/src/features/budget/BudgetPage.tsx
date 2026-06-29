import { useEffect, useState, useMemo, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import api from '../../services/api'
import type { BudgetItem, BudgetTransaction } from '../../types'

const BUDGET_CATEGORIES = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Shopping', 'Other']

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
  const [availableBalance, setAvailableBalance] = useState(0)
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

  const fetchBudgets = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get('/api/budgets')
      const data = res.data
      setBudgets(data.budgets ?? [])
      setAvailableBalance(data.available_balance ?? 0)
    } catch {
      setBudgets([])
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchTransactions = useCallback(async () => {
    try {
      const res = await api.get('/api/budgets/transactions')
      setTransactions(res.data.transactions ?? res.data ?? [])
    } catch {
      setTransactions([])
    }
  }, [])

  useEffect(() => {
    fetchBudgets()
    fetchTransactions()
  }, [fetchBudgets, fetchTransactions])

  const handleAddBudget = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!plannedAmount) return
    setBudgetSubmitting(true)
    setError(null)
    try {
      const [year, month] = budgetMonth.split('-')
      const amt = parseFloat(plannedAmount)
      if (amt > availableBalance) {
        setError(`Insufficient balance for this budget. Available: PKR ${availableBalance.toLocaleString()}, Budget: PKR ${amt.toLocaleString()}`)
        setBudgetSubmitting(false)
        return
      }
      const res = await api.post('/api/budgets', {
        category: budgetCategory,
        planned_amount: amt,
        month,
        year,
      })
      if (res.data?.id) {
        setBudgets((prev) => [...prev, {
          id: res.data.id,
          category: res.data.category,
          planned_amount: res.data.planned_amount,
          spent_amount: 0,
          remaining_amount: res.data.remaining_amount ?? res.data.planned_amount,
          reserved_amount: res.data.reserved_amount ?? res.data.planned_amount,
          month,
          year,
        }])
        setAvailableBalance((prev) => prev - amt)
      } else {
        await fetchBudgets()
      }
      setPlannedAmount('')
      setBudgetCategory('Food')
      setShowBudgetForm(false)
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.response?.data?.error || 'Failed to create budget.'
      setError(msg)
    } finally {
      setBudgetSubmitting(false)
    }
  }

  const handleAddTransaction = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!txDescription || !txAmount || !txBudgetId) return
    setTxSubmitting(true)
    setError(null)
    try {
      const res = await api.post('/api/budgets/transaction', {
        budget_id: txBudgetId,
        description: txDescription,
        amount: parseFloat(txAmount),
      })
      await fetchBudgets()
      await fetchTransactions()
      setTxDescription('')
      setTxAmount('')
      setTxBudgetId(null)
      setShowTxForm(false)
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.response?.data?.error || 'Failed to add transaction.'
      setError(msg)
    } finally {
      setTxSubmitting(false)
    }
  }

  const handleDeleteBudget = async (budgetId: number) => {
    setError(null)
    try {
      const res = await api.delete(`/api/budgets/${budgetId}`)
      setBudgets((prev) => prev.filter((b) => b.id !== budgetId))
      setAvailableBalance((prev) => prev + (res.data?.unreserved ?? 0))
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
  const totalRemaining = budgets.reduce((sum, b) => sum + (b.remaining_amount ?? b.planned_amount - b.spent_amount), 0)
  const totalReserved = budgets.reduce((sum, b) => sum + (b.reserved_amount ?? b.planned_amount - b.spent_amount), 0)
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

      <motion.div className="stats-grid" variants={itemVariants} style={{ marginBottom: 24 }}>
        <div className="stat-card">
          <span>Available Balance</span>
          <strong style={{ color: 'var(--success)' }}>{formatCurrency(availableBalance)}</strong>
        </div>
      </motion.div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: 'clamp(20px, 8vw, 60px)' }}>
          <div className="spinner" />
          <p style={{ marginTop: 12, color: 'var(--text-muted)' }}>Loading budgets...</p>
        </div>
      ) : budgets.length === 0 ? (
        <motion.div className="card" style={{ textAlign: 'center', padding: 'clamp(20px, 8vw, 60px)' }} variants={itemVariants}>
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
              <span>Planned Budget</span>
              <strong style={{ color: 'var(--primary)' }}>{formatCurrency(totalPlanned)}</strong>
            </div>
            <div className="stat-card">
              <span>Spent</span>
              <strong style={{ color: totalSpent > totalPlanned ? 'var(--danger)' : 'var(--success)' }}>{formatCurrency(totalSpent)}</strong>
            </div>
            <div className="stat-card">
              <span>Remaining</span>
              <strong style={{ color: totalRemaining > 0 ? 'var(--success)' : 'var(--danger)' }}>{formatCurrency(totalRemaining)}</strong>
            </div>
            <div className="stat-card">
              <span>Saved / Reserved</span>
              <strong style={{ color: 'var(--primary)' }}>{formatCurrency(totalReserved)}</strong>
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
              const remaining = budget.remaining_amount ?? (budget.planned_amount - budget.spent_amount)
              const reserved = budget.reserved_amount ?? remaining
              const spentPct = budget.planned_amount > 0 ? (budget.spent_amount / budget.planned_amount) * 100 : 0
              const savingPct = budget.planned_amount > 0 ? (remaining / budget.planned_amount) * 100 : 0
              const overspent = spentPct > 100
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
                      <div style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--success)' }}>{formatCurrency(reserved)}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Saved</div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    <span>Spent: {formatCurrency(budget.spent_amount)}</span>
                    <span>Planned: {formatCurrency(budget.planned_amount)}</span>
                  </div>
                  <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
                    <div className="progress-bar" style={{ background: 'rgba(99,102,241,0.1)', height: 12, flex: 1 }}>
                      <motion.div className="progress-fill"
                        style={{
                          background: overspent ? 'linear-gradient(90deg, var(--danger), #f87171)' : `linear-gradient(90deg, ${color}, ${color}88)`,
                          height: 12,
                        }}
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(spentPct, 100)}%` }}
                        transition={{ duration: 1, ease: 'easeOut' }} />
                    </div>
                    <div className="progress-bar" style={{ background: 'rgba(16,185,129,0.1)', height: 12, flex: 1 }}>
                      <motion.div className="progress-fill"
                        style={{ background: 'linear-gradient(90deg, #10b981, #34d399)', height: 12 }}
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(savingPct, 100)}%` }}
                        transition={{ duration: 1, ease: 'easeOut' }} />
                    </div>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: 4 }}>
                    <span style={{ color: 'var(--danger)' }}>Spent {spentPct.toFixed(0)}%</span>
                    <span style={{ color: 'var(--success)' }}>Saved {savingPct.toFixed(0)}%</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginTop: 4 }}>
                    <span style={{ color: remaining > 0 ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }}>
                      {remaining > 0 ? `Remaining: ${formatCurrency(remaining)}` : 'Exhausted'}
                    </span>
                    <span style={{ color: 'var(--text-muted)' }}>Reserved: {formatCurrency(reserved)}</span>
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
