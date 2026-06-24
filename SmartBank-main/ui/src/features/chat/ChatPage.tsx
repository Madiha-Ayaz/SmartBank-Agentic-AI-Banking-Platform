import ThreeDBackground from '../../components/ThreeDBackground'


import { useRef, useEffect, useState } from 'react'
import { useChatStore } from '../../stores/chatStore'
import Loading from '../../components/Loading'

const quickReplies = [
  'Check balance',
  'Send money',
  'Open account',
  'Report card lost',
  'Apply for loan',
  'Pay bill',
]

export default function ChatPage() {
  const { messages, loading, sendMessage } = useChatStore()
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLDivElement>(null)
  const [showQuickReplies, setShowQuickReplies] = useState(true)

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight
    }
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const val = inputRef.current?.value
    if (val) {
      sendMessage(val)
      inputRef.current!.value = ''
      setShowQuickReplies(false)
    }
  }

  const handleQuickReply = (text: string) => {
    sendMessage(text)
    setShowQuickReplies(false)
  }

  return (
    <div className="page chat-page">
      <h1><span className="gradient-text">Chat with Zara</span></h1>
      <div className="chat-container">
        <div className="chat-msgs" ref={listRef}>
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '3rem', marginBottom: 12 }}>
                <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>
                </svg>
              </div>
              <p style={{ fontSize: '1.1rem', marginBottom: 8 }}>Assalam-o-Alaikum!</p>
              <p>I'm <strong style={{ color: 'var(--primary)' }}>Zara</strong>, your AI-powered financial assistant.</p>
              <p style={{ fontSize: '0.85rem', marginTop: 8 }}>Ask me anything about banking, transactions, or accounts.</p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className="chat-bubble" style={{ alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
              <div style={{
                background: msg.role === 'user'
                  ? 'linear-gradient(135deg, var(--primary), #7c3aed)'
                  : 'rgba(255,255,255,0.05)',
                color: '#fff',
                padding: '12px 16px',
                borderRadius: 12,
                borderBottomRightRadius: msg.role === 'user' ? 4 : 12,
                borderBottomLeftRadius: msg.role === 'assistant' ? 4 : 12,
                border: msg.role === 'assistant' ? '1px solid var(--border)' : 'none',
              }}>
                <div className="chat-bubble-text">{msg.text}</div>
                <div className="chat-bubble-time" style={{ color: msg.role === 'user' ? 'rgba(255,255,255,0.6)' : undefined }}>
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="chat-bubble chat-bubble-assistant">
              <div className="chat-typing">
                <span /><span /><span />
              </div>
            </div>
          )}
        </div>
        {showQuickReplies && messages.length <= 1 && (
          <div style={{ display: 'flex', gap: 6, padding: '8px 12px', flexWrap: 'wrap', borderTop: '1px solid var(--border)' }}>
            {quickReplies.map((r) => (
              <button key={r} className="chat-quick-reply" onClick={() => handleQuickReply(r)}>
                {r}
              </button>
            ))}
          </div>
        )}
        <form onSubmit={handleSubmit} className="chat-input-row">
          <input
            ref={inputRef}
            type="text"
            placeholder="Type your message... (English or Roman Urdu)"
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </form>
      </div>
    </div>
  )
}
