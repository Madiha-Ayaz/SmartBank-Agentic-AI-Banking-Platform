import { useState } from 'react'
import { motion } from 'framer-motion'
import ThreeDBackground from '../../components/ThreeDBackground'

const MASK = '\u2022\u2022\u2022\u2022 \u2022\u2022\u2022\u2022 \u2022\u2022\u2022\u2022'

const CARDS = [
  { id: 1, type: 'Visa Platinum', network: 'VISA', number: '4532882167543310', holder: 'Madiha Ayaz', expiry: '09/27', cvv: '392', balance: 284500, limit: 500000, color: 'linear-gradient(135deg, #6366f1, #7c3aed)', gradient: ['#6366f1', '#7c3aed'], status: 'active' },
  { id: 2, type: 'Mastercard Gold', network: 'MC', number: '5412753490218843', holder: 'Madiha Ayaz', expiry: '03/26', cvv: '715', balance: 95200, limit: 200000, color: 'linear-gradient(135deg, #d97706, #f59e0b)', gradient: ['#d97706', '#f59e0b'], status: 'active' },
  { id: 3, type: 'Visa Classic', network: 'VISA', number: '4111223344556677', holder: 'Madiha Ayaz', expiry: '12/25', cvv: '204', balance: 12800, limit: 50000, color: 'linear-gradient(135deg, #1e293b, #334155)', gradient: ['#1e293b', '#334155'], status: 'frozen' },
]

export default function CardsPage() {
  const [selected, setSelected] = useState(1)
  const [showDetails, setShowDetails] = useState(false)
  const [cards, setCards] = useState(CARDS)

  const card = cards.find(c => c.id === selected) || cards[0]
  const usagePct = card.limit > 0 ? Math.round((card.balance / card.limit) * 100) : 0

  const lastFour = card.number.slice(-4)
  const masked = `${MASK} ${lastFour}`

  const toggleFreeze = () => {
    setCards(prev => prev.map(c => c.id === selected ? { ...c, status: c.status === 'frozen' ? 'active' : 'frozen' } : c))
    alert(`Card ${card.status === 'frozen' ? 'Unfrozen' : 'Frozen'} successfully`)
  }

  return (
    <div className="page">
      <ThreeDBackground />
      <h1><span className="gradient-text">My Cards</span></h1>

      <div style={{ display: 'flex', gap: 20, overflowX: 'auto', paddingBottom: 12, marginBottom: 24, scrollSnapType: 'x mandatory' }}>
        {cards.map(c => {
          const isSelected = c.id === selected
          return (
            <motion.div key={c.id} onClick={() => setSelected(c.id)}
              style={{
                minWidth: 320, height: 200, borderRadius: 16, padding: 24, cursor: 'pointer', position: 'relative', overflow: 'hidden', flexShrink: 0, scrollSnapAlign: 'start',
                background: c.color, border: isSelected ? '2px solid #fff' : '2px solid transparent', transform: isSelected ? 'scale(1.03)' : 'scale(1)', transition: 'all 0.3s ease',
              }}
              whileHover={{ scale: isSelected ? 1.03 : 1.02 }}>
              <div style={{ position: 'absolute', top: -30, right: -30, width: 120, height: 120, borderRadius: '50%', background: 'rgba(255,255,255,0.06)' }} />
              <div style={{ position: 'absolute', bottom: -20, left: -20, width: 80, height: 80, borderRadius: '50%', background: 'rgba(255,255,255,0.04)' }} />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', opacity: 0.8, letterSpacing: 1 }}>{c.type}</div>
                  <div style={{ fontSize: '0.7rem', opacity: 0.6, marginTop: 2 }}>{c.holder}</div>
                </div>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, letterSpacing: 1, opacity: 0.9 }}>
                  {c.network === 'VISA' ? 'VISA' : 'MC'}
                </div>
              </div>
              <div style={{ marginTop: 28, fontSize: '1.2rem', letterSpacing: 2, fontFamily: 'monospace' }}>
                {MASK} {c.number.slice(-4)}
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
            </motion.div>
          )
        })}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
        <div className="card">
          <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 12 }}>Available Balance</h3>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--success)' }}>
            PKR {card.balance.toLocaleString()}
          </div>
          <div style={{ marginTop: 12 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4 }}>
              <span>Usage: {usagePct}% of limit</span>
              <span>PKR {(card.limit - card.balance).toLocaleString()} available</span>
            </div>
            <div className="progress-bar" style={{ background: 'rgba(99,102,241,0.1)', height: 10 }}>
              <motion.div className="progress-fill" style={{ height: 10, background: usagePct > 80 ? 'linear-gradient(90deg, var(--danger), #f87171)' : 'linear-gradient(90deg, var(--primary), #8b5cf6)' }}
                initial={{ width: 0 }} animate={{ width: `${usagePct}%` }} transition={{ duration: 1, ease: 'easeOut' }} />
            </div>
          </div>
          <div style={{ marginTop: 8, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Total Limit: PKR {card.limit.toLocaleString()}
          </div>
        </div>
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Card Details</h3>
            <button className="btn btn-sm" onClick={() => setShowDetails(!showDetails)} style={{ background: 'rgba(99,102,241,0.1)', color: 'var(--primary)', border: '1px solid rgba(99,102,241,0.2)' }}>
              {showDetails ? 'Hide' : 'Show'}
            </button>
          </div>
          <div style={{ display: 'grid', gap: 8, fontSize: '0.9rem' }}>
            <div><span style={{ color: 'var(--text-muted)' }}>Number: </span>{showDetails ? card.number : masked}</div>
            <div><span style={{ color: 'var(--text-muted)' }}>CVV: </span>{showDetails ? card.cvv : '***'}</div>
            <div><span style={{ color: 'var(--text-muted)' }}>Expiry: </span>{card.expiry}</div>
            <div><span style={{ color: 'var(--text-muted)' }}>Status: </span><span className={`badge badge-${card.status === 'frozen' ? 'danger' : 'safe'}`}>{card.status}</span></div>
            <div><span style={{ color: 'var(--text-muted)' }}>Transactions: </span>47 this month</div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 16 }}>Quick Actions</h3>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <button className="btn" style={{ background: 'rgba(245,158,11,0.15)', color: 'var(--warning)', border: '1px solid rgba(245,158,11,0.2)' }} onClick={toggleFreeze}>{card.status === 'frozen' ? 'Unfreeze Card' : 'Freeze Card'}</button>
          <button className="btn" style={{ background: 'rgba(99,102,241,0.15)', color: 'var(--primary)', border: '1px solid rgba(99,102,241,0.2)' }} onClick={() => alert('Replacement card ordered. Will arrive in 3-5 days.')}>Replace Card</button>
          <button className="btn" style={{ background: 'rgba(239,68,68,0.15)', color: 'var(--danger)', border: '1px solid rgba(239,68,68,0.2)' }} onClick={() => alert('Card blocked successfully. A new card will be issued.')}>Block Card</button>
          <button className="btn" style={{ background: 'rgba(59,130,246,0.15)', color: 'var(--info)', border: '1px solid rgba(59,130,246,0.2)' }} onClick={() => alert('PIN set successfully. Check SMS for details.')}>Set PIN</button>
          <button className="btn" style={{ background: 'rgba(16,185,129,0.15)', color: 'var(--success)', border: '1px solid rgba(16,185,129,0.2)' }} onClick={() => alert('International usage turned on. Your card can now be used abroad.')}>International Use</button>
          <button className="btn" style={{ background: 'rgba(139,92,246,0.15)', color: '#a78bfa', border: '1px solid rgba(139,92,246,0.2)' }} onClick={() => alert('Spending limit updated. SMS confirmation sent.')}>Spending Limit</button>
        </div>
      </div>

      <motion.div style={{ border: '2px dashed var(--border)', borderRadius: 16, padding: 32, textAlign: 'center', cursor: 'pointer' }}
        whileHover={{ borderColor: 'var(--primary)', background: 'rgba(99,102,241,0.03)' }} onClick={() => alert('New card application submitted!')}>
        <div style={{ fontSize: '2rem', marginBottom: 8 }}>+</div>
        <div style={{ fontWeight: 600 }}>Apply for New Card</div>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Choose from Visa Platinum, Mastercard Gold, and more</div>
      </motion.div>
    </div>
  )
}
