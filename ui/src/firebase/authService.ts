import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
  sendPasswordResetEmail,
  onAuthStateChanged,
  User,
  getIdToken,
  updateProfile,
} from 'firebase/auth'
import { auth } from './config'
import api from '../services/api'

const googleProvider = new GoogleAuthProvider()

function logActivity(action: string, user: User, extra?: Record<string, string>) {
  getIdToken(user).then(() => {
    api.post('/api/auth/activity', {
      action,
      email: user.email,
      uid: user.uid,
      name: user.displayName,
      ...extra,
      timestamp: new Date().toISOString(),
    }).catch(() => {})
  })
}

export function onAuthChange(callback: (user: User | null) => void) {
  return onAuthStateChanged(auth, callback)
}

export async function signUp(email: string, password: string, name: string) {
  const cred = await createUserWithEmailAndPassword(auth, email, password)
  await updateProfile(cred.user, { displayName: name })
  logActivity('signup', cred.user)
  return cred.user
}

export async function logIn(email: string, password: string) {
  const cred = await signInWithEmailAndPassword(auth, email, password)
  logActivity('login', cred.user)
  return cred.user
}

export async function signInWithGoogle() {
  const cred = await signInWithPopup(auth, googleProvider)
  const action = cred.user.metadata.creationTime === cred.user.metadata.lastSignInTime ? 'signup' : 'login'
  logActivity(action, cred.user)
  return cred.user
}

export async function logOut() {
  const user = auth.currentUser
  if (user) {
    try { logActivity('logout', user) } catch {}
  }
  localStorage.removeItem('sb_last_uid')
  await signOut(auth)
}

export async function deleteAccount() {
  const user = auth.currentUser
  if (!user) throw new Error('Not logged in')
  const token = await getIdToken(user)
  const resp = await fetch('/api/auth/delete-account', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
  })
  if (!resp.ok) {
    const err = await resp.json()
    throw new Error(err.error || 'Failed to delete account')
  }
  localStorage.removeItem('sb_last_uid')
  await signOut(auth)
  return resp.json()
}

export async function resetPassword(email: string) {
  await sendPasswordResetEmail(auth, email)
}

export async function getFirebaseToken(): Promise<string | null> {
  const user = auth.currentUser
  if (!user) return null
  return getIdToken(user)
}

export function getCurrentUser(): User | null {
  return auth.currentUser
}
