import ThreeDBackground from '../../components/ThreeDBackground'


import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import api from '../../services/api'
import toast from 'react-hot-toast'
import type { DocumentVerifyResponse } from '../../types'

export default function Document() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DocumentVerifyResponse | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return
    setLoading(true)
    setResult(null)
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await api.post('/api/document/verify', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResult(res.data)
      toast.success('Document verified successfully')
    } catch {
      toast.error('Verification failed')
    } finally {
      setLoading(false)
    }
  }

  const riskColor = (level: string) => {
    if (level === 'safe') return 'var(--success)'
    if (level === 'suspicious') return 'var(--warning)'
    return 'var(--danger)'
  }

  return (
    <div className="page">
      <ThreeDBackground />
      <h1><span className="gradient-text">Document Verification</span></h1>

      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <div className="glass-card" style={{ flex: 1, minWidth: 200, textAlign: 'center', padding: 16 }}>
            <div style={{ fontSize: '2rem', marginBottom: 8 }}>
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
            </div>
            <strong style={{ fontSize: '0.85rem' }}>CNIC / ID Card</strong>
          </div>
          <div className="glass-card" style={{ flex: 1, minWidth: 200, textAlign: 'center', padding: 16 }}>
            <div style={{ fontSize: '2rem', marginBottom: 8 }}>
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
              </svg>
            </div>
            <strong style={{ fontSize: '0.85rem' }}>Passport</strong>
          </div>
          <div className="glass-card" style={{ flex: 1, minWidth: 200, textAlign: 'center', padding: 16 }}>
            <div style={{ fontSize: '2rem', marginBottom: 8 }}>
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
              </svg>
            </div>
            <strong style={{ fontSize: '0.85rem' }}>Bank Statement</strong>
          </div>
        </div>
      </div>

      <form onSubmit={handleUpload} className="doc-form">
        <div className="file-input">
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            required
          />
          <button type="button" className="btn" onClick={() => inputRef.current?.click()}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: 6 }}>
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            Choose File
          </button>
          {file && <span className="file-name">{file.name} ({(file.size / 1024).toFixed(1)} KB)</span>}
        </div>
        <button type="submit" disabled={loading || !file}>
          {loading ? 'Verifying...' : 'Verify Document'}
        </button>
      </form>

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="card result-card"
          >
            <h3>Verification Result</h3>

            <div style={{ display: 'flex', gap: 16, alignItems: 'center', marginBottom: 16 }}>
              <div style={{
                width: 60, height: 60, borderRadius: '50%',
                background: `${riskColor(result.risk_level)}20`,
                border: `2px solid ${riskColor(result.risk_level)}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '1.5rem',
              }}>
                {result.risk_level === 'safe' ? '\u2713' : result.risk_level === 'suspicious' ? '!' : '\u2717'}
              </div>
              <div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: riskColor(result.risk_level) }}>
                  {result.risk_level.toUpperCase()}
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  Decision: {result.decision}
                </div>
              </div>
            </div>

            <div className="result-grid">
              <div><strong>Document Type:</strong> <span className="badge" style={{ background: 'rgba(99,102,241,0.1)', color: '#a78bfa', borderColor: 'rgba(99,102,241,0.2)' }}>{result.document_type}</span></div>
              <div><strong>Risk Score:</strong> {result.risk_score}/100</div>
              {result.filename && <div><strong>Filename:</strong> {result.filename}</div>}
              {result.processing_id && <div><strong>Processing ID:</strong> <code style={{ color: 'var(--primary)' }}>{result.processing_id}</code></div>}
            </div>

            {result.risk_score > 0 && (
              <div style={{ marginTop: 12 }}>
                <strong style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Risk Score</strong>
                <div style={{
                  width: '100%', height: 8,
                  background: 'rgba(255,255,255,0.05)',
                  borderRadius: 4, overflow: 'hidden', marginTop: 4,
                }}>
                  <div style={{
                    width: `${result.risk_score}%`,
                    height: '100%',
                    background: `linear-gradient(90deg, var(--success), var(--warning), var(--danger))`,
                    borderRadius: 4,
                    transition: 'width 0.8s ease',
                  }} />
                </div>
              </div>
            )}

            {result.extracted_fields && Object.keys(result.extracted_fields).length > 0 && (
              <>
                <h4>Extracted Fields (OCR)</h4>
                <div className="result-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))' }}>
                  {Object.entries(result.extracted_fields).map(([k, v]) => (
                    <div key={k} style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <strong>{k}:</strong>
                      <span>{String(v)}</span>
                    </div>
                  ))}
                </div>
              </>
            )}

            {result.fraud_indicators.length > 0 && (
              <>
                <h4 style={{ color: 'var(--danger)' }}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--danger)" strokeWidth="2" style={{ marginRight: 6, verticalAlign: 'middle' }}>
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                  Fraud Indicators
                </h4>
                <ul className="fraud-list">
                  {result.fraud_indicators.map((ind, i) => (
                    <li key={i}>
                      <span style={{ color: 'var(--danger)', fontWeight: 600 }}>&#9654;</span> {ind}
                    </li>
                  ))}
                </ul>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
