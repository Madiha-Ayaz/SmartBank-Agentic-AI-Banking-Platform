import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ThreeDBackground from '../../components/ThreeDBackground'
import api from '../../services/api'

type TabId = 'nadra' | 'cbs' | 'payment' | 'transfer' | 'history'
interface HistoryData {
  verifications: any[]
  transactions: any[]
  payments: any[]
  transfers: any[]
}

const tabs: { id: TabId; label: string; icon: string }[] = [
  { id: 'nadra', label: 'CNIC Verify', icon: '\u{1F464}' },
  { id: 'cbs', label: 'Account Check', icon: '\u{1F3E6}' },
  { id: 'payment', label: '1LINK Pay', icon: '\u{1F4B3}' },
  { id: 'transfer', label: 'Raast Transfer', icon: '\u{1F4E4}' },
  { id: 'history', label: 'History', icon: '\u{1F4CA}' },
]

export default function BankingPage() {
  const [activeTab, setActiveTab] = useState<TabId>('nadra')

  // NADRA
  const [cnic, setCnic] = useState('')
  const [nadraResult, setNadraResult] = useState<any>(null)
  const [nadraLoading, setNadraLoading] = useState(false)

  // CBS
  const [acctNum, setAcctNum] = useState('')
  const [cbsResult, setCbsResult] = useState<any>(null)
  const [cbsLoading, setCbsLoading] = useState(false)

  // 1LINK Payment
  const [payAcct, setPayAcct] = useState('')
  const [payAmount, setPayAmount] = useState('')
  const [payResult, setPayResult] = useState<any>(null)
  const [payLoading, setPayLoading] = useState(false)

  // Raast Transfer
  const [recvAcct, setRecvAcct] = useState('')
  const [transAmount, setTransAmount] = useState('')
  const [transResult, setTransResult] = useState<any>(null)
  const [transLoading, setTransLoading] = useState(false)

  // Workflow
  const [wfLoading, setWfLoading] = useState(false)
  const [wfResult, setWfResult] = useState<any>(null)

  // History
  const [history, setHistory] = useState<HistoryData>({ verifications: [], transactions: [], payments: [], transfers: [] })
  const [histLoading, setHistLoading] = useState(false)

  const loadHistory = useCallback(async () => {
    setHistLoading(true)
    try {
      const r = await api.get('/api/banking/history')
      setHistory(r.data)
    } catch { setHistory({ verifications: [], transactions: [], payments: [], transfers: [] }) }
    setHistLoading(false)
  }, [])

  useEffect(() => { if (activeTab === 'history') loadHistory() }, [activeTab, loadHistory])

  const handleNadraVerify = async () => {
    setNadraLoading(true); setNadraResult(null)
    try {
      const r = await api.post('/api/nadra/verify', { cnic })
      setNadraResult(r.data)
    } catch (e: any) {
      setNadraResult({ success: false, message: e.response?.data?.message || 'Verification failed' })
    }
    setNadraLoading(false)
  }

  const handleCbsCheck = async () => {
    setCbsLoading(true); setCbsResult(null)
    try {
      const r = await api.post('/api/cbs/account-check', { accountNumber: acctNum })
      setCbsResult(r.data)
    } catch (e: any) {
      setCbsResult({ success: false, message: e.response?.data?.message || 'Account check failed' })
    }
    setCbsLoading(false)
  }

  const handlePayment = async () => {
    setPayLoading(true); setPayResult(null)
    try {
      const r = await api.post('/api/onelink/payment', { accountNumber: payAcct, amount: parseFloat(payAmount) })
      setPayResult(r.data)
    } catch (e: any) {
      setPayResult({ success: false, message: e.response?.data?.message || 'Payment failed' })
    }
    setPayLoading(false)
  }

  const handleTransfer = async () => {
    setTransLoading(true); setTransResult(null)
    try {
      const r = await api.post('/api/raast/transfer', { receiverAccount: recvAcct, amount: parseFloat(transAmount) })
      setTransResult(r.data)
    } catch (e: any) {
      setTransResult({ success: false, message: e.response?.data?.message || 'Transfer failed' })
    }
    setTransLoading(false)
  }

  const handleFullWorkflow = async () => {
    setWfLoading(true); setWfResult(null)
    try {
      const r = await api.post('/api/workflows/trigger-banking', {
        cnic: cnic || '12345-1234567-1',
        accountNumber: acctNum || 'PK00123456789',
        amount: parseFloat(payAmount || transAmount || '5000'),
        receiverAccount: recvAcct || 'PK00987654321',
      })
      setWfResult(r.data)
    } catch (e: any) {
      setWfResult({ success: false, message: e.response?.data?.message || 'Workflow failed' })
    }
    setWfLoading(false)
  }

  const tabContent = (tab: TabId) => {
    switch (tab) {
      case 'nadra':
        return (
          <div>
            <h3 style={{ color: '#fff', fontSize: 18, fontWeight: 600, marginBottom: 8 }}>NADRA CNIC Verification</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: 13, marginBottom: 20 }}>Verify a Computerized National Identity Card (CNIC) against NADRA records. Test: <strong>12345-1234567-1</strong></p>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>CNIC Number</label>
              <input value={cnic} onChange={e => setCnic(e.target.value)} placeholder="XXXXX-XXXXXXX-X"
                style={{ width: '100%', padding: '12px 14px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border)', borderRadius: 8, color: '#fff', fontSize: 14, outline: 'none' }} />
            </div>
            <button onClick={handleNadraVerify} disabled={nadraLoading || !cnic}
              style={{ width: '100%', padding: '14px', background: 'linear-gradient(135deg, var(--primary), #7c3aed)', border: 'none', borderRadius: 8, color: '#fff', fontSize: 16, fontWeight: 600, cursor: (nadraLoading || !cnic) ? 'not-allowed' : 'pointer', opacity: (nadraLoading || !cnic) ? 0.7 : 1 }}>
              {nadraLoading ? 'Verifying...' : 'Verify CNIC'}
            </button>
            <AnimatePresence>{nadraResult && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                style={{ marginTop: 16, padding: 20, borderRadius: 'var(--radius)', background: nadraResult.verified ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)', border: `1px solid ${nadraResult.verified ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}` }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                  <span style={{ fontSize: 28 }}>{nadraResult.verified ? '\u2705' : '\u274C'}</span>
                  <span style={{ color: nadraResult.verified ? 'var(--success)' : 'var(--danger)', fontWeight: 600, fontSize: 16 }}>{nadraResult.verified ? 'Verified' : 'Not Found'}</span>
                </div>
                {nadraResult.customerName && <p style={{ color: '#fff', fontSize: 14 }}>Name: <strong>{nadraResult.customerName}</strong></p>}
                {nadraResult.cnicStatus && <p style={{ color: 'var(--text-muted)', fontSize: 12 }}>Status: {nadraResult.cnicStatus}</p>}
                {nadraResult.message && <p style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>{nadraResult.message}</p>}
              </motion.div>
            )}</AnimatePresence>
          </div>
        )

      case 'cbs':
        return (
          <div>
            <h3 style={{ color: '#fff', fontSize: 18, fontWeight: 600, marginBottom: 8 }}>CBS Account Verification</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: 13, marginBottom: 20 }}>Check account status and balance via Core Banking System. Test: <strong>PK00123456789</strong></p>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>Account Number</label>
              <input value={acctNum} onChange={e => setAcctNum(e.target.value)} placeholder="PKXXXXXXXXXXXXX"
                style={{ width: '100%', padding: '12px 14px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border)', borderRadius: 8, color: '#fff', fontSize: 14, outline: 'none' }} />
            </div>
            <button onClick={handleCbsCheck} disabled={cbsLoading || !acctNum}
              style={{ width: '100%', padding: '14px', background: 'linear-gradient(135deg, #10b981, #059669)', border: 'none', borderRadius: 8, color: '#fff', fontSize: 16, fontWeight: 600, cursor: (cbsLoading || !acctNum) ? 'not-allowed' : 'pointer', opacity: (cbsLoading || !acctNum) ? 0.7 : 1 }}>
              {cbsLoading ? 'Checking...' : 'Check Account'}
            </button>
            <AnimatePresence>{cbsResult && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                style={{ marginTop: 16, padding: 20, borderRadius: 'var(--radius)', background: cbsResult.accountStatus === 'active' ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)', border: `1px solid ${cbsResult.accountStatus === 'active' ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}` }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                  <span style={{ fontSize: 28 }}>{cbsResult.accountStatus === 'active' ? '\u2705' : '\u274C'}</span>
                  <span style={{ color: cbsResult.accountStatus === 'active' ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }}>{cbsResult.accountStatus === 'active' ? 'Active' : 'Not Found'}</span>
                </div>
                {cbsResult.customerName && <p style={{ color: '#fff', fontSize: 14 }}>Name: <strong>{cbsResult.customerName}</strong></p>}
                {cbsResult.availableBalance != null && <p style={{ color: 'var(--success)', fontSize: 14 }}>Balance: <strong>{cbsResult.availableBalance.toLocaleString()} {cbsResult.currency || 'PKR'}</strong></p>}
                {cbsResult.message && <p style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>{cbsResult.message}</p>}
              </motion.div>
            )}</AnimatePresence>
          </div>
        )

      case 'payment':
        return (
          <div>
            <h3 style={{ color: '#fff', fontSize: 18, fontWeight: 600, marginBottom: 8 }}>1LINK Payment</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: 13, marginBottom: 20 }}>Process a payment through the 1LINK payment gateway.</p>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>Account Number</label>
              <input value={payAcct} onChange={e => setPayAcct(e.target.value)} placeholder="PKXXXXXXXXXXXXX"
                style={{ width: '100%', padding: '12px 14px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border)', borderRadius: 8, color: '#fff', fontSize: 14, outline: 'none' }} />
            </div>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>Amount (PKR)</label>
              <input type="number" value={payAmount} onChange={e => setPayAmount(e.target.value)} placeholder="1000" min="0"
                style={{ width: '100%', padding: '12px 14px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border)', borderRadius: 8, color: '#fff', fontSize: 14, outline: 'none' }} />
            </div>
            <button onClick={handlePayment} disabled={payLoading || !payAcct || !payAmount}
              style={{ width: '100%', padding: '14px', background: 'linear-gradient(135deg, #f59e0b, #d97706)', border: 'none', borderRadius: 8, color: '#fff', fontSize: 16, fontWeight: 600, cursor: (payLoading || !payAcct || !payAmount) ? 'not-allowed' : 'pointer', opacity: (payLoading || !payAcct || !payAmount) ? 0.7 : 1 }}>
              {payLoading ? 'Processing...' : 'Process Payment'}
            </button>
            <AnimatePresence>{payResult && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                style={{ marginTop: 16, padding: 20, borderRadius: 'var(--radius)', background: payResult.paymentStatus === 'success' ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)', border: `1px solid ${payResult.paymentStatus === 'success' ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}` }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                  <span style={{ fontSize: 28 }}>{payResult.paymentStatus === 'success' ? '\u2705' : '\u274C'}</span>
                  <span style={{ color: payResult.paymentStatus === 'success' ? 'var(--success)' : 'var(--danger)', fontWeight: 600, fontSize: 16 }}>{payResult.paymentStatus === 'success' ? 'Payment Successful' : 'Payment Failed'}</span>
                </div>
                {payResult.transactionId && <p style={{ color: '#fff', fontSize: 13 }}>Txn ID: <code style={{ color: 'var(--primary)' }}>{payResult.transactionId}</code></p>}
                {payResult.amount != null && <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>Amount: PKR {Number(payResult.amount).toLocaleString()}</p>}
              </motion.div>
            )}</AnimatePresence>
          </div>
        )

      case 'transfer':
        return (
          <div>
            <h3 style={{ color: '#fff', fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Raast Instant Transfer</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: 13, marginBottom: 20 }}>Send an instant payment via Pakistan's Raast payment system.</p>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>Receiver Account Number</label>
              <input value={recvAcct} onChange={e => setRecvAcct(e.target.value)} placeholder="PKXXXXXXXXXXXXX"
                style={{ width: '100%', padding: '12px 14px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border)', borderRadius: 8, color: '#fff', fontSize: 14, outline: 'none' }} />
            </div>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', marginBottom: 6 }}>Amount (PKR)</label>
              <input type="number" value={transAmount} onChange={e => setTransAmount(e.target.value)} placeholder="1000" min="0"
                style={{ width: '100%', padding: '12px 14px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border)', borderRadius: 8, color: '#fff', fontSize: 14, outline: 'none' }} />
            </div>
            <button onClick={handleTransfer} disabled={transLoading || !recvAcct || !transAmount}
              style={{ width: '100%', padding: '14px', background: 'linear-gradient(135deg, #8b5cf6, #6d28d9)', border: 'none', borderRadius: 8, color: '#fff', fontSize: 16, fontWeight: 600, cursor: (transLoading || !recvAcct || !transAmount) ? 'not-allowed' : 'pointer', opacity: (transLoading || !recvAcct || !transAmount) ? 0.7 : 1 }}>
              {transLoading ? 'Transferring...' : 'Send Transfer'}
            </button>
            <AnimatePresence>{transResult && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                style={{ marginTop: 16, padding: 20, borderRadius: 'var(--radius)', background: transResult.transferStatus === 'completed' ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)', border: `1px solid ${transResult.transferStatus === 'completed' ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}` }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                  <span style={{ fontSize: 28 }}>{transResult.transferStatus === 'completed' ? '\u2705' : '\u274C'}</span>
                  <span style={{ color: transResult.transferStatus === 'completed' ? 'var(--success)' : 'var(--danger)', fontWeight: 600, fontSize: 16 }}>{transResult.transferStatus === 'completed' ? 'Transfer Completed' : 'Transfer Failed'}</span>
                </div>
                {transResult.referenceId && <p style={{ color: '#fff', fontSize: 13 }}>Ref ID: <code style={{ color: 'var(--primary)' }}>{transResult.referenceId}</code></p>}
                {transResult.amount != null && <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>Amount: PKR {Number(transResult.amount).toLocaleString()}</p>}
              </motion.div>
            )}</AnimatePresence>
          </div>
        )

      case 'history':
        return (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ color: '#fff', fontSize: 18, fontWeight: 600 }}>Banking History</h3>
              <button onClick={loadHistory} style={{ padding: '6px 14px', background: 'rgba(99,102,241,0.15)', border: '1px solid var(--border)', borderRadius: 6, color: 'var(--primary)', cursor: 'pointer', fontSize: 12 }}>
                {histLoading ? 'Loading...' : 'Refresh'}
              </button>
            </div>
            {histLoading ? (
              <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>Loading history...</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                {[
                  { label: 'CNIC Verifications', items: history.verifications, keyField: 'cnic' },
                  { label: 'Account Checks', items: history.transactions, keyField: 'accountNumber' },
                  { label: 'Payments', items: history.payments, keyField: 'transactionId' },
                  { label: 'Transfers', items: history.transfers, keyField: 'referenceId' },
                ].map(section => (
                  <div key={section.label}>
                    <h4 style={{ color: 'var(--text-muted)', fontSize: 13, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>{section.label}</h4>
                    {section.items.length === 0 ? (
                      <div style={{ padding: '12px 16px', background: 'rgba(0,0,0,0.2)', borderRadius: 8, border: '1px solid var(--border-light)', color: 'var(--text-muted)', fontSize: 12, textAlign: 'center' }}>
                        No records found
                      </div>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                        {section.items.slice(0, 10).map((item: any, i: number) => (
                          <div key={item.id || i} style={{ padding: '10px 14px', background: 'rgba(0,0,0,0.2)', borderRadius: 8, border: '1px solid var(--border-light)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <div>
                                {section.keyField && <span style={{ color: 'var(--primary)', fontFamily: 'monospace', fontSize: 12 }}>{item[section.keyField]}</span>}
                                {item.status && <span className={`badge badge-${item.status}`} style={{ marginLeft: 8, fontSize: 10 }}>{item.status}</span>}
                              </div>
                              {item.amount != null && <span style={{ color: '#fff', fontWeight: 600 }}>PKR {Number(item.amount).toLocaleString()}</span>}
                            </div>
                            {item.timestamp && <div style={{ color: 'var(--text-muted)', fontSize: 10, marginTop: 4 }}>{new Date(item.timestamp).toLocaleString()}</div>}
                            {item.verified !== undefined && <div style={{ color: item.verified ? 'var(--success)' : 'var(--danger)', fontSize: 11, marginTop: 2 }}>{item.verified ? 'Verified' : 'Failed'}</div>}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )
    }
  }

  return (
    <div className="banking-page page" style={{ position: 'relative', minHeight: '100vh' }}>
      <ThreeDBackground />
      <div style={{ position: 'relative', zIndex: 1, maxWidth: 800, width: '100%', margin: '0 auto' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div style={{ marginBottom: 24 }}>
            <h1 style={{ fontWeight: 700, color: '#fff' }}>SmartFinance Banking</h1>
            <p style={{ color: 'var(--text-muted)', marginTop: 4 }}>Simulated NADRA, CBS, 1LINK &amp; Raast Banking APIs</p>
          </div>

          {/* Tabs */}
          <div style={{ display: 'flex', gap: 4, marginBottom: 20, flexWrap: 'wrap' }}>
            {tabs.map(t => (
              <button key={t.id} onClick={() => setActiveTab(t.id)}
                style={{
                  padding: '10px 18px', borderRadius: 8, border: activeTab === t.id ? '1px solid var(--primary)' : '1px solid var(--border)',
                  background: activeTab === t.id ? 'rgba(99,102,241,0.15)' : 'rgba(0,0,0,0.2)',
                  color: activeTab === t.id ? 'var(--primary)' : 'var(--text-muted)',
                  cursor: 'pointer', fontSize: 13, fontWeight: activeTab === t.id ? 600 : 400,
                  transition: 'all 0.2s',
                }}>
                <span style={{ marginRight: 6 }}>{t.icon}</span>{t.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="tab-card" style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
            <AnimatePresence mode="wait">
              <motion.div key={activeTab} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} transition={{ duration: 0.15 }}>
                {tabContent(activeTab)}
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Full Workflow Trigger */}
          <div className="wf-card" style={{ marginTop: 20, background: 'var(--bg-card)', borderRadius: 'var(--radius)', border: '1px solid rgba(139,92,246,0.3)' }}>
            <h3 style={{ color: '#fff', fontSize: 16, fontWeight: 600, marginBottom: 8 }}>Full Banking Workflow</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: 13, marginBottom: 16 }}>
              Run the complete end-to-end banking workflow: NADRA Verify → CBS Check → Risk Decision → Payment → Transfer → Firebase Log
            </p>
            <button onClick={handleFullWorkflow} disabled={wfLoading}
              style={{
                width: '100%', padding: '14px', background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
                border: '1px solid rgba(139,92,246,0.3)', borderRadius: 8, color: '#fff', fontSize: 16, fontWeight: 600,
                cursor: wfLoading ? 'not-allowed' : 'pointer', opacity: wfLoading ? 0.7 : 1,
              }}>
              {wfLoading ? 'Running Workflow...' : 'Run Full Banking Workflow'}
            </button>
            <AnimatePresence>{wfResult && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                style={{ marginTop: 16, padding: 20, borderRadius: 'var(--radius)', background: wfResult.success ? 'rgba(139,92,246,0.1)' : 'rgba(239,68,68,0.1)', border: `1px solid ${wfResult.success ? 'rgba(139,92,246,0.2)' : 'rgba(239,68,68,0.2)'}` }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                  <span style={{ fontSize: 28 }}>{wfResult.success ? '\u2705' : '\u274C'}</span>
                  <span style={{ color: wfResult.success ? 'var(--success)' : 'var(--danger)', fontWeight: 600, fontSize: 16 }}>
                    {wfResult.success ? 'Workflow Completed' : 'Workflow Failed'}
                  </span>
                </div>
                {wfResult.caseId && <p style={{ color: 'var(--text-muted)', fontSize: 12 }}>Case ID: <code style={{ color: 'var(--primary)' }}>{wfResult.caseId}</code></p>}
                {wfResult.nadra && <p style={{ color: '#fff', fontSize: 13 }}>NADRA: {wfResult.nadra.verified ? 'Verified' : 'Failed'} | {wfResult.nadra.customerName || ''}</p>}
                {wfResult.cbs && <p style={{ color: '#fff', fontSize: 13 }}>CBS: {wfResult.cbs.accountStatus} | Balance: PKR {wfResult.cbs.availableBalance?.toLocaleString()}</p>}
                {wfResult.payment && <p style={{ color: '#fff', fontSize: 13 }}>1LINK: {wfResult.payment.transactionId}</p>}
                {wfResult.transfer && <p style={{ color: '#fff', fontSize: 13 }}>Raast: {wfResult.transfer.referenceId}</p>}
                {wfResult.message && <p style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 4 }}>{wfResult.message}</p>}
              </motion.div>
            )}</AnimatePresence>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
