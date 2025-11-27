import { useEffect, useMemo, useState } from 'react'
import { listMaterials, listSessions, startSession, endSession } from '@/lib/api'
import type { StudyMaterial, StudySession } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select } from '@/components/ui/select'
import Skeleton from '@/components/ui/skeleton'

export default function StudySessions() {
  const [materials, setMaterials] = useState<StudyMaterial[]>([])
  const [sessions, setSessions] = useState<StudySession[]>([])
  const [materialId, setMaterialId] = useState<string>('')
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true)
    const [m, s] = await Promise.all([listMaterials(), listSessions()])
    setMaterials(m)
    setSessions(s)
    setLoading(false)
  }
  useEffect(() => { load() }, [])

  const activeSession = useMemo(() => sessions.find((s) => !s.end_time), [sessions])

  async function start() {
    if (!materialId) return
    await startSession(Number(materialId))
    await load()
  }
  async function end() {
    if (!activeSession) return
    await endSession(activeSession.id)
    await load()
  }

  if (loading) return <Skeleton className="h-64 w-full" />

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader><CardTitle>Manage Session</CardTitle></CardHeader>
        <CardContent className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="flex-1">
            <label className="mb-1 block text-sm font-medium">Material</label>
            <Select value={materialId} onChange={setMaterialId}>
              <option value="">Select material</option>
              {materials.map((m) => (
                <option key={m.id} value={m.id.toString()}>{m.title}</option>
              ))}
            </Select>
          </div>
          <div className="flex gap-2">
            <Button onClick={start} disabled={!!activeSession}>Start</Button>
            <Button onClick={end} variant="secondary" disabled={!activeSession}>End</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>History</CardTitle></CardHeader>
        <CardContent>
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b">
                <th className="py-2">ID</th>
                <th className="py-2">Material</th>
                <th className="py-2">Start</th>
                <th className="py-2">End</th>
                <th className="py-2">Duration</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((s) => {
                const m = materials.find((m) => m.id === s.material_id)
                return (
                  <tr key={s.id} className="border-b">
                    <td className="py-2">{s.id}</td>
                    <td className="py-2">{m?.title || s.material_id}</td>
                    <td className="py-2">{new Date(s.start_time).toLocaleString()}</td>
                    <td className="py-2">{s.end_time ? new Date(s.end_time).toLocaleString() : '-'}</td>
                    <td className="py-2">{s.duration_minutes || 0} mins</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  )
}
