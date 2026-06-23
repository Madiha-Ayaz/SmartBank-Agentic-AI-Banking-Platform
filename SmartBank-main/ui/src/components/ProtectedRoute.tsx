import { useAuth } from '@clerk/clerk-react'
import { Navigate } from 'react-router-dom'
import Loading from './Loading'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoaded, isSignedIn } = useAuth()

  if (!isLoaded) return <Loading />
  if (!isSignedIn) return <Navigate to="/" replace />

  return <>{children}</>
}
