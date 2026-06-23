import { useAuth, useUser } from '@clerk/clerk-react'

export { useAuth, useUser }

export function useClerkToken() {
  const { getToken } = useAuth()
  return getToken
}
