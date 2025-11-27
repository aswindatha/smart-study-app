import React from 'react'
import { cn } from '@/utils/cn'

type Props = React.TextareaHTMLAttributes<HTMLTextAreaElement>
export const Textarea = React.forwardRef<HTMLTextAreaElement, Props>(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={cn(
      'flex min-h-[80px] w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus-visible:outline-none focus:ring-2 focus:ring-blue-500',
      className
    )}
    {...props}
  />
))
Textarea.displayName = 'Textarea'
