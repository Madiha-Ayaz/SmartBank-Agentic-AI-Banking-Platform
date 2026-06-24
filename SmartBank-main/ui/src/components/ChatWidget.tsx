import { useEffect, useRef, useState } from 'react'
import { useChatStore } from '../stores/chatStore'
import Loading from './Loading'

const quickReplies = [
  'Check balance',
  'Send money',
  'Open account',
  'Report card lost',
]

export default function ChatWidget() {
  const { messages, isOpen, loading, sendMessage, toggle } = useChatStore()
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

  if (!isOpen) return null

  return (
    <div className="chat-widget">
      <div className="chat-header">
        <strong>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--success)', display: 'inline-block', boxShadow: '0 0 8px var(--success-glow)' }} />
          Zara — AI Assistant
        </strong>
        <button onClick={toggle} className="btn-close">&times;</button>
      </div>
      <div className="chat-body" ref={listRef}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', padding: '20px 0', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            <div style={{ fontSize: '2rem', marginBottom: 8 }}>
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>
              </svg>
            </div>
            Assalam-o-Alaikum! I'm Zara, your financial assistant.
            <br />How can I help you today?
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`chat-msg chat-msg-${msg.role}`}>
            {msg.text}
          </div>
        ))}
        {loading && (
          <div className="chat-msg chat-msg-assistant">
            <div className="chat-typing">
              <span /><span /><span />
            </div>
          </div>
        )}
      </div>
      {showQuickReplies && messages.length <= 1 && (
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
          placeholder="Type a message..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </form>
    </div>
  )
}
