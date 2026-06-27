import { create } from 'zustand'

interface BlockedCard {
  cardId: number
  lastFour: string
  reason: string
  ref: string
  timestamp: number
}

interface LoanData {
  amount: string
  purpose: string
  duration: string
  income: string
}

interface SessionContextState {
  blockedCards: BlockedCard[]
  loanData: LoanData | null
  flaggedCount: number
  addBlockedCard: (card: BlockedCard) => void
  setLoanData: (data: LoanData) => void
  setFlaggedCount: (n: number) => void
  clearSession: () => void
  buildSummary: () => string
}

export const useSessionContext = create<SessionContextState>((set, get) => ({
  blockedCards: [],
  loanData: null,
  flaggedCount: 0,

  addBlockedCard: (card) => set((s) => ({ blockedCards: [...s.blockedCards, card] })),

  setLoanData: (data) => set({ loanData: data }),

  setFlaggedCount: (n) => set({ flaggedCount: n }),

  clearSession: () => set({ blockedCards: [], loanData: null, flaggedCount: 0 }),

  buildSummary: () => {
    const state = get()
    const parts: string[] = []
    if (state.blockedCards.length > 0) {
      const last = state.blockedCards[state.blockedCards.length - 1]
      parts.push(`CRITICAL: User's card ending ${last.lastFour} was JUST blocked. Reason: ${last.reason}. Reference: ${last.ref}. Your FIRST response MUST acknowledge this block. Do NOT ask about income, age, or any personal data. Offer only: replacement card OR any other help.`)
    }
    if (state.loanData) {
      parts.push(`Loan data collected: YES (amount: ${state.loanData.amount}, purpose: ${state.loanData.purpose}, duration: ${state.loanData.duration}, income: ${state.loanData.income})`)
    }
    return parts.length > 0 ? parts.join('; ') : 'No recent actions'
  }
}))
