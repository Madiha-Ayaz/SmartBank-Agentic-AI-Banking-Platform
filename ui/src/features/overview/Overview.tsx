import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import api from '../../services/api'
import ThreeDBackground from '../../components/ThreeDBackground'

interface Account {
  account_number: string
  full_name: string
  account_balance: number
  email: string
  phone: string
}

interface Transaction {
  transaction_id: string
  sender_account_number: string
  receiver_account_number: string
  transaction_amount: number
  transaction_type: string
  transaction_status: string
  created_at: string
}

interface CardData {
  id: number
  card_number: string
  card_type: string
  network: string
  holder_name: string
  account_number: string
  expiry: string
  status: string
  card_type_flag: string
}

interface LoanRecord {
  id: number
  case_id: string
  amount: number
  purpose?: string
  duration_months: number
  monthly_installment: number
  status: string
  created_at: string
}

interface BudgetItem {
  id: number
  category: string
  planned_amount: number
  spent_amount: number
  remaining_amount: number
  reserved_amount: number
  month: string
  year: string
}

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#3b82f6', '#ec4899', '#14b8a6']

const fmt = (n: number) => '$' + n.toLocaleString()

export default function Overview() {
  const navigate = useNavigate()

  const [account, setAccount] = useState<Account | null>(null)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [cards, setCards] = useState<CardData[]>([])
  const [loans, setLoans] = useState<LoanRecord[]>([])
  const [budgets, setBudgets] = useState<BudgetItem[]>([])
  const [totalIncome, setTotalIncome] = useState(0)
  const [totalExpenses, setTotalExpenses] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/api/dashboard/finance'),
      api.get('/api/accounts/balance'),
      api.get('/api/cards'),
    ]).then(([finRes, balRes, cardsRes]) => {
      const fin = finRes.data
      setAccount(fin.account || null)
      setTransactions(Array.isArray(fin.transactions) ? fin.transactions : [])
      setLoans(Array.isArray(fin.loans) ? fin.loans : [])
      setBudgets(Array.isArray(fin.budgets) ? fin.budgets : [])
      setTotalIncome(Number(fin.total_income || 0))
      setTotalExpenses(Number(fin.total_expenses || 0))
      if (balRes.data?.balance !== undefined && fin.account) {
        setAccount(prev => prev ? { ...prev, account_balance: balRes.data.balance } : prev)
      }
      // Handle new cards response format with identity verification check
      const cardsData = cardsRes.data?.cards || (Array.isArray(cardsRes.data) ? cardsRes.data : [])
      setCards(Array.isArray(cardsData) ? cardsData : [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="page">
        <ThreeDBackground />
        <div style={{ textAlign: 'center', padding: 'clamp(30px, 10vw, 80px)', color: 'var(--text-muted)' }}>Loading your financial overview...</div>
      </div>
    )
  }

  return (
    <div className="page">
      <ThreeDBackground />
      <h1><span className="gradient-text">Financial Overview</span></h1>

      {/* Balance Card */}
      {account && (
        <div className="card" style={{
          background: 'linear-gradient(135deg, rgba(16,185,129,0.15), rgba(99,102,241,0.15))',
          border: '1px solid rgba(16,185,129,0.3)',
          marginBottom: 20, padding: 24,
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>Account Balance</div>
              <div style={{ fontSize: '2.2rem', fontWeight: 700, color: '#10b981' }}>
                {fmt(account.account_balance)}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 2 }}>
                {account.full_name} &middot; {account.account_number}
              </div>
            </div>
            <div style={{ textAlign: 'right', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              <div>{account.email}</div>
              <div>{account.phone}</div>
            </div>
          </div>
          <div className="stats-grid" style={{ marginTop: 12, marginBottom: 0 }}>
            <div className="stat-card" style={{ padding: '10px 16px' }}>
              <span style={{ fontSize: '0.7rem' }}>Total Income</span>
              <strong style={{ color: '#10b981', fontSize: '1rem' }}>{fmt(totalIncome)}</strong>
            </div>
            <div className="stat-card" style={{ padding: '10px 16px' }}>
              <span style={{ fontSize: '0.7rem' }}>Total Expenses</span>
              <strong style={{ color: '#ef4444', fontSize: '1rem' }}>{fmt(totalExpenses)}</strong>
            </div>
            <div className="stat-card" style={{ padding: '10px 16px' }}>
              <span style={{ fontSize: '0.7rem' }}>Transactions</span>
              <strong style={{ fontSize: '1rem' }}>{transactions.length}</strong>
            </div>
            <div className="stat-card" style={{ padding: '10px 16px' }}>
              <span style={{ fontSize: '0.7rem' }}>Cards</span>
              <strong style={{ fontSize: '1rem' }}>{cards.length}</strong>
            </div>
          </div>
        </div>
      )}

      {/* Quick Action Buttons */}
      <div className="stats-grid" style={{ marginBottom: 20 }}>
        <div className="stat-card" style={{ cursor: 'pointer', borderLeft: '3px solid #6366f1' }}
          onClick={() => navigate('/cards')}
          onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 30px rgba(0,0,0,0.3)' }}
          onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: 2 }}>{'\u{1F4B3}'}</div>
          <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Cards ({cards.length})</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{cards.filter(c => c.status === 'active').length} active</div>
        </div>
        <div className="stat-card" style={{ cursor: 'pointer', borderLeft: '3px solid #10b981' }}
          onClick={() => navigate('/transactions')}
          onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 30px rgba(0,0,0,0.3)' }}
          onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: 2 }}>{'\u{1F4CB}'}</div>
          <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Transactions</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{transactions.length} recent</div>
        </div>
        <div className="stat-card" style={{ cursor: 'pointer', borderLeft: '3px solid #f59e0b' }}
          onClick={() => navigate('/loans')}
          onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 30px rgba(0,0,0,0.3)' }}
          onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: 2 }}>{'\u{1F3E6}'}</div>
          <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Loans</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{loans.length} applications</div>
        </div>
        <div className="stat-card" style={{ cursor: 'pointer', borderLeft: '3px solid #3b82f6' }}
          onClick={() => navigate('/budget')}
          onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 30px rgba(0,0,0,0.3)' }}
          onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: 2 }}>{'\u{1F4B0}'}</div>
          <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Budgets</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{budgets.length} active</div>
        </div>
      </div>

      <div className="grid-responsive" style={{ gap: 20, marginBottom: 20 }}>
        {/* Cards Section */}
        <div className="card">
          <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 12 }}>
            {cards.length > 0 ? 'Your Cards' : 'Cards'}
          </h3>
          {cards.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {cards.map(c => (
                <motion.div key={c.id} whileHover={{ scale: 1.01 }}
                  style={{
                    padding: '14px 16px', borderRadius: 12,
                    background: c.status === 'frozen' ? 'rgba(239,68,68,0.08)' : 'rgba(99,102,241,0.08)',
                    border: `1px solid ${c.status === 'frozen' ? 'rgba(239,68,68,0.2)' : 'rgba(99,102,241,0.2)'}`,
                    cursor: 'pointer',
                  }}
                  onClick={() => navigate('/cards')}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{c.card_type}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                        **** **** **** {c.card_number.slice(-4)}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <span className={`badge badge-${c.status === 'active' ? 'safe' : 'danger'}`} style={{ fontSize: '0.6rem' }}>
                        {c.status}
                      </span>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 2 }}>{c.card_type_flag}</div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: 20, color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '1.5rem', marginBottom: 4 }}>{'\u{1F4B3}'}</div>
              <p style={{ fontSize: '0.85rem', marginBottom: 12 }}>No cards yet</p>
              <button className="btn btn-sm" onClick={() => navigate('/cards')} style={{ background: 'rgba(99,102,241,0.15)', color: 'var(--primary)', border: '1px solid rgba(99,102,241,0.2)' }}>
                Apply for Card
              </button>
            </div>
          )}
        </div>

        {/* Budgets Section */}
        <div className="card">
          <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 12 }}>
            {budgets.length > 0 ? 'Monthly Budgets' : 'Budgets'}
          </h3>
          {budgets.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {budgets.slice(0, 5).map(b => {
                const pct = b.planned_amount > 0 ? Math.min((b.spent_amount / b.planned_amount) * 100, 100) : 0
                const savedPct = b.planned_amount > 0 ? Math.min((b.remaining_amount / b.planned_amount) * 100, 100) : 0
                return (
                  <div key={b.id} style={{ cursor: 'pointer' }} onClick={() => navigate('/budget')}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 4 }}>
                      <span style={{ fontWeight: 600 }}>{b.category}</span>
                      <span style={{ color: 'var(--text-muted)' }}>{fmt(b.spent_amount)} / {fmt(b.planned_amount)}</span>
                    </div>
                    <div style={{ height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden', display: 'flex' }}>
                      <div style={{ width: `${savedPct}%`, height: '100%', background: '#10b981', borderRadius: 3, transition: 'width 0.5s' }} />
                      <div style={{ width: `${pct - savedPct}%`, height: '100%', background: COLORS[budgets.indexOf(b) % COLORS.length], borderRadius: 3, transition: 'width 0.5s' }} />
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 2 }}>
                      <span>Saved: {fmt(b.remaining_amount)}</span>
                      <span>Spent: {fmt(b.spent_amount)}</span>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: 20, color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '1.5rem', marginBottom: 4 }}>{'\u{1F4B0}'}</div>
              <p style={{ fontSize: '0.85rem', marginBottom: 12 }}>No budgets yet</p>
              <button className="btn btn-sm" onClick={() => navigate('/budget')} style={{ background: 'rgba(99,102,241,0.15)', color: 'var(--primary)', border: '1px solid rgba(99,102,241,0.2)' }}>
                Create Budget
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Loans Section */}
      {loans.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 12 }}>
            Loans
          </h3>
          <div className="stats-grid" style={{ marginBottom: 0 }}>
            {loans.map(loan => (
              <div key={loan.id || loan.case_id} className="stat-card" style={{ textAlign: 'left', borderTop: `3px solid ${loan.status === 'approved' ? 'var(--success)' : loan.status === 'denied' ? 'var(--danger)' : 'var(--warning)'}`, cursor: 'pointer' }}
                onClick={() => navigate('/loans')}>
                <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: 2 }}>{loan.purpose || 'Loan'}</div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{fmt(loan.amount)} &middot; {loan.duration_months}mo</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6, fontSize: '0.8rem' }}>
                  <span>{fmt(loan.monthly_installment)}/mo</span>
                  <span className={`badge badge-${loan.status === 'approved' ? 'safe' : loan.status === 'denied' ? 'danger' : 'warning'}`} style={{ fontSize: '0.65rem' }}>{loan.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Transactions */}
      {transactions.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 12 }}>
            Recent Transactions
          </h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>From</th>
                  <th>To</th>
                  <th>Amount</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map(t => (
                  <tr key={t.transaction_id} style={{ cursor: 'pointer' }} onClick={() => navigate('/transactions')}>
                    <td style={{ fontSize: '0.85rem', fontFamily: 'monospace' }}>{t.sender_account_number}</td>
                    <td style={{ fontSize: '0.85rem', fontFamily: 'monospace' }}>{t.receiver_account_number}</td>
                    <td style={{ fontWeight: 600, color: t.sender_account_number === account?.account_number ? '#ef4444' : '#10b981' }}>
                      {t.sender_account_number === account?.account_number ? '-' : '+'}{fmt(t.transaction_amount)}
                    </td>
                    <td><span className="badge" style={{ background: 'rgba(99,102,241,0.1)', color: '#a78bfa' }}>{t.transaction_type}</span></td>
                    <td><span className={`badge badge-${t.transaction_status || 'completed'}`}>{t.transaction_status || 'completed'}</span></td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{t.created_at ? new Date(t.created_at).toLocaleDateString() : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {!account && (
        <div className="card" style={{ textAlign: 'center', padding: 'clamp(20px, 8vw, 60px)', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '3rem', marginBottom: 12 }}>{'\u{1F4B1}'}</div>
          <h2 style={{ marginBottom: 8 }}>No Account Found</h2>
          <p style={{ fontSize: '0.9rem', marginBottom: 16 }}>
            Aapka koi account link nahi hai. Pehle card apply karein.
          </p>
          <button className="btn btn-primary" onClick={() => navigate('/cards')}>
            Apply for Card
          </button>
        </div>
      )}
    </div>
  )
}
