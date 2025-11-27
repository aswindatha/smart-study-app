import { lazy } from 'react'

export const DashboardPage = lazy(() => import('@/pages/Dashboard'))
export const MaterialsPage = lazy(() => import('@/pages/Materials'))
export const MaterialDetailPage = lazy(() => import('@/pages/MaterialDetail'))
export const StudySessionsPage = lazy(() => import('@/pages/StudySessions'))
export const AnalyticsPage = lazy(() => import('@/pages/Analytics'))
export const ProfilePage = lazy(() => import('@/pages/Profile'))
