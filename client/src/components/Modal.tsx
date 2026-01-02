import React, { ReactNode } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import { twMerge } from 'tailwind-merge'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: ReactNode
  footer?: ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

export function Modal({ isOpen, onClose, title, children, footer, size = 'md', className = '' }: ModalProps) {
  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="modal-overlay"
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Modal Content */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            className={twMerge(
              'modal-content',
              sizeClasses[size],
              className
            )}
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-border">
              <h2 id="modal-title" className="text-lg font-semibold text-text">
                {title}
              </h2>
              <button
                onClick={onClose}
                className="p-2 hover:bg-surface rounded transition-colors"
                aria-label="Close modal"
              >
                <X className="w-5 h-5 text-text-muted" />
              </button>
            </div>

            {/* Body */}
            <div className="max-h-[70vh] overflow-y-auto scrollbar-thin">
              {children}
            </div>

            {/* Footer */}
            {footer && (
              <div className="mt-4 pt-4 border-t border-border flex justify-end gap-2">
                {footer}
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

// Pre-styled modal buttons
export function ModalButton({
  children,
  onClick,
  variant = 'primary',
  disabled = false
}: {
  children: ReactNode
  onClick: () => void
  variant?: 'primary' | 'secondary' | 'destructive' | 'outline'
  disabled?: boolean
}) {
  const variantClasses = {
    primary: 'bg-primary hover:bg-primary-dark text-white',
    secondary: 'bg-surface hover:bg-gray-200 text-text',
    destructive: 'bg-error hover:bg-red-600 text-white',
    outline: 'border border-border hover:bg-surface text-text',
  }

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={twMerge(
        'px-4 py-2 rounded-lg font-medium transition-colors active:scale-95',
        'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
        disabled ? 'opacity-50 cursor-not-allowed' : '',
        variantClasses[variant]
      )}
    >
      {children}
    </button>
  )
}
