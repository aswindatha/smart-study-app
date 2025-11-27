import { create } from 'zustand'
import { startSession as apiStart, endSession as apiEnd } from '@/lib/api'
import type { StudySession } from '@/types'

interface SessionState {
  activeSession: StudySession | null
  starting: boolean
  ending: boolean
  startSession: (material_id: number) => Promise<void>
  endSession: () => Promise<void>
  setActive: (s: StudySession | null) => void
}

export const SESSION_STORAGE_KEY = 'smartstudy_session_active'

export const useSessionStore = create<SessionState>((set, get) => ({
  activeSession: (() => {
    try {
      const raw = localStorage.getItem(SESSION_STORAGE_KEY)
      return raw ? (JSON.parse(raw) as StudySession) : null
    } catch {
      return null
    }
  })(),
  starting: false,
  ending: false,
  async startSession(material_id: number) {
    if (get().activeSession) return
    set({ starting: true })
    const session = await apiStart(material_id)
    set({ activeSession: session, starting: false })
    try { localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session)) } catch {}
  },
  async endSession() {
    const s = get().activeSession
    if (!s) return
    set({ ending: true })
    await apiEnd(s.id)
    set({ activeSession: null, ending: false })
    try { localStorage.removeItem(SESSION_STORAGE_KEY) } catch {}
  },
  setActive(s) {
    set({ activeSession: s })
    try {
      if (s) localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(s))
      else localStorage.removeItem(SESSION_STORAGE_KEY)
    } catch {}
  },
}))
