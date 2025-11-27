import React from 'react'
import { cn } from '@/utils/cn'

type Props = React.InputHTMLAttributes<HTMLInputElement>
export const Input = React.forwardRef<HTMLInputElement, Props>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(
      'flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus-visible:outline-none focus:ring-2 focus:ring-blue-500',
      className
    )}
    {...props}
  />
))
Input.displayName = 'Input'
