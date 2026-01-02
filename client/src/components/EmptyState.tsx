import React from 'react'
import { twMerge } from 'tailwind-merge'
import { Inbox, Search, AlertCircle, CheckCircle2 } from 'lucide-react'

interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: React.ReactNode
  className?: string
  variant?: 'default' | 'search' | 'error' | 'success'
}

/**
 * EmptyState Component
 * Consistent empty state display across the application
 */
export function EmptyState({ icon, title, description, action, className = '', variant = 'default' }: EmptyStateProps) {
  const getIcon = () => {
    if (icon) return icon

    switch (variant) {
      case 'search':
        return <Search className="w-12 h-12 text-gray-300" />
      case 'error':
        return <AlertCircle className="w-12 h-12 text-error" />
      case 'success':
        return <CheckCircle2 className="w-12 h-12 text-success" />
      default:
        return <Inbox className="w-12 h-12 text-gray-300" />
    }
  }

  return (
    <div className={twMerge('empty-state', className)}>
      <div className="mb-4">{getIcon()}</div>
      <h3 className="text-lg font-semibold text-text mb-1">{title}</h3>
      {description && (
        <p className="text-sm text-text-muted mb-4 max-w-md">{description}</p>
      )}
      {action && <div className="mt-2">{action}</div>}
    </div>
  )
}

/**
 * EmptyStateAction Component
 * Pre-styled action buttons for EmptyState
 */
export function EmptyStateAction({
  children,
  onClick,
  variant = 'primary'
}: {
  children: React.ReactNode
  onClick: () => void
  variant?: 'primary' | 'outline'
}) {
  const variantClasses = {
    primary: 'bg-primary hover:bg-primary-dark text-white',
    outline: 'border border-border hover:bg-surface text-text',
  }

  return (
    <button
      onClick={onClick}
      className={twMerge(
        'px-4 py-2 rounded-lg font-medium transition-colors active:scale-95',
        variantClasses[variant]
      )}
    >
      {children}
    </button>
  )
}
