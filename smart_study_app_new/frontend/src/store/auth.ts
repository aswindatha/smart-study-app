import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { fetchMe, login as apiLogin } from '@/lib/api'
import type { User } from '@/types'

interface AuthState {
  token: string | null
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  hydrateUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      loading: false,
      async login(email, password) {
        set({ loading: true })
        const data = await apiLogin(email, password)
        const token = data.access_token
        set({ token })
        localStorage.setItem('token', token)
        await get().hydrateUser()
        set({ loading: false })
      },
      logout() {
        localStorage.removeItem('token')
        set({ token: null, user: null })
      },
      async hydrateUser() {
        try {
          const me = await fetchMe()
          set({ user: me })
        } catch (e) {
          // token invalid
          set({ token: null, user: null })
          localStorage.removeItem('token')
        }
      },
    }),
    { name: 'auth-store', partialize: (s) => ({ token: s.token }) }
  )
)
