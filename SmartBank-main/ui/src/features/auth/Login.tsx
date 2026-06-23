import { SignIn } from '@clerk/clerk-react'

export default function Login() {
  return (
    <div className="login-page">
      <div className="login-card">
        <h1 style={{ textAlign: 'center' }}>SmartBank</h1>
        <p className="subtitle" style={{ textAlign: 'center' }}>AI-Powered Banking Operations</p>
        <SignIn />
      </div>
    </div>
  )
}
