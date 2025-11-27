import { useState } from 'react'
import { Button } from '@/components/ui/button'

export default function GoToPageDialog({ open, onClose, numPages, onGo }: {
  open: boolean
  onClose: () => void
  numPages: number
  onGo: (n: number) => void
}) {
  const [value, setValue] = useState('')
  if (!open) return null
  function submit() {
    const n = parseInt(value || '0', 10)
    if (!Number.isFinite(n) || n < 1 || n > Math.max(1, numPages)) return
    onGo(n)
  }
  return (
    <div className="fixed inset-0 z-40 grid place-items-center bg-black/30 p-4">
      <div className="w-full max-w-sm rounded-lg border border-slate-200 bg-white p-4 shadow-lg dark:border-slate-800 dark:bg-slate-900">
        <div className="text-sm font-medium">Go to page</div>
        <div className="mt-2 text-xs text-slate-500">Enter a page number between 1 and {numPages || 1}.</div>
        <input
          className="mt-3 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 dark:bg-slate-900 dark:border-slate-700"
          placeholder="Page number"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') submit() }}
        />
        <div className="mt-3 flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={submit}>Go</Button>
        </div>
      </div>
    </div>
  )
}
