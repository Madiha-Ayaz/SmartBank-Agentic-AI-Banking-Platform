import { create } from 'zustand'
import { useUser } from '@clerk/clerk-react'

interface UserProfile {
  userId: string
  name: string
  email: string
  cnic: string
  phone: string
}

interface AuthState {
  profile: UserProfile | null
  setProfile: (p: UserProfile) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  profile: null,
  setProfile: (p) => set({ profile: p }),
}))

export function useCurrentUser(): UserProfile {
  const { user } = useUser()
  const profile = useAuthStore((s) => s.profile)
  if (profile) return profile
  const fallback: UserProfile = {
    userId: user?.id || 'user_default',
    name: user?.fullName || user?.primaryEmailAddress?.emailAddress?.split('@')[0] || 'User',
    email: user?.primaryEmailAddress?.emailAddress || 'user@smartbank.ai',
    cnic: '35202-XXXXXXX-X',
    phone: '0300-XXXXXXX',
  }
  return fallback
}
