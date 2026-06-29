// ============================================================================
// RAG Knowledge Base — SmartBank App Features & Data
// Every page, its route, data, and how to use it
// ============================================================================

const KNOWLEDGE = {
  pages: [
    {
      route: '/dashboard',
      title: 'Dashboard',
      description: 'Landing page after login. Shows case stats (total, resolved, pending, human review), automation rate gauge, SLA compliance gauge, avg resolution time, critical cases count. Quick Access section with 4 cards linking to My Cards, Transactions, Loans, Budget. Pie charts for cases by status/priority/channel. Area chart for performance trends. Recent cases table.',
      features: ['Quick Access to Cards/Transactions/Loans/Budget', 'Case metrics overview', 'Performance gauges', 'Analytics charts'],
    },
    {
      route: '/cards',
      title: 'My Cards',
      description: 'Displays 3 cards: Visa Platinum (PKR 284,500 balance, PKR 500K limit), Mastercard Gold (PKR 95,200 balance, PKR 200K limit), Visa Classic (PKR 12,800 balance, PKR 50K limit — currently frozen). Card detail panel with show/hide number/CVV. Usage progress bar. Quick actions: Freeze/Unfreeze Card, Replace Card, Block Card, Set PIN, International Use, Spending Limit. Apply for New Card button at bottom.',
      data: [
        { card: 'Visa Platinum', holder: 'Madiha Ayaz', balance: 284500, limit: 500000, expiry: '09/27', network: 'VISA', status: 'active' },
        { card: 'Mastercard Gold', holder: 'Madiha Ayaz', balance: 95200, limit: 200000, expiry: '03/26', network: 'MC', status: 'active' },
        { card: 'Visa Classic', holder: 'Madiha Ayaz', balance: 12800, limit: 50000, expiry: '12/25', network: 'VISA', status: 'frozen' },
      ],
    },
    {
      route: '/transactions',
      title: 'Transactions',
      description: '20 dummy Pakistan-relevant transactions with search bar, type filter (All/Credit/Debit), 13 category pills (Income, Shopping, Food, Transport, Utilities, Transfer, Entertainment, Groceries, Health, Business, Cash, Education). Expandable rows show reference, merchant, card used, status, amount. Raise Dispute and Email Receipt buttons per transaction. Stats: total count, income (PKR 235,000), spent (PKR 130,041), net balance.',
      features: ['Search by description/merchant/ref', 'Filter by Credit/Debit', '13 category filters with colors', 'Expand details per transaction', 'Raise dispute', 'Email receipt'],
      sample_transactions: [
        'Salary Credit TechCorp (PKR 185,000)',
        'Careem Ride (PKR 420)',
        'Khaadi DHA Phase 6 (PKR 8,750)',
        'Nandos Clifton (PKR 3,200)',
        'PTCL Bill (PKR 2,100)',
        'Netflix (PKR 1,100)',
        'Daraz.pk Purchase (PKR 4,299)',
        'Freelance Upwork (PKR 45,000)',
      ],
    },
    {
      route: '/loans',
      title: 'Loans',
      description: 'Loan application form with fields: Full Name (auto-filled), Amount, Purpose (Home/Car/Business/Education/Personal), Duration (12/24/36/60 months), Monthly Income. Submit triggers animated 7-step BPMN tracker (Application Received → Eligibility Check → Sharia Compliance → Fraud Analysis → Credit Score → Human Review → Decision) with auto-advance every 2s. Shows APPROVED result with amount, monthly installment, processing fee PKR 2,500, case ID. Existing loans: Home Loan PKR 2.5M (active), Car Finance PKR 850K (active), Personal Loan PKR 150K (completed).',
      existing_loans: [
        { type: 'Home Loan', amount: 2500000, months: 36, monthly: 82500, status: 'Active' },
        { type: 'Car Finance', amount: 850000, months: 24, monthly: 39200, status: 'Active' },
        { type: 'Personal Loan', amount: 150000, months: 12, monthly: 13500, status: 'Completed' },
      ],
    },
    {
      route: '/budget',
      title: 'Budget Planner',
      description: 'Create monthly budgets per category (Food, Transport, Utilities, Entertainment, Shopping, Other). Add transactions to budgets. Shows total planned, total spent, remaining, overspent categories count. Pie chart of spending distribution. Budget cards with progress bars, transactions list, delete option. Fallback data: Food PKR 25K planned/15K spent, Transport PKR 12K/8.5K, Shopping PKR 30K/22K, Utilities PKR 8K/5.2K, Entertainment PKR 5K/3.1K.',
    },
    {
      route: '/goals',
      title: 'Financial Goals',
      description: 'Create financial goals with title, target amount, deadline, category (Savings, Debt, Investment, Education, Travel, Health, Other). Circular progress indicator per goal. Add progress button to contribute towards goal. Delete goal option. Fallback goals: Emergency Fund PKR 500K target (36%), Laptop Upgrade PKR 120K (63%), Hajj Savings PKR 1.2M (27%). Overdue detection.',
    },
    {
      route: '/arie',
      title: 'ARIE Engine',
      description: 'Autonomous Resilience & Interceptor Engine. Three capabilities: (1) Proactive Scam Interceptor — detects vishing/active fraud/panic patterns in real-time, triggers SEC01 account lockdown with 6-step resolution; (2) Roman Urdu Repair Engine — cross-references ambiguous short Urdu inputs with telemetry logs (e.g. ATM_CARD_RETAINED); (3) Self-Healing Circuit Breaker — when core banking API is down, queues requests with SHA-256 audit hash for auto-replay. Shows system status, test buttons, recent intercepts table.',
      capabilities: ['Proactive Scam Interceptor (SEC01)', 'Roman Urdu Repair Engine', 'Self-Healing Circuit Breaker'],
    },
    {
      route: '/classify',
      title: 'Intent Classification',
      description: 'Classify user text into 14 intent codes (ATM01, PIN02, DEB03, STM04, LTR05, NIC06, IB07, MB08, BAL09, CHQ10, LOAN11, COMP12, INFO13, FRAUD14) with auto-resolution.',
    },
    {
      route: '/chat',
      title: 'Chat Page',
      description: 'Full-page chat interface with Zara AI assistant.',
    },
    {
      route: '/document',
      title: 'Document Verification',
      description: 'Upload and verify documents: CNIC, Passport, Bank Statement, Utility Bill, Tax Document. Returns risk score, OCR confidence, extracted fields, fraud indicators.',
    },
    {
      route: '/workflows',
      title: 'Workflows',
      description: 'View BPMN workflow files from the workflows directory.',
    },
    {
      route: '/guide',
      title: 'Feature Guide',
      description: 'Interactive guide showing all SmartBank features and how to use them.',
    },
  ],
  navigation: {
    sidebar: ['Dashboard /dashboard', 'Classify /classify', 'Chat /chat', 'Cards /cards', 'Transactions /transactions', 'Loans /loans', 'Goals /goals', 'Budget /budget', 'ARIE /arie', 'Document /document', 'Workflows /workflows', 'Guide /guide'],
    quick_access: ['My Cards (Cards page)', 'Transactions', 'Loans', 'Budget'],
  },
  general_info: {
    app_name: 'SmartBank',
    user: 'Madiha Ayaz',
    theme: 'Dark theme with background #0a0b1e, cards with rgba(15,16,40,0.75), primary color #6366f1',
    currency: 'PKR (Pakistani Rupee)',
    amounts_format: 'Use toLocaleString() for PKR formatting, e.g. PKR 284,500',
    ai_assistant: 'Zara — SmartBank AI assistant available via chat widget (bottom-right) or /chat page',
  },
  features_summary: 'SmartBank includes: Dashboard with case analytics, Card management (3 cards with freeze/unfreeze), 20 dummy Pakistan-relevant transactions with search/filter/expand, Loan application with BPMN tracker, Budget planner with 5 categories, Financial goals tracker, ARIE cognitive engine for scam detection/Urdu repair/circuit breaker, Document verification, Intent classification with auto-resolution.',
  emergency_scenarios: [
    {
      scenario: 'Phone snatched / Mobile snatch',
      description: 'When phone is snatched, immediately block debit card via Cards page. Salary is NOT affected — salary goes to account number, not card number. Call 0800-12345. Order replacement card (3-5 days). Internet banking and RAAST still work without card.',
      urdu_description: 'Mobile snatch ho jaye to foran card block karein. Salary account mein ati hai, card mein nahi — fikar na karein. 0800-12345 par call karein. Replacement card order karein.',
      actions: ['Cards page → Block Card', 'Call 0800-12345', 'Order replacement card', 'Change passwords', 'Block SIM with mobile company'],
    },
  ],
}

const KEYWORD_MAP = {
  card: 'pages[1]',
  cards: 'pages[1]',
  'visa': 'pages[1]',
  'mastercard': 'pages[1]',
  'platinum': 'pages[1]',
  'gold': 'pages[1]',
  'classic': 'pages[1]',
  'freeze': 'pages[1]',
  'freez': 'pages[1]',
  'unfreeze': 'pages[1]',
  'block': 'pages[1]',
  'snatch': 'pages[1]',
  'gum': 'pages[1]',
  'kho': 'pages[1]',
  'chori': 'pages[1]',
  'pin': 'pages[1]',
  'cvv': 'pages[1]',

  transaction: 'pages[2]',
  transactions: 'pages[2]',
  salary: 'pages[2]',
  careem: 'pages[2]',
  khaadi: 'pages[2]',
  nandos: 'pages[2]',
  daraz: 'pages[2]',
  upwork: 'pages[2]',
  netflix: 'pages[2]',
  ptcl: 'pages[2]',
  dispute: 'pages[2]',
  receipt: 'pages[2]',

  loan: 'pages[3]',
  loans: 'pages[3]',
  bpmn: 'pages[3]',
  emi: 'pages[3]',
  application: 'pages[3]',
  home: 'pages[3]',
  car: 'pages[3]',
  personal: 'pages[3]',

  budget: 'pages[4]',
  budgets: 'pages[4]',
  planner: 'pages[4]',
  food: 'pages[4]',
  transport: 'pages[4]',
  utilities: 'pages[4]',
  entertainment: 'pages[4]',
  shopping: 'pages[4]',

  goal: 'pages[5]',
  goals: 'pages[5]',
  savings: 'pages[5]',
  emergency: 'pages[5]',
  laptop: 'pages[5]',
  hajj: 'pages[5]',

  arie: 'pages[6]',
  scam: 'pages[6]',
  interceptor: 'pages[6]',
  lockdown: 'pages[6]',
  urdu: 'pages[6]',
  repair: 'pages[6]',
  circuit: 'pages[6]',
  breaker: 'pages[6]',
  sec01: 'pages[6]',

  dashboard: 'pages[0]',
  classify: 'pages[7]',
  document: 'pages[9]',
  workflow: 'pages[10]',
  guide: 'pages[11]',
  feature: 'pages[11]',

  zara: 'general_info',
  assistant: 'general_info',
  help: 'general_info',
  dark: 'general_info',
  theme: 'general_info',
  pkr: 'general_info',
  rupee: 'general_info',
  navigation: 'navigation',
  nav: 'navigation',
  sidebar: 'navigation',
  menu: 'navigation',
}

function getRelevantContext(query) {
  const q = query.toLowerCase()
  const matched = new Set()

  for (const [keyword, path] of Object.entries(KEYWORD_MAP)) {
    if (q.includes(keyword)) {
      matched.add(path)
    }
  }

  const results = []
  for (const path of matched) {
    if (path.startsWith('pages[')) {
      const idx = parseInt(path.match(/\d+/)[0])
      const page = KNOWLEDGE.pages[idx]
      if (page && !results.some(r => r.title === page.title)) {
        results.push({
          type: 'page',
          route: page.route,
          title: page.title,
          description: page.description,
          features: page.features,
          data: page.data || null,
          sample_transactions: page.sample_transactions || null,
          existing_loans: page.existing_loans || null,
          capabilities: page.capabilities || null,
        })
      }
    } else if (path === 'general_info') {
      results.push({ type: 'general_info', ...KNOWLEDGE.general_info })
    } else if (path === 'navigation') {
      results.push({ type: 'navigation', ...KNOWLEDGE.navigation })
    }
  }

  if (results.length === 0) {
    results.push({ type: 'summary', text: KNOWLEDGE.features_summary })
  }

  return results
}

function buildRagContext(query) {
  const contexts = getRelevantContext(query)
  if (contexts.length === 0) return ''

  let rag = '\n[APP CONTEXT — SmartBank Features & Data]\n'
  for (const ctx of contexts) {
    if (ctx.type === 'page') {
      rag += `\n--- ${ctx.title} (${ctx.route}) ---\n${ctx.description}\n`
      if (ctx.features) {
        rag += `Features: ${ctx.features.join(', ')}\n`
      }
      if (ctx.data) {
        rag += 'Cards data:\n'
        for (const c of ctx.data) {
          rag += `  - ${c.card}: PKR ${c.balance.toLocaleString()} balance, PKR ${c.limit.toLocaleString()} limit, ${c.status}\n`
        }
      }
      if (ctx.sample_transactions) {
        rag += `Sample transactions: ${ctx.sample_transactions.join(', ')}\n`
      }
      if (ctx.existing_loans) {
        rag += 'Existing loans:\n'
        for (const l of ctx.existing_loans) {
          rag += `  - ${l.type}: PKR ${l.amount.toLocaleString()} over ${l.months} months (PKR ${l.monthly.toLocaleString()}/mo) — ${l.status}\n`
        }
      }
      if (ctx.capabilities) {
        rag += `Capabilities: ${ctx.capabilities.join(', ')}\n`
      }
    } else if (ctx.type === 'general_info') {
      rag += `\n--- App Info ---\nApp: ${ctx.app_name}, User: ${ctx.user}, Theme: ${ctx.theme}, Currency: ${ctx.currency}\n`
    } else if (ctx.type === 'navigation') {
      rag += `\n--- Navigation ---\nSidebar: ${ctx.sidebar.join(' | ')}\n`
    } else if (ctx.type === 'summary') {
      rag += `\n--- SmartBank Overview ---\n${ctx.text}\n`
    }
  }
  rag += '\n[/APP CONTEXT]\n'
  return rag
}

module.exports = { KNOWLEDGE, buildRagContext, getRelevantContext }
