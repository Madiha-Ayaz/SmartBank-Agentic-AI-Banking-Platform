export interface StatsResponse {
  total_cases: number
  resolved: number
  pending: number
  human_review: number
  critical: number
  avg_resolution_time: string
  automation_rate: number
  sla_compliance: number
}

export interface CaseItem {
  id: string
  customer_name: string
  type: string
  status: string
  priority: string
  channel: string
  time: string
  date: string
}

export interface CaseListResponse {
  cases: CaseItem[]
  total: number
  page: number
  page_size: number
}

export interface AnalyticsResponse {
  by_status: Record<string, number>
  by_priority: Record<string, number>
  by_channel: Record<string, number>
}

export interface ClassifyResponse {
  request_id: string
  timestamp: string
  channel: string
  detected_language: string
  intent: { code: string; label: string; confidence: number }
  entities: Record<string, string | null>
  escalate_to_human: boolean
}

export interface ChatResponse {
  text: string
  language: string
  module: string | null
  escalation: boolean
  escalation_reason: string | null
}

export interface DocumentVerifyResponse {
  filename: string | null
  size: number
  document_type: string
  risk_score: number
  risk_level: string
  decision: string
  extracted_fields: Record<string, unknown>
  fraud_indicators: string[]
  processing_id: string
}

export interface HealthResponse {
  status: string
  service: string
  version: string
  database: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UserResponse {
  id: string
  username: string
  role: string
}

export interface WorkflowItem {
  name: string
  file: string
  size: number
  process_id: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  text: string
  timestamp: number
}

export interface GoalItem {
  id: number
  title: string
  target_amount: number
  current_amount: number
  deadline: string
  category: string
  status: string
  created_at: string
}

export interface BudgetItem {
  id: number
  category: string
  planned_amount: number
  spent_amount: number
  month: string
  year: string
}

export interface BudgetTransaction {
  id: number
  budget_id: number
  description: string
  amount: number
  date: string
}
