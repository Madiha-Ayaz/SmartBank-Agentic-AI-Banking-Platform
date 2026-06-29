import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute, { AdminRoute } from './components/ProtectedRoute'
import Loading from './components/Loading'

const Login = lazy(() => import('./features/auth/Login'))
const SignUpPage = lazy(() => import('./features/auth/SignUpPage'))
const Dashboard = lazy(() => import('./features/dashboard/Dashboard'))
const Classify = lazy(() => import('./features/classify/Classify'))
const ChatPage = lazy(() => import('./features/chat/ChatPage'))
const Document = lazy(() => import('./features/document/Document'))
const Workflows = lazy(() => import('./features/workflows/Workflows'))
const ARIEPage = lazy(() => import('./features/arie/ARIE'))
const CardsPage = lazy(() => import('./features/cards/CardsPage'))
const TransactionsPage = lazy(() => import('./features/transactions/TransactionsPage'))
const FinanceTransferPage = lazy(() => import('./features/finance/FinanceTransferPage'))
const AITransactionWorkflow = lazy(() => import('./features/finance/AITransactionWorkflow'))
const LoanPage = lazy(() => import('./features/loans/LoanPage'))
const GoalsPage = lazy(() => import('./features/goals/GoalsPage'))
const BudgetPage = lazy(() => import('./features/budget/BudgetPage'))
const Overview = lazy(() => import('./features/overview/Overview'))
const SecurityDashboard = lazy(() => import('./features/security/SecurityDashboard'))
const FeatureGuide = lazy(() => import('./features/guide/FeatureGuide'))
const AdminLayout = lazy(() => import('./features/admin/AdminLayout'))
const BankingPage = lazy(() => import('./features/banking/BankingPage'))

export default function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/sign-up" element={<SignUpPage />} />
        <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/overview" element={<Overview />} />
          <Route path="/classify" element={<Classify />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/arie" element={<ARIEPage />} />
          <Route path="/document" element={<Document />} />
          <Route path="/workflows" element={<Workflows />} />
          <Route path="/goals" element={<GoalsPage />} />
          <Route path="/budget" element={<BudgetPage />} />
          <Route path="/cards" element={<CardsPage />} />
          <Route path="/transactions" element={<TransactionsPage />} />
          <Route path="/finance/transfer" element={<FinanceTransferPage />} />
          <Route path="/ai-transaction" element={<AITransactionWorkflow />} />
          <Route path="/loans" element={<LoanPage />} />
          <Route path="/guide" element={<FeatureGuide />} />
          <Route path="/security" element={<SecurityDashboard />} />
          <Route path="/banking" element={<BankingPage />} />
          <Route path="/admin/*" element={<AdminRoute><AdminLayout /></AdminRoute>} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Suspense>
  )
}
