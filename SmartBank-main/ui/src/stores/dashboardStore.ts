import { create } from 'zustand'
import api from '../services/api'
import type { StatsResponse, CaseItem, AnalyticsResponse } from '../types'

const FALLBACK_STATS: StatsResponse = { total_cases: 142, resolved: 98, pending: 31, human_review: 13, automation_rate: 78, sla_compliance: 92, avg_resolution_time: '2.4 hrs', critical: 8 }
const FALLBACK_CASES: CaseItem[] = [
  { id: 'REQ-001', customer_name: 'Ahmed Khan', type: 'Debit Card Block', status: 'Resolved', priority: 'Critical', channel: 'Chat', time: '<1m', date: '2025-06-27' },
  { id: 'REQ-002', customer_name: 'Sara Malik', type: 'PIN Reset', status: 'Resolved', priority: 'High', channel: 'Web', time: '<1m', date: '2025-06-27' },
  { id: 'REQ-003', customer_name: 'Usman Ali', type: 'Balance Inquiry', status: 'Resolved', priority: 'Low', channel: 'Chat', time: '<1m', date: '2025-06-26' },
  { id: 'REQ-004', customer_name: 'Fatima Ahmed', type: 'Fraud Report', status: 'Human Review', priority: 'Critical', channel: 'Phone', time: '5m', date: '2025-06-26' },
  { id: 'REQ-005', customer_name: 'Bilal Hassan', type: 'Loan Inquiry', status: 'Pending', priority: 'Medium', channel: 'Web', time: '2m', date: '2025-06-25' },
]
const FALLBACK_ANALYTICS: AnalyticsResponse = { by_status: { Resolved: 98, Pending: 31, 'Human Review': 13 }, by_priority: { Low: 20, Medium: 45, High: 52, Critical: 25 }, by_channel: { Web: 60, Chat: 50, Phone: 20, SMS: 12 } }

interface DashboardState {
  stats: StatsResponse | null
  cases: CaseItem[]
  analytics: AnalyticsResponse | null
  loading: boolean
  search: string
  priorityFilter: string
  fetchStats: () => Promise<void>
  fetchCases: () => Promise<void>
  fetchAnalytics: () => Promise<void>
  setSearch: (search: string) => void
  setPriorityFilter: (filter: string) => void
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  stats: null,
  cases: [],
  analytics: null,
  loading: false,
  search: '',
  priorityFilter: '',

  fetchStats: async () => {
    try {
      const res = await api.get('/api/dashboard/stats')
      set({ stats: res.data })
    } catch {
      set({ stats: FALLBACK_STATS })
    }
  },

  fetchCases: async () => {
    const { search, priorityFilter } = get()
    try {
      const params: Record<string, string> = {}
      if (search) params.search = search
      if (priorityFilter) params.priority = priorityFilter
      const res = await api.get('/api/dashboard/cases', { params })
      set({ cases: res.data.cases ?? [] })
    } catch {
      set({ cases: FALLBACK_CASES })
    }
  },

  fetchAnalytics: async () => {
    try {
      const res = await api.get('/api/dashboard/analytics')
      set({ analytics: res.data })
    } catch {
      set({ analytics: FALLBACK_ANALYTICS })
    }
  },

  setSearch: (search: string) => set({ search }),
  setPriorityFilter: (filter: string) => set({ priorityFilter: filter }),
}))
