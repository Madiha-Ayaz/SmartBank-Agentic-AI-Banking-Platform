import { useState, useMemo, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import ThreeDBackground from '../../components/ThreeDBackground'
import { useSessionContext } from '../../stores/sessionContextStore'
import api from '../../services/api'

interface TransactionItem {
  transaction_id: string
  sender_account_number: string
  receiver_account_number: string
  sender_name?: string
  receiver_name?: string
  transaction_amount: number
  transaction_type: string
  transaction_status: string
  remaining_balance?: number
  created_at: string
}

function formatTxn(t: TransactionItem) {
  const amt = Number(t.transaction_amount)
  return {
    id: t.transaction_id,
    date: t.created_at ? new Date(t.created_at).toLocaleDateString() : '-',
    time: t.created_at ? new Date(t.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '-',
    description: `${t.sender_name || t.sender_account_number} → ${t.receiver_name || t.receiver_account_number}`,
    category: t.transaction_type === 'routing_transfer' ? 'Transfer' : t.transaction_type || 'Transfer',
    amount: amt,
    type: 'debit',
    status: t.transaction_status?.toLowerCase() || 'completed',
    ref: t.transaction_id,
    merchant: t.sender_name || t.sender_account_number,
    icon: '\u{1F4B1}',
    remaining: t.remaining_balance,
  }
}

export default function TransactionsPage() {
  const navigate = useNavigate()
  const sessionCtx = useSessionContext()
  const setFlaggedCount = useSessionContext((s) => s.setFlaggedCount)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('All')
  const [catFilter, setCatFilter] = useState('All')
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [showFlaggedOnly, setShowFlaggedOnly] = useState(false)
  const [txns, setTxns] = useState<TransactionItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/api/transactions/all').then(r => {
      if (Array.isArray(r.data)) setTxns(r.data)
      else if (r.data.transactions) setTxns(r.data.transactions)
      setLoading(false)
    }).catch(e => { console.error('Txn fetch error:', e); setLoading(false) })
  }, [])

  const TRANSACTIONS = useMemo(() => txns.map(formatTxn), [txns])

  const CATEGORIES = ['All', ...new Set(TRANSACTIONS.map(t => t.category))]

  const CAT_COLORS: Record<string, string> = {
    Income: '#10b981', Shopping: '#6366f1', Food: '#f59e0b', Transport: '#3b82f6', Utilities: '#8b5cf6',
    Transfer: '#06b6d4', Entertainment: '#ec4899', Groceries: '#14b8a6', Health: '#f43f5e',
    Business: '#0ea5e9', Cash: '#f97316', Education: '#a855f7',
  }

  const totalDebit = useMemo(() => TRANSACTIONS.reduce((s, t) => s + t.amount, 0), [TRANSACTIONS])
  const totalCount = TRANSACTIONS.length

  const filtered = useMemo(() => {
    return TRANSACTIONS.filter(t => {
      if (search) {
        const q = search.toLowerCase()
        if (!t.description.toLowerCase().includes(q) && !t.merchant.toLowerCase().includes(q) && !t.ref.toLowerCase().includes(q)) return false
      }
      if (catFilter !== 'All' && t.category !== catFilter) return false
      return true
    })
  }, [search, catFilter, TRANSACTIONS])

  const fmt = (n: number) => '$' + n.toLocaleString()

  if (loading) {
    return <div className="page"><ThreeDBackground /><h1><span className="gradient-text">Transactions</span></h1><div style={{ textAlign: 'center', padding: 60, color: 'var(--text-muted)' }}>Loading...</div></div>
  }

  return (
    <div className="page">
      <ThreeDBackground />
      <h1><span className="gradient-text">Transactions</span></h1>

      <div className="stats-grid" style={{ marginBottom: 20 }}>
        <div className="stat-card"><span>Total</span><strong>{totalCount}</strong></div>
        <div className="stat-card"><span>Total Amount</span><strong style={{ color: '#f59e0b' }}>{fmt(totalDebit)}</strong></div>
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap', alignItems: 'center' }}>
        <input type="text" placeholder="Search..." value={search} onChange={e => setSearch(e.target.value)}
          style={{ padding: '10px 16px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: '0.9rem', minWidth: 'min(260px, 100%)', flex: 1 }} />
      </div>

      <div style={{ display: 'flex', gap: 6, marginBottom: 20, flexWrap: 'wrap' }}>
        {CATEGORIES.map(c => (
          <button key={c} className="btn btn-sm" onClick={() => setCatFilter(c)}
            style={{
              background: catFilter === c ? (CAT_COLORS[c] || 'var(--primary)') : 'rgba(255,255,255,0.04)',
              color: catFilter === c ? '#fff' : 'var(--text-muted)', border: 'none',
            }}>{c}</button>
        ))}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {filtered.map(t => {
          const isExpanded = expandedId === t.id
          return (
            <motion.div key={t.id} layout className="card" style={{ padding: '14px 18px', cursor: 'pointer' }}
              onClick={() => setExpandedId(isExpanded ? null : t.id)} whileHover={{ scale: 1.005 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: `${CAT_COLORS[t.category] || '#6366f1'}20`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', flexShrink: 0 }}>
                  {t.icon}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{t.description}</div>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 2 }}>
                    <span className="badge" style={{ background: `${CAT_COLORS[t.category] || '#6366f1'}20`, color: CAT_COLORS[t.category] || '#6366f1', border: 'none', fontSize: '0.65rem' }}>{t.category}</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t.date} {t.time}</span>
                    {t.status !== 'completed' && (
                      <span className={`badge badge-${t.status === 'pending' ? 'warning' : t.status === 'failed' ? 'danger' : 'safe'}`} style={{ fontSize: '0.6rem', padding: '1px 6px' }}>{t.status}</span>
                    )}
                  </div>
                </div>
                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <div style={{ fontWeight: 700, color: 'var(--text)' }}>
                    {fmt(t.amount)}
                  </div>
                </div>
              </div>
              <AnimatePresence>
                {isExpanded && (
                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} style={{ overflow: 'hidden' }}>
                    <div className="grid-responsive" style={{ marginTop: 14, paddingTop: 14, borderTop: '1px solid var(--border)', gap: 8, fontSize: '0.85rem' }}>
                      <div><span style={{ color: 'var(--text-muted)' }}>Reference: </span>{t.ref}</div>
                      <div><span style={{ color: 'var(--text-muted)' }}>Merchant: </span>{t.merchant}</div>
                      <div><span style={{ color: 'var(--text-muted)' }}>Category: </span>{t.category}</div>
                      <div><span style={{ color: 'var(--text-muted)' }}>Status: </span><span className={`badge badge-${t.status === 'completed' ? 'safe' : t.status === 'pending' ? 'warning' : 'danger'}`}>{t.status}</span></div>
                      <div><span style={{ color: 'var(--text-muted)' }}>Amount: </span><span style={{ fontWeight: 600 }}>{fmt(t.amount)}</span></div>
                      {(t as any).remaining !== undefined && (
                        <div><span style={{ color: 'var(--text-muted)' }}>Balance After: </span><span style={{ color: '#10b981', fontWeight: 600 }}>${Number((t as any).remaining).toLocaleString()}</span></div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )
        })}
        {filtered.length === 0 && (
          <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>No transactions found.</div>
        )}
      </div>
    </div>
  )
}
