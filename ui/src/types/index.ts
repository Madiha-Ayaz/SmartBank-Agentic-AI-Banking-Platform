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
  remaining_amount: number
  reserved_amount: number
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

export interface LoanChatRequest {
  message: string
  application_id?: string
  language?: string
}

export interface LoanChatResponse {
  text: string
  application_id: string
  current_step: string
  data_collected: Record<string, unknown>
  completed: boolean
}

export interface LoanApplicationData {
  id: string
  status: string
  current_step: string
  full_name?: string
  cnic?: string
  phone?: string
  email?: string
  employment_type?: string
  loan_amount?: number
  loan_purpose?: string
  repayment_duration_months?: number
  risk_level?: string
  credit_score?: number
  interest_rate?: number
  monthly_payment?: number
  decision_reason?: string
  terms_accepted: boolean
  created_at: string
  updated_at: string
}

export interface LoanAgreementData {
  id: string
  loan_application_id: string
  agreement_text: string
  payment_schedule: PaymentScheduleItem[]
  created_at: string
}

export interface PaymentScheduleItem {
  installment: number
  due_date: string
  amount: number
  principal: number
  interest: number
  balance: number
  status: string
}

export interface LoanAcceptTermsResponse {
  success: boolean
  message: string
  agreement?: LoanAgreementData
}

export interface LoanMessage {
  role: 'user' | 'assistant' | 'system'
  text: string
  timestamp: number
  step?: string
  data?: Record<string, unknown>
}
