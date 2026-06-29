import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ThreeDBackground from '../../components/ThreeDBackground'
import api from '../../services/api'

interface WorkflowResult {
  success: boolean
  workflow_id: string
  transaction_type: string
  transaction_id?: string
  sender_name?: string
  receiver_name?: string
  receiver_account?: string
  amount: number
  sender_new_balance?: number
  receiver_new_balance?: number
  routing_verified: boolean
  message: string
  timestamp: string
}

export default function AITransactionWorkflow() {
  const [transactionId, setTransactionId] = useState('')
  const [customerName, setCustomerName] = useState('')
  const [amount, setAmount] = useState('')
  const [routingNumber, setRoutingNumber] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<WorkflowResult | null>(null)
  const [error, setError] = useState('')

  const handleSubmit = async () => {
    setError('')
    setResult(null)
    if (!transactionId || !customerName || !amount) {
      setError('Transaction ID, Name, and Amount are required.')
      return
    }
    const amt = parseFloat(amount)
    if (isNaN(amt) || amt <= 0) {
      setError('Please enter a valid amount.')
      return
    }

    setLoading(true)
    try {
      const body: Record<string, any> = {
        transaction_id: transactionId,
        customer_name: customerName,
        amount: amt,
      }
      if (routingNumber.trim()) {
        body.bank_routing_number = routingNumber.trim()
        body.account_number = routingNumber.trim()
      }

      const r = await api.post<WorkflowResult>('/api/smartfinance/transaction/process', body)
      setResult(r.data)
    } catch (e: any) {
      setError(e.response?.data?.detail || e.response?.data?.message || 'Transaction failed. Please try again.')
    }
    setLoading(false)
  }

  const hasLookup = routingNumber.trim().length > 0

  return (
    <div className="page" style={{ minHeight: '100vh' }}>
      <ThreeDBackground />
      <div style={{ position: 'relative', zIndex: 1, maxWidth: 700, width: '100%', margin: '0 auto' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div style={{ marginBottom: 24 }}>
            <h1 style={{ fontWeight: 700, color: '#fff' }}>AI Transaction Workflow</h1>
            <p style={{ color: 'var(--text-muted)', marginTop: 4 }}>
              {hasLookup
                ? 'Dono (Account + Routing) match hon to ADMIN-001 se paise transfer'
                : 'Simple mode: Sirf record ho ga'
              }
            </p>
          </div>

          <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius)', border: '1px solid var(--border)', padding: 24 }}>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>Account Number <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(jis ko paise bhejne hain)</span></label>
              <input
                value={transactionId}
                onChange={e => setTransactionId(e.target.value)}
                placeholder="e.g. 9021426090"
                style={{
                  width: '100%', padding: '12px 14px', background: 'rgba(0,0,0,0.3)',
                  border: '1px solid var(--border)', borderRadius: 8, color: '#fff',
                  fontSize: 14, outline: 'none',
                }}
              />
            </div>

            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>Customer Name</label>
              <input
                value={customerName}
                onChange={e => setCustomerName(e.target.value)}
                placeholder="e.g. Ali Ahmed"
                style={{
                  width: '100%', padding: '12px 14px', background: 'rgba(0,0,0,0.3)',
                  border: '1px solid var(--border)', borderRadius: 8, color: '#fff',
                  fontSize: 14, outline: 'none',
                }}
              />
            </div>

            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>Amount</label>
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

            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>
                Bank Routing Number <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(donon dalna zaroori — account + routing match hon to transfer)</span>
              </label>
              <input
                value={routingNumber}
                onChange={e => setRoutingNumber(e.target.value)}
                placeholder="e.g. 051404260"
                style={{
                  width: '100%', padding: '12px 14px', background: 'rgba(0,0,0,0.3)',
                  border: '1px solid var(--border)', borderRadius: 8, color: '#fff',
                  fontSize: 14, outline: 'none',
                }}
              />
              {hasLookup && (
                <div style={{ marginTop: 8, padding: '8px 12px', background: 'rgba(245,158,11,0.1)', borderRadius: 6, border: '1px solid rgba(245,158,11,0.2)' }}>
                  <span style={{ color: 'var(--warning)', fontSize: 13 }}>
                    ⚠ Account + Routing dono match hon to ADMIN-001 se paise deduct ho kar transfer ho jayenge
                  </span>
                </div>
              )}
            </div>

            {error && (
              <div style={{ padding: '12px 16px', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 8, color: 'var(--danger)', marginBottom: 16, fontSize: 13 }}>
                {error}
              </div>
            )}

            <motion.button
              whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
              onClick={handleSubmit}
              disabled={loading}
              style={{
                width: '100%', padding: '14px',
                background: hasLookup
                  ? 'linear-gradient(135deg, #f59e0b, #d97706)'
                  : 'linear-gradient(135deg, var(--primary), #7c3aed)',
                border: 'none', borderRadius: 8, color: '#fff', fontSize: 16, fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1,
              }}
            >
              {loading
                ? 'Processing...'
                : hasLookup
                  ? `Admin se Transfer (${amount ? `${parseFloat(amount).toLocaleString()}` : ''})`
                  : `Record Transaction${amount ? ` (${parseFloat(amount).toLocaleString()})` : ''}`
              }
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
                  <div>
                    <div style={{ color: result.success ? 'var(--success)' : 'var(--danger)', fontWeight: 600, fontSize: 16 }}>
                      {result.success
                        ? (result.transaction_type === 'routing_transfer' ? 'Routing Transfer Successful' : 'Transaction Recorded')
                        : 'Transaction Failed'
                      }
                    </div>
                    <div style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 2 }}>
                      Workflow ID: {result.workflow_id}
                    </div>
                  </div>
                </div>
                <p style={{ color: 'var(--text)', fontSize: 14, lineHeight: 1.6 }}>{result.message}</p>
                {result.success && (
                  <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 16, fontSize: 13, color: 'var(--text-muted)' }}>
                    {result.transaction_id && (
                      <span>Txn ID: <strong style={{ color: 'var(--primary)', fontFamily: 'monospace' }}>{result.transaction_id}</strong></span>
                    )}
                    {result.sender_name && (
                      <span>From: <strong style={{ color: '#fff' }}>{result.sender_name}</strong></span>
                    )}
                    {result.receiver_name && (
                      <span>To: <strong style={{ color: '#fff' }}>{result.receiver_name}</strong></span>
                    )}
                    {result.receiver_account && (
                      <span>Account: <strong style={{ color: '#fff' }}>{result.receiver_account}</strong></span>
                    )}
                    {result.routing_verified && (
                      <span style={{ color: 'var(--success)' }}>🔐 Routing Verified</span>
                    )}
                    {result.sender_new_balance !== undefined && (
                      <span>Admin New Balance: <strong style={{ color: '#10b981' }}>${Number(result.sender_new_balance).toLocaleString()}</strong></span>
                    )}
                    {result.receiver_new_balance !== undefined && (
                      <span>Receiver New Balance: <strong style={{ color: '#10b981' }}>${Number(result.receiver_new_balance).toLocaleString()}</strong></span>
                    )}
                    <span>Time: <strong style={{ color: '#fff' }}>{new Date(result.timestamp).toLocaleString()}</strong></span>
                    <span>Amount: <strong style={{ color: '#f59e0b' }}>${Number(result.amount).toLocaleString()}</strong></span>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  )
}
