import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import api from '../../services/api'
import toast from 'react-hot-toast'
import type { ClassifyResponse } from '../../types'
import ThreeDBackground from '../../components/ThreeDBackground'

const sampleTexts = [
  { label: '🔴 Complaint', text: 'My debit card was charged twice for the same transaction. Please reverse the extra amount immediately.' },
  { label: '💡 Inquiry', text: 'What is the current profit rate on my savings account and how is it calculated?' },
  { label: '🇵🇰 Urdu/Roman Urdu', text: 'Mera account open karwana hai. Kya documents chahiye? Mei naya customer hoon.' },
  { label: '💰 Loan Request', text: 'I want to apply for a business loan of 5 lakh rupees. What is the process?' },
  { label: '🔒 Card Block', text: 'Mera debit card kho gaya hai. Please isay block kar dijiye.' },
  { label: '📄 Statement', text: 'Mujhe apne account ka statement chahiye January se March tak.' },
]

const intentCodes: Record<string, { label: string; icon: string; description: string }> = {
  ATM01: { label: 'ATM Card Activation', icon: '🏧', description: 'Customer wants to activate their ATM card' },
  PIN02: { label: 'PIN Generation/Reset', icon: '🔑', description: 'Customer forgot their PIN or wants to generate a new one' },
  DEB03: { label: 'Debit Card Block/Unblock', icon: '🛡️', description: 'CRITICAL: Customer wants to block or unblock their card' },
  STM04: { label: 'Bank Statement', icon: '📊', description: 'Customer needs their bank statement' },
  LTR05: { label: 'Account Opening Letter', icon: '📨', description: 'Customer needs an account opening/introduction letter' },
  NIC06: { label: 'CNIC Update', icon: '🪪', description: 'Customer wants to update their ID card details' },
  IB07: { label: 'Internet Banking Recovery', icon: '🌐', description: 'Customer needs help with internet banking access' },
  MB08: { label: 'Mobile Banking Activation', icon: '📱', description: 'Customer wants to activate mobile banking' },
  BAL09: { label: 'Balance Inquiry', icon: '💰', description: 'Customer wants to check their balance' },
  CHQ10: { label: 'Cheque Book Request', icon: '📒', description: 'Customer needs a new cheque book' },
  LOAN11: { label: 'Loan Inquiry', icon: '🏦', description: 'Customer wants information about loans' },
  COMP12: { label: 'Complaint', icon: '⚠️', description: 'Customer is filing a complaint' },
  INFO13: { label: 'General Inquiry', icon: '❓', description: 'Customer has a general question' },
  FRAUD14: { label: 'Fraud Report', icon: '🚨', description: 'CRITICAL: Customer is reporting fraud' },
  UNKNOWN: { label: 'Unknown Intent', icon: '🤷', description: 'Could not determine the customer intent' },
}

export default function Classify() {
  const [text, setText] = useState('')
  const [result, setResult] = useState<ClassifyResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    try {
      const res = await api.post('/api/classify', { text })
      setResult(res.data)
      toast.success('Classification complete')
    } catch {
      toast.error('Classification failed')
    } finally {
      setLoading(false)
    }
  }

  const loadSample = (t: string) => {
    setText(t)
    setResult(null)
  }

  const confidenceColor = (v: number) => {
    if (v >= 0.8) return 'var(--success)'
    if (v >= 0.5) return 'var(--warning)'
    return 'var(--danger)'
  }

  return (
    <div className="page">
      <ThreeDBackground />
      <h1><span className="gradient-text">Intent Classification</span></h1>

      {/* What is this? */}
      <div className="card" style={{ marginBottom: 16, padding: '12px 16px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
        <strong style={{ color: 'var(--primary)' }}>🤖 Ye kya karta hai?</strong><br />
        <strong>English:</strong> Type a customer message (English or Roman Urdu) and the AI will detect the intent — card block, PIN reset, loan request, etc. The system then auto-resolves the problem.<br />
        <strong>اردو:</strong> Koi bhi customer message type karein. AI automatically detect karega ke message mein kya problem hai aur usay resolve karega.
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
        {sampleTexts.map((s) => (
          <button key={s.label} className="btn btn-sm" onClick={() => loadSample(s.text)} title={s.text}>
            + {s.label}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="classify-form">
        <textarea
          rows={4}
          placeholder="Enter customer message in English or Roman Urdu..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Classifying...' : 'Classify Intent'}
        </button>
        {text && (
          <button type="button" className="btn" style={{ marginLeft: 8 }} onClick={() => { setText(''); setResult(null) }}>
            Clear
          </button>
        )}
      </form>

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="card result-card"
          >
            <h3>Classification Result</h3>
            <div className="result-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
              <div>
                <strong>Intent:</strong>
                <div style={{ marginTop: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span>{result.intent.label}</span>
                  <span className="badge" style={{
                    background: `${confidenceColor(result.intent.confidence)}20`,
                    color: confidenceColor(result.intent.confidence),
                    borderColor: `${confidenceColor(result.intent.confidence)}30`,
                  }}>
                    {Math.round(result.intent.confidence * 100)}%
                  </span>
                </div>
              </div>
              <div><strong>Channel:</strong> <span style={{ color: 'var(--primary)' }}>{result.channel}</span></div>
              <div><strong>Language:</strong> <span className="badge" style={{ background: 'rgba(99,102,241,0.1)', color: '#a78bfa', borderColor: 'rgba(99,102,241,0.2)' }}>{result.detected_language}</span></div>
              <div>
                <strong>Escalate to Human:</strong>{' '}
                <span className={`badge badge-${result.escalate_to_human ? 'danger' : 'safe'}`}>
                  {result.escalate_to_human ? 'Yes' : 'No'}
                </span>
              </div>
            </div>

            <div style={{ marginTop: 16 }}>
              <h4>Confidence Meter</h4>
              <div style={{
                width: '100%', height: 8,
                background: 'rgba(255,255,255,0.05)',
                borderRadius: 4, overflow: 'hidden',
                marginTop: 4,
              }}>
                <div style={{
                  width: `${Math.round(result.intent.confidence * 100)}%`,
                  height: '100%',
                  background: `linear-gradient(90deg, ${confidenceColor(result.intent.confidence)}, ${confidenceColor(result.intent.confidence)}dd)`,
                  borderRadius: 4,
                  transition: 'width 0.5s ease',
                  boxShadow: `0 0 10px ${confidenceColor(result.intent.confidence)}`,
                }} />
              </div>
            </div>

            {result.entities && Object.keys(result.entities).length > 0 && (
              <>
                <h4>Extracted Entities</h4>
                <div className="result-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))' }}>
                  {Object.entries(result.entities).map(([k, v]) => (
                    <div key={k} style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <strong>{k}:</strong>
                      <span>{v ?? 'N/A'}</span>
                    </div>
                  ))}
                </div>
              </>
            )}

            <div style={{ marginTop: 16, display: 'flex', gap: 8, alignItems: 'center' }}>
              <strong style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Routing:</strong>
              <span className="badge" style={{
                background: result.escalate_to_human ? 'rgba(239,68,68,0.1)' : 'rgba(16,185,129,0.1)',
                color: result.escalate_to_human ? 'var(--danger)' : 'var(--success)',
                borderColor: result.escalate_to_human ? 'rgba(239,68,68,0.2)' : 'rgba(16,185,129,0.2)',
              }}>
                {result.escalate_to_human ? 'Agent Queue' : 'Automated Response'}
              </span>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Request ID: {result.request_id}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
