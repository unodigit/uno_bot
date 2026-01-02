import React from 'react'
import { twMerge } from 'tailwind-merge'

export type BadgeVariant = 'primary' | 'success' | 'error' | 'warning' | 'info' | 'neutral'

interface BadgeProps {
  children: React.ReactNode
  variant?: BadgeVariant
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

/**
 * Badge Component
 * Consistent badge styling across the application
 */
export function Badge({ children, variant = 'neutral', className = '', size = 'md' }: BadgeProps) {
  const variantClasses: Record<BadgeVariant, string> = {
    primary: 'bg-primary/10 text-primary border-primary/20',
    success: 'bg-success/10 text-success border-success/20',
    error: 'bg-error/10 text-error border-error/20',
    warning: 'bg-warning/10 text-warning border-warning/20',
    info: 'bg-blue-100 text-blue-700 border-blue-200',
    neutral: 'bg-gray-100 text-gray-700 border-gray-200',
  }

  const sizeClasses: Record<string, string> = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  }

  return (
    <span
      className={twMerge(
        'inline-flex items-center gap-1 rounded-full border font-medium',
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
    >
      {children}
    </span>
  )
}

/**
 * StatusBadge Component
 * Badge with a dot indicator for status
 */
interface StatusBadgeProps {
  status: 'active' | 'inactive' | 'pending' | 'completed' | 'error'
  label?: string
  className?: string
}

export function StatusBadge({ status, label, className = '' }: StatusBadgeProps) {
  const statusConfig = {
    active: { color: 'bg-success', text: 'text-success', label: label || 'Active' },
    inactive: { color: 'bg-gray-400', text: 'text-gray-600', label: label || 'Inactive' },
    pending: { color: 'bg-warning', text: 'text-warning', label: label || 'Pending' },
    completed: { color: 'bg-primary', text: 'text-primary', label: label || 'Completed' },
    error: { color: 'bg-error', text: 'text-error', label: label || 'Error' },
  }

  const config = statusConfig[status]

  return (
    <span className={twMerge('inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium bg-gray-50', className)}>
      <span className={twMerge('w-2 h-2 rounded-full', config.color)} />
      <span className={config.text}>{config.label}</span>
    </span>
  )
}
