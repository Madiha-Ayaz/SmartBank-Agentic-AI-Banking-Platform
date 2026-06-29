import { useEffect, useState, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useSessionContext } from '../stores/sessionContextStore'

const PAGE_SCRIPTS: Record<string, (ctx: any) => { title: string; lines: string[]; actions: {label:string; fn: ()=>void}[] }> = {
  '/dashboard': (ctx) => ({
    title: '👋 Khush aamdeed!',
    lines: [
      ctx.cardBlocked
        ? `Aapka card •••• ${ctx.blockedCardLast4} block hai. Replacement ke liye Cards page jayen.`
        : 'Aaj 8 critical cases hain — Dashboard mein neeche dekhen.',
      'Quick Access se Cards, Transactions ya Loans pe ja sakte hain.'
    ],
    actions: [
      { label: '💳 Cards dekhni hain', fn: () => { navigate('/cards') } },
      { label: '🏦 Loan apply karna hai', fn: () => { navigate('/loans') } }
    ]
  }),
  '/cards': (ctx) => ({
    title: ctx.cardBlocked ? '✅ Card Block Ho Gaya!' : '💳 Card Management',
    lines: ctx.cardBlocked ? [
      `Card •••• ${ctx.blockedCardLast4} block ho gaya. Ref: ${ctx.blockRef}.`,
      'Replacement card mangwane ke liye "Replace Card" button dabayein.',
      'Agle 2 ghante mein agent rabta karega.'
    ] : [
      'Aapke 3 cards hain. Card block karna ho toh Block button dabayein.',
      'PIN 1111 aur OTP 1234 se verify hoga.',
      'Freeze option temporary block ke liye hai — PIN nahi chahiye.'
    ],
    actions: ctx.cardBlocked
      ? [{ label: '🔄 Replace Card', fn: () => { window.dispatchEvent(new CustomEvent('openReplaceModal')) } }]
      : [{ label: '❓ Card block kaise karein?', fn: () => { window.dispatchEvent(new CustomEvent('openChatWidget')) } }]
  }),
  '/transactions': (ctx) => ({
    title: ctx.flaggedCount > 0 ? '⚠️ Suspicious Activity!' : '📋 Transactions',
    lines: ctx.flaggedCount > 0 ? [
      `Main ne ${ctx.flaggedCount} suspicious transactions detect kiye hain!`,
      'Neeche scroll karein — warning icon wali transactions dekhen.',
      '"Raise Dispute" button se complaint darj karein.'
    ] : [
      'Aapki last credit: Salary PKR 1,85,000 aaj.',
      'Search bar se koi bhi transaction dhundh sakte hain.',
      'Transaction expand karein — merchant aur reference number dekhne ke liye.'
    ],
    actions: [
      { label: '🔍 Suspicious filter karo', fn: () => { window.dispatchEvent(new CustomEvent('filterSuspicious')) } }
    ]
  }),
  '/loans': (ctx) => ({
    title: ctx.loanData ? '📋 Application Tayyar!' : '🏦 Loan Apply Karein',
    lines: ctx.loanData ? [
      `Chat se collect kiya data aa gaya hai: PKR ${ctx.loanData.amount}, ${ctx.loanData.purpose}.`,
      'EMI calculator mein apna amount check karein.',
      'Terms & Conditions parh kar checkbox tick karein, phir submit.'
    ] : [
      'Pehle EMI calculator mein apna amount check karein.',
      'Ya chatbot se apply karein — wo data pre-fill kar dega.',
      'Sharia-compliant murabaha loan — koi sood nahi.'
    ],
    actions: ctx.loanData
      ? [{ label: '✅ Submit karo', fn: () => { document.getElementById('loan-submit-btn')?.click() } }]
      : [{ label: '💬 Chatbot se apply karein', fn: () => { window.dispatchEvent(new CustomEvent('openChatWidget')) } }]
  }),
  '/budget': () => ({
    title: '💰 Budget Tracker',
    lines: [
      'Shopping budget 73% use ho gaya is mahine.',
      'Food aur Transport on track hain.',
      'Naya budget add karne ke liye "+" button dabayein.'
    ],
    actions: [{ label: '➕ Budget add karein', fn: () => {} }]
  }),
  '/goals': () => ({
    title: '🎯 Financial Goals',
    lines: [
      'Emergency Fund 36% complete hai.',
      'Hajj savings mein PKR 5,000/month add karein — 4 saal mein poora hoga.',
      '"Add Progress" se aaj ka contribution darj karein.'
    ],
    actions: [{ label: '➕ Progress add karein', fn: () => {} }]
  }),
}

const DEFAULT_SCRIPT = () => ({
  title: '🤖 SmartBank Assistant',
  lines: ['Koi bhi sawal ho toh chat widget (neeche right) use karein.'],
  actions: []
})

let navigate: ReturnType<typeof useNavigate>
let location: ReturnType<typeof useLocation>

export default function LiveRobot() {
  location = useLocation()
  navigate = useNavigate()
  const ctx = useSessionContext()

  const [phase, setPhase] = useState<'hidden'|'walking-in'|'talking'|'walking-out'|'idle'>('hidden')
  const [bubbleVisible, setBubbleVisible] = useState(false)
  const [currentLine, setCurrentLine] = useState(0)
  const [minimized, setMinimized] = useState(false)
  const timerRefs = useRef<ReturnType<typeof setTimeout>[]>([])

  const cardBlocked = ctx.blockedCards.length > 0
  const lastBlock = cardBlocked ? ctx.blockedCards[ctx.blockedCards.length - 1] : null
  const botCtx = {
    cardBlocked,
    blockedCardLast4: lastBlock?.lastFour || '',
    blockRef: lastBlock?.ref || '',
    loanData: ctx.loanData,
    flaggedCount: ctx.flaggedCount,
  }

  const script = (PAGE_SCRIPTS[location.pathname] || DEFAULT_SCRIPT)(botCtx)

  const clearTimers = () => {
    timerRefs.current.forEach(clearTimeout)
    timerRefs.current = []
  }

  const addTimer = (fn: ()=>void, ms: number) => {
    const t = setTimeout(fn, ms)
    timerRefs.current.push(t)
  }

  const startSequence = () => {
    clearTimers()
    setMinimized(false)
    setCurrentLine(0)
    setBubbleVisible(false)
    setPhase('hidden')

    addTimer(() => setPhase('walking-in'), 800)
    addTimer(() => { setPhase('talking'); setBubbleVisible(true) }, 2000)
    script.lines.forEach((_, i) => {
      if (i > 0) addTimer(() => setCurrentLine(i), 2000 + i * 3000)
    })
    const walkOutTime = 2000 + script.lines.length * 3000 + 1000
    addTimer(() => setPhase('walking-out'), walkOutTime)
    addTimer(() => { setPhase('idle'); setMinimized(true) }, walkOutTime + 1200)
  }

  useEffect(() => {
    startSequence()
    return clearTimers
  }, [location.pathname, cardBlocked, ctx.loanData, ctx.flaggedCount])

  const robotX = phase === 'hidden' ? -80
    : phase === 'walking-in' ? 0
    : phase === 'talking' ? 0
    : phase === 'walking-out' ? -80
    : -60

  if (phase === 'hidden' && !minimized) return null

  return (
    <div style={{
      position: 'fixed',
      bottom: 24,
      left: 24,
      zIndex: 999,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-start',
      gap: 8,
      pointerEvents: minimized ? 'auto' : 'none',
    }}>
      {bubbleVisible && !minimized && (
        <div style={{
          background: 'rgba(15,16,40,0.96)',
          border: '1px solid rgba(99,102,241,0.3)',
          borderRadius: '16px 16px 16px 4px',
          padding: '14px 16px',
          maxWidth: 280,
          pointerEvents: 'auto',
          animation: 'robotBubbleIn 0.3s ease',
          marginLeft: 8,
        }}>
          <div style={{ color: '#a78bfa', fontSize: '0.75rem', fontWeight: 600, marginBottom: 6 }}>
            {script.title}
          </div>
          <div style={{ color: '#e2e8f0', fontSize: '0.82rem', lineHeight: 1.6 }}>
            {script.lines[currentLine]}
          </div>
          {script.lines.length > 1 && (
            <div style={{ display: 'flex', gap: 4, marginTop: 8 }}>
              {script.lines.map((_, i) => (
                <div key={i} style={{
                  width: 6, height: 6, borderRadius: '50%',
                  background: i === currentLine ? '#6366f1' : 'rgba(99,102,241,0.25)',
                  transition: 'background 0.3s'
                }} />
              ))}
            </div>
          )}
          {currentLine === script.lines.length - 1 && script.actions.length > 0 && (
            <div style={{ display: 'flex', gap: 8, marginTop: 10, flexWrap: 'wrap' }}>
              {script.actions.map((action, i) => (
                <button key={i} onClick={action.fn} style={{
                  padding: '5px 12px',
                  background: i === 0 ? 'rgba(99,102,241,0.25)' : 'transparent',
                  border: '1px solid rgba(99,102,241,0.4)',
                  borderRadius: 20,
                  color: '#a78bfa',
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                  pointerEvents: 'auto',
                }}>
                  {action.label}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      <div
        onClick={() => { if (minimized) startSequence() }}
        style={{
          transform: `translateX(${robotX}px)`,
          transition: phase === 'talking' ? 'none' : 'transform 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)',
          cursor: minimized ? 'pointer' : 'default',
          pointerEvents: 'auto',
          userSelect: 'none',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div style={{
            width: 44, height: 44,
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            borderRadius: 12,
            display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            gap: 5, position: 'relative',
            boxShadow: '0 0 20px rgba(99,102,241,0.5)',
          }}>
            <div style={{
              position: 'absolute', top: -4, right: -4,
              width: 10, height: 10, borderRadius: '50%',
              background: '#10b981',
              boxShadow: '0 0 6px rgba(16,185,129,0.8)',
              animation: 'robotPulse 2s infinite',
            }} />
            <div style={{ display: 'flex', gap: 8 }}>
              {[0,1].map(i => (
                <div key={i} style={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: '#fff',
                  animation: `robotBlink 4s ${i*0.15}s infinite`,
                }} />
              ))}
            </div>
            <div style={{
              width: 18, height: 3,
              background: phase === 'talking' ? '#a5f3fc' : '#7c3aed',
              borderRadius: 2,
              animation: phase === 'talking' ? 'robotMouth 0.35s steps(1) infinite' : 'none',
            }} />
          </div>
          <div style={{
            width: 36, height: 18,
            background: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
            borderRadius: '0 0 8px 8px',
            marginTop: 2,
          }} />
          <div style={{ display: 'flex', gap: 6, marginTop: 2 }}>
            {[0,1].map(i => (
              <div key={i} style={{
                width: 10, height: 14,
                background: '#4f46e5',
                borderRadius: '0 0 4px 4px',
                animation: phase === 'walking-in' || phase === 'walking-out'
                  ? `robotWalk 0.4s ${i*0.2}s ease-in-out infinite alternate`
                  : 'none',
                transformOrigin: 'top center',
              }} />
            ))}
          </div>
        </div>
      </div>

      {minimized && (
        <div style={{
          fontSize: '0.65rem', color: 'rgba(99,102,241,0.6)',
          marginLeft: 8, marginTop: -4,
        }}>
          click to summon
        </div>
      )}
    </div>
  )
}
