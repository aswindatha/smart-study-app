import { NavLink } from 'react-router-dom'
import { LayoutDashboard, BookText, LineChart, User, Play, FolderOpen } from 'lucide-react'

const nav = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/materials', label: 'Materials', icon: FolderOpen },
  { to: '/study', label: 'Study Sessions', icon: Play },
  { to: '/analytics', label: 'Analytics', icon: LineChart },
  { to: '/profile', label: 'Profile', icon: User },
]

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-full w-[var(--sidebar-width)] border-r border-slate-200 bg-white/90 backdrop-blur">
      <div className="p-4 font-semibold text-xl">Smart Study</div>
      <nav className="mt-2 flex flex-col gap-1 p-2">
        {nav.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-md px-3 py-2 text-sm hover:bg-slate-100 ${
                  isActive ? 'bg-slate-100 font-medium' : 'text-slate-700'
                }`
              }
            >
              <Icon size={18} /> {item.label}
            </NavLink>
          )
        })}
      </nav>
    </aside>
  )
}
