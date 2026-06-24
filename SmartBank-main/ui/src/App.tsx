import { useAuth } from '@clerk/clerk-react'
import { lazy, Suspense, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute, { AdminRoute } from './components/ProtectedRoute'
import Loading from './components/Loading'
import { setTokenGetter } from './services/api'

const Login = lazy(() => import('./features/auth/Login'))
const SignUpPage = lazy(() => import('./features/auth/SignUpPage'))
const Dashboard = lazy(() => import('./features/dashboard/Dashboard'))
const Classify = lazy(() => import('./features/classify/Classify'))
const ChatPage = lazy(() => import('./features/chat/ChatPage'))
const Document = lazy(() => import('./features/document/Document'))
const Workflows = lazy(() => import('./features/workflows/Workflows'))
const GoalsPage = lazy(() => import('./features/goals/GoalsPage'))
const BudgetPage = lazy(() => import('./features/budget/BudgetPage'))
const FeatureGuide = lazy(() => import('./features/guide/FeatureGuide'))
const AdminLayout = lazy(() => import('./features/admin/AdminLayout'))

export default function App() {
  const { getToken } = useAuth()

  useEffect(() => {
    setTokenGetter(() => getToken())
  }, [getToken])

  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/sign-up" element={<SignUpPage />} />
        <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/classify" element={<Classify />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/document" element={<Document />} />
          <Route path="/workflows" element={<Workflows />} />
          <Route path="/goals" element={<GoalsPage />} />
          <Route path="/budget" element={<BudgetPage />} />
          <Route path="/guide" element={<FeatureGuide />} />
          <Route path="/admin/*" element={<AdminRoute><AdminLayout /></AdminRoute>} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Suspense>
  )
}
