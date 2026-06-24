import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface GuideItem {
  id: string
  title: string
  urduTitle: string
  icon: string
  english: string
  urdu: string
}

const guides: GuideItem[] = [
  {
    id: 'dashboard',
    title: 'Dashboard',
    urduTitle: 'ڈیش بورڈ',
    icon: '📊',
    english: 'App ka home page. Yahan aap ko total cases, resolved cases, automation rate, SLA compliance aur cases ki list dekhenge. Ye sab se important page hai operations monitor karne ke liye.',
    urdu: 'Dashboard app ka home page hai. Yahan aap total cases, resolved cases, automation rate, SLA compliance aur cases ki list dekhenge. Ye sab se important page hai operations monitor karne ke liye.',
  },
  {
    id: 'classify',
    title: 'Classify (Intent Classification)',
    urduTitle: 'کلاسیفائی (انٹینٹ کلاسیفیکیشن)',
    icon: '🏷️',
    english: 'Is page par aap kisi bhi customer message ko type kar ke check kar sakte hain ke system usay kis category mein classify karta hai. Ye AI agent automatically detect karta hai ke message mein kya problem hai - card block, PIN reset, statement, etc.',
    urdu: 'Is page par aap kisi bhi customer message ko type karke check kar sakte hain ke system usay kis category mein classify karta hai. AI agent automatically detect karta hai ke message mein kya problem hai - card block, PIN reset, statement, etc.',
  },
  {
    id: 'chat',
    title: 'Chat with Zara',
    urduTitle: 'Zara se Baat Karein',
    icon: '💬',
    english: 'Zara SmartBank ka AI assistant hai. Aap Urdu ya English mein baat kar sakte hain. Zara aap ke banking questions ka jawab deti hai aur agar koi problem hai to automatically resolve bhi kar deti hai.',
    urdu: 'Zara SmartBank ka AI assistant hai. Aap Urdu ya English mein baat kar sakte hain. Zara aap ke banking questions ka jawab deti hai aur agar koi problem hai to automatically resolve bhi kar deti hai.',
  },
  {
    id: 'document',
    title: 'Document Verification',
    urduTitle: 'دستاویز کی تصدیق',
    icon: '📄',
    english: 'Is par aap CNIC, Passport ya bank statement upload kar sakte hain. System AI se document verify karta hai, OCR se text extract karta hai, aur fraud detection bhi karta hai.',
    urdu: 'Is par aap CNIC, Passport ya bank statement upload kar sakte hain. System AI se document verify karta hai, OCR se text extract karta hai, aur fraud detection bhi karta hai.',
  },
  {
    id: 'workflows',
    title: 'Workflows',
    urduTitle: 'ورک فلو',
    icon: '⚙️',
    english: 'Yahan aap sab BPMN workflows dekh sakte hain jo system mein deploy hain. Har workflow ek banking process automate karta hai (card block, PIN generation, statement, etc.)',
    urdu: 'Yahan aap sab BPMN workflows dekh sakte hain jo system mein deploy hain. Har workflow ek banking process automate karta hai (card block, PIN generation, statement, etc.)',
  },
  {
    id: 'goals',
    title: 'Financial Goals',
    urduTitle: 'مالی اہداف',
    icon: '🎯',
    english: 'Naya feature! Yahan aap financial goals set kar sakte hain jaise "5 lakh ka loan clear karna" ya "10 lakh ki savings". Progress track kar sakte hain, target amount set kar sakte hain, aur deadline bhi add kar sakte hain.',
    urdu: 'Naya feature! Yahan aap financial goals set kar sakte hain jaise "5 lakh ka loan clear karna" ya "10 lakh ki savings". Progress track kar sakte hain, target amount set kar sakte hain, aur deadline bhi add kar sakte hain.',
  },
  {
    id: 'budget',
    title: 'Budget Planner',
    urduTitle: 'بجٹ پلانر',
    icon: '💰',
    english: 'Naya feature! Yahan aap monthly budget bana sakte hain. Categories wise planned vs actual spending dekh sakte hain. Zaroorat se zyada kharch karne se bach sakte hain. Pie chart se spending distribution dekh sakte hain.',
    urdu: 'Naya feature! Yahan aap monthly budget bana sakte hain. Categories wise planned vs actual spending dekh sakte hain. Zaroorat se zyada kharch karne se bach sakte hain. Pie chart se spending distribution dekh sakte hain.',
  },
  {
    id: 'admin',
    title: 'Admin Panel',
    urduTitle: 'ایڈمن پینل',
    icon: '🔑',
    english: 'Users aur audit logs dekhne ke liye. Sirf authorized users ke liye. Yahan aap system users manage kar sakte hain aur sab activities ki audit trail dekh sakte hain.',
    urdu: 'Users aur audit logs dekhne ke liye. Sirf authorized users ke liye. Yahan aap system users manage kar sakte hain aur sab activities ki audit trail dekh sakte hain.',
  },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.06 },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
}

export default function FeatureGuide() {
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [language, setLanguage] = useState<'english' | 'urdu'>('english')
  const [search, setSearch] = useState('')

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id)
  }

  const filteredGuides = guides.filter(
    (g) =>
      g.title.toLowerCase().includes(search.toLowerCase()) ||
      g.urduTitle.toLowerCase().includes(search.toLowerCase()) ||
      (language === 'english' ? g.english : g.urdu).toLowerCase().includes(search.toLowerCase())
  )

  return (
    <motion.div className="page" variants={containerVariants} initial="hidden" animate="visible">
      <motion.div variants={itemVariants} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8, flexWrap: 'wrap', gap: 12 }}>
        <h1><span className="gradient-text">Feature Guide</span></h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-sm" onClick={() => setLanguage('english')}
            style={{ background: language === 'english' ? 'linear-gradient(135deg, var(--primary), #8b5cf6)' : 'rgba(255,255,255,0.05)', color: '#fff', border: 'none' }}>
            🇬🇧 English
          </button>
          <button className="btn btn-sm" onClick={() => setLanguage('urdu')}
            style={{ background: language === 'urdu' ? 'linear-gradient(135deg, var(--primary), #8b5cf6)' : 'rgba(255,255,255,0.05)', color: '#fff', border: 'none' }}>
            🇵🇰 اردو (Roman)
          </button>
        </div>
      </motion.div>

      <motion.div variants={itemVariants} style={{ marginBottom: 24 }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6 }}>
          {language === 'english'
            ? 'Welcome to SmartBank! Every feature explained. Click to expand.'
            : 'SmartBank mein khush aamdeed! Har feature yahan explain hai. Click karein.'}
        </p>
      </motion.div>

      <motion.div variants={itemVariants} style={{ marginBottom: 24 }}>
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
          placeholder={language === 'english' ? 'Search features...' : 'Features dhoondein...'}
          style={{ width: '100%', padding: '12px 16px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', color: 'var(--text)', fontSize: '0.9rem' }} />
      </motion.div>

      {filteredGuides.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 60 }}>
          <div style={{ fontSize: '3rem', marginBottom: 12 }}>🔍</div>
          <h3 style={{ marginBottom: 8 }}>{language === 'english' ? 'No Features Found' : 'Koi Feature Nahi Mila'}</h3>
          <p style={{ color: 'var(--text-muted)' }}>
            {language === 'english' ? 'Try different keywords.' : 'Different keywords se search karein.'}
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {filteredGuides.map((guide) => {
            const isExpanded = expandedId === guide.id
            return (
              <motion.div key={guide.id} className="card" variants={itemVariants} layout
                style={{ cursor: 'pointer', padding: isExpanded ? 24 : 16 }}
                onClick={() => toggleExpand(guide.id)}
                whileHover={!isExpanded ? { y: -2 } : undefined}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                  <span style={{ fontSize: '1.5rem' }}>{guide.icon}</span>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <h3 style={{ fontSize: '1rem', margin: 0 }}>
                      {language === 'english' ? guide.title : guide.urduTitle}
                    </h3>
                    {!isExpanded && (
                      <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {(language === 'english' ? guide.english : guide.urdu).slice(0, 80)}...
                      </p>
                    )}
                  </div>
                  <motion.span animate={{ rotate: isExpanded ? 180 : 0 }} transition={{ duration: 0.2 }}
                    style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>▼</motion.span>
                </div>
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.3 }} style={{ overflow: 'hidden' }}>
                      <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
                        <p style={{ fontSize: '0.95rem', lineHeight: 1.7 }}>
                          {language === 'english' ? guide.english : guide.urdu}
                        </p>
                        {language === 'urdu' && (
                          <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--border-light)' }}>
                            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 8 }}>English:</p>
                            <p style={{ fontSize: '0.9rem', lineHeight: 1.7 }}>{guide.english}</p>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )
          })}
        </div>
      )}
    </motion.div>
  )
}