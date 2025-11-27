import { useEffect, useMemo, useState, lazy, Suspense } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import Skeleton from '@/components/ui/skeleton'
import { getUserAnalytics, listSessions } from '@/lib/api'
import { useAuthStore } from '@/store/auth'
const BarChart = lazy(() => import('react-chartjs-2').then((m) => ({ default: m.Bar })))
const LineChart = lazy(() => import('react-chartjs-2').then((m) => ({ default: m.Line })))
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
  TimeSeriesScale,
} from 'chart.js'
import DateRangeSelector from '@/components/charts/DateRangeSelector'
import SubjectPieChart from '@/components/charts/SubjectPieChart'
import { motion } from 'framer-motion'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend)

function toWeekKey(dateStr: string) {
  const d = new Date(dateStr)
  const onejan = new Date(d.getFullYear(),0,1)
  const week = Math.ceil((((d.valueOf() - onejan.valueOf()) / 86400000) + onejan.getDay() + 1)/7)
  return `${d.getFullYear()}-W${week}`
}

export default function Analytics() {
  const user = useAuthStore((s) => s.user)
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)
  const [sessions, setSessions] = useState<any[]>([])
  const [range, setRange] = useState<{ preset: '7' | '30' | 'all' | 'custom'; from?: string; to?: string }>({ preset: '30' })

  useEffect(() => {
    async function load() {
      if (!user) return
      setLoading(true)
      const { from, to } = computeRange(range)
      const [res, sess] = await Promise.all([
        getUserAnalytics(user.id, range.preset === '7' ? 7 : 30, { from, to }),
        listSessions(),
      ])
      setData(res)
      setSessions(sess)
      setLoading(false)
    }
    load()
  }, [user, range])

  if (loading) return <Skeleton className="h-64 w-full" />

  const timeSeries = filterByRange(data?.time_series || [], range)
  const labels = timeSeries.map((d: any) => d.date)
  const minutes = timeSeries.map((d: any) => d.minutes)

  const studyTimeBar = {
    labels,
    datasets: [{ label: 'Study Minutes', data: minutes, backgroundColor: '#60a5fa' }],
  }

  // Materials used per week from sessions
  const weeklyMap: Record<string, Set<number>> = {}
  sessions.forEach((s: any) => {
    const key = toWeekKey(s.start_time)
    weeklyMap[key] = weeklyMap[key] || new Set<number>()
    weeklyMap[key].add(s.material_id)
  })
  const weeklyLabels = Object.keys(weeklyMap).sort()
  const weeklyCounts = weeklyLabels.map((k) => weeklyMap[k].size)
  const materialsPerWeekLine = {
    labels: weeklyLabels,
    datasets: [{ label: 'Materials per Week', data: weeklyCounts, borderColor: '#22c55e' }],
  }

  // Quiz scores (use overall.average_score if present)
  const avg = data?.overall?.average_score ?? 0
  const quizBar = {
    labels: ['Average Score'],
    datasets: [{ label: 'Score', data: [avg], backgroundColor: '#f59e0b' }],
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="text-lg font-semibold">Analytics</div>
        <DateRangeSelector value={range} onChange={setRange} />
      </div>

      {/* Top stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total Study Hours" value={Math.round(((data?.overall?.total_study_time||0)/60)*10)/10} suffix="" />
        <StatCard title="Total Materials" value={data?.overall?.materials_studied||0} />
        <StatCard title="Average Score" value={avg || 0} />
        <StatCard title="Current Streak" value={data?.overall?.current_streak||0} suffix=" days" />
      </div>

      {/* Study time per day (Bar) */}
      <Card>
        <CardHeader><CardTitle>Study Time per Day</CardTitle></CardHeader>
        <CardContent>
          <Suspense fallback={<Skeleton className="h-40 w-full" />}>
            <BarChart data={studyTimeBar} />
          </Suspense>
        </CardContent>
      </Card>

      {/* Materials per week (Line) */}
      <Card>
        <CardHeader><CardTitle>Materials Used per Week</CardTitle></CardHeader>
        <CardContent>
          <Suspense fallback={<Skeleton className="h-40 w-full" />}>
            <LineChart data={materialsPerWeekLine} />
          </Suspense>
        </CardContent>
      </Card>

      {/* Subject breakdown (Pie) */}
      <Card>
        <CardHeader><CardTitle>Study Time by Subject</CardTitle></CardHeader>
        <CardContent>
          <SubjectPieChart bySubject={data?.by_subject || []} />
        </CardContent>
      </Card>

      {/* Quiz scores (Bar) */}
      <Card>
        <CardHeader><CardTitle>Quiz Scores</CardTitle></CardHeader>
        <CardContent>
          <Suspense fallback={<Skeleton className="h-40 w-full" />}>
            <BarChart data={quizBar} />
          </Suspense>
        </CardContent>
      </Card>
    </div>
  )
}

function computeRange(range: { preset: '7' | '30' | 'all' | 'custom'; from?: string; to?: string }) {
  if (range.preset === 'custom') return { from: range.from, to: range.to }
  const to = new Date()
  if (range.preset === '7') { const from = new Date(Date.now() - 7*86400000); return { from: toISO(from), to: toISO(to) } }
  if (range.preset === '30') { const from = new Date(Date.now() - 30*86400000); return { from: toISO(from), to: toISO(to) } }
  return { from: undefined, to: undefined }
}

function toISO(d: Date) { return d.toISOString().slice(0,10) }

function filterByRange(series: any[], range: { preset: '7' | '30' | 'all' | 'custom'; from?: string; to?: string }) {
  if (range.preset === 'all' || (!range.from && !range.to)) return series
  const fromTs = range.from ? new Date(range.from).getTime() : -Infinity
  const toTs = range.to ? new Date(range.to).getTime() : Infinity
  return series.filter((d) => {
    const ts = new Date(d.date).getTime()
    return ts >= fromTs && ts <= toTs
  })
}

function StatCard({ title, value, suffix = '' }: { title: string; value: number; suffix?: string }) {
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
      <Card>
        <CardHeader><CardTitle>{title}</CardTitle></CardHeader>
        <CardContent className="text-2xl font-semibold">{value}{suffix}</CardContent>
      </Card>
    </motion.div>
  )
}
