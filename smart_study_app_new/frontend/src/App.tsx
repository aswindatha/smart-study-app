import { Routes, Route, Navigate } from 'react-router-dom'
import { Suspense } from 'react'
import { useAuthStore } from '@/store/auth'
import Login from '@/pages/auth/Login'
import Register from '@/pages/auth/Register'
import { DashboardPage, MaterialsPage, MaterialDetailPage, StudySessionsPage, AnalyticsPage, ProfilePage } from '@/routes/lazyRoutes'
import AppLayout from '@/components/layout/AppLayout'
import Skeleton from '@/components/ui/skeleton'

function Protected({ children }: { children: JSX.Element }) {
  const token = useAuthStore((s) => s.token)
  if (!token) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <Suspense fallback={<div className="p-6"><Skeleton className="h-64 w-full" /></div>}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/"
          element={
            <Protected>
              <AppLayout />
            </Protected>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="materials" element={<MaterialsPage />} />
          <Route path="materials/:id" element={<MaterialDetailPage />} />
          <Route path="study" element={<StudySessionsPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Suspense>
  )
}
