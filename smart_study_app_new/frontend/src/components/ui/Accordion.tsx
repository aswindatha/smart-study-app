import React, { useState } from 'react'
import { cn } from '@/utils/cn'
import { ChevronDown } from 'lucide-react'

export interface AccordionItemProps {
  id: string
  title: React.ReactNode
  badge?: React.ReactNode
  children: React.ReactNode
  defaultOpen?: boolean
}

export function AccordionItem({ id, title, badge, children, defaultOpen }: AccordionItemProps) {
  const [open, setOpen] = useState(!!defaultOpen)
  return (
    <div className="rounded-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className={cn(
          'flex w-full items-center justify-between gap-3 rounded-md px-3 py-2 text-left',
          'hover:bg-slate-50 dark:hover:bg-slate-800'
        )}
      >
        <div className="flex items-center gap-2">
          <ChevronDown size={16} className={cn('transition-transform', open ? 'rotate-180' : '')} />
          <div className="font-medium">{title}</div>
          {badge}
        </div>
      </button>
      {open && <div className="border-t border-slate-200 dark:border-slate-800 p-3">{children}</div>}
    </div>
  )
}

export default function Accordion({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <div className={cn('space-y-2', className)}>{children}</div>
}
