import React from 'react'
import { cn } from '@/utils/cn'

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'default' | 'secondary' | 'outline' | 'ghost' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
}

export const Button = React.forwardRef<HTMLButtonElement, Props>(
  ({ className, variant = 'default', size = 'md', ...props }, ref) => {
    const variants: Record<string, string> = {
      default: 'bg-primary text-white hover:bg-blue-600',
      secondary: 'bg-secondary text-secondary-foreground hover:bg-slate-200',
      outline: 'border border-slate-300 hover:bg-slate-100',
      ghost: 'hover:bg-slate-100',
      destructive: 'bg-red-600 text-white hover:bg-red-700',
    }
    const sizes: Record<string, string> = {
      sm: 'h-8 px-3 text-sm',
      md: 'h-10 px-4',
      lg: 'h-12 px-6 text-lg',
    }
    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50',
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'
