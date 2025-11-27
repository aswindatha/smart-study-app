import React from 'react'

export default function DateRangeSelector({ value, onChange }: {
  value: { preset: '7' | '30' | 'all' | 'custom'; from?: string; to?: string }
  onChange: (v: { preset: '7' | '30' | 'all' | 'custom'; from?: string; to?: string }) => void
}) {
  function setPreset(preset: '7' | '30' | 'all' | 'custom') {
    const next = { ...value, preset }
    if (preset !== 'custom') { delete next.from; delete next.to }
    onChange(next)
  }
  return (
    <div className="flex items-center gap-2 text-sm">
      <select
        className="h-9 rounded-md border border-slate-300 bg-white px-2 dark:bg-slate-900 dark:border-slate-700"
        value={value.preset}
        onChange={(e) => setPreset(e.target.value as any)}
      >
        <option value="7">Last 7 days</option>
        <option value="30">Last 30 days</option>
        <option value="all">All</option>
        <option value="custom">Custom</option>
      </select>
      {value.preset === 'custom' && (
        <>
          <input
            type="date"
            className="h-9 rounded-md border border-slate-300 bg-white px-2 dark:bg-slate-900 dark:border-slate-700"
            value={value.from || ''}
            onChange={(e) => onChange({ ...value, from: e.target.value })}
          />
          <input
            type="date"
            className="h-9 rounded-md border border-slate-300 bg-white px-2 dark:bg-slate-900 dark:border-slate-700"
            value={value.to || ''}
            onChange={(e) => onChange({ ...value, to: e.target.value })}
          />
        </>
      )}
    </div>
  )
}
