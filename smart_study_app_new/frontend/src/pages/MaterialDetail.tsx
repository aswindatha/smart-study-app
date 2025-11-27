import { useParams } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import { getMaterial } from '@/lib/api'
import type { StudyMaterial } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Skeleton from '@/components/ui/skeleton'
import PDFViewer from '@/components/pdf/PDFViewer'
import AIToolsPanel from '@/components/ai/AIToolsPanel'
import { useSessionStore } from '@/store/session'
import { useElapsed } from '@/hooks/useElapsed'
import { toast } from 'sonner'
import { motion } from 'framer-motion'

function toUploadsUrl(file_path: string) {
  const norm = file_path.replace(/\\/g, '/');
  const idx = norm.toLowerCase().lastIndexOf('/uploads/')
  if (idx >= 0) {
    const suffix = norm.substring(idx)
    return suffix
  }
  // fallback: just try to use as-is
  return norm
}

export default function MaterialDetail() {
  const { id } = useParams()
  const [material, setMaterial] = useState<StudyMaterial | null>(null)
  const [loading, setLoading] = useState(true)
  const activeSession = useSessionStore((s) => s.activeSession)
  const startSession = useSessionStore((s) => s.startSession)
  const endSession = useSessionStore((s) => s.endSession)
  const { label } = useElapsed(activeSession?.start_time || null)

  useEffect(() => {
    async function load() {
      setLoading(true)
      const m = await getMaterial(Number(id))
      setMaterial(m)
      setLoading(false)
    }
    load()
  }, [id])

  const pdfUrl = useMemo(() => (material ? toUploadsUrl(material.file_path) : ''), [material])

  if (loading || !material) return <Skeleton className="h-96 w-full" />

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="grid gap-6 lg:grid-cols-2">
      <PDFViewer url={pdfUrl} />

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Study Session</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center justify-between gap-3">
            <div className="text-sm text-slate-600">
              {activeSession ? (
                <div>Active • Time spent: <span className="font-medium text-slate-900">{label}</span></div>
              ) : (
                <div>No active session</div>
              )}
            </div>
            <div className="flex gap-2">
              {!activeSession ? (
                <Button onClick={async () => {
                  try { await startSession(material.id); toast.success('Session started') } catch (e: any) { toast.error(e?.response?.data?.detail || 'Failed to start') }
                }}>Start Session</Button>
              ) : (
                <Button variant="secondary" onClick={async () => {
                  try { await endSession(); toast.success('Session ended') } catch (e: any) { toast.error(e?.response?.data?.detail || 'Failed to end') }
                }}>End Session</Button>
              )}
            </div>
          </CardContent>
        </Card>

        <AIToolsPanel materialId={material.id} />
      </div>
    </motion.div>
  )
}
