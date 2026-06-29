import { create } from 'zustand'
import { getCurrentUser } from '../firebase/authService'

interface UserProfile {
  userId: string
  name: string
  email: string
  cnic: string
  phone: string
}

interface AuthState {
  profile: UserProfile | null
  setProfile: (p: UserProfile | null) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  profile: null,
  setProfile: (p) => set({ profile: p }),
}))

export function useCurrentUser(): UserProfile {
  const user = getCurrentUser()
  const profile = useAuthStore((s) => s.profile)
  if (profile) return profile
  const fallback: UserProfile = {
    userId: user?.uid || 'user_default',
    name: user?.displayName || user?.email?.split('@')[0] || 'User',
    email: user?.email || 'user@smartbank.ai',
    cnic: '35202-XXXXXXX-X',
    phone: '0300-XXXXXXX',
  }
  return fallback
}
