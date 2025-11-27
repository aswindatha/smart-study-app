import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import Skeleton from '@/components/ui/skeleton'
import { useAuthStore } from '@/store/auth'
import { getUserAnalytics, listMaterials } from '@/lib/api'
import type { StudyMaterial } from '@/types'
import { Link } from 'react-router-dom'
import { Upload, Play, LineChart } from 'lucide-react'
import { motion } from 'framer-motion'

export default function Dashboard() {
  const user = useAuthStore((s) => s.user)
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<any>(null)
  const [recent, setRecent] = useState<StudyMaterial[]>([])

  useEffect(() => {
    async function load() {
      if (!user) return
      setLoading(true)
      const [analytics, materials] = await Promise.all([
        getUserAnalytics(user.id),
        listMaterials(),
      ])
      setStats(analytics)
      setRecent(materials.slice(0, 5))
      setLoading(false)
    }
    load()
  }, [user])

  if (loading) return <Skeleton className="h-64 w-full" />

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader><CardTitle>Total Study Time</CardTitle></CardHeader>
          <CardContent className="text-2xl font-semibold">{stats?.overall?.total_study_time || 0} mins</CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Materials</CardTitle></CardHeader>
          <CardContent className="text-2xl font-semibold">{stats?.overall?.materials_studied || 0}</CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Sessions</CardTitle></CardHeader>
          <CardContent className="text-2xl font-semibold">{stats?.overall?.total_sessions || 0}</CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Current Streak</CardTitle></CardHeader>
          <CardContent className="text-2xl font-semibold">{stats?.overall?.current_streak || 0} days</CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Quick Actions</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Link to="/materials" className="inline-flex items-center gap-2 rounded-md border px-3 py-2 hover:bg-slate-50">
              <Upload size={16} /> Upload Material
            </Link>
            <Link to="/study" className="inline-flex items-center gap-2 rounded-md border px-3 py-2 hover:bg-slate-50">
              <Play size={16} /> Start Session
            </Link>
            <Link to="/analytics" className="inline-flex items-center gap-2 rounded-md border px-3 py-2 hover:bg-slate-50">
              <LineChart size={16} /> View Analytics
            </Link>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Recent Materials</CardTitle></CardHeader>
        <CardContent>
          <ul className="divide-y">
            {recent.map((m) => (
              <li key={m.id} className="flex items-center justify-between py-3">
                <div>
                  <div className="font-medium">{m.title}</div>
                  <div className="text-sm text-slate-500">{m.subject} {m.tags && `• ${m.tags}`}</div>
                </div>
                <a href={`/materials/${m.id}`} className="text-blue-600 hover:underline">Open</a>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </motion.div>
  )
}
