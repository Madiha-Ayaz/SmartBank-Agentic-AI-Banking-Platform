import { create } from 'zustand'
import api from '../services/api'
import type { LoanMessage, LoanChatResponse, LoanApplicationData, LoanAgreementData } from '../types'

interface LoanState {
  messages: LoanMessage[]
  applicationId: string | null
  application: LoanApplicationData | null
  agreement: LoanAgreementData | null
  loading: boolean
  currentStep: string
  dataCollected: Record<string, unknown>
  completed: boolean

  sendMessage: (text: string) => Promise<void>
  acceptTerms: () => Promise<void>
  rejectTerms: () => Promise<void>
  fetchApplication: (id: string) => Promise<void>
  fetchAgreement: (id: string) => Promise<void>
  reset: () => void
  addSystemMessage: (text: string) => void
}

export const useLoanStore = create<LoanState>((set, get) => ({
  messages: [],
  applicationId: null,
  application: null,
  agreement: null,
  loading: false,
  currentStep: 'greeting',
  dataCollected: {},
  completed: false,

  sendMessage: async (text: string) => {
    if (!text.trim()) return

    const userMsg: LoanMessage = {
      role: 'user',
      text: text.trim(),
      timestamp: Date.now(),
    }
    set((s) => ({ messages: [...s.messages, userMsg], loading: true }))

    try {
      const { applicationId } = get()
      const body: Record<string, unknown> = { message: text, language: 'en' }
      if (applicationId) {
        body.application_id = applicationId
      }

      const res = await api.post<LoanChatResponse>('/api/loan/chat', body)
      const data = res.data

      const assistantMsg: LoanMessage = {
        role: 'assistant',
        text: data.text,
        timestamp: Date.now(),
        step: data.current_step,
        data: data.data_collected,
      }

      set({
        messages: [...get().messages, assistantMsg],
        applicationId: data.application_id,
        currentStep: data.current_step,
        dataCollected: data.data_collected,
        loading: false,
        completed: data.completed,
      })

      if (data.current_step === 'risk_assessment' || data.current_step === 'terms_acceptance' || data.current_step === 'rejected') {
        get().fetchApplication(data.application_id)
      }
    } catch {
      const errorMsg: LoanMessage = {
        role: 'assistant',
        text: 'Sorry, I encountered an error. Please try again.',
        timestamp: Date.now(),
      }
      set((s) => ({ messages: [...s.messages, errorMsg], loading: false }))
    }
  },

  acceptTerms: async () => {
    const { applicationId } = get()
    if (!applicationId) return

    set({ loading: true })
    try {
      const res = await api.post('/api/loan/accept-terms', {
        application_id: applicationId,
        accepted: true,
      })
      if (res.data.success && res.data.agreement) {
        set({
          agreement: res.data.agreement,
          currentStep: 'agreement_generated',
          completed: true,
          loading: false,
        })
        const sysMsg: LoanMessage = {
          role: 'system',
          text: 'Terms accepted. Loan agreement generated.',
          timestamp: Date.now(),
        }
        set((s) => ({ messages: [...s.messages, sysMsg] }))
      }
    } catch {
      set({ loading: false })
    }
  },

  rejectTerms: async () => {
    const { applicationId } = get()
    if (!applicationId) return

    set({ loading: true })
    try {
      await api.post('/api/loan/accept-terms', {
        application_id: applicationId,
        accepted: false,
      })
      set({ currentStep: 'rejected', loading: false })
    } catch {
      set({ loading: false })
    }
  },

  fetchApplication: async (id: string) => {
    try {
      const res = await api.get<LoanApplicationData>(`/api/loan/application/${id}`)
      set({ application: res.data })
    } catch {
      // silently fail
    }
  },

  fetchAgreement: async (id: string) => {
    try {
      const res = await api.get<LoanAgreementData>(`/api/loan/agreement/${id}`)
      set({ agreement: res.data })
    } catch {
      // silently fail
    }
  },

  reset: () => {
    set({
      messages: [],
      applicationId: null,
      application: null,
      agreement: null,
      loading: false,
      currentStep: 'greeting',
      dataCollected: {},
      completed: false,
    })
  },

  addSystemMessage: (text: string) => {
    const msg: LoanMessage = {
      role: 'system',
      text,
      timestamp: Date.now(),
    }
    set((s) => ({ messages: [...s.messages, msg] }))
  },
}))
