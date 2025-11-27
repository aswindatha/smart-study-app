import React from 'react'

export function Select({ value, onChange, children, className = '' }: {
  value?: string
  onChange?: (v: string) => void
  children: React.ReactNode
  className?: string
}) {
  return (
    <select
      className={`h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm focus:ring-2 focus:ring-blue-500 ${className}`}
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
    >
      {children}
    </select>
  )
}
