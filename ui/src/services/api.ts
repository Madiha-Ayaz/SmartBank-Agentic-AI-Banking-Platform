import axios from 'axios'
import { getFirebaseToken } from '../firebase/authService'

const api = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use(async (config) => {
  const token = await getFirebaseToken()
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export function setTokenGetter(_fn: () => Promise<string | null>) {}

export default api
