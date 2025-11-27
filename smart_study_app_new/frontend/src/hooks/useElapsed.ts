import { useEffect, useState } from 'react'

export function useElapsed(startISO?: string | null) {
  const [now, setNow] = useState<number>(Date.now())

  useEffect(() => {
    if (!startISO) return
    const id = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(id)
  }, [startISO])

  if (!startISO) return { seconds: 0, label: '0m 0s' }
  const start = new Date(startISO).getTime()
  const seconds = Math.max(0, Math.floor((now - start) / 1000))
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  const label = h > 0 ? `${h}h ${m}m ${s}s` : `${m}m ${s}s`
  return { seconds, label }
}
