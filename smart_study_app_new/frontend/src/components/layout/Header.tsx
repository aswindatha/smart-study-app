import { useAuthStore } from '@/store/auth'
import { Button } from '@/components/ui/button'
import { useTheme } from '@/components/theme/ThemeProvider'
import { useSessionStore } from '@/store/session'
import { Moon, Sun, Timer } from 'lucide-react'
import { useElapsed } from '@/hooks/useElapsed'
import { useNavigate } from 'react-router-dom'

export default function Header() {
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const { theme, toggle } = useTheme()
  const active = useSessionStore((s) => s.activeSession)
  const { label } = useElapsed(active?.start_time || null)
  const navigate = useNavigate()
  return (
    <header className="sticky top-0 z-10 flex h-14 items-center justify-between border-b border-slate-200 bg-white/80 px-4 backdrop-blur dark:bg-slate-900/80 dark:border-slate-800">
      <div className="font-medium text-slate-900 dark:text-slate-100">Welcome, {user?.full_name || user?.email}</div>
      <div className="flex items-center gap-2">
        {active && (
          <button onClick={() => navigate(`/materials/${active.material_id}`)} className="inline-flex items-center gap-1 rounded-full border border-blue-300 bg-blue-50 px-2 py-1 text-xs text-blue-700 shadow-sm transition hover:brightness-95 dark:bg-blue-900/30 dark:border-blue-800 dark:text-blue-300">
            <Timer size={14} /> {label}
          </button>
        )}
        <Button variant="outline" onClick={toggle} title="Toggle theme">
          {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
        </Button>
        <Button variant="outline" onClick={logout}>Logout</Button>
      </div>
    </header>
  )
}
