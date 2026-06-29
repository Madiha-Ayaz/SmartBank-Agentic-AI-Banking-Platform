import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ThreeDBackground from '../../components/ThreeDBackground'
import api from '../../services/api'

interface CustomerInfo {
  customer_id: number
  full_name: string
  account_number: string
  account_balance: number
  credit_score: number
  phone?: string
  email?: string
  city?: string
  profession?: string
}

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

interface TransferResult {
  success: boolean
  transaction_id?: string
  sender_name?: string
  receiver_name?: string
  amount?: number
  sender_new_balance?: number
  receiver_new_balance?: number
  message: string
}

export default function FinanceTransferPage() {
  const [senderAcct, setSenderAcct] = useState('')
  const [receiverAcct, setReceiverAcct] = useState('')
  const [amount, setAmount] = useState('')
  const [password, setPassword] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<TransferResult | null>(null)
  const [error, setError] = useState('')
  const [senderInfo, setSenderInfo] = useState<CustomerInfo | null>(null)
  const [receiverInfo, setReceiverInfo] = useState<CustomerInfo | null>(null)
  const [txns, setTxns] = useState<TransactionItem[]>([])
  const [currentBal, setCurrentBal] = useState<number | null>(null)
  const [searchQ, setSearchQ] = useState('')
  const [searchResults, setSearchResults] = useState<CustomerInfo[]>([])
  const [searching, setSearching] = useState(false)
  const [showReceiverPicker, setShowReceiverPicker] = useState(false)
  const [customerCount, setCustomerCount] = useState(0)

  useEffect(() => {
    api.get('/api/finance/count').then(r => setCustomerCount(r.data.total_customers)).catch(() => {})
  }, [])

  const lookupSender = useCallback(async () => {
    if (senderAcct.length < 3) { setSenderInfo(null); return }
    try {
      const r = await api.get(`/api/finance/customer/${senderAcct}`)
      setSenderInfo(r.data)
    } catch { setSenderInfo(null) }
  }, [senderAcct])

  const lookupReceiver = useCallback(async () => {
    if (receiverAcct.length < 3) { setReceiverInfo(null); return }
    try {
      const r = await api.get(`/api/finance/customer/${receiverAcct}`)
      setReceiverInfo(r.data)
    } catch { setReceiverInfo(null) }
  }, [receiverAcct])

  useEffect(() => { lookupSender() }, [lookupSender])
  useEffect(() => { lookupReceiver() }, [lookupReceiver])

  const searchCustomers = useCallback(async (q: string) => {
    if (q.length < 2) { setSearchResults([]); return }
    setSearching(true)
    try {
      const r = await api.get('/api/finance/customer/search', { params: { q } })
      setSearchResults(r.data)
    } catch { setSearchResults([]) }
    setSearching(false)
  }, [])

  useEffect(() => { searchCustomers(searchQ) }, [searchQ, searchCustomers])

  const loadTransactions = useCallback(async () => {
    if (!senderAcct && !receiverAcct) return
    const acct = senderAcct || receiverAcct
    try {
      const r = await api.get(`/api/finance/transactions/${acct}`, { params: { limit: 10 } })
      setTxns(r.data.transactions || [])
      setCurrentBal(r.data.current_balance ?? null)
    } catch { setTxns([]); setCurrentBal(null) }
  }, [senderAcct, receiverAcct])

  const handleTransfer = async () => {
    setError('')
    setResult(null)
    if (!senderAcct || !receiverAcct || !amount) {
      setError('Please fill in sender, receiver, and amount.')
      return
    }
    const amt = parseFloat(amount)
    if (isNaN(amt) || amt <= 0) {
      setError('Please enter a valid amount.')
      return
    }

    setLoading(true)
    try {
      const r = await api.post<TransferResult>('/api/finance/transfer', {
        sender_account: senderAcct,
        receiver_account: receiverAcct,
        amount: amt,
        password: password || undefined,
        description: description || undefined,
      })
      setResult(r.data)
      setAmount('')
      setPassword('')
      setDescription('')
      lookupSender()
      loadTransactions()
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Transfer failed. Please try again.')
    }
    setLoading(false)
  }

  return (
    <div className="page" style={{ minHeight: '100vh' }}>
      <ThreeDBackground />
      <div style={{ position: 'relative', zIndex: 1, maxWidth: 1200, width: '100%', margin: '0 auto' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex-between" style={{ marginBottom: 24 }}>
            <div>
              <h1 style={{ fontWeight: 700, color: '#fff' }}>Banking Transfer</h1>
              <p style={{ color: 'var(--text-muted)', marginTop: 4 }}>
                {customerCount.toLocaleString()} customers in the banking network
              </p>
            </div>
          </div>

          <div className="grid-2">
            <div>
              <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius)', border: '1px solid var(--border)', padding: 24 }}>
                <h2 style={{ fontSize: 18, fontWeight: 600, color: '#fff', marginBottom: 20 }}>Send Money</h2>

                <div style={{ marginBottom: 16 }}>
                  <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>Sender Account Number</label>
                  <input
                    value={senderAcct}
                    onChange={e => setSenderAcct(e.target.value)}
                    placeholder="Enter sender account number"
                    style={{
                      width: '100%', padding: '12px 14px', background: 'rgba(0,0,0,0.3)',
                      border: '1px solid var(--border)', borderRadius: 8, color: '#fff',
                      fontSize: 14, outline: 'none',
                    }}
                  />
                  {senderInfo && (
                    <div style={{ marginTop: 8, padding: '8px 12px', background: 'rgba(16,185,129,0.1)', borderRadius: 6, border: '1px solid rgba(16,185,129,0.2)' }}>
                      <span style={{ color: 'var(--success)', fontWeight: 600 }}>{senderInfo.full_name}</span>
                      <span style={{ color: 'var(--text-muted)', marginLeft: 12 }}>Balance: ${senderInfo.account_balance.toLocaleString()}</span>
                    </div>
                  )}
                </div>

                <div style={{ marginBottom: 16 }}>
                  <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>Receiver Account Number</label>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <input
                      value={receiverAcct}
                      onChange={e => setReceiverAcct(e.target.value)}
                      placeholder="Enter receiver account number"
                      style={{
                        flex: 1, padding: '12px 14px', background: 'rgba(0,0,0,0.3)',
                        border: '1px solid var(--border)', borderRadius: 8, color: '#fff',
                        fontSize: 14, outline: 'none',
                      }}
                    />
                    <button
                      onClick={() => setShowReceiverPicker(!showReceiverPicker)}
                      style={{
                        padding: '12px 16px', background: 'rgba(99,102,241,0.15)',
                        border: '1px solid var(--border)', borderRadius: 8, color: 'var(--primary)',
                        cursor: 'pointer', whiteSpace: 'nowrap',
                      }}
                    >Search</button>
                  </div>
                  {receiverInfo && (
                    <div style={{ marginTop: 8, padding: '8px 12px', background: 'rgba(99,102,241,0.1)', borderRadius: 6, border: '1px solid rgba(99,102,241,0.2)' }}>
                      <span style={{ color: 'var(--primary)', fontWeight: 600 }}>{receiverInfo.full_name}</span>
                      <span style={{ color: 'var(--text-muted)', marginLeft: 12 }}>City: {receiverInfo.city || 'N/A'}</span>
                    </div>
                  )}
                </div>

                <AnimatePresence>
                  {showReceiverPicker && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      style={{ marginBottom: 16, overflow: 'hidden' }}
                    >
                      <input
                        value={searchQ}
                        onChange={e => setSearchQ(e.target.value)}
                        placeholder="Search by name, account, or phone..."
                        style={{
                          width: '100%', padding: '10px 14px', marginBottom: 8,
                          background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border)',
                          borderRadius: 8, color: '#fff', fontSize: 13, outline: 'none',
                        }}
                      />
                      {searching && <div style={{ color: 'var(--text-muted)', padding: 8 }}>Searching...</div>}
                      {searchResults.map(c => (
                        <div
                          key={c.account_number}
                          onClick={() => { setReceiverAcct(c.account_number); setShowReceiverPicker(false) }}
                          style={{
                            padding: '10px 12px', cursor: 'pointer', borderBottom: '1px solid var(--border-light)',
                            transition: 'background 0.2s',
                          }}
                          onMouseEnter={e => e.currentTarget.style.background = 'rgba(99,102,241,0.1)'}
                          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                        >
                          <div style={{ color: '#fff', fontWeight: 500 }}>{c.full_name}</div>
                          <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                            Acct: {c.account_number} | {c.city || 'N/A'}
                          </div>
                        </div>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>

                <div style={{ marginBottom: 16 }}>
                  <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>Amount ($)</label>
                  <input
                    type="number"
                    value={amount}
                    onChange={e => setAmount(e.target.value)}
                    placeholder="0.00"
                    min="0"
                    step="0.01"
                    style={{
                      width: '100%', padding: '12px 14px', background: 'rgba(0,0,0,0.3)',
                      border: '1px solid var(--border)', borderRadius: 8, color: '#fff',
                      fontSize: 14, outline: 'none',
                    }}
                  />
                </div>

                <div style={{ marginBottom: 16 }}>
                  <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>Description (optional)</label>
                  <input
                    value={description}
                    onChange={e => setDescription(e.target.value)}
                    placeholder="What's this for?"
                    style={{
                      width: '100%', padding: '12px 14px', background: 'rgba(0,0,0,0.3)',
                      border: '1px solid var(--border)', borderRadius: 8, color: '#fff',
                      fontSize: 14, outline: 'none',
                    }}
                  />
                </div>

                <div style={{ marginBottom: 20 }}>
                  <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>Account Password</label>
                  <input
                    type="password"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    placeholder="Enter account password"
                    style={{
                      width: '100%', padding: '12px 14px', background: 'rgba(0,0,0,0.3)',
                      border: '1px solid var(--border)', borderRadius: 8, color: '#fff',
                      fontSize: 14, outline: 'none',
                    }}
                  />
                </div>

                {error && (
                  <div style={{ padding: '12px 16px', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 8, color: 'var(--danger)', marginBottom: 16, fontSize: 13 }}>
                    {error}
                  </div>
                )}

                <motion.button
                  whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                  onClick={handleTransfer}
                  disabled={loading}
                  style={{
                    width: '100%', padding: '14px', background: 'linear-gradient(135deg, var(--primary), #7c3aed)',
                    border: 'none', borderRadius: 8, color: '#fff', fontSize: 16, fontWeight: 600,
                    cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1,
                  }}
                >
                  {loading ? 'Processing...' : `Send ${amount && !isNaN(parseFloat(amount)) ? `$${parseFloat(amount).toLocaleString()}` : ''}`}
                </motion.button>
              </div>

              <AnimatePresence>
                {result && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                    style={{
                      marginTop: 16, padding: 20, borderRadius: 'var(--radius)',
                      background: result.success ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                      border: `1px solid ${result.success ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}`,
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                      <span style={{ fontSize: 28 }}>{result.success ? '✅' : '❌'}</span>
                      <span style={{ color: result.success ? 'var(--success)' : 'var(--danger)', fontWeight: 600, fontSize: 16 }}>
                        {result.success ? 'Transfer Successful' : 'Transfer Failed'}
                      </span>
                    </div>
                    <p style={{ color: 'var(--text)', fontSize: 14, lineHeight: 1.6 }}>{result.message}</p>
                    {result.success && result.sender_new_balance !== undefined && (
                      <div style={{ marginTop: 12, display: 'flex', gap: 24, fontSize: 13, color: 'var(--text-muted)' }}>
                        <span>New Balance: <strong style={{ color: '#fff' }}>${result.sender_new_balance.toLocaleString()}</strong></span>
                        <span>Txn ID: <strong style={{ color: 'var(--primary)', fontFamily: 'monospace' }}>{result.transaction_id}</strong></span>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <div>
              <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius)', border: '1px solid var(--border)', padding: 24 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                  <h2 style={{ fontSize: 18, fontWeight: 600, color: '#fff' }}>Transaction History</h2>
                  <button
                    onClick={loadTransactions}
                    style={{
                      padding: '6px 14px', background: 'rgba(99,102,241,0.15)',
                      border: '1px solid var(--border)', borderRadius: 6, color: 'var(--primary)',
                      cursor: 'pointer', fontSize: 12,
                    }}
                  >Refresh</button>
                </div>
                {currentBal !== null && (
                  <div style={{ marginBottom: 12, padding: '10px 14px', background: 'rgba(16,185,129,0.1)', borderRadius: 8, border: '1px solid rgba(16,185,129,0.2)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>Current Balance</span>
                    <span style={{ color: 'var(--success)', fontWeight: 700, fontSize: 18 }}>${currentBal.toLocaleString()}</span>
                  </div>
                )}
                <p style={{ color: 'var(--text-muted)', fontSize: 12, marginBottom: 16 }}>
                  Enter a sender or receiver account above to view transactions
                </p>

                {txns.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {txns.map(txn => {
                      const isSent = txn.sender_account_number === (senderAcct || '')
                      return (
                        <div
                          key={txn.transaction_id}
                          style={{
                            padding: '12px 16px', background: 'rgba(0,0,0,0.2)',
                            borderRadius: 8, border: '1px solid var(--border-light)',
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                              <span style={{ color: '#fff', fontWeight: 500, fontSize: 14 }}>
                                {isSent ? `→ ${txn.receiver_name || txn.receiver_account_number}` : `← ${txn.sender_name || txn.sender_account_number}`}
                              </span>
                              <div style={{ color: 'var(--text-muted)', fontSize: 11, marginTop: 2 }}>
                                {new Date(txn.created_at).toLocaleDateString()} | {txn.transaction_type || 'Transfer'} | <span className={`badge badge-${txn.transaction_status}`}>{txn.transaction_status}</span>
                              </div>
                              {txn.remaining_balance !== undefined && (
                                <div style={{ color: 'var(--text-muted)', fontSize: 10, marginTop: 2 }}>
                                  Balance after: ${Number(txn.remaining_balance).toLocaleString()}
                                </div>
                              )}
                            </div>
                            <span style={{
                              fontWeight: 600, fontSize: 15,
                              color: isSent ? 'var(--danger)' : 'var(--success)',
                            }}>
                              {isSent ? '-' : '+'}${Number(txn.transaction_amount).toLocaleString()}
                            </span>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)', fontSize: 13 }}>
                    No transactions found. Make a transfer to get started.
                  </div>
                )}
              </div>

              {senderInfo && (
                <div style={{ marginTop: 16, background: 'var(--bg-card)', borderRadius: 'var(--radius)', border: '1px solid var(--border)', padding: 24 }}>
                  <h2 style={{ fontSize: 16, fontWeight: 600, color: '#fff', marginBottom: 16 }}>Account Summary</h2>
                  <div className="grid-responsive" style={{ gap: 12 }}>
                    {[
                      ['Balance', `$${senderInfo.account_balance.toLocaleString()}`, 'var(--success)'],
                      ['Credit Score', senderInfo.credit_score.toString(), senderInfo.credit_score >= 700 ? 'var(--success)' : senderInfo.credit_score >= 500 ? 'var(--warning)' : 'var(--danger)'],
                      ['Name', senderInfo.full_name, '#fff'],
                      ['City', senderInfo.city || 'N/A', 'var(--text-muted)'],
                      ['Profession', senderInfo.profession || 'N/A', 'var(--text-muted)'],
                      ['Account #', senderInfo.account_number, 'var(--primary)'],
                    ].map(([label, value, color]) => (
                      <div key={label as string} style={{ padding: '8px 12px', background: 'rgba(0,0,0,0.2)', borderRadius: 6 }}>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>{label as string}</div>
                        <div style={{ fontSize: 14, fontWeight: 600, color: color as string }}>{value as string}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
