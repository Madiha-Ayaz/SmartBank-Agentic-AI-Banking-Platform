import { SignIn, useAuth } from '@clerk/clerk-react'
import { Navigate } from 'react-router-dom'

export default function Login() {
  const { isLoaded, isSignedIn } = useAuth()

  if (!isLoaded) return null
  if (isSignedIn) return <Navigate to="/dashboard" replace />

  return (
    <div className="login-page">
      <div className="login-card">
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 16 }}>
          <div style={{
            width: 56, height: 56,
            background: 'linear-gradient(135deg, var(--primary), #8b5cf6)',
            borderRadius: 14,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.5rem', fontWeight: 800, color: '#fff',
            boxShadow: '0 0 30px var(--primary-glow)',
          }}>S</div>
        </div>
        <h1 style={{ textAlign: 'center' }}>SmartBank</h1>
        <p className="subtitle" style={{ textAlign: 'center' }}>AI-Powered Banking Operations Platform</p>
        <SignIn />
      </div>
    </div>
  )
}
