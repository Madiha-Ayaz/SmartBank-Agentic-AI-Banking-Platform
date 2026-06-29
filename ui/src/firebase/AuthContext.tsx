import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User } from 'firebase/auth'
import { onAuthChange, getFirebaseToken } from './authService'
import { setTokenGetter } from '../services/api'
import { useSessionContext } from '../stores/sessionContextStore'
import { useAuthStore } from '../stores/authStore'

interface AuthContextType {
  user: User | null
  isLoaded: boolean
  isSignedIn: boolean
  getToken: () => Promise<string | null>
  deleteAccount: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoaded: false,
  isSignedIn: false,
  getToken: async () => null,
  deleteAccount: async () => {},
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    let prevUidForCleanup = localStorage.getItem('sb_last_uid')

    const unsub = onAuthChange(async (firebaseUser) => {
      const newUid = firebaseUser?.uid

      // Clear stale session data when user changes or logs out
      if (newUid !== prevUidForCleanup) {
        useSessionContext.getState().clearSession()
        useAuthStore.getState().setProfile(null)
      }

      if (firebaseUser) {
        localStorage.setItem('sb_last_uid', firebaseUser.uid)
        prevUidForCleanup = firebaseUser.uid
      } else if (prevUidForCleanup && !firebaseUser) {
        // User was logged out unexpectedly (deleted from Firebase console)
        try {
          await fetch('/api/auth/delete-account-by-uid', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uid: prevUidForCleanup })
          })
        } catch {}
        localStorage.removeItem('sb_last_uid')
        prevUidForCleanup = null
      }

      setUser(firebaseUser)
      setIsLoaded(true)
    })
    return unsub
  }, [])

  useEffect(() => {
    setTokenGetter(() => getFirebaseToken())
  }, [user])

  const value: AuthContextType = {
    user,
    isLoaded,
    isSignedIn: !!user,
    getToken: getFirebaseToken,
    deleteAccount: async () => {
      const { deleteAccount } = await import('./authService')
      await deleteAccount()
    },
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuthCtx() {
  return useContext(AuthContext)
}
