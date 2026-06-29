import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useLocation } from 'react-router-dom'
import ThreeDBackground from '../../components/ThreeDBackground'
import { useCurrentUser } from '../../stores/authStore'
import { useSessionContext } from '../../stores/sessionContextStore'
import api from '../../services/api'

const MASK = '\u2022\u2022\u2022\u2022 \u2022\u2022\u2022\u2022 \u2022\u2022\u2022\u2022'
const VERIFY_FIELDS = [
  { key: 'cnic', label: 'CNIC Number', placeholder: '42201-1234567-1' },
  { key: 'mother_name', label: 'Mother Name (ماں کا نام)', placeholder: 'Mother\'s full name' },
  { key: 'phone', label: 'Mobile Number', placeholder: '03XX-XXXXXXX' },
]

interface CardData {
  id: number
  card_number: string
  card_type: string
  network: string
  holder_name: string
  account_number: string
  expiry: string
  cvv: string
  status: string
  card_type_flag: string
  created_at: string
}

type BlockStep = 'reason' | 'verify' | 'confirmed' | null
type BioStep = 'register' | 'thumb' | 'eye' | 'pin' | 'done'

const REASONS = ['Card lost', 'Card stolen', 'Suspicious transaction', 'Temporary block']

export default function CardsPage() {
  const user = useCurrentUser()
  const location = useLocation()
  const sessionCtx = useSessionContext()
  const [selected, setSelected] = useState(0)
  const [showDetails, setShowDetails] = useState(false)
  const [cards, setCards] = useState<CardData[]>([])
  const [loading, setLoading] = useState(true)
  const [needsManualAcct, setNeedsManualAcct] = useState(false)
  const [orderingId, setOrderingId] = useState<number | null>(null)

  // Registration form state
  const [regForm, setRegForm] = useState({
    full_name: '', father_name: '', mother_name: '', date_of_birth: '', cnic: '',
    phone: '', email: user.email, address: '', city: '', profession: '',
    monthly_income: '', guardian_name: '', father_cnic: '', helpline: '', password: '',
  })
  const [regLoading, setRegLoading] = useState(false)

  // Biometric apply flow
  const [showBioModal, setShowBioModal] = useState(false)
  const [bioStep, setBioStep] = useState<BioStep>('register')
  const [thumbScanned, setThumbScanned] = useState(false)
  const [eyeScanned, setEyeScanned] = useState(false)
  const [pin, setPin] = useState('')
  const [bioResult, setBioResult] = useState<any>(null)
  const [bioLoading, setBioLoading] = useState(false)
  const [scanProgress, setScanProgress] = useState(0)

  const [blockStep, setBlockStep] = useState<BlockStep>(null)
  const [blockReason, setBlockReason] = useState('')
  const [pinInput, setPinInput] = useState('')
  const [otpInput, setOtpInput] = useState('')
  const [verifyError, setVerifyError] = useState('')
  const [blockRef, setBlockRef] = useState('')
  const [shake, setShake] = useState(false)
  // Identity verification state
  const [needsIdentityVerify, setNeedsIdentityVerify] = useState(false)
  const [verifyForm, setVerifyForm] = useState({ cnic: '', mother_name: '', phone: '' })
  const [idVerifyLoading, setIdVerifyLoading] = useState(false)
  const [idVerifyError, setIdVerifyError] = useState('')
  const [verifySuccess, setVerifySuccess] = useState(false)

  const loadMyCards = async () => {
    setLoading(true)
    try {
      const r = await api.get('/api/cards')
      const data = r.data || {}
      
      // Handle new response format with identity verification check
      if (data.needs_identity_verification) {
        setNeedsIdentityVerify(true)
        setCards([])
        setNeedsManualAcct(true)
        setLoading(false)
        return
      }
      
      const cardsData = data.cards || (Array.isArray(data) ? data : [])
      setNeedsIdentityVerify(false)
      setCards(cardsData)
      if (cardsData.length > 0) {
        setSelected(cardsData[0].id)
        setNeedsManualAcct(false)
      } else {
        setNeedsManualAcct(true)
      }
    } catch {
      setCards([])
      setNeedsManualAcct(true)
    }
    setLoading(false)
  }

  const handleVerifyIdentity = async () => {
    const { cnic, mother_name, phone } = verifyForm
    if (!cnic || !mother_name || !phone) {
      setIdVerifyError('CNIC, Mother Name aur Phone number zaroori hai')
      return
    }
    setIdVerifyLoading(true)
    setIdVerifyError('')
    try {
      const r = await api.post('/api/auth/verify-identity', { cnic, mother_name, phone })
      if (r.data.identity_match && r.data.existing_card) {
        // Identity matched with existing card (may be already_linked)
        setVerifySuccess(true)
        setNeedsIdentityVerify(false)
        setCards([r.data.existing_card as CardData])
        setSelected((r.data.existing_card as CardData).id)
      } else if (r.data.identity_match) {
        setVerifySuccess(true)
        setNeedsIdentityVerify(false)
        // Reload cards now that identity is linked
        await loadMyCards()
      } else if (r.data.is_new) {
        setVerifySuccess(false)
        // New account created! Show registration form for card apply
        setNeedsIdentityVerify(false)
        setNeedsManualAcct(true)
        // Pre-fill reg form with verified data
        setRegForm(prev => ({
          ...prev,
          cnic: verifyForm.cnic,
          mother_name: verifyForm.mother_name,
          phone: verifyForm.phone,
        }))
      } else {
        setVerifySuccess(false)
        // No match and no new account
        setNeedsIdentityVerify(false)
        setNeedsManualAcct(true)
      }
    } catch (e: any) {
      setIdVerifyError(e.response?.data?.message || 'Verification failed. Try again.')
    }
    setIdVerifyLoading(false)
  }

  useEffect(() => {
    loadMyCards()
  }, [])

  const card = cards.find(c => c.id === selected) || cards[0]
  const lastFour = card ? card.card_number.slice(-4) : ''
  const masked = `${MASK} ${lastFour}`

  // Bio verification flow
  const openBioModal = () => {
    setShowBioModal(true)
    setBioStep(cards.length === 0 ? 'register' : 'thumb')
    setThumbScanned(false)
    setEyeScanned(false)
    setPin('')
    setBioResult(null)
    setScanProgress(0)
  }

  const closeBioModal = () => {
    setShowBioModal(false)
    setBioStep('register')
    setThumbScanned(false)
    setEyeScanned(false)
    setPin('')
    setBioResult(null)
    setScanProgress(0)
    setRegForm(f => ({ ...f, full_name: '', father_name: '', mother_name: '', date_of_birth: '', cnic: '', phone: '', address: '', city: '', profession: '', monthly_income: '', guardian_name: '', father_cnic: '', helpline: '', password: '' }))
  }

  const handleRegSubmit = async () => {
    const { full_name, cnic, date_of_birth } = regForm
    if (!full_name || !cnic || !date_of_birth) { alert('Required: full name, CNIC, date of birth'); return }
    setRegLoading(true)
    try {
      const r = await api.post('/api/cards/register-profile', regForm)
      setBioStep('thumb')
    } catch (e: any) {
      const msg = e.response?.data?.message || e.message || 'Registration failed'
      console.error('[RegSubmit] Error:', msg, e.response?.data)
      alert(msg)
    } finally {
      setRegLoading(false)
    }
  }

  const handleThumbScan = () => {
    setScanProgress(0)
    const interval = setInterval(() => {
      setScanProgress(p => {
        if (p >= 100) {
          clearInterval(interval)
          setThumbScanned(true)
          setTimeout(() => setBioStep('eye'), 600)
          return 100
        }
        return p + 5
      })
    }, 60)
  }

  const handleEyeScan = () => {
    setScanProgress(0)
    const interval = setInterval(() => {
      setScanProgress(p => {
        if (p >= 100) {
          clearInterval(interval)
          setEyeScanned(true)
          setTimeout(() => setBioStep('pin'), 600)
          return 100
        }
        return p + 5
      })
    }, 60)
  }

  const handleBioSubmit = async () => {
    if (pin.length < 4) return
    setBioLoading(true)
    try {
      const r = await api.post('/api/cards/biometric-apply', { pin })
      setBioResult(r.data)
      setBioStep('done')
      loadMyCards()
    } catch (e: any) {
      alert(e.response?.data?.message || 'Card application failed')
    }
    setBioLoading(false)
  }

  const openBlockModal = () => {
    setBlockStep('reason')
    setBlockReason('')
    setPinInput('')
    setOtpInput('')
    setVerifyError('')
    setBlockRef('')
    setShake(false)
  }

  const closeBlockModal = () => {
    setBlockStep(null)
    setBlockReason('')
    setPinInput('')
    setOtpInput('')
    setVerifyError('')
    setBlockRef('')
  }

  const handleReasonContinue = () => {
    if (!blockReason) { setShake(true); setTimeout(() => setShake(false), 500); return }
    setBlockStep('verify')
    setVerifyError('')
  }

  const handleVerify = () => {
    const pinOk = pinInput === '1111'
    const otpOk = otpInput === '1234'
    if (!pinOk || !otpOk) {
      setVerifyError('Incorrect PIN or OTP. Try again.')
      setShake(true); setTimeout(() => setShake(false), 500)
      return
    }
    const ref = 'BLK-' + Math.floor(100000 + Math.random() * 900000)
    setBlockRef(ref)
    setCards(prev => prev.map(c => c.id === selected ? { ...c, status: 'frozen' } : c))
    setBlockStep('confirmed')
    sessionCtx.addBlockedCard({ cardId: selected, lastFour, reason: blockReason, ref, timestamp: Date.now() })
  }

  const handleOrderPhysical = async (cardId: number) => {
    setOrderingId(cardId)
    try {
      const r = await api.post('/api/cards/order-physical', { card_id: cardId })
      alert(r.data.message)
      loadMyCards()
    } catch (e: any) { alert(e.response?.data?.message || 'Order failed') }
    setOrderingId(null)
  }

  useEffect(() => {
    if (location.state?.triggerBlock) {
      openBlockModal()
      if (location.state?.cardId) setSelected(location.state.cardId)
    }
  }, [location.state])

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && blockStep && blockStep !== 'confirmed') closeBlockModal()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [blockStep])

  const showEmpty = needsManualAcct && cards.length === 0 && !loading

  return (
    <div className="page">
      <ThreeDBackground />
      <h1><span className="gradient-text">My Cards</span></h1>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 60, color: 'var(--text-muted)' }}>Loading...</div>
      ) : needsIdentityVerify ? (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          className="card" style={{ maxWidth: 480, margin: '40px auto', padding: 32, textAlign: 'center' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: 8 }}>{'\u{1F511}'}</div>
          <h2 style={{ marginBottom: 8 }}>Apni Identity Verify Karein</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 20 }}>
            Cards dekhne ke liye pehle apni identity verify karein
          </p>

          {VERIFY_FIELDS.map(f => (
            <div key={f.key} className="form-group" style={{ marginBottom: 14, textAlign: 'left' }}>
              <label style={{ fontSize: '0.85rem', marginBottom: 4, display: 'block', fontWeight: 500 }}>{f.label}</label>
              <input
                value={(verifyForm as any)[f.key]}
                onChange={e => setVerifyForm({ ...verifyForm, [f.key]: e.target.value })}
                placeholder={f.placeholder}
                style={{
                  width: '100%', padding: '10px 12px', background: 'rgba(0,0,0,0.3)',
                  border: '1px solid var(--border)', borderRadius: 8, color: '#fff',
                  fontSize: '0.95rem', outline: 'none'
                }}
              />
            </div>
          ))}

          {idVerifyError && (
            <p style={{ color: 'var(--danger)', fontSize: '0.85rem', marginBottom: 8 }}>{idVerifyError}</p>
          )}

          <button className="btn btn-primary" onClick={handleVerifyIdentity}
            disabled={idVerifyLoading || !verifyForm.cnic || !verifyForm.mother_name || !verifyForm.phone}
            style={{ width: '100%', marginTop: 8 }}>
            {idVerifyLoading ? 'Verifying...' : 'Verify Identity'}
          </button>

          <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: 12 }}>
            Aapka CNIC, Mother Name aur Phone number sirf identity match ke liye check kiya jayega
          </p>
        </motion.div>
      ) : showEmpty ? (
        <div className="card" style={{ maxWidth: 500, margin: '40px auto', textAlign: 'center', padding: 32 }}>
          <div style={{ fontSize: '2.5rem', marginBottom: 12 }}>{'\u{1F4B3}'}</div>
          <h2 style={{ marginBottom: 12 }}>No Cards Yet</h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: 12 }}>
            Nayab card apply karne ke liye biometric verification karein
          </p>
          <button className="btn btn-primary" onClick={openBioModal} style={{ width: '100%', marginBottom: 8 }}>
            Apply for New Card
          </button>
        </div>
      ) : cards.length > 0 ? (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            {card && (
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Acct: {card.account_number}</span>
            )}
          </div>

          {/* Card Carousel */}
          <div style={{ display: 'flex', gap: 20, overflowX: 'auto', paddingBottom: 12, marginBottom: 24, scrollSnapType: 'x mandatory' }}>
            {cards.map(c => {
              const isSelected = c.id === selected
              const colorMap: Record<string, string> = {
                'Visa Platinum': 'linear-gradient(135deg, #6366f1, #7c3aed)',
                'Mastercard Gold': 'linear-gradient(135deg, #d97706, #f59e0b)',
                'Visa Classic': 'linear-gradient(135deg, #1e293b, #334155)',
              }
              return (
                <motion.div key={c.id} onClick={() => setSelected(c.id)}
                  style={{
                    minWidth: 'min(320px, 85vw)', height: 200, borderRadius: 16, padding: 24, cursor: 'pointer', position: 'relative', overflow: 'hidden', flexShrink: 0, scrollSnapAlign: 'start',
                    background: c.status === 'frozen' ? 'linear-gradient(135deg, #475569, #334155)' : (colorMap[c.card_type] || 'linear-gradient(135deg, #6366f1, #7c3aed)'),
                    border: isSelected ? '2px solid #fff' : '2px solid transparent',
                    transform: isSelected ? 'scale(1.03)' : 'scale(1)', transition: 'all 0.3s ease',
                    filter: c.status === 'frozen' ? 'grayscale(0.6)' : 'none',
                  }}
                  whileHover={{ scale: isSelected ? 1.03 : 1.02 }}>
                  <div style={{ position: 'absolute', top: -30, right: -30, width: 120, height: 120, borderRadius: '50%', background: 'rgba(255,255,255,0.06)' }} />
                  <div style={{ position: 'absolute', bottom: -20, left: -20, width: 80, height: 80, borderRadius: '50%', background: 'rgba(255,255,255,0.04)' }} />
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontSize: '0.75rem', opacity: 0.8, letterSpacing: 1 }}>{c.card_type}</div>
                      <div style={{ fontSize: '0.7rem', opacity: 0.6, marginTop: 2 }}>{c.holder_name}</div>
                    </div>
                    <div style={{ fontSize: '1.4rem', fontWeight: 800, letterSpacing: 1, opacity: 0.9 }}>
                      {c.network === 'VISA' ? 'VISA' : 'MC'}
                    </div>
                  </div>
                  <div style={{ marginTop: 28, fontSize: '1.2rem', letterSpacing: 2, fontFamily: 'monospace' }}>
                    {MASK} {c.card_number.slice(-4)}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 20, fontSize: '0.8rem', opacity: 0.8 }}>
                    <span>EXP {c.expiry}</span>
                    <span>CVV ***</span>
                  </div>
                  {c.status === 'frozen' && (
                    <div style={{ position: 'absolute', top: 12, right: 12, background: 'rgba(239,68,68,0.9)', color: '#fff', fontSize: '0.65rem', fontWeight: 700, padding: '2px 10px', borderRadius: 20, letterSpacing: 1 }}>
                      FROZEN
                    </div>
                  )}
                  {c.card_type_flag === 'digital' && (
                    <div style={{ position: 'absolute', bottom: 12, right: 12, background: 'rgba(16,185,129,0.9)', color: '#fff', fontSize: '0.6rem', fontWeight: 700, padding: '2px 8px', borderRadius: 20 }}>
                      DIGITAL
                    </div>
                  )}
                </motion.div>
              )
            })}
          </div>

          <div className="grid-2" style={{ marginBottom: 24 }}>
            <div className="card">
              <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 12 }}>Card Details</h3>
              <div style={{ display: 'grid', gap: 8, fontSize: '0.9rem' }}>
                <div><span style={{ color: 'var(--text-muted)' }}>Number: </span>{showDetails ? card.card_number : masked}</div>
                <div><span style={{ color: 'var(--text-muted)' }}>CVV: </span>{showDetails ? card.cvv : '***'}</div>
                <div><span style={{ color: 'var(--text-muted)' }}>Expiry: </span>{card.expiry}</div>
                <div><span style={{ color: 'var(--text-muted)' }}>Type: </span>{card.card_type} ({card.card_type_flag})</div>
                <div><span style={{ color: 'var(--text-muted)' }}>Status: </span><span className={`badge badge-${card.status === 'frozen' ? 'danger' : 'safe'}`}>{card.status}</span></div>
              </div>
              <button className="btn btn-sm" onClick={() => setShowDetails(!showDetails)} style={{ marginTop: 8, background: 'rgba(99,102,241,0.1)', color: 'var(--primary)', border: '1px solid rgba(99,102,241,0.2)' }}>
                {showDetails ? 'Hide Details' : 'Show Details'}
              </button>
            </div>
            <div className="card">
              <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 12 }}>Quick Actions</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <button className="btn" style={{ background: 'rgba(239,68,68,0.15)', color: 'var(--danger)', border: '1px solid rgba(239,68,68,0.2)' }} onClick={openBlockModal}>
                  Block Card
                </button>
                <button className="btn" style={{ background: 'rgba(99,102,241,0.15)', color: 'var(--primary)', border: '1px solid rgba(99,102,241,0.2)' }}
                  onClick={() => handleOrderPhysical(card.id)} disabled={orderingId === card.id || card.card_type_flag === 'physical'}>
                  {card.card_type_flag === 'physical' ? 'Physical Card Ordered' : orderingId === card.id ? 'Ordering...' : 'Order Physical Card ($2000 fee)'}
                </button>
                <button className="btn" style={{ background: 'rgba(16,185,129,0.15)', color: 'var(--success)', border: '1px solid rgba(16,185,129,0.2)' }}
                  onClick={openBioModal}>
                  Apply New Card (Biometric)
                </button>
              </div>
            </div>
          </div>
        </>
      ) : null}

      {/* Biometric Verification Modal */}
      <AnimatePresence>
        {showBioModal && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
            <motion.div initial={{ scale: 0.85 }} animate={{ scale: 1 }} exit={{ scale: 0.85 }}
              className="card" style={{ maxWidth: 420, width: '100%', padding: 32, textAlign: 'center' }}>
              {bioStep === 'register' && (
                <div style={{ textAlign: 'left', maxHeight: '70vh', overflowY: 'auto', paddingRight: 4 }}>
                  <div style={{ fontSize: '2rem', marginBottom: 8, textAlign: 'center' }}>{'\u{1F464}'}</div>
                  <h2 style={{ textAlign: 'center', marginBottom: 4 }}>Registration</h2>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center', marginBottom: 16 }}>
                    Card apply karne se pehle apna profile complete karein
                  </p>
                  <div className="reg-form-grid">
                    {[
                      ['full_name', 'Full Name *', 'text'],
                      ['father_name', "Father's Name", 'text'],
                      ['mother_name', "Mother's Name", 'text'],
                      ['date_of_birth', 'Date of Birth *', 'date'],
                      ['cnic', 'CNIC *', 'text'],
                      ['father_cnic', "Father's CNIC", 'text'],
                      ['phone', 'Phone Number', 'tel'],
                      ['email', 'Email', 'email'],
                      ['address', 'Address', 'text'],
                      ['city', 'City', 'text'],
                      ['profession', 'Profession', 'text'],
                      ['monthly_income', 'Monthly Income', 'number'],
                      ['guardian_name', 'Guardian Name', 'text'],
                      ['helpline', 'Help Line Number', 'tel'],
                      ['password', 'Password', 'password'],
                    ].map(([key, label, type]) => (
                      <div key={key} className={`reg-field${['address','password'].includes(key) ? ' reg-full' : ''}`}>
                        <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: 3 }}>{label}</label>
                        <input type={type} value={(regForm as any)[key]} placeholder={label}
                          onChange={e => setRegForm(f => ({ ...f, [key]: e.target.value }))}
                          style={{ width: '100%', padding: '8px 10px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border)', borderRadius: 6, color: '#fff', fontSize: '0.85rem', outline: 'none' }} />
                      </div>
                    ))}
                  </div>
                  <button className="btn btn-primary" onClick={handleRegSubmit} disabled={regLoading} style={{ width: '100%', marginTop: 14 }}>
                    {regLoading ? 'Saving...' : 'Save & Continue'}
                  </button>
                </div>
              )}

              {bioStep === 'thumb' && (
                <>
                  <motion.div animate={{ scale: [1, 1.05, 1] }} transition={{ repeat: Infinity, duration: 1.5 }}
                    style={{ fontSize: '4rem', marginBottom: 12 }}>
                    {'\u{1F91A}'}
                  </motion.div>
                  <h2 style={{ marginBottom: 8 }}>Thumb Scan</h2>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 16 }}>
                    Apna thumb scanner par rakhein
                  </p>
                  {!thumbScanned ? (
                    <>
                      <div style={{ height: 6, background: 'rgba(255,255,255,0.1)', borderRadius: 3, marginBottom: 16, overflow: 'hidden' }}>
                        <motion.div style={{ height: '100%', background: 'var(--primary)', borderRadius: 3, width: `${scanProgress}%` }} />
                      </div>
                      <button className="btn btn-primary" onClick={handleThumbScan} disabled={scanProgress > 0 && scanProgress < 100}>
                        {scanProgress > 0 ? 'Scanning...' : 'Start Scan'}
                      </button>
                    </>
                  ) : (
                    <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} style={{ color: '#10b981', fontSize: '1.2rem' }}>
                      {'\u2714\uFE0F'} Thumb verified!
                    </motion.div>
                  )}
                </>
              )}

              {bioStep === 'eye' && (
                <>
                  <motion.div animate={{ scale: [1, 1.08, 1] }} transition={{ repeat: Infinity, duration: 1.8 }}
                    style={{ fontSize: '4rem', marginBottom: 12 }}>
                    {'\u{1F441}\uFE0F'}
                  </motion.div>
                  <h2 style={{ marginBottom: 8 }}>Eye Scan</h2>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 16 }}>
                    Camera ki taraf dekhein for iris verification
                  </p>
                  {!eyeScanned ? (
                    <>
                      <div style={{ height: 6, background: 'rgba(255,255,255,0.1)', borderRadius: 3, marginBottom: 16, overflow: 'hidden' }}>
                        <motion.div style={{ height: '100%', background: 'var(--primary)', borderRadius: 3, width: `${scanProgress}%` }} />
                      </div>
                      <button className="btn btn-primary" onClick={handleEyeScan} disabled={scanProgress > 0 && scanProgress < 100}>
                        {scanProgress > 0 ? 'Scanning...' : 'Start Scan'}
                      </button>
                    </>
                  ) : (
                    <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} style={{ color: '#10b981', fontSize: '1.2rem' }}>
                      {'\u2714\uFE0F'} Iris verified!
                    </motion.div>
                  )}
                </>
              )}

              {bioStep === 'pin' && (
                <>
                  <div style={{ fontSize: '4rem', marginBottom: 12 }}>{'\u{1F511}'}</div>
                  <h2 style={{ marginBottom: 8 }}>Set Your Card PIN</h2>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 16 }}>
                    4-digit PIN set karein apne new card ke liye
                  </p>
                  <input type="password" maxLength={4} value={pin}
                    onChange={e => setPin(e.target.value.replace(/\D/g, '').slice(0, 4))}
                    placeholder="****" style={{
                      width: '100%', padding: '14px', fontSize: '1.5rem', letterSpacing: 8, textAlign: 'center',
                      background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border)', borderRadius: 8, color: '#fff',
                      outline: 'none', marginBottom: 16,
                    }} />
                  <button className="btn btn-primary" onClick={handleBioSubmit} disabled={pin.length < 4 || bioLoading} style={{ width: '100%' }}>
                    {bioLoading ? 'Issuing Card...' : 'Verify & Issue Card'}
                  </button>
                </>
              )}

              {bioStep === 'done' && bioResult && (
                <>
                  <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} style={{ fontSize: '3rem', marginBottom: 8 }}>{'\u2705'}</motion.div>
                  <h2 style={{ color: '#10b981', marginBottom: 8 }}>Card Issued Successfully!</h2>
                  <div style={{ background: 'rgba(16,185,129,0.08)', borderRadius: 12, padding: 20, marginBottom: 16, border: '1px solid rgba(16,185,129,0.15)', textAlign: 'left', fontSize: '0.85rem' }}>
                    <div style={{ display: 'grid', gap: 8 }}>
                      <div><span style={{ color: 'var(--text-muted)' }}>Card: </span><strong>{bioResult.card_number}</strong></div>
                      <div><span style={{ color: 'var(--text-muted)' }}>Expiry: </span>{bioResult.expiry}</div>
                      <div><span style={{ color: 'var(--text-muted)' }}>CVV: </span>{bioResult.cvv}</div>
                      <div><span style={{ color: 'var(--text-muted)' }}>PIN: </span><strong style={{ color: '#f59e0b', fontSize: '1.1rem' }}>{bioResult.pin}</strong></div>
                      <div><span style={{ color: 'var(--text-muted)' }}>Account: </span><strong>{bioResult.account_number}</strong></div>
                      <div><span style={{ color: 'var(--text-muted)' }}>Holder: </span>{bioResult.holder_name}</div>
                    </div>
                  </div>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: 16 }}>
                    PIN save karein. Yeh screen dobara nahi dikhe gi.
                  </p>
                  <button className="btn btn-primary" onClick={closeBioModal} style={{ width: '100%' }}>Done</button>
                </>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {blockStep && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}
            onClick={(e) => { if (e.target === e.currentTarget && blockStep !== 'confirmed') closeBlockModal() }}>
            <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
              className="card" style={{ maxWidth: 460, width: '100%', padding: 32, position: 'relative' }}>
              <button onClick={blockStep !== 'confirmed' ? closeBlockModal : undefined}
                style={{ position: 'absolute', top: 12, right: 16, background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '1.5rem', cursor: 'pointer' }}>&times;</button>

              {blockStep === 'reason' && (
                <>
                  <h2 style={{ marginBottom: 20 }}>Why do you want to block this card?</h2>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 20 }}>
                    {REASONS.map(r => (
                      <label key={r} style={{
                        display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px',
                        background: blockReason === r ? 'rgba(99,102,241,0.1)' : 'rgba(255,255,255,0.03)',
                        border: blockReason === r ? '1px solid var(--primary)' : '1px solid var(--border)',
                        borderRadius: 8, cursor: 'pointer', transition: 'all 0.2s',
                        animation: shake ? 'shake 0.4s ease' : 'none',
                      }}>
                        <input type="radio" name="blockReason" value={r} checked={blockReason === r}
                          onChange={() => setBlockReason(r)} style={{ accentColor: 'var(--primary)' }} />
                        {r}
                      </label>
                    ))}
                  </div>
                  {shake && !blockReason && <p style={{ color: 'var(--danger)', fontSize: '0.85rem', marginBottom: 8 }}>Please select a reason</p>}
                  <button className="btn btn-primary" onClick={handleReasonContinue} style={{ width: '100%' }}>Continue</button>
                </>
              )}

              {blockStep === 'verify' && (
                <>
                  <h2 style={{ marginBottom: 8 }}>Verify your identity</h2>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 20 }}>
                    Card ending in <strong>{lastFour}</strong> &middot; Reason: {blockReason}
                  </p>
                  <div className="form-group" style={{ marginBottom: 14 }}>
                    <label>Enter your 4-digit PIN</label>
                    <input type="password" maxLength={4} value={pinInput} onChange={e => setPinInput(e.target.value.replace(/\D/g, '').slice(0, 4))}
                      placeholder="****" style={{ fontSize: '1.2rem', letterSpacing: 4 }} />
                  </div>
                  <div className="form-group" style={{ marginBottom: 14 }}>
                    <label>Enter OTP sent to {user.phone}</label>
                    <input type="text" maxLength={4} value={otpInput} onChange={e => setOtpInput(e.target.value.replace(/\D/g, '').slice(0, 4))}
                      placeholder="****" style={{ fontSize: '1.2rem', letterSpacing: 4 }} />
                  </div>
                  {verifyError && (
                    <motion.p initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                      style={{ color: 'var(--danger)', fontSize: '0.85rem', marginBottom: 8, animation: shake ? 'shake 0.4s ease' : 'none' }}>
                      {verifyError}
                    </motion.p>
                  )}
                  <button className="btn btn-danger" onClick={handleVerify} style={{ width: '100%' }}
                    disabled={pinInput.length < 4 || otpInput.length < 4}>
                    Verify &amp; Block Card
                  </button>
                </>
              )}

              {blockStep === 'confirmed' && (
                <div style={{ textAlign: 'center', padding: 20 }}>
                  <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} style={{ fontSize: '3rem', marginBottom: 12 }}>{'\u2714\uFE0F'}</motion.div>
                  <h2 style={{ color: 'var(--success)', marginBottom: 12 }}>Card Blocked Successfully</h2>
                  <div style={{ background: 'rgba(16,185,129,0.08)', borderRadius: 12, padding: 20, marginBottom: 16, border: '1px solid rgba(16,185,129,0.15)' }}>
                    <div style={{ fontSize: '0.9rem', marginBottom: 6 }}>Card ending in <strong>{lastFour}</strong></div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 4 }}>Reason: {blockReason}</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Reference: <strong style={{ color: 'var(--primary)' }}>{blockRef}</strong></div>
                  </div>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 16 }}>Our agent will contact you within 2 hours</p>
                  <button className="btn btn-primary" onClick={closeBlockModal} style={{ width: '100%' }}>Done</button>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0) }
          10%, 30%, 50%, 70%, 90% { transform: translateX(-6px) }
          20%, 40%, 60%, 80% { transform: translateX(6px) }
        }
        .reg-form-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 10px;
        }
        .reg-field.reg-full {
          grid-column: 1 / -1;
        }
        @media (max-width: 500px) {
          .reg-form-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  )
}
