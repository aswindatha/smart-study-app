import axios from 'axios'
import { useAuthStore } from '@/store/auth'

const DEV_URL = import.meta.env.VITE_API_BASE_URL || ''
const PROD_URL = import.meta.env.VITE_API_BASE_URL_PROD || DEV_URL
const baseURL = import.meta.env.PROD ? PROD_URL : DEV_URL

export const api = axios.create({
  baseURL,
})

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token || localStorage.getItem('token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth
export async function login(username: string, password: string) {
  const form = new URLSearchParams()
  form.append('username', username)
  form.append('password', password)
  const { data } = await api.post('/api/token', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data as { access_token: string; token_type: string }
}

export async function register(payload: {
  email: string
  full_name?: string
  password: string
  role?: 'student' | 'teacher' | 'admin'
}) {
  const { data } = await api.post('/api/register', payload)
  return data
}

// Users
export async function fetchMe() {
  const { data } = await api.get('/api/users/me')
  return data
}

// Materials
export async function listMaterials(params?: { subject?: string; tag?: string }) {
  const { data } = await api.get('/api/materials/', { params })
  return data
}

export async function getMaterial(id: number) {
  const { data } = await api.get(`/api/materials/${id}`)
  return data
}

export async function uploadMaterial(payload: {
  title: string
  description?: string
  subject?: string
  tags?: string
  file: File
}) {
  const form = new FormData()
  form.append('title', payload.title)
  if (payload.description) form.append('description', payload.description)
  if (payload.subject) form.append('subject', payload.subject)
  if (payload.tags) form.append('tags', payload.tags)
  form.append('file', payload.file)
  const { data } = await api.post('/api/materials/upload/', form)
  return data
}

export async function deleteMaterial(id: number) {
  await api.delete(`/api/materials/${id}`)
}

// AI
export async function summarize(text: string, max_length = 300) {
  const { data } = await api.post('/api/ai/summarize', { text, max_length })
  return data as { summary: string }
}

export async function generateFlashcards(text: string, num_cards = 5) {
  const { data } = await api.post('/api/ai/generate-flashcards', { text, num_cards })
  return data as { flashcards: { question: string; answer: string }[] }
}

export async function generateMCQ(text: string, num_questions = 5) {
  const { data } = await api.post('/api/ai/generate-mcq', { text, num_questions })
  return data as { questions: { question: string; options: { text: string; is_correct: boolean }[] }[] }
}

export async function explain(concept: string, context?: string) {
  const { data } = await api.post('/api/ai/explain', { concept, context })
  return data as { explanation: string }
}

export async function processMaterial(material_id: number) {
  const { data } = await api.post(`/api/ai/process-material/${material_id}`)
  return data as {
    material_id: number
    summary: string
    text_extract: string
    suggested_flashcards: any
    suggested_questions: any
  }
}

// Study Sessions
export async function startSession(material_id: number) {
  const { data } = await api.post('/api/study-sessions/start', null, { params: { material_id } })
  return data
}

export async function endSession(session_id: number) {
  const { data } = await api.post(`/api/study-sessions/${session_id}/end`)
  return data
}

export async function listSessions(params?: { material_id?: number; user_id?: number }) {
  const { data } = await api.get('/api/study-sessions/', { params })
  return data
}

// Analytics
export async function getUserAnalytics(user_id: number, days = 30, opts?: { from?: string; to?: string }) {
  const params: any = { days }
  if (opts?.from) params.from = opts.from
  if (opts?.to) params.to = opts.to
  const { data } = await api.get(`/api/analytics/user/${user_id}`, { params })
  return data
}

export async function getMaterialAnalytics(material_id: number) {
  const { data } = await api.get(`/api/analytics/materials/${material_id}`)
  return data
}
