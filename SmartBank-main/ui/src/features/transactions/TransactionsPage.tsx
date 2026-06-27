import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ThreeDBackground from '../../components/ThreeDBackground'

const TRANSACTIONS = [
  { id: 1, date: '2025-06-27', time: '09:30', description: 'Salary Credit TechCorp', category: 'Income', amount: 185000, type: 'credit', status: 'completed', card: '•••• 3310', ref: 'SAL-2025-06-001', merchant: 'TechCorp Solutions (Pvt) Ltd', icon: '\u{1F3E2}' },
  { id: 2, date: '2025-06-26', time: '14:15', description: 'Careem Ride', category: 'Transport', amount: 420, type: 'debit', status: 'completed', card: '•••• 3310', ref: 'CRM-98472', merchant: 'Careem Networks', icon: '\u{1F698}' },
  { id: 3, date: '2025-06-26', time: '12:00', description: 'Khaadi DHA Phase 6', category: 'Shopping', amount: 8750, type: 'debit', status: 'completed', card: '•••• 8843', ref: 'POS-8821', merchant: 'Khaadi Retail', icon: '\u{1F45A}' },
  { id: 4, date: '2025-06-25', time: '20:45', description: 'Nandos Clifton', category: 'Food', amount: 3200, type: 'debit', status: 'completed', card: '•••• 3310', ref: 'POS-7734', merchant: 'Nandos Pakistan', icon: '\u{1F354}' },
  { id: 5, date: '2025-06-25', time: '10:00', description: 'PTCL Bill', category: 'Utilities', amount: 2100, type: 'debit', status: 'completed', card: '•••• 8843', ref: 'PTCL-0625', merchant: 'PTCL', icon: '\u{1F4DE}' },
  { id: 6, date: '2025-06-24', time: '16:30', description: 'Online Transfer to Ali Raza', category: 'Transfer', amount: 15000, type: 'debit', status: 'completed', card: '•••• 3310', ref: 'IBFT-66501', merchant: 'Ali Raza', icon: '\u{1F4B1}' },
  { id: 7, date: '2025-06-24', time: '08:00', description: 'Netflix', category: 'Entertainment', amount: 1100, type: 'debit', status: 'completed', card: '•••• 6677', ref: 'SUB-99001', merchant: 'Netflix Inc.', icon: '\u{1F3AC}' },
  { id: 8, date: '2025-06-23', time: '18:20', description: 'Imtiaz Store Gulshan', category: 'Groceries', amount: 6340, type: 'debit', status: 'completed', card: '•••• 8843', ref: 'POS-6612', merchant: 'Imtiaz Super Store', icon: '\u{1F96B}' },
  { id: 9, date: '2025-06-23', time: '11:45', description: 'JazzCash Received Sana B', category: 'Income', amount: 5000, type: 'credit', status: 'completed', card: '•••• 3310', ref: 'JC-77201', merchant: 'Sana B', icon: '\u{1F4B5}' },
  { id: 10, date: '2025-06-22', time: '15:00', description: 'Daraz.pk Purchase', category: 'Shopping', amount: 4299, type: 'debit', status: 'completed', card: '•••• 6677', ref: 'DZ-332415', merchant: 'Daraz Pakistan', icon: '\u{1F6CD}' },
  { id: 11, date: '2025-06-22', time: '09:00', description: 'SSGC Gas Bill', category: 'Utilities', amount: 1850, type: 'debit', status: 'completed', card: '•••• 3310', ref: 'SSGC-0622', merchant: 'Sui Southern Gas', icon: '\u{1F525}' },
  { id: 12, date: '2025-06-21', time: '13:30', description: 'PSO Fuel', category: 'Transport', amount: 7500, type: 'debit', status: 'completed', card: '•••• 8843', ref: 'POS-5512', merchant: 'PSO Petrol Station', icon: '\u{26FD}' },
  { id: 13, date: '2025-06-21', time: '07:00', description: 'ATM Withdrawal HBL', category: 'Cash', amount: 20000, type: 'debit', status: 'completed', card: '•••• 3310', ref: 'ATM-4401', merchant: 'HBL ATM', icon: '\u{1F3E6}' },
  { id: 14, date: '2025-06-20', time: '16:00', description: 'Doctor Aga Khan', category: 'Health', amount: 3000, type: 'debit', status: 'pending', card: '•••• 8843', ref: 'HSP-11802', merchant: 'Aga Khan University Hospital', icon: '\u{1F3E5}' },
  { id: 15, date: '2025-06-20', time: '11:15', description: 'Amazon AWS', category: 'Business', amount: 12400, type: 'debit', status: 'completed', card: '•••• 3310', ref: 'AWS-772-443', merchant: 'Amazon Web Services', icon: '\u{2601}' },
  { id: 16, date: '2025-06-19', time: '14:00', description: 'Freelance Upwork', category: 'Income', amount: 45000, type: 'credit', status: 'completed', card: '•••• 3310', ref: 'UPW-66201', merchant: 'Upwork Global', icon: '\u{1F4BB}' },
  { id: 17, date: '2025-06-19', time: '10:30', description: 'KESC Electricity', category: 'Utilities', amount: 9200, type: 'debit', status: 'failed', card: '•••• 6677', ref: 'KESC-0619', merchant: 'K-Electric', icon: '\u{26A1}' },
  { id: 18, date: '2025-06-18', time: '21:00', description: 'McDonalds Tariq Road', category: 'Food', amount: 1650, type: 'debit', status: 'completed', card: '•••• 8843', ref: 'POS-4421', merchant: 'McDonalds Pakistan', icon: '\u{1F539}' },
  { id: 19, date: '2025-06-18', time: '07:30', description: 'Spotify Premium', category: 'Entertainment', amount: 350, type: 'debit', status: 'completed', card: '•••• 3310', ref: 'SUB-7710', merchant: 'Spotify AB', icon: '\u{1F3B5}' },
  { id: 20, date: '2025-06-17', time: '08:00', description: 'City School Fee', category: 'Education', amount: 28000, type: 'debit', status: 'completed', card: '•••• 8843', ref: 'SCH-0625', merchant: 'City School System', icon: '\u{1F393}' },
]

const CATEGORIES = ['All', 'Income', 'Shopping', 'Food', 'Transport', 'Utilities', 'Transfer', 'Entertainment', 'Groceries', 'Health', 'Business', 'Cash', 'Education']
const TYPE_FILTERS = ['All', 'Credit', 'Debit']

const CAT_COLORS: Record<string, string> = {
  Income: '#10b981', Shopping: '#6366f1', Food: '#f59e0b', Transport: '#3b82f6', Utilities: '#8b5cf6',
  Transfer: '#06b6d4', Entertainment: '#ec4899', Groceries: '#14b8a6', Health: '#f43f5e',
  Business: '#0ea5e9', Cash: '#f97316', Education: '#a855f7',
}

export default function TransactionsPage() {
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('All')
  const [catFilter, setCatFilter] = useState('All')
  const [expandedId, setExpandedId] = useState<number | null>(null)

  const filtered = useMemo(() => {
    return TRANSACTIONS.filter(t => {
      if (search) {
        const q = search.toLowerCase()
        if (!t.description.toLowerCase().includes(q) && !t.merchant.toLowerCase().includes(q) && !t.ref.toLowerCase().includes(q)) return false
      }
      if (typeFilter === 'Credit' && t.type !== 'credit') return false
      if (typeFilter === 'Debit' && t.type !== 'debit') return false
      if (catFilter !== 'All' && t.category !== catFilter) return false
      return true
    })
  }, [search, typeFilter, catFilter])

  const totalIncome = useMemo(() => TRANSACTIONS.filter(t => t.type === 'credit').reduce((s, t) => s + t.amount, 0), [])
  const totalSpent = useMemo(() => TRANSACTIONS.filter(t => t.type === 'debit').reduce((s, t) => s + t.amount, 0), [])
  const netBalance = totalIncome - totalSpent

  const fmt = (n: number) => 'PKR ' + n.toLocaleString()

  return (
    <div className="page">
      <ThreeDBackground />
      <h1><span className="gradient-text">Transactions</span></h1>

      <div className="stats-grid" style={{ marginBottom: 20 }}>
        <div className="stat-card"><span>Total</span><strong>{TRANSACTIONS.length}</strong></div>
        <div className="stat-card"><span>Income</span><strong style={{ color: 'var(--success)' }}>{fmt(totalIncome)}</strong></div>
        <div className="stat-card"><span>Spent</span><strong style={{ color: 'var(--warning)' }}>{fmt(totalSpent)}</strong></div>
        <div className="stat-card"><span>Net Balance</span><strong style={{ color: netBalance >= 0 ? 'var(--success)' : 'var(--danger)' }}>{fmt(netBalance)}</strong></div>
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap', alignItems: 'center' }}>
        <input type="text" placeholder="Search description, merchant, ref..." value={search} onChange={e => setSearch(e.target.value)}
          style={{ padding: '10px 16px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', fontSize: '0.9rem', minWidth: 260, flex: 1 }} />
        <div style={{ display: 'flex', gap: 6 }}>
          {TYPE_FILTERS.map(t => (
            <button key={t} className={`btn btn-sm`} onClick={() => setTypeFilter(t)}
              style={{ background: typeFilter === t ? 'var(--primary)' : 'rgba(99,102,241,0.1)', color: typeFilter === t ? '#fff' : 'var(--text)', border: 'none' }}>{t}</button>
          ))}
        </div>
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
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t.card}</span>
                    {t.status !== 'completed' && (
                      <span className={`badge badge-${t.status === 'pending' ? 'warning' : 'danger'}`} style={{ fontSize: '0.6rem', padding: '1px 6px' }}>{t.status}</span>
                    )}
                  </div>
                </div>
                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <div style={{ fontWeight: 700, color: t.type === 'credit' ? 'var(--success)' : t.status === 'failed' ? 'var(--danger)' : 'var(--text)' }}>
                    {t.type === 'credit' ? '+' : '-'}PKR {t.amount.toLocaleString()}
                  </div>
                </div>
              </div>
              <AnimatePresence>
                {isExpanded && (
                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} style={{ overflow: 'hidden' }}>
                    <div style={{ marginTop: 14, paddingTop: 14, borderTop: '1px solid var(--border)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, fontSize: '0.85rem' }}>
                      <div><span style={{ color: 'var(--text-muted)' }}>Reference: </span>{t.ref}</div>
                      <div><span style={{ color: 'var(--text-muted)' }}>Merchant: </span>{t.merchant}</div>
                      <div><span style={{ color: 'var(--text-muted)' }}>Card Used: </span>{t.card}</div>
                      <div><span style={{ color: 'var(--text-muted)' }}>Category: </span>{t.category}</div>
                      <div><span style={{ color: 'var(--text-muted)' }}>Status: </span><span className={`badge badge-${t.status === 'completed' ? 'safe' : t.status === 'pending' ? 'warning' : 'danger'}`}>{t.status}</span></div>
                      <div><span style={{ color: 'var(--text-muted)' }}>Amount: </span><span style={{ color: t.type === 'credit' ? 'var(--success)' : 'var(--text)', fontWeight: 600 }}>PKR {t.amount.toLocaleString()}</span></div>
                    </div>
                    <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                      <button className="btn btn-sm" style={{ background: 'rgba(239,68,68,0.1)', color: 'var(--danger)', border: '1px solid rgba(239,68,68,0.2)' }} onClick={(e) => { e.stopPropagation(); alert('Dispute raised for transaction ' + t.ref); }}>Raise Dispute</button>
                      <button className="btn btn-sm" style={{ background: 'rgba(139,92,246,0.1)', color: '#a78bfa', border: '1px solid rgba(139,92,246,0.2)' }} onClick={(e) => { e.stopPropagation(); alert('Receipt emailed to registered address.'); }}>Email Receipt</button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )
        })}
        {filtered.length === 0 && (
          <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>No transactions match your filters.</div>
        )}
      </div>
    </div>
  )
}
