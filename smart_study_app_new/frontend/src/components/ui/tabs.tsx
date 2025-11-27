import React, { useState } from 'react'
import { cn } from '@/utils/cn'

export function Tabs({ tabs, defaultTab, onChange }: {
  tabs: { id: string; label: string; content: React.ReactNode }[]
  defaultTab?: string
  onChange?: (id: string) => void
}) {
  const [active, setActive] = useState<string>(defaultTab || tabs[0]?.id)
  return (
    <div>
      <div className="mb-3 flex gap-2 border-b">
        {tabs.map((t) => (
          <button
            key={t.id}
            className={cn(
              'rounded-t-md px-3 py-2 text-sm',
              active === t.id ? 'bg-white font-medium shadow-inner' : 'text-slate-600 hover:text-slate-900'
            )}
            onClick={() => { setActive(t.id); onChange?.(t.id) }}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div>
        {tabs.find((t) => t.id === active)?.content}
      </div>
    </div>
  )
}
