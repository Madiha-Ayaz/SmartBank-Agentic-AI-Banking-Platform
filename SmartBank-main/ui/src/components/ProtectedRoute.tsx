import { useAuth, useUser } from '@clerk/clerk-react'
import { Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import api from '../services/api'
import Loading from './Loading'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoaded, isSignedIn } = useAuth()

  if (!isLoaded) return <Loading />
  if (!isSignedIn) return <Navigate to="/" replace />

  return <>{children}</>
}

// AdminRoute — only allows users with admin@smartbank.ai email
export function AdminRoute({ children }: { children: React.ReactNode }) {
  const { isLoaded, isSignedIn, getToken } = useAuth()
  const { user } = useUser()
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null)

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return
    
    // Check admin status from backend
    api.get('/api/auth/check-admin')
      .then(res => setIsAdmin(res.data.isAdmin === true))
      .catch(() => setIsAdmin(false))
  }, [isLoaded, isSignedIn])

  if (!isLoaded) return <Loading />
  if (!isSignedIn) return <Navigate to="/" replace />
  
  if (isAdmin === null) return <Loading />
  
  if (!isAdmin) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div className="card" style={{ textAlign: 'center', padding: 40, maxWidth: 400 }}>
          <div style={{ fontSize: '3rem', marginBottom: 16 }}>🔒</div>
          <h2 style={{ marginBottom: 12 }}>Admin Access Only</h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: 20 }}>
            Sorry, only the admin can access this page.<br />
            Your email is not authorized as admin.
          </p>
          <a href="/dashboard" className="btn btn-primary" style={{ textDecoration: 'none' }}>
            Go to Dashboard
          </a>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
