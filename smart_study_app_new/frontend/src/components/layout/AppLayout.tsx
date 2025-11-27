import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import FloatingTimer from '@/components/session/FloatingTimer'

export default function AppLayout() {
  return (
    <div className="min-h-screen">
      <Sidebar />
      <main className="ml-[var(--sidebar-width)]">
        <Header />
        <div className="p-6">
          <Outlet />
        </div>
      </main>
      <FloatingTimer />
    </div>
  )
}
