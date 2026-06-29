import { useEffect, useRef, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useChatStore } from '../stores/chatStore'
import { useSessionContext } from '../stores/sessionContextStore'

const quickReplies = [
  'Check balance',
  'Send money',
  'Open account',
  'Report card lost',
]

interface LoanData {
  amount: string
  purpose: string
  duration: string
  income: string
}

const LOAN_KEYWORDS = /loan|qarz|finance|car finance|home loan|personal loan|apply/i
const LOAN_QUESTIONS = [
  'Assalam o Alaikum! Main aapki loan application mein madad karunga. Pehle mujhe kuch information chahiye. Aap kitni raqam ka loan lena chahte hain? (PKR mein)',
  'Loan ka maqsad kya hai? (Home / Car / Business / Education / Personal)',
  'Kitne mahine ka loan chahiye? (12 / 24 / 36 / 60)',
  'Aapki maheena aamdan (monthly income) kitni hai? (PKR mein)',
]

export default function ChatWidget() {
  const navigate = useNavigate()
  const { messages, isOpen, loading, sendMessage, toggle, addMessage } = useChatStore()
  const sessionCtx = useSessionContext()
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLDivElement>(null)
  const [showQuickReplies, setShowQuickReplies] = useState(true)
  const [loanMode, setLoanMode] = useState(false)
  const [loanStep, setLoanStep] = useState(-1)
  const [loanData, setLoanData] = useState<LoanData>(sessionCtx.loanData || { amount: '', purpose: '', duration: '', income: '' })
  const [reviewReady, setReviewReady] = useState(false)

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight
    }
  }, [messages, loanStep])

  const startLoanFlow = useCallback(() => {
    setLoanMode(true)
    setReviewReady(false)
    setShowQuickReplies(false)
    const existing = sessionCtx.loanData
    if (existing && existing.income) {
      setLoanData(existing)
      setLoanStep(2)
      setTimeout(() => {
        addMessage({ role: 'assistant' as const, text: LOAN_QUESTIONS[2], timestamp: Date.now() })
      }, 500)
    } else {
      setLoanData({ amount: '', purpose: '', duration: '', income: '' })
      setLoanStep(0)
    }
  }, [sessionCtx.loanData, addMessage])

  const handleLoanReply = useCallback((text: string) => {
    const userMsg = { role: 'user' as const, text, timestamp: Date.now() }
    addMessage(userMsg)

    if (loanStep === 0) {
      setLoanData(prev => ({ ...prev, amount: text }))
      setLoanStep(1)
      setTimeout(() => {
        addMessage({ role: 'assistant' as const, text: LOAN_QUESTIONS[1], timestamp: Date.now() })
      }, 500)
    } else if (loanStep === 1) {
      setLoanData(prev => ({ ...prev, purpose: text }))
      setLoanStep(2)
      setTimeout(() => {
        addMessage({ role: 'assistant' as const, text: LOAN_QUESTIONS[2], timestamp: Date.now() })
      }, 500)
    } else if (loanStep === 2) {
      setLoanData(prev => ({ ...prev, duration: text }))
      setLoanStep(3)
      setTimeout(() => {
        addMessage({ role: 'assistant' as const, text: LOAN_QUESTIONS[3], timestamp: Date.now() })
      }, 500)
    } else if (loanStep === 3) {
      const updated: LoanData = { ...loanData, income: text }
      setLoanData(updated)
      sessionCtx.setLoanData(updated)
      setLoanStep(4)
      setReviewReady(true)
      setTimeout(() => {
        addMessage({
          role: 'assistant' as const,
          text: 'Shukriya! Main aapki application tayyar kar raha hoon. Neeche "Review & Submit" button par click karein.',
          timestamp: Date.now(),
        })
      }, 500)
    }
  }, [loanStep, loanData, addMessage, sessionCtx])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const val = inputRef.current?.value
    if (!val) return

    if (loanMode && loanStep >= 0 && loanStep <= 3) {
      handleLoanReply(val)
      inputRef.current!.value = ''
      return
    }

    if (LOAN_KEYWORDS.test(val)) {
      startLoanFlow()
      inputRef.current!.value = ''
      if (!(sessionCtx.loanData?.income)) {
        setTimeout(() => {
          addMessage({ role: 'assistant' as const, text: LOAN_QUESTIONS[0], timestamp: Date.now() })
        }, 500)
      }
      return
    }

    const ctxSummary = sessionCtx.buildSummary()
    sendMessage(val, ctxSummary)
    inputRef.current!.value = ''
    setShowQuickReplies(false)
    setLoanMode(false)
    setLoanStep(-1)
    setReviewReady(false)
  }

  const handleQuickReply = (text: string) => {
    if (LOAN_KEYWORDS.test(text)) {
      startLoanFlow()
      if (!(sessionCtx.loanData?.income)) {
        setTimeout(() => {
          addMessage({ role: 'assistant' as const, text: LOAN_QUESTIONS[0], timestamp: Date.now() })
        }, 500)
      }
      return
    }
    const ctxSummary = sessionCtx.buildSummary()
    sendMessage(text, ctxSummary)
    setShowQuickReplies(false)
  }

  const handleReviewSubmit = () => {
    navigate('/loans', { state: { prefill: loanData } })
    setLoanStep(0)
    setLoanMode(false)
    setReviewReady(false)
    toggle()
  }

  // Listen for openChatWidget event from robot
  useEffect(() => {
    const handler = () => { toggle() }
    window.addEventListener('openChatWidget', handler)
    return () => window.removeEventListener('openChatWidget', handler)
  }, [toggle])

  if (!isOpen) return null

  const inputDisabled = loading || (loanMode && loanStep >= 4)

  return (
    <div className="chat-widget">
      <div className="chat-header">
        <strong>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--success)', display: 'inline-block', boxShadow: '0 0 8px var(--success-glow)' }} />
          SmartBank Assistant
        </strong>
        <button onClick={toggle} className="btn-close">&times;</button>
      </div>
      <div className="chat-body" ref={listRef}>
        {messages.length === 0 && !loanMode && (
          <div style={{ textAlign: 'center', padding: '20px 0', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            <div style={{ fontSize: '2rem', marginBottom: 8 }}>
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>
              </svg>
            </div>
            Assalam-o-Alaikum! Main SmartBank Assistant hoon. Aap ka balance check kar sakte hain, paise transfer kar sakte hain, ya mini statement le sakte hain.
            <br />How can I help you today?
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`chat-msg chat-msg-${msg.role}`}>
            {msg.text}
          </div>
        ))}
        {reviewReady && (
          <div style={{ padding: '8px 12px' }}>
            <button
              className="btn btn-primary"
              style={{ width: '100%', fontSize: '0.85rem' }}
              onClick={handleReviewSubmit}
            >
              ✅ Form Pe Jayen aur Submit Karein &rarr;
            </button>
          </div>
        )}
        {loading && !loanMode && (
          <div className="chat-msg chat-msg-assistant">
            <div className="chat-typing">
              <span /><span /><span />
            </div>
          </div>
        )}
      </div>
      {showQuickReplies && messages.length <= 1 && !loanMode && (
        <div className="chat-quick-replies">
          {quickReplies.map((r) => (
            <button key={r} className="chat-quick-reply" onClick={() => handleQuickReply(r)}>
              {r}
            </button>
          ))}
        </div>
      )}
      <form onSubmit={handleSubmit} className="chat-footer">
        <input
          ref={inputRef}
          type="text"
          placeholder={loanMode && loanStep >= 0 && loanStep <= 3 ? LOAN_QUESTIONS[loanStep]?.split('(')[0] || 'Type a message...' : 'Type a message...'}
          disabled={inputDisabled}
        />
        <button type="submit" disabled={inputDisabled}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </form>
    </div>
  )
}
